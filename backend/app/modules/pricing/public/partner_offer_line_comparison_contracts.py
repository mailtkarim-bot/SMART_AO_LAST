from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PartnerOfferLineMemberRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_event_id: UUID
    line_locator_state: Literal["UNKNOWN", "DECLARED"]
    line_locator: str | None = Field(default=None, max_length=500)
    item_reference_state: Literal["UNKNOWN", "DECLARED"]
    item_reference: str | None = Field(default=None, max_length=120)
    designation_state: Literal["UNKNOWN", "DECLARED"]
    designation: str | None = Field(default=None, max_length=500)
    unit_state: Literal["UNKNOWN", "DECLARED"]
    unit: str | None = Field(default=None, max_length=32)
    quantity_state: Literal["UNKNOWN", "DECLARED"]
    quantity: str | None = Field(default=None, max_length=80)


class PartnerOfferLineGroupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: UUID
    disposition: Literal[
        "LINKED_BY_PATRON",
        "DISTINCT_POSITIONS",
        "NEEDS_CLARIFICATION",
    ]
    rationale: str = Field(min_length=1, max_length=2_000)
    members: tuple[PartnerOfferLineMemberRequest, ...] = Field(min_length=2, max_length=20)


class RecordPartnerOfferLineComparisonRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    record_id: UUID
    comparison_id: UUID
    scope_review_id: UUID
    expected_revision: int = Field(ge=0)
    groups: tuple[PartnerOfferLineGroupRequest, ...] = Field(min_length=1, max_length=100)


class PartnerOfferLineMemberResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
    partner_label: str
    source_locator: str
    receipt_is_current: bool
    line_locator_state: Literal["UNKNOWN", "DECLARED"]
    line_locator: str | None
    item_reference_state: Literal["UNKNOWN", "DECLARED"]
    item_reference: str | None
    designation_state: Literal["UNKNOWN", "DECLARED"]
    designation: str | None
    unit_state: Literal["UNKNOWN", "DECLARED"]
    unit: str | None
    quantity_state: Literal["UNKNOWN", "DECLARED"]
    quantity: str | None


class PartnerOfferLineGroupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: UUID
    disposition: Literal[
        "LINKED_BY_PATRON",
        "DISTINCT_POSITIONS",
        "NEEDS_CLARIFICATION",
    ]
    rationale: str
    members: list[PartnerOfferLineMemberResponse]


class PartnerOfferLineComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    record_id: UUID
    comparison_id: UUID
    revision: int = Field(ge=1)
    scope_review_id: UUID
    scope_review_revision: int = Field(ge=1)
    scope_review_decision: Literal[
        "SAME_SCOPE_CONFIRMED",
        "DIFFERENT_SCOPE",
        "NEEDS_CLARIFICATION",
    ]
    requires_reassessment: bool
    actor_id: UUID
    recorded_at: datetime
    groups: list[PartnerOfferLineGroupResponse]


class PartnerOfferLineComparisonListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    comparisons: list[PartnerOfferLineComparisonResponse]


class RecordPartnerOfferLineComparisonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    result_code: Literal["PARTNER_OFFER_LINE_COMPARISON_RECORDED"]
    aggregate_refs: list[dict[str, object]]
    event_ids: list[UUID]
    replayed: bool = False
