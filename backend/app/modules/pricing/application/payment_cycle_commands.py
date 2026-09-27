from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordPaymentPostReceptionCycleCommand(ApplicationCommand):
    command_type = "RecordPaymentPostReceptionCycle"
    cycle_id: UUID
    case_id: UUID
    source_refs: tuple[str, ...] = Field(min_length=1)
    trigger_event: str = Field(min_length=1)
    status: Literal["SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"]
    cash_assumption: str | None = None
    post_reception_cost_note: str | None = None
