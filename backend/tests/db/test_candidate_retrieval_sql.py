"""SQL source / v6 contract only: deterministic vectors, no model or active factory."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
from math import sqrt
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService
from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
from app.modules.knowledge.domain.retrieval import RetrievalScope
from tests.db.test_knowledge_source_freshness import NOW, seed_indexed_source
from tests.db.test_knowledge_source_freshness import indexed_source as indexed_source

TEXT = "Équipement synthétique. Lot 7 : la visite médicale est obligatoire."
QUERY = "La visite médicale est-elle obligatoire pour le lot 7 ?"


class SqlProbeEncoder:
    def __init__(self, profile):
        self.profile_id = profile.profile_id
        self.passages = []
        self.queries = []
        self.after_query = lambda: None

    def encode_passages(self, texts):
        self.passages.append(tuple(texts))
        return [(0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382 for _ in texts]

    def encode_query(self, text):
        self.queries.append(text)
        self.after_query()
        return (1.0,) + (0.0,) * 383


def _append(
    session_factory,
    seed,
    *,
    text=TEXT,
    status="COMPLETED",
    same_time=False,
    fragment_hash=None,
    input_hash=None,
):
    tenant, _, version, document, _, _, digest, _, _ = seed
    extraction = uuid4()
    fragment = uuid4() if status in {"COMPLETED", "REVIEW_REQUIRED"} else None
    with session_factory.begin() as session:
        session.add(
            DceDocumentExtractionRecord(
                id=extraction,
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                input_sha256=input_hash or digest,
                extractor_id=f"sql-v6-{extraction}",
                extractor_version="1",
                status=status,
                fragment_count=1 if fragment else 0,
                extracted_char_count=len(text) if fragment else 0,
                failure_code=None if status == "COMPLETED" else "SYNTHETIC_INCOMPLETE",
                created_at=NOW if same_time else NOW + timedelta(seconds=1),
            )
        )
        session.flush()
        if fragment:
            session.add(
                DceDocumentExtractionFragmentRecord(
                    id=fragment,
                    tenant_id=tenant,
                    extraction_id=extraction,
                    ordinal=1,
                    locator_json={"kind": "pdf_region", "page": 7, "region": [12, 30, 400, 90]},
                    text=text,
                    text_sha256=fragment_hash or sha256(text.encode()).hexdigest(),
                )
            )
    return extraction, fragment


def _candidate(seed):
    profile = CandidateRetrievalProfile(
        **json.loads(
            (
                Path(__file__).resolve().parents[3] / "ops/retrieval-candidate/profile-v6.json"
            ).read_text()
        )
    )
    encoder = SqlProbeEncoder(profile)
    return CandidateRetrievalService(profile=profile, source=seed[7], encoder=encoder), encoder


def _scope(seed):
    return RetrievalScope(tenant_id=seed[0], case_id=seed[1], dce_version_id=seed[2])


def _empty(reading):
    assert reading.answer_state == "UNKNOWN"
    assert not reading.hits and not reading.score_trace and not reading.visit_type_evidence
    assert not reading.rc_projection.clauses and not reading.rc_projection.links
    assert not reading.rc_unscoped_evidence and not reading.review_source_ids


@pytest.mark.parametrize(
    "text,unknown",
    [
        (TEXT, False),
        (TEXT.replace("est obligatoire", "n'est pas obligatoire"), False),
        (TEXT + " Sauf dispense écrite.", True),
        (TEXT + " Annexe. " * 150 + "Sauf dispense écrite.", True),
    ],
)
def test_v6_sql_proofs_use_exact_stored_fragment_and_regions(
    session_factory,
    indexed_source,
    text,
    unknown,
):
    extraction, fragment = _append(session_factory, indexed_source, text=text)
    service, encoder = _candidate(indexed_source)
    result = service.retrieve(query=QUERY, scope=_scope(indexed_source))
    assert result.hits and result.answer_state == "UNKNOWN"
    assert result.profile_id == service.profile.profile_id
    assert any(t.decision == "RC_TYPED_RESCUE" for t in result.score_trace)
    assert result == service.retrieve(query=QUERY, scope=_scope(indexed_source))
    assert len(encoder.passages) == 1
    with session_factory() as session:
        row = session.get(DceDocumentExtractionFragmentRecord, fragment)
        assert row.extraction_id == extraction and row.tenant_id == indexed_source[0]
        assert row.text_sha256 == sha256(text.encode()).hexdigest()
        for hit in result.hits:
            assert hit.result.chunk.source_fragment_id == fragment
            assert hit.source_sha256 == row.text_sha256
            raw = text.encode()[hit.start_byte : hit.end_byte]
            assert raw.decode() == hit.result.chunk.text
            assert sha256(raw).hexdigest() == hit.segment_sha256
            assert all(hit.result.chunk.locator[k] == v for k, v in row.locator_json.items())
        proofs = [p for p in result.visit_type_evidence if p.directive_signal == "CANDIDATE"]
        assert proofs
        for p in proofs:
            assert p.source_fragment_id == fragment and p.dce_version_id == indexed_source[2]
            assert text.encode()[p.start_byte : p.end_byte].decode() == p.excerpt
            assert p.source_sha256 == row.text_sha256 and p.lot == 7
            anchor = p.visit_type_proof
            assert anchor.signal == "VISIT_MEDICAL"
            assert text.encode()[anchor.start_byte : anchor.end_byte].decode() == anchor.excerpt
            if unknown:
                assert p.value == p.kind == "UNKNOWN" and p.condition_signals
                for a in p.condition_signals:
                    assert text.encode()[a.start_byte : a.end_byte].decode() == a.excerpt
        if not unknown:
            assert {p.kind for p in proofs} == ({"NEGATION"} if "n'est" in text else {"ASSERTION"})


@pytest.mark.parametrize(
    "status", ["REVIEW_REQUIRED", "FAILED_SAFE", "UNSUPPORTED", "REJECTED_LIMIT"]
)
@pytest.mark.parametrize("same_time", [False, True])
def test_v6_sql_incomplete_extraction_never_encodes_available_partial_text(
    session_factory,
    indexed_source,
    status,
    same_time,
):
    extraction, fragment = _append(
        session_factory, indexed_source, status=status, same_time=same_time
    )
    service, encoder = _candidate(indexed_source)
    _empty(service.retrieve(query=QUERY, scope=_scope(indexed_source)))
    assert encoder.passages == encoder.queries == []
    with session_factory() as session:
        assert session.get(DceDocumentExtractionRecord, extraction).status == status
        if fragment:
            assert session.get(DceDocumentExtractionFragmentRecord, fragment) is not None


@pytest.mark.parametrize("phase", ["cached", "during_query"])
def test_v6_sql_new_extraction_invalidates_proofs_and_cached_vectors(
    session_factory,
    indexed_source,
    phase,
):
    _, old_fragment = _append(session_factory, indexed_source)
    service, encoder = _candidate(indexed_source)
    assert service.retrieve(query=QUERY, scope=_scope(indexed_source)).hits

    def invalidate():
        # A later refusal supersedes the eligible extraction, even with stored text.
        with session_factory.begin() as session:
            session.add(
                DceDocumentExtractionRecord(
                    id=uuid4(),
                    tenant_id=indexed_source[0],
                    dce_version_id=indexed_source[2],
                    dce_document_id=indexed_source[3],
                    input_sha256=indexed_source[6],
                    extractor_id="later-refusal",
                    extractor_version="1",
                    status="REVIEW_REQUIRED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC_INCOMPLETE",
                    created_at=NOW + timedelta(seconds=2),
                )
            )

    if phase == "cached":
        invalidate()
    else:
        encoder.after_query = invalidate
    result = service.retrieve(query=QUERY, scope=_scope(indexed_source))
    _empty(result)
    assert result.reason == ("NO_CURRENT_SOURCE" if phase == "cached" else "SOURCE_CHANGED")
    with session_factory() as session:
        assert session.get(DceDocumentExtractionFragmentRecord, old_fragment) is not None


@pytest.mark.parametrize("field", ["tenant_id", "case_id", "dce_version_id"])
def test_v6_sql_foreign_scope_cannot_reuse_warm_proofs(session_factory, indexed_source, field):
    _append(session_factory, indexed_source)
    service, encoder = _candidate(indexed_source)
    assert service.retrieve(query=QUERY, scope=_scope(indexed_source)).hits
    other = seed_indexed_source(session_factory)
    _append(session_factory, other, text=TEXT.replace("Lot 7", "Lot 8"))
    before = (len(encoder.passages), len(encoder.queries))
    foreign = getattr(_scope(other), field)
    _empty(service.retrieve(query=QUERY, scope=replace(_scope(indexed_source), **{field: foreign})))
    assert before == (len(encoder.passages), len(encoder.queries))


def test_v6_sql_financial_refusal_precedes_reader_and_encoder(indexed_source, monkeypatch):
    service, encoder = _candidate(indexed_source)
    monkeypatch.setattr(
        indexed_source[7], "read_chunks", lambda **kw: pytest.fail("financial SQL read")
    )
    with pytest.raises(FinancialRetrievalQueryRejected, match="FINANCIAL_RETRIEVAL_SCOPE_REQUIRED"):
        service.retrieve(query="Quel est le montant DPGF du lot 7 ?", scope=_scope(indexed_source))
    assert encoder.passages == encoder.queries == []


@pytest.mark.parametrize("phase", ["cached", "during_query"])
def test_v6_sql_rectificatif_switch_refuses_predecessor_scope(
    session_factory, indexed_source, phase
):
    _append(session_factory, indexed_source)
    service, encoder = _candidate(indexed_source)
    assert service.retrieve(query=QUERY, scope=_scope(indexed_source)).hits
    successor = uuid4()

    def switch():
        with session_factory.begin() as session:
            old = session.get(DceVersionRecord, indexed_source[2])
            values = {c.name: getattr(old, c.name) for c in DceVersionRecord.__table__.columns}
            values.update(
                id=successor,
                predecessor_dce_version_id=old.id,
                corpus_hash=sha256(str(successor).encode()).hexdigest(),
            )
            session.add(DceVersionRecord(**values))
            session.flush()
            session.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == indexed_source[1])
                .values(applicable_dce_version_id=successor, dce_freshness="REVIEW_REQUIRED")
            )

    if phase == "cached":
        switch()
    else:
        encoder.after_query = switch
    result = service.retrieve(query=QUERY, scope=_scope(indexed_source))
    _empty(result)
    assert result.reason == ("NO_CURRENT_SOURCE" if phase == "cached" else "SOURCE_CHANGED")
    encoder.after_query = lambda: None
    _empty(
        service.retrieve(
            query=QUERY, scope=replace(_scope(indexed_source), dce_version_id=successor)
        )
    )


def test_v6_sql_discordant_stored_hash_is_never_promoted(session_factory, indexed_source):
    _append(session_factory, indexed_source, fragment_hash="0" * 64)
    service, encoder = _candidate(indexed_source)
    with pytest.raises(ValueError, match="^DCE_FRAGMENT_INTEGRITY_MISMATCH$"):
        service.retrieve(query=QUERY, scope=_scope(indexed_source))
    assert encoder.passages == encoder.queries == []


def _clone(row, **overrides):
    values = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    return type(row)(**(values | overrides))


def _successor(session_factory, seed):
    tenant, case, version, document, _, _, _, _, _ = seed
    successor, staged, new_document = uuid4(), uuid4(), uuid4()
    text = "Rectificatif : lot 7 : la visite médicale n'est pas obligatoire."
    digest = sha256(text.encode()).hexdigest()
    with session_factory.begin() as session:
        old = session.get(DceVersionRecord, version)
        session.add(
            _clone(old, id=successor, predecessor_dce_version_id=version, corpus_hash=digest)
        )
        session.flush()
        old_doc = session.get(DceDocumentRecord, document)
        old_staged = session.get(DceStagedObjectRecord, old_doc.storage_object_id)
        key = f"synthetic/{staged}"
        session.add(
            _clone(
                old_staged,
                id=staged,
                storage_key=key,
                consumed_by_dce_version_id=successor,
                sha256=digest,
                expected_byte_size=len(text.encode()),
                actual_byte_size=len(text.encode()),
            )
        )
        session.flush()
        session.add(
            _clone(
                old_doc,
                id=new_document,
                dce_version_id=successor,
                storage_object_id=staged,
                storage_key=key,
                sha256=digest,
                byte_size=len(text.encode()),
            )
        )
    return (tenant, case, successor, new_document, seed[4], seed[5], digest, seed[7], seed[8]), text


def test_v6_sql_rectificatif_new_proofs_do_not_inherit_old_conditions(
    session_factory, indexed_source
):
    _, old_fragment = _append(session_factory, indexed_source, text=TEXT + " Sauf dispense écrite.")
    service, encoder = _candidate(indexed_source)
    first = service.retrieve(query=QUERY, scope=_scope(indexed_source))
    assert first.hits and all(p.value == "UNKNOWN" for p in first.visit_type_evidence)
    new_seed, text = _successor(session_factory, indexed_source)
    _, new_fragment = _append(session_factory, new_seed, text=text)
    with session_factory.begin() as session:
        session.execute(
            sa.update(CaseRecord)
            .where(CaseRecord.id == indexed_source[1])
            .values(applicable_dce_version_id=new_seed[2], dce_freshness="CURRENT")
        )
    _empty(service.retrieve(query=QUERY, scope=_scope(indexed_source)))
    reading = service.retrieve(query=QUERY, scope=_scope(new_seed))
    assert reading.hits and reading.answer_state == "UNKNOWN"
    assert {h.result.chunk.source_fragment_id for h in reading.hits} == {new_fragment}
    assert all(
        p.dce_version_id == new_seed[2] and p.kind == "RECTIFICATION" and not p.condition_signals
        for p in reading.visit_type_evidence
    )
    assert not reading.rc_projection.links  # No implicit contractual precedence.
    assert len(encoder.passages) == 2
    with session_factory() as session:
        assert session.get(DceDocumentExtractionFragmentRecord, old_fragment) is not None


def test_v6_sql_extraction_input_must_match_document_hash(session_factory, indexed_source):
    _append(session_factory, indexed_source, input_hash="0" * 64)
    service, encoder = _candidate(indexed_source)
    _empty(service.retrieve(query=QUERY, scope=_scope(indexed_source)))
    assert encoder.passages == encoder.queries == []


def test_v6_sql_document_from_other_version_is_not_claimed_as_current(
    session_factory, indexed_source
):
    new_seed, text = _successor(session_factory, indexed_source)
    wrong = list(new_seed)
    wrong[2] = indexed_source[2]  # Same tenant, extraction falsely claims predecessor version.
    _, fragment = _append(session_factory, wrong, text=text)
    chunks = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    assert fragment not in {c.source_fragment_id for c in chunks}


def test_v6_sql_same_tenant_other_case_cannot_borrow_version_or_warm_proofs(
    session_factory, indexed_source
):
    _append(session_factory, indexed_source)
    service, _ = _candidate(indexed_source)
    assert service.retrieve(query=QUERY, scope=_scope(indexed_source)).hits
    successor_seed, text = _successor(session_factory, indexed_source)
    _, fragment = _append(session_factory, successor_seed, text=text)
    other_case = uuid4()
    with session_factory.begin() as session:
        original = session.get(CaseRecord, indexed_source[1])
        session.add(
            _clone(
                original,
                id=other_case,
                applicable_dce_version_id=successor_seed[2],
                functional_identity_hash=sha256(str(other_case).encode()).hexdigest(),
                scope_fingerprint=sha256(str(other_case).encode()).hexdigest(),
            )
        )
    _empty(service.retrieve(query=QUERY, scope=replace(_scope(indexed_source), case_id=other_case)))
    reading = service.retrieve(
        query=QUERY, scope=replace(_scope(successor_seed), case_id=other_case)
    )
    assert reading.hits
    assert {h.result.chunk.source_fragment_id for h in reading.hits} == {fragment}
    assert all(
        p.case_id == other_case and p.tenant_id == indexed_source[0]
        for p in reading.visit_type_evidence
    )
