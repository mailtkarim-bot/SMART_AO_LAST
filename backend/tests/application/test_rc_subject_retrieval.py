from dataclasses import replace
from math import sqrt
from uuid import UUID

import pytest

from tests.application.test_candidate_retrieval import chunk, profile, scope, service

POLICY = "rc-subject-proof-v7"


def run(texts, query, score=1.0, top_k=10):
    docs = [
        replace(chunk(text), chunk_id=UUID(int=100 + i), source_fragment_id=UUID(int=100 + i))
        for i, text in enumerate(texts)
    ]
    retrieval, encoder = service(docs, p=profile(review_policy=POLICY))
    encoder.query_vector = (score, sqrt(1 - score**2)) + (0.0,) * 382
    return retrieval.retrieve(query=query, scope=scope(), top_k=top_k)


@pytest.mark.parametrize("score", [0.84, 1.0])
def test_generic_visit_requires_all_proven_kinds_and_preserves_conditions(score):
    texts = [
        "Lot 17 : la visite médicale est requise.",
        "Lot 18 : la visite de chantier est obligatoire.",
        "Lot 19 : la visite des locaux n'est pas exigée.",
        "Lot 20 : la visite est obligatoire. Sauf dispense.",
        "Lot 21 : la visite médicale est citée dans une annexe.",
        "« Lot 22 : la visite de site est obligatoire. »",
        "Lot 23 : le DC2 est requis.",
    ]
    result = run(texts, "Quelles sont les obligations de visite ?", score)
    assert {h.result.chunk.source_fragment_id for h in result.hits} == {
        UUID(int=i) for i in range(100, 104)
    }
    evidence = (
        *result.rc_unscoped_evidence,
        *result.rc_projection.clauses,
        *result.rc_projection.unknown_regions,
    )
    assert {e.subject for e in evidence} >= {"VISIT", "VISIT_MEDICAL", "VISIT_SITE"}
    conditional = next(e for e in evidence if e.source_fragment_id == UUID(int=103))
    assert conditional.value == conditional.kind == "UNKNOWN" and conditional.condition_signals
    assert result.answer_state == "UNKNOWN"


@pytest.mark.parametrize(
    "query",
    [
        "À quelle heure commence la visite du lot 17 ?",
        "Quelle date est prévue pour la visite ?",
        "Quel est le rendez-vous pour la visite ?",
        "La visite est-elle obligatoire si le site est fermé ?",
    ],
)
def test_unproved_visit_question_never_falls_back_to_dense(query):
    result = run(
        ["Lot 17 : la visite médicale est requise.", "Lot 17 : la visite est obligatoire."], query
    )
    assert not result.hits and result.specific_intent.state == "UNKNOWN"
    assert result.answer_state == "UNKNOWN"


@pytest.mark.parametrize("score", [0.84, 1.0])
def test_dc2_query_filters_dpgf_and_unproved_mentions_with_scoped_proof(score):
    result = run(
        [
            "Lot 17 : le DC2 est requis.",
            "Lot 17 : la DPGF est requise.",
            "Lot 17 : le DC2 est cité dans le guide.",
            "Lot 18 : le DC2 est requis.",
            "« Lot 17 : le DC2 est requis. »",
        ],
        "Le DC2 est-il requis pour le lot 17 ?",
        score,
    )
    assert [h.result.chunk.source_fragment_id for h in result.hits] == [UUID(int=100)]
    assert result.rc_projection.clauses[0].subject == "DC2"
    assert result.rc_projection.clauses[0].lot == 17
    assert result.answer_state == "UNKNOWN"


def test_subject_rescue_budget_does_not_claim_unselected_candidate():
    result = run(
        ["Lot 17 : la visite médicale est requise.", "Lot 18 : la visite de chantier est requise."],
        "Quelles sont les obligations de visite ?",
        score=0.84,
        top_k=1,
    )
    assert len(result.hits) == 1
    assert [t.decision for t in result.score_trace] == ["RC_TYPED_RESCUE", "TOP_K_LIMIT"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("tenant_id", UUID(int=99)),
        ("case_id", UUID(int=99)),
        ("dce_version_id", UUID(int=99)),
    ],
)
def test_v7_foreign_sources_never_reach_encoder(field, value):
    retrieval, encoder = service(
        [replace(chunk("Lot 17 : le DC2 est requis."), **{field: value})],
        p=profile(review_policy=POLICY),
    )
    reading = retrieval.retrieve(query="Le DC2 est-il requis pour le lot 17 ?", scope=scope())
    assert not reading.hits and not reading.score_trace and not reading.visit_type_evidence
    assert encoder.passages == encoder.queries == []


def test_v7_zero_score_does_not_gain_typed_rescue():
    assert not run(
        ["Lot 17 : la visite médicale est requise."],
        "Quelles sont les obligations de visite ?",
        score=0,
    ).hits


@pytest.mark.parametrize(
    "query",
    [
        "Le DC2 et le DC1 sont-ils requis pour le lot 17 ?",
        "Le DC2 est-il requis pour le lot 17 ou 18 ?",
    ],
)
@pytest.mark.parametrize("score", [0.84, 1.0])
def test_v7_ambiguous_obligation_never_gets_subject_rescue(query, score):
    reading = run(["Lot 17 : le DC2 est requis."], query, score=score)
    assert not reading.hits and reading.answer_state == "UNKNOWN"


def test_v7_dc2_suffix_condition_and_retry_keep_exact_unknown():
    text = "Lot 17 : le DC2 est requis." + " Notice." * 150 + " Sauf dispense."
    retrieval, encoder = service([chunk(text)], p=profile(review_policy=POLICY))
    encoder.query_vector = (0.84, sqrt(1 - 0.84**2)) + (0.0,) * 382
    result = retrieval.retrieve(query="Le DC2 est-il requis pour le lot 17 ?", scope=scope())
    assert result == retrieval.retrieve(
        query="Le DC2 est-il requis pour le lot 17 ?", scope=scope()
    )
    evidence = result.rc_projection.unknown_regions[0]
    assert evidence.subject == "DC2" and evidence.value == evidence.kind == "UNKNOWN"
    assert (
        evidence.condition_signals
        and evidence.condition_signals[0].start_byte > result.hits[0].end_byte
    )
    assert len(encoder.passages) == 1


def test_v7_mixed_segment_keeps_raw_context_but_does_not_type_dpgf_as_requested():
    text = "Lot 17 : le DC2 est requis. Lot 17 : la DPGF est requise."
    result = run([text], "Le DC2 est-il requis pour le lot 17 ?")
    assert len(result.hits) == 1 and "DPGF" in result.hits[0].result.chunk.text
    assert {e.subject for e in result.rc_projection.clauses} == {"DC2"}
    assert len(result.rc_unscoped_evidence) == 1
    assert result.rc_unscoped_evidence[0].subject == "DPGF"
    assert result.rc_unscoped_evidence[0].directive_signal == "UNKNOWN"
