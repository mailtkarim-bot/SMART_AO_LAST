"""Closed human input contract for the dated capacity profile."""

from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.platform.events.command_contracts import ApplicationCommand


class CapacitySourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    reference: str = Field(min_length=1, max_length=500)
    revision: str = Field(min_length=1, max_length=500)
    locator: str = Field(min_length=1, max_length=500)


class CapacityRowRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: UUID
    label: str = Field(min_length=1, max_length=200)
    resource_type: str | None = Field(default=None, min_length=1, max_length=100)
    units: Annotated[int, Field(strict=True, ge=0, le=10000)] | None = None
    start: date | None = None
    end: date | None = None
    source: CapacitySourceRequest | None = None

    @model_validator(mode="after")
    def period_is_complete(self):
        if (self.start is None) != (self.end is None):
            raise ValueError("both dates or explicit unknown required")
        if self.start is not None and self.end is not None and self.end <= self.start:
            raise ValueError("end must be after start (end excluded)")
        return self


class CapacityDemandRequest(CapacityRowRequest):
    named_supply_id: UUID | None = None

    @model_validator(mode="after")
    def demand_is_positive(self):
        if self.units == 0:
            raise ValueError("demand units must be positive or unknown")
        return self


class RecordDatedCapacityRequest(ApplicationCommand):
    command_type = "RecordDatedCapacity"
    run_id: UUID
    expected_revision: int = Field(ge=0)
    context_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    demands: list[CapacityDemandRequest] | None = Field(max_length=100)
    supplies: list[CapacityRowRequest] | None = Field(max_length=100)
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]

    @model_validator(mode="after")
    def unique_resources(self):
        for rows in (self.demands or (), self.supplies or ()):
            if len({row.id for row in rows}) != len(rows):
                raise ValueError("duplicate resource identity")
        return self


class RecordDatedCapacityCommand(RecordDatedCapacityRequest):
    case_id: UUID
