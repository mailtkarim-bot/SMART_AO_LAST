from dataclasses import dataclass
from typing import Literal
from uuid import UUID

ScopeReviewDecision = Literal[
    "SAME_SCOPE_CONFIRMED",
    "DIFFERENT_SCOPE",
    "NEEDS_CLARIFICATION",
]
InclusionState = Literal["UNKNOWN", "DECLARED"]
ExclusionsReviewState = Literal["UNKNOWN", "REVIEWED"]
TransportState = Literal["UNKNOWN", "INCLUDED", "EXCLUDED", "SEPARATE"]


@dataclass(frozen=True, slots=True)
class PartnerOfferScopeFact:
    receipt_event_id: UUID
    inclusion_state: InclusionState
    included_scope_note: str | None
    exclusions_review_state: ExclusionsReviewState
    transport_state: TransportState
    transport_note: str | None


@dataclass(frozen=True, slots=True)
class PartnerOfferScopeReview:
    comparison_id: UUID
    decision: ScopeReviewDecision
    rationale: str
    offers: tuple[PartnerOfferScopeFact, ...]


def build_partner_offer_scope_review(
    *,
    comparison_id: UUID,
    decision: ScopeReviewDecision,
    rationale: str,
    offers: tuple[PartnerOfferScopeFact, ...],
) -> PartnerOfferScopeReview:
    if decision not in {
        "SAME_SCOPE_CONFIRMED",
        "DIFFERENT_SCOPE",
        "NEEDS_CLARIFICATION",
    }:
        raise ValueError("PARTNER_SCOPE_REVIEW_DECISION_UNKNOWN")
    if not rationale.strip():
        raise ValueError("PARTNER_SCOPE_REVIEW_RATIONALE_REQUIRED")
    if len(offers) < 2 or len(offers) > 20:
        raise ValueError("PARTNER_SCOPE_REVIEW_MINIMUM_OFFERS")
    receipt_ids = tuple(offer.receipt_event_id for offer in offers)
    if len(set(receipt_ids)) != len(receipt_ids):
        raise ValueError("PARTNER_SCOPE_REVIEW_DUPLICATE_RECEIPT")

    for offer in offers:
        if offer.inclusion_state not in {"UNKNOWN", "DECLARED"}:
            raise ValueError("PARTNER_SCOPE_REVIEW_INCLUSION_STATE_UNKNOWN")
        if offer.exclusions_review_state not in {"UNKNOWN", "REVIEWED"}:
            raise ValueError("PARTNER_SCOPE_REVIEW_EXCLUSIONS_REVIEW_STATE_UNKNOWN")
        if offer.transport_state not in {"UNKNOWN", "INCLUDED", "EXCLUDED", "SEPARATE"}:
            raise ValueError("PARTNER_SCOPE_REVIEW_TRANSPORT_STATE_UNKNOWN")
        if offer.inclusion_state == "DECLARED" and not (offer.included_scope_note or "").strip():
            raise ValueError("PARTNER_SCOPE_REVIEW_INCLUSION_NOTE_REQUIRED")
        if offer.transport_state != "UNKNOWN" and not (offer.transport_note or "").strip():
            raise ValueError("PARTNER_SCOPE_REVIEW_TRANSPORT_NOTE_REQUIRED")

    if decision == "SAME_SCOPE_CONFIRMED" and any(
        offer.inclusion_state != "DECLARED"
        or offer.exclusions_review_state != "REVIEWED"
        or offer.transport_state == "UNKNOWN"
        for offer in offers
    ):
        raise ValueError("PARTNER_SCOPE_REVIEW_INCOMPLETE")

    return PartnerOfferScopeReview(
        comparison_id=comparison_id,
        decision=decision,
        rationale=rationale.strip(),
        offers=offers,
    )
