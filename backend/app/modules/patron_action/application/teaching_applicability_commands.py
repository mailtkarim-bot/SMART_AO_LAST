from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordCaseTeachingApplicabilityCommand(ApplicationCommand):
    """Record the Patron's explicit applicability assessment for one frozen source."""

    command_type = "RecordCaseTeachingApplicability"

    applicability_id: UUID
    target_case_id: UUID
    source_case_id: UUID
    source_interview_id: UUID
    source_rex_id: UUID
    decision: Literal["APPLICABLE", "NOT_APPLICABLE", "REVIEW_REQUIRED"]
    rationale: str = Field(min_length=1, max_length=2_000)
    target_source_locator: str = Field(min_length=1, max_length=500)
