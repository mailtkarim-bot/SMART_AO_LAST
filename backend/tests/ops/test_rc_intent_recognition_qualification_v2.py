import importlib.util
from pathlib import Path


def test_intent_measurement_distinguishes_abstention_from_positive_recall():
    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v2.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_qualifier", path)
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

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v2.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_sealed_guard", path)
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

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v2.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_gates", path)
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

    path = Path(__file__).resolve().parents[3] / "scripts/qualify_rc_intent_recognition_v2.py"
    spec = importlib.util.spec_from_file_location("rc_recognition_v2_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.evaluate([])["anchor_convention"] == "lexical-cue-v2"
    fixture = tmp_path / "empty.json"
    fixture.write_text(json.dumps(dict(synthetic=True, cases=[])))
    with pytest.raises(ValueError, match="nonempty"):
        module.main(["--fixture", str(fixture), "--output", str(tmp_path / "out.json")])
    assert not (tmp_path / "out.json").exists()
