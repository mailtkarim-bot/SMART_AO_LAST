from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PartnerKindValue = Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
PartnerEventTypeValue = Literal["REQUESTED", "RECEIVED", "ENGAGEMENT_DECLARED"]
PartnerValidityValue = Literal["UNKNOWN", "VALID", "EXPIRED"]
PartnerExclusionsStateValue = Literal["UNKNOWN", "DECLARED"]
PartnerMandateStateValue = Literal[
    "NOT_APPLICABLE",
    "UNKNOWN",
    "REQUESTED",
    "RECEIVED",
    "REVIEW_REQUIRED",
]


class RecordCasePartnerRequestRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    partner_kind: PartnerKindValue
    partner_label: str = Field(min_length=1, max_length=240)
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)


class RecordCasePartnerReceiptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    request_event_id: UUID | None = None
    partner_kind: PartnerKindValue
    partner_label: str = Field(min_length=1, max_length=240)
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)
    valid_until: date | None = None
    exclusions_state: PartnerExclusionsStateValue
    exclusions: list[str] = Field(default_factory=list, max_length=32)
    mandate_state: PartnerMandateStateValue
    mandate_source_locator: str | None = Field(default=None, max_length=500)


class DeclareCasePartnerEngagementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    event_id: UUID
    partner_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=1)
    receipt_event_id: UUID
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)


class RecordCasePartnerEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    result_code: str
    aggregate_refs: list[dict[str, object]]
    event_ids: list[str]
    replayed: bool


class CasePartnerEventResponse(BaseModel):
    event_id: UUID
    partner_id: UUID
    case_id: UUID
    revision: int = Field(ge=1)
    event_type: PartnerEventTypeValue
    partner_kind: PartnerKindValue
    partner_label: str
    related_event_id: UUID | None
    source_locator: str
    rationale: str
    valid_until: date | None
    validity_at_recording: PartnerValidityValue
    validity_current: PartnerValidityValue
    exclusions_state: PartnerExclusionsStateValue
    exclusions: list[str]
    mandate_state: PartnerMandateStateValue
    mandate_source_locator: str | None
    actor_id: UUID
    recorded_at: datetime


class CasePartnerEventsResponse(BaseModel):
    case_id: UUID
    events: list[CasePartnerEventResponse]
    can_request: bool
    can_receive: bool
    can_declare_engagement: bool
