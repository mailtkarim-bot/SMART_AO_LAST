# ruff: noqa: I001
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
class RecordPaymentUnknownAuditOwnerActRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    owner_act_id: UUID
    approved: bool
    rationale: str = Field(min_length=1)
class RecordPaymentUnknownAuditOwnerActResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    owner_act_id: UUID
    result_code: str
    replayed: bool

class PaymentUnknownAuditOwnerActReadResponse(BaseModel):
    owner_act_id: UUID
    case_id: UUID
    owner_id: UUID
    approved: bool
    rationale: str
    created_at: datetime
