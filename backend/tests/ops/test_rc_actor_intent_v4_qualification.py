import importlib.util
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


def load():
    path = ROOT / "scripts/qualify_rc_actor_intent_v4.py"
    assert path.exists(), "V4 evaluator missing"
    spec = importlib.util.spec_from_file_location("actor_v4_qualifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def example():
    return dict(
        id="dev",
        text="Le candidat doit-il joindre le DC1 ?",
        expected=dict(
            covered=True,
            subject="DC1",
            lot=None,
            actor="Le candidat",
            object="le DC1",
            request="doit-il joindre",
            action="joindre",
            contexts=[],
        ),
    )


def test_separate_components_and_exact_provenance():
    report = load().evaluate([example()])
    assert report["positive_exact"] == 1 and report["promotions"] == 0
    assert report["invalid_anchors"] == 0 and not report["admitted"]
    assert report["source_reads"] == report["encoder_calls"] == 0


def test_wrong_component_is_not_hidden_by_correct_coverage():
    case = deepcopy(example())
    case["expected"]["actor"] = "candidat"
    report = load().evaluate([case])
    assert report["positive_exact"] == 0
    assert report["rows"][0]["components"]["actor"] is False


def test_financial_and_ambiguity_are_not_promoted():
    cases = [
        dict(
            id="financial",
            text="La DPGF est-elle obligatoire ?",
            expected=dict(covered=False, financial=True),
        ),
        dict(id="multi", text="Le DC1 et le DC2 sont-ils requis ?", expected=dict(covered=False)),
    ]
    report = load().evaluate(cases)
    assert report["exact_count"] == 2 and report["promotions"] == 0


def test_invalid_anchor_is_detected_even_if_components_match(monkeypatch):
    from dataclasses import replace

    module = load()
    original = module.recognize_rc_intent

    def corrupt(q):
        r = original(q)
        return replace(r, actor=replace(r.actor, start_byte=1))

    monkeypatch.setattr(module, "recognize_rc_intent", corrupt)
    report = module.evaluate([example()])
    assert report["positive_exact"] == 0 and report["invalid_anchors"] == 1


def test_positive_gold_must_cover_all_independent_components():
    case = example()
    case["expected"] = dict(covered=True, lot=None)
    with pytest.raises(ValueError, match="component"):
        load().evaluate([case])
