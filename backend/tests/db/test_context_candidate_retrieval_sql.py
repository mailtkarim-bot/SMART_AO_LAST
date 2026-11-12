import json
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionFragmentRecord
from app.modules.knowledge.application.context_candidate_retrieval import ContextCandidateRetrieval
from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
from app.modules.knowledge.domain.retrieval import RetrievalScope
from tests.db.test_candidate_retrieval_sql import SqlProbeEncoder, _append, _clone, _successor
from tests.db.test_knowledge_source_freshness import indexed_source as indexed_source
from tests.db.test_knowledge_source_freshness import seed_indexed_source

ROOT = Path(__file__).resolve().parents[3]
QUERY = "Pour préparer notre offre, la visite médicale est-elle obligatoire pour le lot 7 ?"
TEXT = "Lot 7 : la visite médicale est obligatoire."


def service(seed):
    p = CandidateRetrievalProfile(
        **json.loads(
            (ROOT / "ops/retrieval-candidate/profile-context-transport-v1.json").read_text()
        )
    )
    encoder = SqlProbeEncoder(p)
    return ContextCandidateRetrieval(transport_profile=p, source=seed[7], encoder=encoder), encoder


def scope(seed):
    return RetrievalScope(tenant_id=seed[0], case_id=seed[1], dce_version_id=seed[2])


def empty(result):
    r = result.reading
    assert r.answer_state == "UNKNOWN" and not r.hits and not r.score_trace
    assert (
        not r.rc_projection.clauses
        and not r.rc_projection.unknown_regions
        and not r.rc_projection.links
    )
    assert not r.rc_unscoped_evidence and not r.visit_type_evidence and not r.review_source_ids


@pytest.mark.parametrize(
    "text,unknown",
    [
        (TEXT, False),
        (TEXT.replace("est obligatoire", "n'est pas obligatoire"), False),
        (TEXT + " Sauf dispense.", True),
    ],
)
def test_sql_exact_fragment_provenance_and_read_only_call(
    session_factory, indexed_source, text, unknown
):
    extraction, fragment = _append(session_factory, indexed_source, text=text)
    adapter, encoder = service(indexed_source)
    engine = session_factory.kw["bind"]
    statements = []

    def capture(*args):
        statements.append(args[2])

    sa.event.listen(engine, "before_cursor_execute", capture)
    try:
        result = adapter.retrieve(query=QUERY, scope=scope(indexed_source))
    finally:
        sa.event.remove(engine, "before_cursor_execute", capture)
    assert len(statements) == 3 and all(s.lstrip().upper().startswith("SELECT") for s in statements)
    r = result.reading
    assert encoder.queries == [QUERY] and encoder.passages == [(text,)]
    assert result.recognition.context_evidence and r.query_intent == result.recognition.intent
    assert len(r.hits) == 1 and r.answer_state == "UNKNOWN"
    assert r.state == ("REVIEW_REQUIRED" if unknown else "CANDIDATES_ONLY")
    assert r.score_trace[0].decision == "RC_TYPED_RESCUE" and r.score_trace[0].threshold == 0.85
    with session_factory() as s:
        row = s.get(DceDocumentExtractionFragmentRecord, fragment)
        assert row.extraction_id == extraction
        for h in r.hits:
            assert (
                h.result.chunk.source_fragment_id == fragment
                and h.result.chunk.dce_version_id == indexed_source[2]
            )
            assert h.source_sha256 == row.text_sha256 == sha256(row.text.encode()).hexdigest()
            assert row.text.encode()[h.start_byte : h.end_byte] == h.result.chunk.text.encode()
            assert h.result.chunk.locator["page"] == row.locator_json["page"] == 7
            assert h.result.chunk.locator["region"] == row.locator_json["region"]
        for c in (*r.rc_projection.clauses, *r.rc_projection.unknown_regions):
            assert c.source_fragment_id == fragment and c.source_sha256 == row.text_sha256
            assert row.text.encode()[c.start_byte : c.end_byte] == c.excerpt.encode()
            assert c.locator["region"] == row.locator_json["region"]
    assert result == adapter.retrieve(query=QUERY, scope=scope(indexed_source))


@pytest.mark.parametrize(
    "status", ["REVIEW_REQUIRED", "FAILED_SAFE", "UNSUPPORTED", "REJECTED_LIMIT"]
)
def test_sql_incomplete_extraction_never_encodes_partial_or_predecessor(
    session_factory, indexed_source, status
):
    _append(session_factory, indexed_source, text=TEXT, status=status)
    adapter, encoder = service(indexed_source)
    empty(adapter.retrieve(query=QUERY, scope=scope(indexed_source)))
    assert not encoder.passages and not encoder.queries


@pytest.mark.parametrize("field", ["tenant_id", "case_id", "dce_version_id"])
def test_sql_populated_foreign_scope_and_poison_hash_are_not_observable(
    session_factory, indexed_source, field
):
    _append(session_factory, indexed_source, text=TEXT)
    foreign = seed_indexed_source(session_factory)
    _append(session_factory, foreign, text=TEXT, fragment_hash="0" * 64)
    adapter, encoder = service(indexed_source)
    assert adapter.retrieve(query=QUERY, scope=scope(indexed_source)).reading.hits
    encoder.queries.clear()
    encoder.passages.clear()
    value = foreign[{"tenant_id": 0, "case_id": 1, "dce_version_id": 2}[field]]
    empty(adapter.retrieve(query=QUERY, scope=replace(scope(indexed_source), **{field: value})))
    assert not encoder.passages and not encoder.queries


def test_sql_financial_and_uncovered_requests_never_read(
    session_factory, indexed_source, monkeypatch
):
    adapter, encoder = service(indexed_source)
    monkeypatch.setattr(
        indexed_source[7], "read_chunks", lambda **kw: pytest.fail("refused query read SQL")
    )
    with pytest.raises(FinancialRetrievalQueryRejected):
        adapter.retrieve(
            query="Pour préparer notre réponse à la DPGF, la visite est-elle obligatoire ?",
            scope=scope(indexed_source),
        )
    empty(
        adapter.retrieve(
            query="Pour information, où a lieu la visite ?", scope=scope(indexed_source)
        )
    )
    assert not encoder.passages and not encoder.queries


def test_sql_discordant_hashes_refuse_without_encoder(session_factory, indexed_source):
    _append(session_factory, indexed_source, text=TEXT, fragment_hash="0" * 64)
    adapter, encoder = service(indexed_source)
    with pytest.raises(ValueError, match="^DCE_FRAGMENT_INTEGRITY_MISMATCH$"):
        adapter.retrieve(query=QUERY, scope=scope(indexed_source))
    assert not encoder.passages and not encoder.queries


def test_sql_input_hash_mismatch_has_no_fallback_to_old_extraction(session_factory, indexed_source):
    _append(session_factory, indexed_source, text=TEXT, input_hash="0" * 64)
    adapter, encoder = service(indexed_source)
    empty(adapter.retrieve(query=QUERY, scope=scope(indexed_source)))
    assert not encoder.passages and not encoder.queries


@pytest.mark.parametrize("phase", ["encoding", "projection"])
def test_sql_invalidation_clears_proofs_and_preserves_history(
    session_factory, indexed_source, monkeypatch, phase
):
    from app.modules.knowledge.application import context_candidate_retrieval as module

    _, fragment = _append(session_factory, indexed_source, text=TEXT)
    adapter, encoder = service(indexed_source)

    def invalidate():
        _append(session_factory, indexed_source, text=TEXT, status="REVIEW_REQUIRED")

    if phase == "encoding":
        encoder.after_query = invalidate
    else:
        original = module._projection
        changed = False

        def update(hits, sources):
            nonlocal changed
            result = original(hits, sources)
            if not changed:
                invalidate()
                changed = True
            return result

        monkeypatch.setattr(module, "_projection", update)
    result = adapter.retrieve(query=QUERY, scope=scope(indexed_source))
    empty(result)
    assert result.reading.reason == "SOURCE_CHANGED" and result.recognition.context_evidence
    with session_factory() as s:
        assert s.get(DceDocumentExtractionFragmentRecord, fragment) is not None


def test_sql_rectificatif_refuses_old_scope_and_reads_new_exact_source(
    session_factory, indexed_source
):
    _append(session_factory, indexed_source, text=TEXT)
    adapter, encoder = service(indexed_source)
    assert adapter.retrieve(query=QUERY, scope=scope(indexed_source)).reading.hits
    successor, text = _successor(session_factory, indexed_source)
    _, fragment = _append(session_factory, successor, text=text)

    def switch():
        with session_factory.begin() as s:
            s.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == indexed_source[1])
                .values(applicable_dce_version_id=successor[2], dce_freshness="REVIEW_REQUIRED")
            )

    encoder.after_query = switch
    changed = adapter.retrieve(query=QUERY, scope=scope(indexed_source))
    empty(changed)
    assert changed.reading.reason == "SOURCE_CHANGED"
    encoder.after_query = lambda: None
    empty(adapter.retrieve(query=QUERY, scope=scope(indexed_source)))
    new = adapter.retrieve(query=QUERY, scope=scope(successor)).reading
    assert {h.result.chunk.source_fragment_id for h in new.hits} == {fragment}
    assert not new.rc_projection.links and new.state == "REVIEW_REQUIRED"
    assert new.rc_projection.clauses[0].value == "NOT_REQUIRED"
    assert all(c.dce_version_id == successor[2] for c in new.rc_projection.clauses)


def test_sql_same_tenant_other_affaire_cannot_borrow_predecessor_proofs(
    session_factory, indexed_source
):
    _append(session_factory, indexed_source, text=TEXT)
    adapter, encoder = service(indexed_source)
    assert adapter.retrieve(query=QUERY, scope=scope(indexed_source)).reading.hits
    successor, text = _successor(session_factory, indexed_source)
    _, fragment = _append(session_factory, successor, text=text)
    other = uuid4()
    with session_factory.begin() as s:
        original = s.get(CaseRecord, indexed_source[1])
        s.add(
            _clone(
                original,
                id=other,
                applicable_dce_version_id=successor[2],
                functional_identity_hash=sha256(str(other).encode()).hexdigest(),
                scope_fingerprint=sha256(str(other).encode()).hexdigest(),
            )
        )
    empty(adapter.retrieve(query=QUERY, scope=replace(scope(indexed_source), case_id=other)))
    new = adapter.retrieve(query=QUERY, scope=replace(scope(successor), case_id=other)).reading
    assert {h.result.chunk.source_fragment_id for h in new.hits} == {fragment}
    assert all(c.case_id == other for c in new.rc_projection.clauses)
