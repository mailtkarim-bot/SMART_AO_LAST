import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts/measure_dce_critical_omissions.py"


def module():
    assert SCRIPT.is_file(), "critical omission measurement must exist"
    spec = importlib.util.spec_from_file_location("critical_measurement", SCRIPT)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def setup(
    tmp_path,
    *,
    status="COMPLETED",
    case="synthetic",
    kind="RC_SITE_VISIT",
    excerpt="Visite obligatoire.",
):
    fragment = {"ordinal": 1, "text": "Visite obligatoire.", "locator_json": {"page": 2}}
    projection = {
        "status": status,
        "source_sha256": "a" * 64,
        "fragments": [fragment],
        "analysis": {
            "observations": [
                {"requirement_kind": kind, "fragment_id": "fragment", "excerpt": excerpt}
            ],
            "source_fragments": [{"fragment_id": "fragment", "ordinal": 1}],
        },
    }
    (tmp_path / "p.json").write_text(json.dumps(projection))
    ledger = {
        "ledger": [
            {
                "case_alias": case,
                "content_sha256": "a" * 64,
                "status": status,
                "root_version": "b" * 64,
                "projection_file": "p.json",
            }
        ]
    }
    reference = {
        "points": [
            {
                "reference_id": "critical-1",
                "case_alias": "synthetic",
                "source_sha256": "a" * 64,
                "page": 2,
                "evidence": "Visite obligatoire.",
                "expected_requirement_kinds": ["RC_SITE_VISIT"],
                "critical": True,
                "field": "visit",
            }
        ]
    }
    return ledger, reference


def test_signal_requires_same_source_page_and_evidence(tmp_path):
    m = module()
    ledger, reference = setup(tmp_path)
    result = m.measure(ledger, reference, tmp_path)
    assert result["points"][0]["status"] == "SIGNAL_SUPPORTED"
    assert result["whole_dce_analysis_claim"] is False
    assert result["normalized_value_accuracy"] == "NOT_MEASURED"
    reference["points"][0]["page"] = 3
    assert m.measure(ledger, reference, tmp_path)["points"][0]["status"] == "SOURCE_TEXT_NOT_FOUND"


def test_complete_text_without_matching_signal_is_visible_omission(tmp_path):
    ledger, reference = setup(tmp_path, excerpt="Autre article.")
    result = module().measure(ledger, reference, tmp_path)
    assert result["points"][0]["status"] == "CONFIRMED_SIGNAL_OMISSION"


def test_review_text_is_never_counted_as_an_admissible_success(tmp_path):
    ledger, reference = setup(tmp_path, status="REVIEW_REQUIRED")
    result = module().measure(ledger, reference, tmp_path)
    assert result["points"][0]["source_text_found"] is True
    assert result["points"][0]["status"] == "SOURCE_NOT_ELIGIBLE"
    assert result["counts"].get("SIGNAL_SUPPORTED", 0) == 0


def test_other_case_same_hash_does_not_match(tmp_path):
    ledger, reference = setup(tmp_path, case="other")
    assert (
        module().measure(ledger, reference, tmp_path)["points"][0]["status"]
        == "SOURCE_NOT_IN_INVENTORY"
    )


def test_absent_target_rule_is_not_fabricated_semantic_recall(tmp_path):
    ledger, reference = setup(tmp_path)
    reference["points"][0]["expected_requirement_kinds"] = []
    result = module().measure(ledger, reference, tmp_path)
    assert result["points"][0]["status"] == "NO_TARGET_RULE_IN_RC_REGISTER"
    assert result["normalized_value_accuracy"] == "NOT_MEASURED"


def test_mismatched_projection_hash_cannot_support_a_fact(tmp_path):
    ledger, reference = setup(tmp_path)
    path = tmp_path / "p.json"
    projection = json.loads(path.read_text())
    projection["source_sha256"] = "c" * 64
    path.write_text(json.dumps(projection))
    result = module().measure(ledger, reference, tmp_path)
    assert result["points"][0]["status"] == "SOURCE_NOT_ELIGIBLE"
    assert result["points"][0]["diagnostic"] == "PROJECTION_SOURCE_HASH_MISMATCH"
    assert result["counts"].get("SIGNAL_SUPPORTED", 0) == 0


def test_pdf_layout_spaces_do_not_invent_missing_source_text(tmp_path):
    ledger, reference = setup(tmp_path)
    path = tmp_path / "p.json"
    projection = json.loads(path.read_text())
    projection["fragments"][0]["text"] = "Visite obli gatoire ."
    projection["analysis"]["observations"][0]["excerpt"] = "Visite obli gatoire ."
    path.write_text(json.dumps(projection))
    result = module().measure(ledger, reference, tmp_path)
    assert result["points"][0]["status"] == "SIGNAL_SUPPORTED"
    projection["fragments"][0]["text"] = "Visite non obligatoire."
    path.write_text(json.dumps(projection))
    assert (
        module().measure(ledger, reference, tmp_path)["points"][0]["status"]
        == "SOURCE_TEXT_NOT_FOUND"
    )
