"""Explicit human publication; never a reclassification of private evidence files."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.membership.public.text_safety import contains_forbidden_text

POLICY = "HUMAN_OPERATIONAL_CHANGE_V1"


class OperationalPublication(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    human_confirmed: Literal[True]
    justification: str = Field(min_length=1, max_length=2000)
    publish: bool = False

    @field_validator("justification")
    @classmethod
    def safe_justification(cls, value):
        if contains_forbidden_text(value):
            raise ValueError("FINANCIAL_TEXT_NOT_PUBLISHABLE")
        return value


class OperationalChangeContext(OperationalPublication):
    expected_view_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    point_ids: list[UUID] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def unique_points(self):
        if len(set(self.point_ids)) != len(self.point_ids):
            raise ValueError("DUPLICATE_HANDOVER_POINT")
        return self


class OperationalActionDetails(OperationalPublication):
    responsible: str | None = Field(default=None, min_length=1, max_length=500)
    expected_evidence: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("responsible", "expected_evidence")
    @classmethod
    def safe_details(cls, value):
        if value and contains_forbidden_text(value):
            raise ValueError("FINANCIAL_TEXT_NOT_PUBLISHABLE")
        return value
