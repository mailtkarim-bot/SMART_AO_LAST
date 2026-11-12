import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[3]
DEVELOPMENT = json.loads(
    (ROOT / "backend/tests/fixtures/knowledge/rc_intent_development_context_v3.json").read_text()
)


@pytest.mark.parametrize("case", DEVELOPMENT["cases"], ids=lambda c: c["id"])
def test_v3_original_intent_and_context_provenance(case):
    from app.modules.knowledge.application.rc_context_intent_v3 import recognize_rc_intent

    result = recognize_rc_intent(case["text"])
    intent = result.intent
    assert intent is not None
    expected = case["expected_intent"]
    assert result.mechanism == "rc-context-v3" and result.anchor_convention == "lexical-cue-v3"
    assert result.reason == case["expected_reason"]
    assert {k: getattr(intent, k) for k in ["subject", "demand", "coverage"]} == {
        k: expected[k] for k in ["subject", "demand", "coverage"]
    }
    assert intent.scope.state == expected["scope_state"] and intent.scope.lot == expected["lot"]
    assert intent.query_sha256 == case["query_sha256"]
    assert [asdict(a) for a in intent.anchors] == case["expected_anchors"]
    assert [asdict(a) for a in result.context_evidence] == case["expected_contexts"]
    assert result == recognize_rc_intent(case["text"])


@pytest.mark.parametrize(
    "query",
    [
        "Pour préparer notre offre et le DC2, le DC1 est-il requis ?",
        "Sans obligation, le DC1 est-il requis ?",
        "Pour préparer notre offre si le titulaire change, le DC1 est-il requis ?",
        "Pour préparer notre offre du lot 32, le DC1 est-il requis ?",
        "Pour préparer notre offre version 2, le DC1 est-il requis ?",
        "Pour organiser notre réponse à une autre entreprise, le DC1 est-il requis ?",
        "Le DC1 est-il requis, sauf pour préparer notre offre ?",
        "Le DC1 est-il requis, pour préparer notre offre sans engagement ?",
        "Pour rédiger une attestation, le DC1 est-il requis ?",
        "Pour préparer notre offre, le DC1 est-il requis et le DC2 est-il nécessaire ?",
        "Pour information, peut-on ne pas les fournir ?",
        "Pour information, la visite virtuelle est-elle obligatoire ?",
    ],
)
def test_v3_neutrality_does_not_promote_charged_or_unknown_context(query):
    from app.modules.knowledge.application.rc_context_intent_v3 import recognize_rc_intent

    result = recognize_rc_intent(query)
    assert result.intent is not None
    assert result.intent.coverage != "COVERED"
    assert all(
        a.excerpt.lower() in ["pour préparer notre offre, ", "pour information, "]
        for a in result.context_evidence
    )


def test_v3_legitimate_scope_is_retained_without_neutralizing_it():
    from app.modules.knowledge.application.rc_context_intent_v3 import recognize_rc_intent

    result = recognize_rc_intent("Pour le lot 33, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.intent.scope.lot == 33 and result.intent.coverage == "COVERED"
    assert not result.context_evidence


@pytest.mark.parametrize(
    "query",
    [
        "Pour information, le prix du DC1 est-il obligatoire ?",
        "Le DC1 est-il requis, pour préparer notre réponse à la DPGF ?",
    ],
)
def test_v3_financial_guard_precedes_context_and_core(query, monkeypatch):
    from app.modules.knowledge.application import rc_context_intent_v3 as module

    monkeypatch.setattr(
        module, "_recognize_v2", lambda q: pytest.fail("financial query reached core")
    )
    result = module.recognize_rc_intent(query)
    assert result.intent is None and result.reason == "FINANCIAL_SCOPE_REFUSED"
    assert not result.context_evidence


@pytest.mark.parametrize("query", [None, "", "  ", "x" * 2001, "\ud800"])
def test_v3_invalid_input_is_refused_before_core(query, monkeypatch):
    from app.modules.knowledge.application import rc_context_intent_v3 as module

    monkeypatch.setattr(
        module, "_recognize_v2", lambda q: pytest.fail("invalid query reached core")
    )
    result = module.recognize_rc_intent(query)
    assert result.intent is None and result.reason == "INVALID_QUERY_BUDGET"
    assert not result.context_evidence


def test_v3_timeout_does_not_fallback_to_raw_recognition(monkeypatch):
    from app.modules.knowledge.application import rc_context_intent_v3 as module

    calls = []

    def unavailable(q):
        calls.append(q)
        raise TimeoutError()

    monkeypatch.setattr(module, "_recognize_v2", unavailable)
    result = module.recognize_rc_intent("Pour préparer notre offre, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.reason == "RECOGNIZER_UNAVAILABLE" and result.intent.coverage == "UNKNOWN"
    assert len(calls) == 1


def test_v3_rejects_fabricated_provenance(monkeypatch):
    from dataclasses import replace

    from app.modules.knowledge.application import rc_context_intent_v3 as module
    from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor
    from app.modules.knowledge.application.rc_compositional_intent_v2 import (
        recognize_rc_intent as base,
    )

    def corrupt(view):
        result = base(view)
        assert result.intent is not None
        return replace(
            result,
            intent=replace(result.intent, anchors=(RcSignalAnchor("SUBJECT", 0, 1, "FAKE"),)),
        )

    monkeypatch.setattr(module, "_recognize_v2", corrupt)
    result = module.recognize_rc_intent("Pour préparer notre offre, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.reason == "INVALID_RECOGNIZER_OUTPUT" and result.intent.coverage == "UNKNOWN"


def test_v3_overlapping_contexts_and_incomplete_output_are_not_certified(monkeypatch):
    from dataclasses import replace

    from app.modules.knowledge.application import rc_context_intent_v3 as module
    from app.modules.knowledge.application.rc_compositional_intent_v2 import (
        recognize_rc_intent as base,
    )

    result = module.recognize_rc_intent("Pour information, pour préparer notre offre ?")
    assert result.intent is not None
    assert result.intent.coverage == "UNKNOWN" and not result.context_evidence

    def missing(view):
        result = base(view)
        assert result.intent is not None
        return replace(result, intent=replace(result.intent, anchors=()))

    monkeypatch.setattr(module, "_recognize_v2", missing)
    result = module.recognize_rc_intent("Pour information, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.reason == "INVALID_RECOGNIZER_OUTPUT" and result.intent.coverage == "UNKNOWN"


def test_v3_malformed_core_reason_abstains(monkeypatch):
    from types import SimpleNamespace

    from app.modules.knowledge.application import rc_context_intent_v3 as module
    from app.modules.knowledge.application.rc_compositional_intent_v2 import (
        recognize_rc_intent as base,
    )

    def missing_reason(view):
        return SimpleNamespace(intent=base(view).intent)

    monkeypatch.setattr(module, "_recognize_v2", missing_reason)
    result = module.recognize_rc_intent("Pour information, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.reason == "INVALID_RECOGNIZER_OUTPUT" and result.intent.coverage == "UNKNOWN"


@pytest.mark.parametrize(
    "case",
    json.loads(
        (
            ROOT / "backend/tests/fixtures/knowledge/rc_intent_development_compositional_v2.json"
        ).read_text()
    )["cases"],
    ids=lambda c: "retained-" + c["id"],
)
def test_v3_preserves_v2_development_without_using_old_challenges(case):
    from app.modules.knowledge.application.rc_context_intent_v3 import recognize_rc_intent

    result = recognize_rc_intent(case["text"])
    expected = case["expected_intent"]
    assert result.reason == case["expected_reason"]
    if expected is None:
        assert result.intent is None
        return
    intent = result.intent
    assert intent is not None
    assert {k: getattr(intent, k) for k in ["subject", "demand", "coverage"]} == {
        k: expected[k] for k in ["subject", "demand", "coverage"]
    }
    assert intent.scope.state == expected["scope_state"] and intent.scope.lot == expected["lot"]
    assert [asdict(a) for a in intent.anchors] == case["expected_anchors"]
    assert not result.context_evidence


def test_v3_neutral_patterns_are_explicitly_versioned():
    from app.modules.knowledge.application.rc_context_intent_v3 import NEUTRAL_CONTEXT_PATTERNS

    contract = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/rc_intent_context_contract_v3.json").read_text()
    )
    assert list(NEUTRAL_CONTEXT_PATTERNS) == contract["context_patterns"]


@pytest.mark.parametrize("corruption", ["boolean-lot", "unknown-subject-enum"])
def test_v3_invalid_slot_types_or_classes_cannot_be_promoted(corruption, monkeypatch):
    from dataclasses import replace

    from app.modules.knowledge.application import rc_context_intent_v3 as module
    from app.modules.knowledge.application.rc_compositional_intent_v2 import (
        recognize_rc_intent as base,
    )

    def corrupt(view):
        result = base(view)
        assert result.intent is not None
        intent = (
            replace(result.intent, scope=replace(result.intent.scope, lot=True))
            if corruption == "boolean-lot"
            else replace(result.intent, subject=cast(Any, "OTHER"))
        )
        return replace(result, intent=intent)

    monkeypatch.setattr(module, "_recognize_v2", corrupt)
    result = module.recognize_rc_intent("Pour information, le DC1 est-il requis pour le lot 1 ?")
    assert result.intent is not None
    assert result.reason == "INVALID_RECOGNIZER_OUTPUT" and result.intent.coverage == "UNKNOWN"


@pytest.mark.parametrize(
    "corruption", ["subject-mismatch", "coverage-enum", "state-reason", "demand-cue"]
)
def test_v3_slots_reason_and_lexical_anchors_must_agree(corruption, monkeypatch):
    from dataclasses import replace

    from app.modules.knowledge.application import rc_context_intent_v3 as module
    from app.modules.knowledge.application.rc_compositional_intent_v2 import (
        recognize_rc_intent as base,
    )

    def corrupt(view):
        result = base(view)
        if corruption == "subject-mismatch":
            assert result.intent is not None
            return replace(result, intent=replace(result.intent, subject="DC2"))
        if corruption == "coverage-enum":
            assert result.intent is not None
            return replace(result, intent=replace(result.intent, coverage=cast(Any, "INVALID")))
        assert result.intent is not None
        changed = replace(result.intent, demand="DATE_TIME", coverage="UNSUPPORTED")
        return replace(
            result,
            intent=changed,
            reason="UNSUPPORTED_TIME" if corruption == "demand-cue" else result.reason,
        )

    monkeypatch.setattr(module, "_recognize_v2", corrupt)
    result = module.recognize_rc_intent("Pour information, le DC1 est-il requis ?")
    assert result.intent is not None
    assert result.reason == "INVALID_RECOGNIZER_OUTPUT" and result.intent.coverage == "UNKNOWN"
