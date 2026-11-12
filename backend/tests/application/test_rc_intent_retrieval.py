from dataclasses import replace
from math import sqrt
from uuid import UUID

import pytest
from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected
from app.modules.knowledge.domain.retrieval import DataClassification

from tests.application.test_candidate_retrieval import chunk, profile, scope, service

POLICY = "rc-intent-v8"


@pytest.mark.parametrize(
    "query,text,subject",
    [
        (
            "Faut-il effectuer une visite médicale pour le lot 17 ?",
            "Lot 17 : la visite médicale est obligatoire.",
            "VISIT_MEDICAL",
        ),
        ("Faut-il joindre le DC2 au dossier du lot 17 ?", "Lot 17 : le DC2 est requis.", "DC2"),
        (
            "Le mémoire technique doit-il être remis pour le lot 17 ?",
            "Lot 17 : le mémoire technique n'est pas exigé.",
            "MEMOIRE_TECHNIQUE",
        ),
        (
            "Quelles visites sont imposées par le règlement ?",
            "Lot 17 : la visite de chantier est obligatoire.",
            "VISIT_SITE",
        ),
    ],
)
def test_paraphrase_is_routed_by_intent_without_rewriting_query(query, text, subject):
    retrieval, encoder = service([chunk(text)], p=profile(review_policy=POLICY))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    reading = retrieval.retrieve(query=query, scope=scope())
    assert len(reading.hits) == 1 and reading.query_intent.coverage == "COVERED"
    assert encoder.queries == [query] and reading.answer_state == "UNKNOWN"
    evidence = (
        *reading.rc_projection.clauses,
        *reading.rc_unscoped_evidence,
        *reading.rc_projection.unknown_regions,
    )
    assert any(e.subject == subject for e in evidence)
    assert reading.score_trace[0].decision == "RC_TYPED_RESCUE"


@pytest.mark.parametrize(
    "query",
    [
        "À quelle heure commence la visite du lot 17 ?",
        "Le DC1 et le DC2 sont-ils requis pour le lot 17 ?",
        "Le DC2 est-il requis pour le lot 17 ou 18 ?",
        "Quelle couleur RAL choisir ?",
    ],
)
def test_uncovered_intent_refuses_before_any_source_or_encoder(query):
    retrieval, encoder = service([], p=profile(review_policy=POLICY))
    retrieval._source.read_chunks = lambda **kwargs: pytest.fail("uncovered query read source")
    reading = retrieval.retrieve(query=query, scope=scope())
    assert reading.state == "ABSTAIN" and reading.query_intent.coverage != "COVERED"
    assert not reading.hits and not reading.score_trace and not reading.visit_type_evidence
    assert encoder.passages == encoder.queries == []


@pytest.mark.parametrize(
    "changes",
    [
        {"tenant_id": UUID(int=99)},
        {"case_id": UUID(int=99)},
        {"dce_version_id": UUID(int=99)},
        {"classification": DataClassification.FINANCIAL_PRIVATE},
        {"classification": DataClassification.PERSONAL_DATA},
    ],
)
def test_intent_never_changes_source_access(changes):
    retrieval, encoder = service(
        [replace(chunk("Lot 17 : le DC2 est requis."), **changes)], p=profile(review_policy=POLICY)
    )
    reading = retrieval.retrieve(query="Faut-il joindre le DC2 pour le lot 17 ?", scope=scope())
    assert reading.query_intent.coverage == "COVERED" and not reading.hits
    assert encoder.passages == encoder.queries == []


def test_intent_retry_and_source_change_do_not_reuse_old_proof():
    docs = [chunk("Lot 17 : le DC2 est requis. Sauf dispense.")]
    retrieval, encoder = service(docs, p=profile(review_policy=POLICY))
    query = "Faut-il fournir le DC2 pour le lot 17 ?"
    first = retrieval.retrieve(query=query, scope=scope())
    assert first == retrieval.retrieve(query=query, scope=scope()) and len(encoder.passages) == 1
    assert first.rc_projection.unknown_regions[0].value == "UNKNOWN"
    encoder.after_query = docs.clear
    changed = retrieval.retrieve(query=query, scope=scope())
    assert changed.reason == "SOURCE_CHANGED" and changed.query_intent == first.query_intent
    assert not changed.hits and not changed.score_trace


def test_financial_guard_precedes_intent_and_all_sources(monkeypatch):
    retrieval, encoder = service([], p=profile(review_policy=POLICY))
    retrieval._source.read_chunks = lambda **kwargs: pytest.fail("financial source read")
    from app.modules.knowledge.application import candidate_retrieval

    monkeypatch.setattr(
        candidate_retrieval,
        "parse_rc_query_intent",
        lambda q: pytest.fail("financial intent parsed"),
    )
    with pytest.raises(FinancialRetrievalQueryRejected):
        retrieval.retrieve(query="Faut-il fournir la DPGF pour le lot 17 ?", scope=scope())
    assert encoder.passages == encoder.queries == []
