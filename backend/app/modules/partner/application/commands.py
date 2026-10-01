from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand

PartnerKind = Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
ExclusionsState = Literal["UNKNOWN", "DECLARED"]
MandateState = Literal[
    "NOT_APPLICABLE",
    "UNKNOWN",
    "REQUESTED",
    "RECEIVED",
    "REVIEW_REQUIRED",
]


class RecordCasePartnerRequestCommand(ApplicationCommand):
    command_type = "RecordCasePartnerRequest"

    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    partner_kind: PartnerKind
    partner_label: str = Field(min_length=1, max_length=240)
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)


class RecordCasePartnerReceiptCommand(ApplicationCommand):
    command_type = "RecordCasePartnerReceipt"

    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    request_event_id: UUID | None = None
    partner_kind: PartnerKind
    partner_label: str = Field(min_length=1, max_length=240)
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)
    valid_until: date | None = None
    exclusions_state: ExclusionsState
    exclusions: tuple[str, ...] = Field(default=(), max_length=32)
    mandate_state: MandateState
    mandate_source_locator: str | None = Field(default=None, max_length=500)


class DeclareCasePartnerEngagementCommand(ApplicationCommand):
    command_type = "DeclareCasePartnerEngagement"

    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=1)
    receipt_event_id: UUID
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)
