from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class TransitionPostReceptionObligationCommand(ApplicationCommand):
    command_type = "TransitionPostReceptionObligation"
    transition_id: UUID
    obligation_id: UUID
    case_id: UUID
    expected_revision: int = Field(ge=0)
    resulting_status: Literal["IN_PROGRESS", "FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"]
    rationale: str = Field(min_length=1, max_length=2000)
    evidence_refs: tuple[str, ...] = Field(default=(), max_length=32)
