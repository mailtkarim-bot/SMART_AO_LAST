from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.platform.events.command_contracts import ApplicationCommand


class PreparationResponsePlanItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    section_code: Literal[
        "COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"
    ]
    source_proposal_id: UUID | None = None


class CreatePreparationResponsePlanCommand(ApplicationCommand):
    """Create one immutable response-plan version for an exact preparation package."""

    command_type = "CreatePreparationResponsePlan"

    plan_id: UUID
    package_id: UUID
    expected_package_revision: int = Field(ge=0)
    items: list[PreparationResponsePlanItem] = Field(min_length=1, max_length=64)

    @field_validator("items")
    @classmethod
    def unique_requirement_sections(
        cls, items: list[PreparationResponsePlanItem]
    ) -> list[PreparationResponsePlanItem]:
        identities = [(item.requirement_id, item.section_code) for item in items]
        if len(identities) != len(set(identities)):
            raise ValueError("RESPONSE_PLAN_ITEM_DUPLICATE")
        return items
