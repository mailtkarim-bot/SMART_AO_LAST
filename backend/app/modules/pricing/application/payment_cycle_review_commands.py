from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordPaymentCycleReviewCommand(ApplicationCommand):
    command_type = "RecordPaymentCycleReview"
    review_id: UUID
    cycle_id: UUID
    decision: Literal["ACCEPTED_FOR_PLANNING", "REVIEW_REQUIRED", "REJECTED"]
    rationale: str = Field(min_length=1)
