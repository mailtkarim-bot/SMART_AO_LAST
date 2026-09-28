from uuid import uuid4
import pytest
from app.modules.pricing.domain.payment_cycle_review import PaymentCycleReview, PaymentCycleReviewDecision

def test_payment_review_is_explicit_and_not_cash_certainty() -> None:
    PaymentCycleReview(uuid4(), uuid4(), PaymentCycleReviewDecision.ACCEPTED_FOR_PLANNING, "Planification uniquement").validate()

def test_payment_review_requires_rationale() -> None:
    with pytest.raises(ValueError, match="PAYMENT_REVIEW_RATIONALE_REQUIRED"):
        PaymentCycleReview(uuid4(), uuid4(), PaymentCycleReviewDecision.REJECTED, "").validate()
