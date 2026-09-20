from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordCaseOutcomeCommand(ApplicationCommand):
    command_type = "RecordCaseOutcome"
    outcome_id: UUID
    case_id: UUID
    lot_reference: str = Field(min_length=1, max_length=120)
    outcome: Literal["WON", "LOST", "UNKNOWN"]
    source_locator: str | None = Field(default=None, max_length=500)
    reservations: list[str] = Field(default_factory=list, max_length=32)
    unknown_reason: str | None = Field(default=None, max_length=1000)
