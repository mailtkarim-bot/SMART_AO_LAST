from dataclasses import dataclass
from typing import Literal
from uuid import UUID

LineFieldState = Literal["UNKNOWN", "DECLARED"]
LineGroupDisposition = Literal[
    "LINKED_BY_PATRON",
    "DISTINCT_POSITIONS",
    "NEEDS_CLARIFICATION",
]


@dataclass(frozen=True, slots=True)
class PartnerOfferLineMember:
    receipt_event_id: UUID
    line_locator_state: LineFieldState
    line_locator: str | None
    item_reference_state: LineFieldState
    item_reference: str | None
    designation_state: LineFieldState
    designation: str | None
    unit_state: LineFieldState
    unit: str | None
    quantity_state: LineFieldState
    quantity: str | None


@dataclass(frozen=True, slots=True)
class PartnerOfferLineGroup:
    group_id: UUID
    disposition: LineGroupDisposition
    rationale: str
    members: tuple[PartnerOfferLineMember, ...]


@dataclass(frozen=True, slots=True)
class PartnerOfferLineComparison:
    comparison_id: UUID
    scope_review_id: UUID
    groups: tuple[PartnerOfferLineGroup, ...]


def build_partner_offer_line_comparison(
    *,
    comparison_id: UUID,
    scope_review_id: UUID,
    groups: tuple[PartnerOfferLineGroup, ...],
) -> PartnerOfferLineComparison:
    if not groups or len(groups) > 100:
        raise ValueError("PARTNER_OFFER_LINE_GROUP_COUNT_INVALID")
    if len({group.group_id for group in groups}) != len(groups):
        raise ValueError("PARTNER_OFFER_LINE_DUPLICATE_GROUP")

    for group in groups:
        if group.disposition not in {
            "LINKED_BY_PATRON",
            "DISTINCT_POSITIONS",
            "NEEDS_CLARIFICATION",
        }:
            raise ValueError("PARTNER_OFFER_LINE_DISPOSITION_UNKNOWN")
        if not group.rationale.strip():
            raise ValueError("PARTNER_OFFER_LINE_RATIONALE_REQUIRED")
        if len(group.members) < 2 or len(group.members) > 20:
            raise ValueError("PARTNER_OFFER_LINE_MEMBER_COUNT_INVALID")
        receipt_ids = tuple(member.receipt_event_id for member in group.members)
        if len(set(receipt_ids)) != len(receipt_ids):
            raise ValueError("PARTNER_OFFER_LINE_DUPLICATE_RECEIPT")
        for member in group.members:
            for state, value in (
                (member.line_locator_state, member.line_locator),
                (member.item_reference_state, member.item_reference),
                (member.designation_state, member.designation),
                (member.unit_state, member.unit),
                (member.quantity_state, member.quantity),
            ):
                _validate_source_field(state=state, value=value)

    return PartnerOfferLineComparison(
        comparison_id=comparison_id,
        scope_review_id=scope_review_id,
        groups=groups,
    )


def _validate_source_field(*, state: str, value: str | None) -> None:
    if state not in {"UNKNOWN", "DECLARED"}:
        raise ValueError("PARTNER_OFFER_LINE_FIELD_STATE_UNKNOWN")
    if state == "DECLARED" and not (value or "").strip():
        raise ValueError("PARTNER_OFFER_LINE_DECLARED_VALUE_REQUIRED")
    if state == "UNKNOWN" and value is not None:
        raise ValueError("PARTNER_OFFER_LINE_UNKNOWN_VALUE_PRESENT")
