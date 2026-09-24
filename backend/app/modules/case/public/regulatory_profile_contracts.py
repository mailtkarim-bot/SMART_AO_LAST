from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordRegulatoryProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    profile_id: UUID
    profile_version: int = Field(ge=1)
    status: Literal["ACTIVE", "FUTURE", "EXPIRED", "UNKNOWN_APPLICABILITY", "REVIEW_REQUIRED"]
    facts: dict[str, object] = Field(min_length=1)
    source_refs: tuple[str, ...] = Field(min_length=1)
    effective_from: datetime | None = None
    effective_until: datetime | None = None


class RecordRegulatoryProfileResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["REGULATORY_PROFILE_RECORDED"]
    profile_id: UUID
    version: int
    event_ids: list[UUID]
    replayed: bool


class RegulatoryProfileProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_id: UUID
    case_id: UUID
    profile_version: int
    status: Literal["ACTIVE", "FUTURE", "EXPIRED", "UNKNOWN_APPLICABILITY", "REVIEW_REQUIRED"]
    facts: dict[str, object]
    source_refs: list[str]
    effective_from: datetime | None
    effective_until: datetime | None


class RegulatoryProfilePageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    items: list[RegulatoryProfileProjection]
