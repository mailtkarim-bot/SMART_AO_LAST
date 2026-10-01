from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DeclarePartnerOfferPriceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    declaration_id: UUID
    expected_revision: int = Field(ge=0)
    amount_as_declared: str = Field(min_length=1, max_length=80)
    currency_code: str = Field(min_length=3, max_length=3)


class PartnerOfferPriceDeclarationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    declaration_id: UUID
    revision: int = Field(ge=1)
    amount_as_declared: str
    currency_code: str
    actor_id: UUID
    created_at: datetime


class PartnerOfferPriceViewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_event_id: UUID
    partner_id: UUID
    partner_kind: Literal["SUPPLIER", "SUBCONTRACTOR", "CO_CONTRACTOR"]
    partner_label: str
    partner_revision: int = Field(ge=1)
    source_locator: str
    source_rationale: str
    valid_until: date | None
    validity_current: Literal["UNKNOWN", "VALID", "EXPIRED"]
    exclusions_state: Literal["UNKNOWN", "DECLARED"]
    exclusions: list[str]
    mandate_state: Literal["NOT_APPLICABLE", "UNKNOWN", "REQUESTED", "RECEIVED", "REVIEW_REQUIRED"]
    is_latest_receipt: bool
    price_state: Literal["UNKNOWN", "DECLARED"]
    declarations: list[PartnerOfferPriceDeclarationResponse]


class PartnerOfferPriceListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    offers: list[PartnerOfferPriceViewResponse]


class DeclarePartnerOfferPriceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    result_code: Literal["PARTNER_OFFER_PRICE_DECLARED"]
    aggregate_refs: list[dict[str, object]]
    event_ids: list[UUID]
    replayed: bool = False
