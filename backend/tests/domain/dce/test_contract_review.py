from uuid import uuid4

import pytest
from app.modules.dce.domain.contract_review import ContractProofReview, ContractReviewDecision


def test_human_review_requires_explicit_decision_and_rationale() -> None:
    review = ContractProofReview(
        uuid4(), uuid4(), ContractReviewDecision.ACCEPTED, "Source relue", 1
    )
    review.validate()


@pytest.mark.parametrize(
    "revision, rationale, error",
    [(0, "ok", "REVIEWED_REVISION_REQUIRED"), (1, "  ", "REVIEW_RATIONALE_REQUIRED")],
)
def test_human_review_rejects_incomplete_act(revision, rationale, error) -> None:
    with pytest.raises(ValueError, match=error):
        ContractProofReview(
            uuid4(), uuid4(), ContractReviewDecision.REJECTED, rationale, revision
        ).validate()
