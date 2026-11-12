import json
from dataclasses import asdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
DEVELOPMENT = json.loads(
    (ROOT / "backend/tests/fixtures/knowledge/rc_intent_development_design_v1.json").read_text()
)


@pytest.mark.parametrize("case", DEVELOPMENT["cases"], ids=lambda c: c["id"])
def test_compositional_development_contract(case):
    from app.modules.knowledge.application.rc_compositional_intent import recognize_rc_intent

    result = recognize_rc_intent(case["text"])
    assert result.reason == case["expected_reason"]
    expected = case["expected_intent"]
    if expected is None:
        assert result.intent is None
        return
    intent = result.intent
    assert intent is not None
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
        "Le DC1 est disponible ; est-il obligatoire de signer une attestation ?",
        "Le mot obligatoire apparaît dans le DC1 ; est-il correctement orthographié ?",
        "La visite virtuelle est-elle obligatoire ?",
        "La visite technique est-elle obligatoire ?",
        "Le DC1 est-il obligatoire pour le lot 1.5 ?",
        "Le DC1 est-il obligatoire pour le lot 1 bis ?",
        "La visite est-elle non obligatoire ?",
        "La visite obligatoire est-elle prévue ?",
        "Le DC1 est-il disponible et une attestation est-elle obligatoire ?",
    ],
)
def test_independent_counterexamples_never_promote_a_request(query):
    from app.modules.knowledge.application.rc_compositional_intent import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"


@pytest.mark.parametrize(
    "query",
    [
        "Concernant le DC1, une attestation est-elle obligatoire ?",
        "La visite de chantier virtuelle est-elle obligatoire ?",
        "Le DC1 est-il obligatoire pour le lot 1-A ?",
        "Le DC1 est-il obligatoire pour le lot 1, 2 ?",
        "Le DC1 est-il obligatoire et interdit ?",
        "Faut-il joindre le DC1 ou une attestation ?",
        "Faut-il effectuer le DC1 ?",
    ],
)
def test_unconsumed_relation_or_scope_is_not_covered(query):
    from app.modules.knowledge.application.rc_compositional_intent import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"


@pytest.mark.parametrize(
    "query",
    [
        "Le document dans le DC1 est-il obligatoire ?",
        "La pièce dans le formulaire DC1 est-elle obligatoire ?",
    ],
)
def test_subject_head_is_not_an_object_contained_in_the_recognized_document(query):
    from app.modules.knowledge.application.rc_compositional_intent import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"
