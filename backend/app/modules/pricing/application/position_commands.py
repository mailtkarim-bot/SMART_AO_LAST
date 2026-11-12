"""Human source links; amounts are always read from existing registers."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.platform.events.command_contracts import ApplicationCommand


class PositionCostReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_id: UUID
    report_revision: int = Field(ge=0)
    allocated_amount_minor: str | None = Field(
        default=None, pattern=r"^(0|[1-9][0-9]{0,18})$", exclude_if=lambda value: value is None
    )

    @model_validator(mode="after")
    def allocation_range(self):
        if self.allocated_amount_minor is not None and int(self.allocated_amount_minor) > 2**63 - 1:
            raise ValueError("POSITION_ALLOCATION_OUT_OF_RANGE")
        return self


class RecordPositionReviewRequest(ApplicationCommand):
    command_type = "RecordPricingPositionReview"
    record_id: UUID
    expected_revision: int = Field(ge=0)
    position_context_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    requirement_id: UUID | None = None
    requirement_revision: int | None = Field(default=None, ge=1)
    cost_refs: list[PositionCostReference] = Field(default_factory=list, max_length=20)
    offer_price_id: UUID | None = None
    offer_price_revision: int | None = Field(default=None, ge=1)
    scope_review_id: UUID | None = None
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]

    @model_validator(mode="after")
    def exact_references(self):
        if len({r.line_id for r in self.cost_refs}) != len(self.cost_refs):
            raise ValueError("POSITION_DUPLICATE_COST_REFERENCE")
        for identity, revision in [
            (self.requirement_id, self.requirement_revision),
            (self.offer_price_id, self.offer_price_revision),
        ]:
            if (identity is None) != (revision is None):
                raise ValueError("POSITION_REFERENCE_REVISION_REQUIRED")
        if self.scope_review_id and self.offer_price_id is None:
            raise ValueError("POSITION_OFFER_REQUIRED_FOR_SCOPE")
        return self


class RecordPositionReviewCommand(RecordPositionReviewRequest):
    case_id: UUID
    batch_id: UUID
    position_id: UUID
