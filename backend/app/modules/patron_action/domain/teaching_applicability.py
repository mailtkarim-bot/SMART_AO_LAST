from dataclasses import dataclass
from datetime import date
from typing import Literal
from uuid import UUID

ApplicabilityDecision = Literal["APPLICABLE", "NOT_APPLICABLE", "REVIEW_REQUIRED"]
SourceValidity = Literal["USABLE", "EXPIRED"]


@dataclass(frozen=True, slots=True)
class CaseTeachingApplicability:
    source_case_id: UUID
    target_case_id: UUID
    source_interview_id: UUID
    source_rex_id: UUID
    decision: ApplicabilityDecision
    rationale: str
    target_source_locator: str
    source_expires_on: date
    source_snapshot: dict[str, object]

    def source_validity(self, on_date: date) -> SourceValidity:
        return "USABLE" if self.source_expires_on >= on_date else "EXPIRED"


def build_case_teaching_applicability(
    *,
    source_case_id: UUID,
    target_case_id: UUID,
    source_interview_id: UUID,
    source_rex_id: UUID,
    decision: ApplicabilityDecision,
    rationale: str,
    target_source_locator: str,
    source_expires_on: date,
    source_snapshot: dict[str, object],
) -> CaseTeachingApplicability:
    if decision not in {"APPLICABLE", "NOT_APPLICABLE", "REVIEW_REQUIRED"}:
        raise ValueError("APPLICABILITY_DECISION_UNKNOWN")
    if not rationale.strip():
        raise ValueError("APPLICABILITY_RATIONALE_REQUIRED")
    if not target_source_locator.strip():
        raise ValueError("APPLICABILITY_SOURCE_REQUIRED")

    snapshot_rex_id = source_snapshot.get("rex_id")
    scope = source_snapshot.get("scope")
    validation = source_snapshot.get("validation")
    if snapshot_rex_id != str(source_rex_id):
        raise ValueError("SOURCE_SNAPSHOT_ID_MISMATCH")
    if scope not in {"CASE_ONLY", "LOT_PATTERN", "ENTERPRISE_PATTERN"}:
        raise ValueError("SOURCE_SCOPE_UNKNOWN")
    if validation not in {"PENDING", "APPROVED"}:
        raise ValueError("SOURCE_VALIDATION_UNKNOWN")
    if scope == "CASE_ONLY" and source_case_id != target_case_id:
        raise ValueError("CASE_ONLY_TEACHING_CANNOT_CROSS_CASES")
    if decision == "APPLICABLE" and validation != "APPROVED":
        raise ValueError("REX_APPROVAL_REQUIRED_FOR_APPLICABILITY")

    return CaseTeachingApplicability(
        source_case_id=source_case_id,
        target_case_id=target_case_id,
        source_interview_id=source_interview_id,
        source_rex_id=source_rex_id,
        decision=decision,
        rationale=rationale.strip(),
        target_source_locator=target_source_locator.strip(),
        source_expires_on=source_expires_on,
        source_snapshot=dict(source_snapshot),
    )
