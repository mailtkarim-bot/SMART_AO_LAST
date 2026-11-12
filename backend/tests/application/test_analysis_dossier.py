from uuid import uuid4

import pytest
from app.modules.case.application.analysis_dossier import (
    AnalysisTreatment,
    DossierAxisReview,
    RecordAnalysisDossierCommand,
)
from app.modules.case.application.analysis_summary import AXES
from pydantic import ValidationError


def treatment():
    return dict(
        axis_code="TECHNICAL",
        applicability="UNKNOWN",
        applicability_reason="Portée à confirmer",
        consequences={code: None for code in ["technical", "price", "delay", "cash", "contract"]},
        unknown_reason="Conséquences à instruire",
        action="Demander confirmation d'accès",
        responsible="SELF",
        due_at=None,
    )


def test_treatment_requires_meaningful_action_and_explicit_unknowns():
    assert AnalysisTreatment(**treatment()).responsible == "SELF"
    for change in [
        dict(axis_code="OTHER"),
        dict(action=" "),
        dict(unknown_reason=None),
        dict(applicability_reason=" "),
    ]:
        with pytest.raises(ValidationError):
            AnalysisTreatment(**dict(treatment(), **change))


def test_dossier_requires_exactly_twelve_distinct_axis_reviews():
    fields = dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        review_id=uuid4(),
        case_id=uuid4(),
        expected_revision=0,
        dossier_sha256="a" * 64,
        phase="PREPARED",
        axes=[
            dict(
                code=c,
                state="UNKNOWN",
                note="A instruire",
                follow_up="Relire les sources",
                responsible="SELF",
            )
            for c, _ in AXES
        ],
        justification="Préparation humaine",
        human_confirmed=True,
    )
    assert len(RecordAnalysisDossierCommand(**fields).axes) == 12
    for change in [
        dict(axes=fields["axes"][:-1]),
        dict(axes=[fields["axes"][0]] * 12),
        dict(human_confirmed=False),
    ]:
        with pytest.raises(ValidationError):
            RecordAnalysisDossierCommand(**dict(fields, **change))
    with pytest.raises(ValidationError):
        DossierAxisReview(
            code="CASH", state="UNKNOWN", note="Inconnu", follow_up=None, responsible="SELF"
        )


def test_legacy_assessment_retry_hash_is_unchanged_when_treatment_is_absent():
    from types import SimpleNamespace

    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.platform.events.dispatcher import canonical_request_hash

    from tests.application.test_analysis_assessment import fields

    cmd = RecordAnalysisAssessmentCommand(**fields())
    old_payload = cmd.model_dump(mode="json")
    old_payload.pop("treatment", None)
    legacy = SimpleNamespace(command_type=cmd.command_type, model_dump=lambda **kw: old_payload)
    assert canonical_request_hash(cmd) == canonical_request_hash(legacy)
    treated = cmd.model_copy(update={"treatment": AnalysisTreatment(**treatment())})
    assert canonical_request_hash(treated) != canonical_request_hash(legacy)
