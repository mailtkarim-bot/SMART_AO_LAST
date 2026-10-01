"""Commands for publishing immutable enterprise method profiles and adopting them."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.platform.events.command_contracts import ApplicationCommand

ProfileTerm = Literal["affair", "lot", "owner", "collaborator", "evidence"]
ProfileAxis = Literal["CONTRACT", "COST", "CASH", "SCHEDULE", "CAPACITY", "PARTNER", "DOCUMENT"]


class BusinessMethodCheckInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    key: str = Field(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]+$")
    label: str = Field(min_length=1, max_length=160)
    axis: ProfileAxis


class BusinessMethodProfileContent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    schema_version: Literal[1] = 1
    terminology: dict[ProfileTerm, str] = Field(default_factory=dict, max_length=5)
    additional_checks: tuple[BusinessMethodCheckInput, ...] = Field(default=(), max_length=40)

    @model_validator(mode="after")
    def check_unique_keys(self) -> BusinessMethodProfileContent:
        keys = [item.key for item in self.additional_checks]
        if len(keys) != len(set(keys)):
            raise ValueError("additional check keys must be unique")
        return self


class PublishBusinessMethodProfileCommand(ApplicationCommand):
    command_type = "PublishBusinessMethodProfile"

    profile_version_id: UUID
    company_id: UUID
    expected_version: int = Field(ge=0)
    profile: BusinessMethodProfileContent


class AdoptBusinessMethodProfileCommand(ApplicationCommand):
    command_type = "AdoptBusinessMethodProfile"

    adoption_id: UUID
    case_id: UUID
    expected_adoption_revision: int = Field(ge=0)
    profile_version_id: UUID
    profile_version: int = Field(gt=0)
    profile_content_sha256: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
