import json
from dataclasses import asdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DEVELOPMENT = json.loads(
    (
        ROOT / "backend/tests/fixtures/knowledge/rc_intent_development_compositional_v2.json"
    ).read_text()
)


@pytest.mark.parametrize("case", DEVELOPMENT["cases"], ids=lambda c: c["id"])
def test_v2_development_family_contract(case):
    from app.modules.knowledge.application.rc_compositional_intent_v2 import recognize_rc_intent

    result = recognize_rc_intent(case["text"])
    expected = case["expected_intent"]
    assert (
        result.mechanism == "rc-compositional-v2" and result.anchor_convention == "lexical-cue-v2"
    )
    assert result.reason == case["expected_reason"]
    if expected is None:
        assert result.intent is None
        return
    intent = result.intent
    assert {k: getattr(intent, k) for k in ["subject", "demand", "coverage"]} == {
        k: expected[k] for k in ["subject", "demand", "coverage"]
    }
    assert intent.scope.state == expected["scope_state"] and intent.scope.lot == expected["lot"]
    assert intent.query_sha256 == case["query_sha256"]
    assert [asdict(a) for a in intent.anchors] == case["expected_anchors"]
    assert result == recognize_rc_intent(case["text"])


@pytest.mark.parametrize(
    "query",
    [
        "Peut-on ne pas le fournir ?",
        "Le DC1 est disponible ; peut-on ne pas fournir une attestation ?",
        "Le DC1 ou le DC2, peut-on ne pas le fournir ?",
        "Le DC1 doit-il être requis si le titulaire",
        "Quand le DC1 est-il requis et où le déposer ?",
        "Quand faut-il effectuer la visite de site et doit-on fournir le DC2 ?",
        "La visite commerciale, est-il nécessaire de la réaliser ?",
        "Le DC1 est-il nécessaire pour le lot -2 ou -3 ?",
        "Est-il nécessaire de réaliser le DC1 ?",
        "Le document dans le DC1, peut-on ne pas le fournir ?",
    ],
)
def test_v2_new_relations_keep_refusals(query):
    from app.modules.knowledge.application.rc_compositional_intent_v2 import recognize_rc_intent

    assert recognize_rc_intent(query).intent.coverage != "COVERED"


@pytest.mark.parametrize(
    "case",
    json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/rc_intent_development_design_v1.json").read_text()
    )["cases"],
    ids=lambda c: "retained-" + c["id"],
)
def test_v2_retains_prior_development_not_prior_challenge(case):
    from app.modules.knowledge.application.rc_compositional_intent_v2 import recognize_rc_intent

    result = recognize_rc_intent(case["text"])
    expected = case["expected_intent"]
    assert result.reason == case["expected_reason"]
    if expected is None:
        assert result.intent is None
        return
    intent = result.intent
    assert {k: getattr(intent, k) for k in ["subject", "demand", "coverage"]} == {
        k: expected[k] for k in ["subject", "demand", "coverage"]
    }
    assert intent.scope.state == expected["scope_state"] and intent.scope.lot == expected["lot"]
    assert [asdict(a) for a in intent.anchors] == case["expected_anchors"]


@pytest.mark.parametrize(
    "query",
    [
        "Quand faut-il joindre le DC1, est-il obligatoire ?",
        "Quand faut-il joindre le DC1 et est-ce obligatoire ?",
    ],
)
def test_v2_does_not_merge_two_active_questions_into_a_time_auxiliary(query):
    from app.modules.knowledge.application.rc_compositional_intent_v2 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.reason == "MULTIPLE_DEMANDS"
    assert result.intent.coverage == "AMBIGUOUS" and result.intent.demand == "UNKNOWN"
    assert not any(a.signal == "DEMAND" for a in result.intent.anchors)


@pytest.mark.parametrize(
    "query",
    [
        "Le DC1 : peut-on ne pas les fournir ?",
        "Le DC1 : peut-on ne pas la fournir ?",
        "Peut-on ne pas le fournir, le DC1 ?",
    ],
)
def test_v2_local_reference_needs_matching_prior_antecedent(query):
    from app.modules.knowledge.application.rc_compositional_intent_v2 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.reason == "UNRESOLVED_REFERENCE" and result.intent.coverage == "UNKNOWN"
    assert not any(a.signal == "DEMAND" for a in result.intent.anchors)
