from copy import deepcopy
from uuid import uuid4

from app.modules.case.application.analysis_dossier import AnalysisTreatment
from app.modules.decision.application.commitment_card import project_commitment_points
from app.modules.decision.application.lifecycle_commands import DecisionContextReferenceInput

from tests.application.test_analysis_dossier import treatment


def point():
    return dict(
        item_id="p1",
        kind="RISK",
        source_state="CURRENT_SOURCE",
        source_context_sha256="a" * 64,
        source_anchor={"locator": "page 2"},
        title="Accès contraint",
        severity="CRITICAL",
        human_assessment=dict(
            assessment_id="act1",
            revision=2,
            state="CURRENT",
            source_context_sha256="a" * 64,
            expected_evidence="Plan accès",
            residual_risk=None,
            treatment={**treatment(), "hypotheses": "Livraison en deux rotations"},
        ),
        follow_ups=[],
    )


def test_same_point_in_two_axes_preserves_exact_source_and_does_not_invent_links():
    p = point()
    summary = {
        "axes": [{"code": "TECHNICAL", "items": [p]}, {"code": "CONTRACT", "items": [deepcopy(p)]}]
    }
    rows = project_commitment_points(summary)
    assert len(rows) == 1 and rows[0]["axes"] == ["TECHNICAL", "CONTRACT"]
    assert rows[0]["point"]["source_anchor"] == p["source_anchor"]
    assert rows[0]["hypotheses"] == "Livraison en deux rotations"
    assert rows[0]["relations_state"] == "UNKNOWN" and rows[0]["point"]["follow_ups"] == []


def test_unknown_or_stale_assessment_never_provides_current_hypotheses():
    p = point()
    p["human_assessment"]["state"] = "REVIEW_REQUIRED"
    assert (
        project_commitment_points({"axes": [{"code": "TECHNICAL", "items": [p]}]})[0]["hypotheses"]
        is None
    )


def test_hypotheses_are_explicit_but_legacy_payload_remains_identical():
    original = treatment()
    assert AnalysisTreatment(**original).model_dump() == original
    parsed = AnalysisTreatment(**{**original, "hypotheses": "Deux rotations de livraison"})
    assert parsed.model_dump()["hypotheses"] == "Deux rotations de livraison"


def test_decision_can_reference_one_exact_human_assessment():
    reference = DecisionContextReferenceInput(
        aggregate_type="ANALYSIS_ASSESSMENT",
        aggregate_id=uuid4(),
        aggregate_revision=2,
        content_hash="a" * 64,
        reference_role="CRITICAL_POINT",
    )
    assert reference.aggregate_type == "ANALYSIS_ASSESSMENT"
