# ruff: noqa: I001
from uuid import UUID
from pydantic import Field
from app.platform.events.command_contracts import ApplicationCommand

class RecordPaymentUnknownAuditOwnerActCommand(ApplicationCommand):
    command_type = "RecordPaymentUnknownAuditOwnerAct"
    owner_act_id: UUID
    case_id: UUID
    approved: bool
    rationale: str = Field(min_length=1)
