from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordPostReceptionObligationCommand(ApplicationCommand):
    command_type = "RecordPostReceptionObligation"
    obligation_id: UUID
    case_id: UUID
    obligation_type: Literal[
        "OPR",
        "TESTS",
        "COMMISSIONING",
        "TRAINING",
        "DOE_DIUO",
        "RESERVES_LIFTING",
        "GPA",
        "INITIAL_MAINTENANCE",
        "SPARE_STOCK",
        "ON_CALL",
        "ADMIN_CLOSURE",
        "GUARANTEE_RELEASE",
    ]
    origin_reception_act_id: UUID | None = None
    summary: str = Field(min_length=1, max_length=2000)
    source_refs: tuple[str, ...] = Field(min_length=1, max_length=32)
    due_date: date | None = None
    resource_note: str | None = Field(default=None, max_length=2000)
    cost_estimate_note: str | None = Field(default=None, max_length=2000)
    fulfillment_proof_refs: tuple[str, ...] = Field(default=(), max_length=32)
    sanction_ref: str | None = Field(default=None, max_length=500)
