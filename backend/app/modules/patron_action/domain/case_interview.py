# ruff: noqa: E501, I001
from dataclasses import dataclass
from datetime import date
from uuid import UUID

@dataclass(frozen=True, slots=True)
class CaseInterview:
    case_id: UUID
    held_on: date
    source_locator: str
    rationale: str
    expires_on: date

    def validate(self) -> None:
        if not self.source_locator.strip():
            raise ValueError("INTERVIEW_SOURCE_REQUIRED")
        if not self.rationale.strip():
            raise ValueError("INTERVIEW_RATIONALE_REQUIRED")
        if self.expires_on <= self.held_on:
            raise ValueError("INTERVIEW_EXPIRY_AFTER_HOLDING")

def build_case_interview(*, case_id: UUID, held_on: date, source_locator: str, rationale: str, expires_on: date) -> CaseInterview:
    interview = CaseInterview(case_id=case_id, held_on=held_on, source_locator=source_locator, rationale=rationale, expires_on=expires_on)
    interview.validate()
    return interview
