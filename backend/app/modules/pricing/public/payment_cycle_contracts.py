from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RecordPaymentCycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    cycle_id: UUID
    source_refs: tuple[str, ...] = Field(min_length=1)
    trigger_event: str = Field(min_length=1)
    status: Literal["SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"]
    cash_assumption: str | None = None
    post_reception_cost_note: str | None = None

class RecordPaymentCycleResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    cycle_id: UUID
    result_code: str
    replayed: bool

class QualifyPaymentCycleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    cash_assumption: str | None = None
    post_reception_cost_note: str | None = None

class PaymentUnknownAuditEntryResponse(BaseModel):
    cycle_id: UUID
    status: Literal["SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"]
    source_refs: tuple[str, ...]
    trigger_event: str

class PaymentUnknownAuditResponse(BaseModel):
    status_counts: dict[str, int]
    entries: list[PaymentUnknownAuditEntryResponse]
    rejected_count: int = 0
