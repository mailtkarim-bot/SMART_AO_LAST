# ruff: noqa: E501
from typing import Literal
from uuid import UUID

from pydantic import Field, model_validator

from app.platform.events.command_contracts import ApplicationCommand


class RecordContractBaselineImpactCommand(ApplicationCommand):
    command_type = "RecordContractBaselineImpact"
    proof_id: UUID
    case_id: UUID
    baseline_observation_id: UUID | None = None
    dce_requirement_id: UUID | None = None
    dce_requirement_revision: int | None = Field(default=None, ge=1)
    proof_revision: int = Field(ge=1)
    baseline_source_refs: tuple[str, ...] = Field(min_length=1)
    baseline_statement: str = Field(min_length=1)
    deviation_statement: str | None = None
    impact_statement: str | None = None
    status: Literal[
        "SOURCE_SIGNAL_ONLY", "HUMAN_REVIEW_REQUIRED", "CONFIRMED", "UNKNOWN", "SUPERSEDED"
    ]

    @model_validator(mode="after")
    def require_requirement_pair(self):
        if (self.dce_requirement_id is None) != (self.dce_requirement_revision is None):
            raise ValueError("DCE requirement id and revision must be supplied together")
        return self
