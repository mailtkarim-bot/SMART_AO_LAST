from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

class PaymentCycleReviewDecision(StrEnum):
    ACCEPTED_FOR_PLANNING = "ACCEPTED_FOR_PLANNING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    REJECTED = "REJECTED"

@dataclass(frozen=True, slots=True)
class PaymentCycleReview:
    cycle_id: UUID
    reviewer_id: UUID
    decision: PaymentCycleReviewDecision
    rationale: str

    def validate(self) -> None:
        if not self.rationale.strip():
            raise ValueError("PAYMENT_REVIEW_RATIONALE_REQUIRED")
