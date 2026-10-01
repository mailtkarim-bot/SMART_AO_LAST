"""Bounded public contract for versioned company-method configuration."""

from __future__ import annotations

from typing import Literal
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import BaseModel, ConfigDict, Field

from app.modules.enterprise.application.business_method_profile_commands import (
    AdoptBusinessMethodProfileCommand,
    BusinessMethodProfileContent,
    PublishBusinessMethodProfileCommand,
)


class PublishBusinessMethodProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_version: int = Field(ge=0)
    profile: BusinessMethodProfileContent

    def to_command(self, *, company_id: UUID) -> PublishBusinessMethodProfileCommand:
        return PublishBusinessMethodProfileCommand(
            command_id=self.command_id,
            idempotency_key=self.idempotency_key,
            correlation_id=self.correlation_id,
            profile_version_id=uuid5(NAMESPACE_URL, f"business-method-profile:{self.command_id}"),
            company_id=company_id,
            expected_version=self.expected_version,
            profile=self.profile.model_dump(mode="json"),
        )


class AdoptBusinessMethodProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    adoption_id: UUID | None = None
    expected_adoption_revision: int = Field(ge=0)
    profile_version_id: UUID
    profile_version: int = Field(gt=0)
    profile_content_sha256: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")

    def to_command(self, *, case_id: UUID) -> AdoptBusinessMethodProfileCommand:
        return AdoptBusinessMethodProfileCommand(
            command_id=self.command_id,
            idempotency_key=self.idempotency_key,
            correlation_id=self.correlation_id,
            adoption_id=self.adoption_id
            or uuid5(NAMESPACE_URL, f"business-method-profile-adoption:{self.command_id}"),
            case_id=case_id,
            expected_adoption_revision=self.expected_adoption_revision,
            profile_version_id=self.profile_version_id,
            profile_version=self.profile_version,
            profile_content_sha256=self.profile_content_sha256,
        )


class BusinessMethodProfileReceiptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: str
    aggregate_refs: list[dict[str, object]]
    event_ids: list[UUID]
    replayed: bool


class BusinessMethodProfileVersionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_version_id: UUID
    version: int
    schema_version: int
    profile: BusinessMethodProfileContent
    content_sha256: str


class BusinessMethodProfileVersionsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    company_id: UUID
    versions: list[BusinessMethodProfileVersionResponse]


class BusinessMethodProfileAdoptionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    adoption_id: UUID
    case_id: UUID
    adoption_revision: int
    profile_version_id: UUID
    profile_version: int
    profile_content_sha256: str
