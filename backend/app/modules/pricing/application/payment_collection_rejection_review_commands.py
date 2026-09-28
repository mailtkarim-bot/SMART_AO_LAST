# ruff: noqa: I001
from uuid import UUID
from typing import Literal
from pydantic import Field
from app.platform.events.command_contracts import ApplicationCommand

class RecordPaymentCollectionRejectionReviewCommand(ApplicationCommand):
    command_type = "RecordPaymentCollectionRejectionReview"
    review_id: UUID
    case_id: UUID
    rejected_count: int = Field(ge=1)
    decision: Literal["ACKNOWLEDGED", "FOLLOW_UP_REQUIRED"]
    rationale: str = Field(min_length=1)
