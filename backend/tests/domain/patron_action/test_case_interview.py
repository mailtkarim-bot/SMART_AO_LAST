# ruff: noqa: E501, I001
from datetime import date
from uuid import uuid4
import pytest
from app.modules.patron_action.domain.case_interview import build_case_interview

def test_interview_is_sourced_scoped_and_expiring() -> None:
    interview = build_case_interview(case_id=uuid4(), held_on=date(2026, 9, 30), source_locator="entretien://comite/2026-09-30", rationale="Revue des enseignements du lot 01", expires_on=date(2027, 3, 30))
    assert interview.source_locator == "entretien://comite/2026-09-30"
    assert interview.expires_on.isoformat() == "2027-03-30"

def test_interview_requires_a_source() -> None:
    with pytest.raises(ValueError, match="INTERVIEW_SOURCE_REQUIRED"):
        build_case_interview(case_id=uuid4(), held_on=date(2026, 9, 30), source_locator="  ", rationale="Revue", expires_on=date(2027, 3, 30))

def test_interview_expiry_must_follow_holding() -> None:
    with pytest.raises(ValueError, match="INTERVIEW_EXPIRY_AFTER_HOLDING"):
        build_case_interview(case_id=uuid4(), held_on=date(2026, 9, 30), source_locator="entretien://comite/1", rationale="Revue", expires_on=date(2026, 9, 29))

def test_interview_requires_a_rationale() -> None:
    with pytest.raises(ValueError, match="INTERVIEW_RATIONALE_REQUIRED"):
        build_case_interview(case_id=uuid4(), held_on=date(2026, 9, 30), source_locator="entretien://comite/1", rationale=" ", expires_on=date(2027, 3, 30))
