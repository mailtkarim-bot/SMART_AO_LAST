from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordHumanResumptionCommand(ApplicationCommand):
    command_type = "RecordHumanResumption"
    act_id: UUID
    export_id: UUID
    state: Literal["ACKNOWLEDGED", "FOLLOW_UP_REQUIRED", "BLOCKED"]
    rationale: str = Field(min_length=1)
