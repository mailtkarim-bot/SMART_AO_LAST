from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.platform.events.command_contracts import ApplicationCommand
from app.modules.pricing.domain.partner_offer_line_comparison import LineFieldState


class PartnerOfferLineMemberCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    receipt_event_id: UUID
    line_locator_state: LineFieldState
    line_locator: str | None = Field(default=None, max_length=500)
    item_reference_state: LineFieldState
    item_reference: str | None = Field(default=None, max_length=120)
    designation_state: LineFieldState
    designation: str | None = Field(default=None, max_length=500)
    unit_state: LineFieldState
    unit: str | None = Field(default=None, max_length=32)
    quantity_state: LineFieldState
    quantity: str | None = Field(default=None, max_length=80)


class PartnerOfferLineGroupCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")

    group_id: UUID
    disposition: Literal[
        "LINKED_BY_PATRON",
        "DISTINCT_POSITIONS",
        "NEEDS_CLARIFICATION",
    ]
    rationale: str = Field(min_length=1, max_length=2_000)
    members: tuple[PartnerOfferLineMemberCommand, ...] = Field(min_length=2, max_length=20)


class RecordPartnerOfferLineComparisonCommand(ApplicationCommand):
    command_type = "RecordPartnerOfferLineComparison"

    record_id: UUID
    comparison_id: UUID
    case_id: UUID
    scope_review_id: UUID
    expected_revision: int = Field(ge=0)
    groups: tuple[PartnerOfferLineGroupCommand, ...] = Field(min_length=1, max_length=100)
