from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
class RecordPaymentCollectionRejectionReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    review_id: UUID
    rejected_count: int = Field(ge=1)
    decision: Literal["ACKNOWLEDGED", "FOLLOW_UP_REQUIRED"]
    rationale: str = Field(min_length=1)
class PaymentCollectionRejectionReviewResponse(BaseModel):
    review_id: UUID
    case_id: UUID
    reviewer_id: UUID
    rejected_count: int
    decision: Literal["ACKNOWLEDGED", "FOLLOW_UP_REQUIRED"]
    rationale: str
    created_at: datetime
