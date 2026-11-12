from hashlib import sha256

import pytest
from app.modules.knowledge.application.rc_candidate_conflicts import project_rc_conflicts

from tests.application.test_candidate_retrieval import chunk, profile, scope, service


def project(text, enabled=True, **kwargs):
    return project_rc_conflicts(
        [chunk(text)],
        qualified_visits=True,
        independent_visit_type=True,
        independent_rc_directive=True,
        imperative_sources=True,
        conditional_imperatives=enabled,
        **kwargs,
    )


@pytest.mark.parametrize(
    "text",
    [
        "Pour le lot n° 37, fournir le DC2.",
        "Lot no 38 : remettre le formulaire DC1.",
        "Présenter un mémoire technique pour le lot n° 39.",
    ],
)
def test_numbered_imperative_has_exact_source_proof_without_changing_v9(text):
    assert not project(text, False).clauses
    c = project(text).clauses[0]
    assert c.value == "REQUIRED" and c.kind == "ASSERTION" and c.directive_signal == "CANDIDATE"
    assert c.source_sha256 == sha256(text.encode()).hexdigest()
    assert len(c.directive_anchors) == 3
    for a in c.directive_anchors:
        assert text.encode()[a.start_byte : a.end_byte] == a.excerpt.encode()


@pytest.mark.parametrize(
    "suffix",
    [
        "si demandé",
        "sauf dispense écrite",
        "lorsque le candidat est retenu",
        "sous réserve de confirmation",
        "si le candidat n'est pas dispensé",
    ],
)
def test_condition_is_sourced_but_never_converted_to_known_obligation(suffix):
    text = f"Lot n° 37 : joindre le DC2 {suffix}."
    c = project(text).unknown_regions[0]
    assert (c.subject, c.lot, c.value, c.kind, c.directive_signal) == (
        "DC2",
        37,
        "UNKNOWN",
        "UNKNOWN",
        "CANDIDATE",
    )
    assert not project(text).clauses
    assert len(c.condition_signals) == 1 and c.condition_signals[0].excerpt == suffix
    for a in (*c.condition_signals, *c.directive_anchors):
        assert text.encode()[a.start_byte : a.end_byte] == a.excerpt.encode()
    legacy = project(text, False)
    assert all(c.directive_signal == "UNKNOWN" for c in legacy.unknown_regions)


@pytest.mark.parametrize(
    "text",
    [
        "Lot n° 37 : joindre le DC2 si.",
        "Lot n° 37 : joindre le DC2 si demandé et le DC1.",
        "Lot n° 37 : joindre le DC1 et le DC2.",
        "Lot n° 37 ou 38 : joindre le DC2.",
        "Exemple non applicable. Lot n° 37 : joindre le DC2.",
        "« Lot n° 37 : joindre le DC2 si demandé. »",
        "Lot n° 37 : ne pas joindre le DC2.",
        "Lot n° 37 : joindre le DC2. Ce n'est qu'un exemple.",
    ],
)
def test_unproved_condition_or_context_is_not_promoted(text):
    result = project(text)
    assert not result.clauses
    assert all(c.directive_signal == "UNKNOWN" for c in result.unknown_regions)


def test_conditional_candidate_requests_review_and_revalidates_source():
    from math import sqrt

    docs = [chunk("Lot n° 37 : joindre le DC2 si le candidat n'est pas dispensé.")]
    retrieval, encoder = service(docs, p=profile(review_policy="rc-conditional-v10"))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    query = "Pour le lot 37, faut-il joindre le DC2 ?"
    read = retrieval.retrieve(query=query, scope=scope())
    assert read.state == "REVIEW_REQUIRED" and read.answer_state == "UNKNOWN"
    assert read.rc_projection.unknown_regions[0].value == "UNKNOWN"
    assert read == retrieval.retrieve(query=query, scope=scope())
    assert encoder.queries == [query, query]
    encoder.after_query = docs.clear
    changed = retrieval.retrieve(query=query, scope=scope())
    assert changed.reason == "SOURCE_CHANGED" and not changed.hits


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", 99),
        ("case_id", 99),
        ("dce_version_id", 99),
        ("classification", "FINANCIAL_PRIVATE"),
        ("classification", "PERSONAL_DATA"),
    ],
)
def test_v10_conditional_private_and_foreign_source_never_encoded(field, value):
    from dataclasses import replace
    from uuid import UUID

    from app.modules.knowledge.domain.retrieval import DataClassification

    change = DataClassification(value) if field == "classification" else UUID(int=value)
    doc = replace(chunk("Lot 37 : joindre le DC2 si demandé."), **{field: change})
    retrieval, encoder = service([doc], p=profile(review_policy="rc-conditional-v10"))
    result = retrieval.retrieve(query="Pour le lot 37, faut-il joindre le DC2 ?", scope=scope())
    assert result.answer_state == "UNKNOWN" and not result.hits
    assert not encoder.passages
    assert not result.rc_projection.unknown_regions and not result.rc_unscoped_evidence
