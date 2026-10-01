from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.platform.events.command_contracts import ApplicationCommand


class PartnerOfferScopeReviewOfferCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    receipt_event_id: UUID
    inclusion_state: Literal["UNKNOWN", "DECLARED"]
    included_scope_note: str | None = Field(default=None, max_length=2_000)
    exclusions_review_state: Literal["UNKNOWN", "REVIEWED"]
    transport_state: Literal["UNKNOWN", "INCLUDED", "EXCLUDED", "SEPARATE"]
    transport_note: str | None = Field(default=None, max_length=1_000)


class RecordPartnerOfferScopeReviewCommand(ApplicationCommand):
    command_type = "RecordPartnerOfferScopeReview"

    review_id: UUID
    comparison_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    decision: Literal["SAME_SCOPE_CONFIRMED", "DIFFERENT_SCOPE", "NEEDS_CLARIFICATION"]
    rationale: str = Field(min_length=1, max_length=2_000)
    offers: tuple[PartnerOfferScopeReviewOfferCommand, ...] = Field(min_length=2, max_length=20)
