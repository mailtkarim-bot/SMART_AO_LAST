from uuid import UUID

from pydantic import Field, StrictBool, model_validator

from app.modules.pricing.domain.cash_schedule import CashDeclaration
from app.platform.events.command_contracts import ApplicationCommand


class RecordCashScheduleCommand(ApplicationCommand):
    command_type = "RecordCashSchedule"
    revision_id: UUID
    case_id: UUID
    expected_revision: int = Field(strict=True, ge=0)
    expected_view_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    human_confirmed: StrictBool
    justification: str = Field(min_length=1, max_length=2000)
    declaration: CashDeclaration

    @model_validator(mode="after")
    def consent(self):
        if not self.human_confirmed:
            raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
        return self
