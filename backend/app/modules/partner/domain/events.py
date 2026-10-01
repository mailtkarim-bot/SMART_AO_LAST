from dataclasses import dataclass
from datetime import date
from typing import Literal
from uuid import UUID

PartnerKind = Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
PartnerEventKind = Literal["REQUESTED", "RECEIVED", "ENGAGEMENT_DECLARED"]
ExclusionsState = Literal["UNKNOWN", "DECLARED"]
MandateState = Literal[
    "NOT_APPLICABLE",
    "UNKNOWN",
    "REQUESTED",
    "RECEIVED",
    "REVIEW_REQUIRED",
]
PartnerValidity = Literal["UNKNOWN", "VALID", "EXPIRED"]


@dataclass(frozen=True, slots=True)
class PartnerRequest:
    partner_kind: PartnerKind
    partner_label: str
    source_locator: str
    rationale: str
    external_dispatch_performed: bool = False


@dataclass(frozen=True, slots=True)
class PartnerReceipt:
    receipt_id: UUID
    event_type: PartnerEventKind
    partner_kind: PartnerKind
    partner_label: str
    source_locator: str
    rationale: str
    valid_until: date | None
    exclusions_state: ExclusionsState
    exclusions: tuple[str, ...]
    mandate_state: MandateState
    mandate_source_locator: str | None

    def validity(self, on_date: date) -> PartnerValidity:
        if self.valid_until is None:
            return "UNKNOWN"
        return "VALID" if self.valid_until >= on_date else "EXPIRED"


@dataclass(frozen=True, slots=True)
class PartnerEngagementDeclaration:
    source_receipt_id: UUID
    source_locator: str
    rationale: str
    legal_validity_assessed: bool = False


def build_partner_request(
    *,
    partner_kind: PartnerKind,
    partner_label: str,
    source_locator: str,
    rationale: str,
) -> PartnerRequest:
    _validate_partner_identity(partner_kind=partner_kind, partner_label=partner_label)
    _require_text(source_locator, "PARTNER_REQUEST_SOURCE_REQUIRED")
    _require_text(rationale, "PARTNER_REQUEST_RATIONALE_REQUIRED")
    return PartnerRequest(
        partner_kind=partner_kind,
        partner_label=partner_label.strip(),
        source_locator=source_locator.strip(),
        rationale=rationale.strip(),
    )


def build_partner_receipt(
    *,
    receipt_id: UUID,
    partner_kind: PartnerKind,
    partner_label: str,
    source_locator: str,
    rationale: str,
    valid_until: date | None,
    exclusions_state: ExclusionsState,
    exclusions: tuple[str, ...],
    mandate_state: MandateState,
    mandate_source_locator: str | None,
) -> PartnerReceipt:
    _validate_partner_identity(partner_kind=partner_kind, partner_label=partner_label)
    _require_text(source_locator, "PARTNER_RECEIPT_SOURCE_REQUIRED")
    _require_text(rationale, "PARTNER_RECEIPT_RATIONALE_REQUIRED")
    if exclusions_state not in {"UNKNOWN", "DECLARED"}:
        raise ValueError("PARTNER_EXCLUSIONS_STATE_UNKNOWN")
    if exclusions_state == "UNKNOWN" and exclusions:
        raise ValueError("PARTNER_UNKNOWN_EXCLUSIONS_MUST_NOT_CARRY_VALUES")
    normalized_exclusions = tuple(item.strip() for item in exclusions)
    if any(not item for item in normalized_exclusions):
        raise ValueError("PARTNER_EXCLUSION_EMPTY")
    if len(set(normalized_exclusions)) != len(normalized_exclusions):
        raise ValueError("PARTNER_EXCLUSION_DUPLICATE")
    if mandate_state not in {
        "NOT_APPLICABLE",
        "UNKNOWN",
        "REQUESTED",
        "RECEIVED",
        "REVIEW_REQUIRED",
    }:
        raise ValueError("PARTNER_MANDATE_STATE_UNKNOWN")
    if partner_kind == "CO_CONTRACTOR" and mandate_state == "NOT_APPLICABLE":
        raise ValueError("COTRAITANT_MANDATE_STATE_REQUIRED")
    if mandate_state == "RECEIVED":
        _require_text(mandate_source_locator or "", "PARTNER_MANDATE_SOURCE_REQUIRED")
    elif mandate_source_locator is not None:
        raise ValueError("PARTNER_MANDATE_SOURCE_WITHOUT_RECEIPT")
    if partner_kind != "CO_CONTRACTOR" and mandate_state not in {"NOT_APPLICABLE", "UNKNOWN"}:
        raise ValueError("PARTNER_MANDATE_NOT_APPLICABLE_FOR_KIND")

    return PartnerReceipt(
        receipt_id=receipt_id,
        event_type="RECEIVED",
        partner_kind=partner_kind,
        partner_label=partner_label.strip(),
        source_locator=source_locator.strip(),
        rationale=rationale.strip(),
        valid_until=valid_until,
        exclusions_state=exclusions_state,
        exclusions=normalized_exclusions,
        mandate_state=mandate_state,
        mandate_source_locator=(mandate_source_locator.strip() if mandate_source_locator else None),
    )


def validate_partner_engagement(
    *,
    receipt: PartnerReceipt,
    source_locator: str,
    rationale: str,
) -> PartnerEngagementDeclaration:
    if receipt.event_type != "RECEIVED":
        raise ValueError("PARTNER_RECEIPT_REQUIRED")
    _require_text(source_locator, "PARTNER_ENGAGEMENT_SOURCE_REQUIRED")
    _require_text(rationale, "PARTNER_ENGAGEMENT_RATIONALE_REQUIRED")
    if receipt.partner_kind == "CO_CONTRACTOR" and (
        receipt.mandate_state != "RECEIVED" or not receipt.mandate_source_locator
    ):
        raise ValueError("PARTNER_MANDATE_NOT_RECEIVED")
    return PartnerEngagementDeclaration(
        source_receipt_id=receipt.receipt_id,
        source_locator=source_locator.strip(),
        rationale=rationale.strip(),
    )


def _validate_partner_identity(*, partner_kind: str, partner_label: str) -> None:
    if partner_kind not in {"SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"}:
        raise ValueError("PARTNER_KIND_UNKNOWN")
    _require_text(partner_label, "PARTNER_LABEL_REQUIRED")


def _require_text(value: str, error_code: str) -> None:
    if not value.strip():
        raise ValueError(error_code)
