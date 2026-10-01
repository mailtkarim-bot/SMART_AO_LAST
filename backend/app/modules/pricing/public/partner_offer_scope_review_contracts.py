from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PartnerOfferScopeReviewOfferRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    receipt_event_id: UUID
    inclusion_state: Literal["UNKNOWN", "DECLARED"]
    included_scope_note: str | None = Field(default=None, max_length=2_000)
    exclusions_review_state: Literal["UNKNOWN", "REVIEWED"]
    transport_state: Literal["UNKNOWN", "INCLUDED", "EXCLUDED", "SEPARATE"]
    transport_note: str | None = Field(default=None, max_length=1_000)


class RecordPartnerOfferScopeReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    review_id: UUID
    comparison_id: UUID
    expected_revision: int = Field(ge=0)
    decision: Literal["SAME_SCOPE_CONFIRMED", "DIFFERENT_SCOPE", "NEEDS_CLARIFICATION"]
    rationale: str = Field(min_length=1, max_length=2_000)
    offers: tuple[PartnerOfferScopeReviewOfferRequest, ...] = Field(min_length=2, max_length=20)


class PartnerOfferScopeReviewOfferResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
    partner_label: str
    source_locator: str
    source_rationale: str
    validity_current: Literal["UNKNOWN", "VALID", "EXPIRED"]
    exclusions_state: Literal["UNKNOWN", "DECLARED"]
    exclusions: list[str]
    inclusion_state: Literal["UNKNOWN", "DECLARED"]
    included_scope_note: str | None
    exclusions_review_state: Literal["UNKNOWN", "REVIEWED"]
    transport_state: Literal["UNKNOWN", "INCLUDED", "EXCLUDED", "SEPARATE"]
    transport_note: str | None
    receipt_is_current: bool


class PartnerOfferScopeReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: UUID
    comparison_id: UUID
    revision: int = Field(ge=1)
    decision: Literal["SAME_SCOPE_CONFIRMED", "DIFFERENT_SCOPE", "NEEDS_CLARIFICATION"]
    rationale: str
    actor_id: UUID
    recorded_at: datetime
    requires_reassessment: bool
    offers: list[PartnerOfferScopeReviewOfferResponse]


class PartnerOfferScopeReviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    reviews: list[PartnerOfferScopeReviewResponse]


class RecordPartnerOfferScopeReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    result_code: Literal["PARTNER_SCOPE_REVIEW_RECORDED"]
    aggregate_refs: list[dict[str, object]]
    event_ids: list[UUID]
    replayed: bool = False
