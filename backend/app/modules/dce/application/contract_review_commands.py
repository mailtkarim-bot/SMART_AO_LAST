from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordContractProofReviewCommand(ApplicationCommand):
    command_type = "RecordContractProofReview"
    review_id: UUID
    proof_id: UUID
    reviewed_revision: int = Field(ge=1)
    decision: Literal["ACCEPTED", "REJECTED", "NEEDS_CLARIFICATION"]
    rationale: str = Field(min_length=1)
