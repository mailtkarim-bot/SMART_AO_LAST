from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PositionSourcesResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    costs: list[dict] = Field(max_length=1000)
    requirements: list[dict] = Field(max_length=1000)
    offers: list[dict] = Field(max_length=1000)
    scopes: list[dict] = Field(max_length=1000)


class PositionSourceLimitsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    costs: bool
    requirements: bool
    offers: bool
    scopes: bool


class PricingPositionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    position_id: UUID
    source_state: Literal["CURRENT_SOURCE", "UNKNOWN"]
    position_context_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    import_source: dict
    import_origin: dict
    review_id: UUID | None
    revision: int = Field(ge=0)
    actor_id: UUID | None
    created_at: datetime | None
    justification: str | None
    state: Literal["CURRENT", "REVIEW_REQUIRED"]
    cost_state: Literal["DECLARED", "UNKNOWN"]
    declared_cost_minor: str | None
    currency_code: str | None
    coverage_state: Literal["UNKNOWN"]
    applicability: Literal["UNKNOWN"]
    costs: list[dict] = Field(max_length=20)
    requirement: dict | None
    offer: dict | None
    scope: dict | None
    limitations: list[str] = Field(max_length=40)


class PricingPositionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    batch_id: UUID
    dce_version_id: UUID | None
    coverage_state: Literal["UNKNOWN"]
    positions: list[PricingPositionResponse] = Field(max_length=50)
    offset: int = Field(ge=0)
    next_offset: int | None
    sources: PositionSourcesResponse
    sources_limited: PositionSourceLimitsResponse


def exact_position_money(value):
    """JSON numbers cannot preserve all native BigInteger monetary facts in browsers."""
    if isinstance(value, dict):
        return {
            key: str(item)
            if key
            in {
                "amount_minor",
                "total_minor",
                "unit_price_minor",
                "declared_cost_minor",
                "allocated_amount_minor",
                "remaining_amount_minor",
            }
            and isinstance(item, int)
            and not isinstance(item, bool)
            else exact_position_money(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [exact_position_money(item) for item in value]
    return value
