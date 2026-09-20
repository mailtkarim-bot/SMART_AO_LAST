from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class TransmitWonOutcomeCommand(ApplicationCommand):
    command_type = "TransmitWonOutcome"
    transmission_id: UUID
    outcome_id: UUID
    case_id: UUID
    recipient: str = Field(min_length=1, max_length=120)
