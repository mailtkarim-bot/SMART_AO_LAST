from datetime import date
from uuid import uuid4

import pytest
from app.modules.patron_action.domain.teaching_applicability import (
    build_case_teaching_applicability,
)


def _snapshot(
    *, scope: str = "ENTERPRISE_PATTERN", validation: str = "APPROVED"
) -> dict[str, object]:
    return {
        "rex_id": str(uuid4()),
        "lot_reference": "01",
        "scope": scope,
        "validation": validation,
        "observation": "Retour d’expérience sourcé",
        "source_locator": "dce://source/section-4",
    }


def _build(
    *, decision: str = "APPLICABLE", source_case_id=None, target_case_id=None, snapshot=None
):
    source_case_id = source_case_id or uuid4()
    target_case_id = target_case_id or source_case_id
    snapshot = snapshot or _snapshot()
    return build_case_teaching_applicability(
        source_case_id=source_case_id,
        target_case_id=target_case_id,
        source_interview_id=uuid4(),
        source_rex_id=snapshot["rex_id"],
        decision=decision,
        rationale="Comparaison humaine avec le lot cible",
        target_source_locator="dce://target/cctp/lot-01",
        source_expires_on=date(2027, 3, 30),
        source_snapshot=snapshot,
    )


def test_applicability_keeps_exact_source_snapshot_and_decision_separate_from_validity() -> None:
    source_case_id, target_case_id = uuid4(), uuid4()
    snapshot = _snapshot()

    act = _build(source_case_id=source_case_id, target_case_id=target_case_id, snapshot=snapshot)

    assert act.source_snapshot == snapshot
    assert act.source_case_id == source_case_id
    assert act.target_case_id == target_case_id
    assert act.decision == "APPLICABLE"
    assert act.source_validity(date(2027, 4, 1)) == "EXPIRED"


def test_pending_teaching_cannot_be_declared_applicable_but_can_remain_under_review() -> None:
    snapshot = _snapshot(validation="PENDING")
    with pytest.raises(ValueError, match="REX_APPROVAL_REQUIRED_FOR_APPLICABILITY"):
        _build(snapshot=snapshot)

    assert _build(decision="REVIEW_REQUIRED", snapshot=snapshot).decision == "REVIEW_REQUIRED"


def test_case_only_teaching_cannot_be_declared_applicable_to_another_case() -> None:
    with pytest.raises(ValueError, match="CASE_ONLY_TEACHING_CANNOT_CROSS_CASES"):
        _build(
            source_case_id=uuid4(), target_case_id=uuid4(), snapshot=_snapshot(scope="CASE_ONLY")
        )


@pytest.mark.parametrize(
    ("rationale", "source_locator", "error"),
    [
        (" ", "dce://target/1", "APPLICABILITY_RATIONALE_REQUIRED"),
        ("Décision", " ", "APPLICABILITY_SOURCE_REQUIRED"),
    ],
)
def test_applicability_requires_human_reason_and_target_source(
    rationale, source_locator, error
) -> None:
    with pytest.raises(ValueError, match=error):
        build_case_teaching_applicability(
            source_case_id=uuid4(),
            target_case_id=uuid4(),
            source_interview_id=uuid4(),
            source_rex_id=uuid4(),
            decision="REVIEW_REQUIRED",
            rationale=rationale,
            target_source_locator=source_locator,
            source_expires_on=date(2027, 3, 30),
            source_snapshot=_snapshot(),
        )
