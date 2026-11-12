from dataclasses import replace
from math import sqrt
from types import SimpleNamespace
from uuid import UUID

import pytest
from app.modules.knowledge.domain.retrieval import DataClassification

from tests.application.test_candidate_retrieval import Encoder, chunk, profile, scope

QUERY = "Pour préparer notre offre, le DC2 est-il requis pour le lot 17 ?"


def adapter(documents, **kwargs):
    from app.modules.knowledge.application.context_candidate_retrieval import (
        ContextCandidateRetrieval,
    )

    p = profile(minimum_score=0.0)
    encoder = Encoder(p)
    source = SimpleNamespace(read_chunks=lambda **kw: tuple(documents))
    return ContextCandidateRetrieval(
        transport_profile=p, source=source, encoder=encoder, **kwargs
    ), encoder


@pytest.mark.parametrize("score", [0.84, 0.95])
def test_raw_query_provenance_and_typed_selection(score):
    service, encoder = adapter([chunk("Lot 17 : le DC2 est requis.")])
    encoder.query_vector = (score, sqrt(1 - score**2)) + (0.0,) * 382
    result = service.retrieve(query=QUERY, scope=scope())
    assert encoder.queries == [QUERY]
    assert result.recognition.intent.coverage == "COVERED" and result.recognition.context_evidence
    reading = result.reading
    assert reading.answer_state == "UNKNOWN" and reading.state == "CANDIDATES_ONLY"
    assert len(reading.hits) == 1 and reading.rc_projection.clauses[0].subject == "DC2"
    assert reading.query_intent == result.recognition.intent
    assert reading.score_trace[0].threshold == 0.85
    assert reading.score_trace[0].decision == ("RC_TYPED_RESCUE" if score < 0.85 else "DENSE_FLOOR")
    assert result == service.retrieve(query=QUERY, scope=scope())
    assert result.adapter_id.startswith("rc-context-retrieval-v1:")


@pytest.mark.parametrize(
    "text",
    [
        "Lot 17 : le DC1 est requis.",
        "Lot 18 : le DC2 est requis.",
        "Lot 17 : fournir le DC1 et le DC2.",
        "Lot 17 : le DC2 est",
    ],
)
def test_dense_score_never_promotes_unproved_or_wrong_scope_source(text):
    service, encoder = adapter([chunk(text)])
    reading = service.retrieve(query=QUERY, scope=scope()).reading
    assert not reading.hits and not reading.rc_projection.clauses
    assert reading.answer_state == "UNKNOWN"


@pytest.mark.parametrize(
    "query",
    [
        "Pour information, à quelle date faut-il fournir le DC2 ?",
        "Le DC1 et le DC2 sont-ils requis ?",
        "Le DC2 est-il requis si le titulaire change ?",
    ],
)
def test_uncovered_query_does_not_read_or_encode(query):
    service, encoder = adapter([])
    service._source.read_chunks = lambda **kw: pytest.fail("uncovered query reached source")
    result = service.retrieve(query=query, scope=scope())
    assert result.reading.state == "ABSTAIN" and not result.reading.hits
    assert not encoder.passages and not encoder.queries


@pytest.mark.parametrize(
    "change",
    [
        dict(tenant_id=UUID(int=99)),
        dict(case_id=UUID(int=99)),
        dict(dce_version_id=UUID(int=99)),
        dict(classification=DataClassification.FINANCIAL_PRIVATE),
        dict(classification=DataClassification.PERSONAL_DATA),
    ],
)
def test_foreign_or_private_source_never_reaches_encoder(change):
    service, encoder = adapter([replace(chunk("Lot 17 : le DC2 est requis."), **change)])
    reading = service.retrieve(query=QUERY, scope=scope()).reading
    assert not reading.hits and not reading.score_trace
    assert not encoder.passages and not encoder.queries


def test_financial_guard_before_reader_or_encoder():
    from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected

    service, encoder = adapter([])
    service._source.read_chunks = lambda **kw: pytest.fail("financial source read")
    with pytest.raises(FinancialRetrievalQueryRejected):
        service.retrieve(
            query="Pour préparer notre réponse à la DPGF, le DC2 est-il requis ?", scope=scope()
        )
    assert not encoder.passages and not encoder.queries


def test_source_change_during_query_clears_every_source_proof():
    docs = [chunk("Lot 17 : le DC2 est requis.")]
    service, encoder = adapter(docs)
    encoder.after_query = docs.clear
    result = service.retrieve(query=QUERY, scope=scope())
    assert result.reading.reason == "SOURCE_CHANGED" and result.reading.state == "REVIEW_REQUIRED"
    assert not result.reading.hits and not result.reading.score_trace
    assert not result.reading.rc_projection.clauses and not result.reading.rc_unscoped_evidence
    assert result.recognition.context_evidence


def test_condition_and_unknown_lot_require_review():
    service, _ = adapter([chunk("Lot 17 : joindre le DC2 si demandé.")])
    reading = service.retrieve(query=QUERY, scope=scope()).reading
    assert (
        reading.state == "REVIEW_REQUIRED"
        and reading.rc_projection.unknown_regions[0].value == "UNKNOWN"
    )
    service, _ = adapter([chunk("Lot 17 : le DC2 est requis.")])
    reading = service.retrieve(
        query="Pour information, le DC2 est-il requis ?", scope=scope()
    ).reading
    assert reading.reason == "RC_QUERY_LOT_UNKNOWN" and reading.state == "REVIEW_REQUIRED"
    assert not reading.rc_projection.clauses and reading.rc_unscoped_evidence


def test_final_revalidation_detects_locator_change_during_projection(monkeypatch):
    from app.modules.knowledge.application import context_candidate_retrieval as module

    docs = [chunk("Lot 17 : le DC2 est requis.")]
    service, _ = adapter(docs)
    original = module._projection
    changed = False

    def mutate(hits, sources):
        nonlocal changed
        result = original(hits, sources)
        if not changed:
            docs[0] = replace(docs[0], locator={"kind": "pdf_page", "page": 99})
            changed = True
        return result

    monkeypatch.setattr(module, "_projection", mutate)
    result = service.retrieve(query=QUERY, scope=scope())
    assert result.reading.reason == "SOURCE_CHANGED"
    assert not result.reading.hits and not result.reading.score_trace
    assert not result.reading.rc_projection.clauses and not result.reading.review_source_ids


def test_concurrent_affaires_do_not_share_capture_or_index():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    first = chunk("Lot 17 : le DC2 est requis.")
    second = replace(
        chunk("Lot 18 : le DC2 est requis."),
        chunk_id=UUID(int=18),
        source_fragment_id=UUID(int=18),
        case_id=UUID(int=20),
        dce_version_id=UUID(int=21),
    )
    service, encoder = adapter([first, second])
    barrier = Barrier(2, timeout=5)
    encoder.after_query = barrier.wait
    other_scope = replace(scope(), case_id=second.case_id, dce_version_id=second.dce_version_id)
    with ThreadPoolExecutor(max_workers=2) as pool:
        a = pool.submit(service.retrieve, query=QUERY, scope=scope())
        b = pool.submit(service.retrieve, query=QUERY.replace("17", "18"), scope=other_scope)
        for result, wanted in [(a.result(timeout=10), first), (b.result(timeout=10), second)]:
            assert {h.result.chunk.source_fragment_id for h in result.reading.hits} == {
                wanted.source_fragment_id
            }
            assert all(h.result.chunk.case_id == wanted.case_id for h in result.reading.hits)
            assert result.reading.query_intent.scope.lot in {17, 18}


@pytest.mark.parametrize("top_k", [True, 0, 51, 1.5])
def test_invalid_selection_budget_does_not_read(top_k):
    service, encoder = adapter([])
    service._source.read_chunks = lambda **kw: pytest.fail("invalid budget read")
    with pytest.raises(ValueError, match="top_k"):
        service.retrieve(query=QUERY, scope=scope(), top_k=top_k)
    assert not encoder.passages and not encoder.queries


def test_transport_profile_is_explicit_and_identity_contains_policy():
    from app.modules.knowledge.application.context_candidate_retrieval import (
        ContextCandidateRetrieval,
    )

    p = profile()
    with pytest.raises(ValueError, match="zero-floor"):
        ContextCandidateRetrieval(
            transport_profile=p,
            source=SimpleNamespace(read_chunks=lambda **kw: ()),
            encoder=Encoder(p),
        )
    service, _ = adapter([])
    another = profile(minimum_score=0.0, overlap_chars=100)
    other = ContextCandidateRetrieval(
        transport_profile=another,
        source=SimpleNamespace(read_chunks=lambda **kw: ()),
        encoder=Encoder(another),
    )
    assert service.adapter_id != other.adapter_id
