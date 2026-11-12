import importlib.util
import json
from pathlib import Path


def test_intent_measurement_distinguishes_abstention_from_positive_recall():
    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v3.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_qualifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = dict(
        id="probe",
        text="Le DC1 est-il incontournable ?",
        expected_intent=dict(
            subject="DC1", demand="OBLIGATION", coverage="COVERED", scope_state="UNKNOWN", lot=None
        ),
        expected_reason="UNIQUE_EXPLICIT_REQUEST",
        expected_anchors=[],
    )
    report = module.evaluate([case])
    assert report["positive_count"] == 1 and report["positive_exact"] == 0
    assert report["covered_count"] == 1 and report["anchor_mismatches"] == 1
    assert report["production_engine_changed"] is False


def test_sealed_challenge_is_not_read_without_freeze(tmp_path):
    import pytest

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v3.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_sealed_guard", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with pytest.raises(ValueError, match="freeze required"):
        module.main(
            [
                "--fixture",
                str(tmp_path / "absent.sealed.json"),
                "--output",
                str(tmp_path / "out.json"),
            ]
        )
    assert not (tmp_path / "out.json").exists()


def test_report_has_separate_gates_and_sealed_freeze_requires_candidate(tmp_path):
    import json

    import pytest

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v3.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_gates", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.evaluate([])
    assert report["gates"]["no_promotions"] and report["recognizer_calls"] == 0
    assert report["groups"] == {}
    manifest = tmp_path / "freeze.json"
    manifest.write_text(json.dumps(dict(files={})))
    with pytest.raises(ValueError, match="essential"):
        module.main(
            [
                "--fixture",
                str(tmp_path / "absent.sealed.json"),
                "--output",
                str(tmp_path / "out.json"),
                "--freeze-manifest",
                str(manifest),
            ]
        )


def test_v2_report_names_anchor_convention_and_refuses_empty_measurement(tmp_path):
    import json

    import pytest

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v3.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_v2_contract", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.evaluate([])["anchor_convention"] == "lexical-cue-v3"
    fixture = tmp_path / "empty.json"
    fixture.write_text(json.dumps(dict(synthetic=True, cases=[])))
    with pytest.raises(ValueError, match="nonempty"):
        module.main(["--fixture", str(fixture), "--output", str(tmp_path / "out.json")])
    assert not (tmp_path / "out.json").exists()


def test_v3_context_gold_and_integrity_are_separate(monkeypatch):
    from dataclasses import replace

    from app.modules.knowledge.application.rc_candidate_conflicts import RcSignalAnchor

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v3.py"
    spec = importlib.util.spec_from_file_location("rc_context_measurement", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    case = json.loads(
        (
            path.parents[1]
            / "backend/tests/fixtures/knowledge/rc_intent_development_context_v3.json"
        ).read_text()
    )["cases"][0]
    report = module.evaluate([case])
    assert report["positive_exact"] == 1 and report["context_regions"] == 1
    assert report["gates"]["contexts_exact"] and report["gates"]["context_integrity"]
    wrong = {**case, "expected_contexts": []}
    report = module.evaluate([wrong])
    assert report["positive_exact"] == 0 and not report["gates"]["contexts_exact"]
    assert report["gates"]["context_integrity"]
    genuine = module.recognize_rc_intent(case["text"])
    a = genuine.context_evidence[0]
    monkeypatch.setattr(
        module,
        "recognize_rc_intent",
        lambda q: replace(
            genuine,
            context_evidence=(RcSignalAnchor(a.signal, a.start_byte + 1, a.end_byte, a.excerpt),),
        ),
    )
    report = module.evaluate([case])
    assert not report["gates"]["context_integrity"]
