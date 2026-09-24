"""Explicit human review act for a contract proof."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ContractReviewDecision(StrEnum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"


@dataclass(frozen=True, slots=True)
class ContractProofReview:
    proof_id: UUID
    reviewer_id: UUID
    decision: ContractReviewDecision
    rationale: str
    reviewed_revision: int

    def validate(self) -> None:
        if self.reviewed_revision < 1:
            raise ValueError("REVIEWED_REVISION_REQUIRED")
        if not self.rationale.strip():
            raise ValueError("REVIEW_RATIONALE_REQUIRED")
