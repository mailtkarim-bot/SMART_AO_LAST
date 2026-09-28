from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordPaymentCycleReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    review_id: UUID
    decision: Literal["ACCEPTED_FOR_PLANNING", "REVIEW_REQUIRED", "REJECTED"]
    rationale: str = Field(min_length=1)

class RecordPaymentCycleReviewResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    review_id: UUID
    result_code: str
    replayed: bool

class PaymentCycleReviewReadResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: UUID
    cycle_id: UUID
    reviewer_id: UUID
    decision: Literal["ACCEPTED_FOR_PLANNING", "REVIEW_REQUIRED", "REJECTED"]
    rationale: str
    created_at: datetime
