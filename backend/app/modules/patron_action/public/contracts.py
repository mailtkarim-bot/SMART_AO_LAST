from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreatePatronActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    action_id: UUID
    case_id: UUID | None = None
    functional_key: str = Field(min_length=1, max_length=240)
    action_type: Literal[
        "REVIEW_PREPARATION",
        "CONTROL_SUBMISSION",
        "VALIDATE_PRICE",
        "DECIDE_GO_NO_GO",
    ]
    severity: Literal["URGENT", "BLOCKING", "AT_RISK", "MONITOR"]
    title: str = Field(min_length=1, max_length=240)
    why_now: str = Field(min_length=1, max_length=1000)
    impact: str = Field(min_length=1, max_length=1000)
    recommended_action: str = Field(min_length=1, max_length=1000)
    due_at: datetime | None = None
    source_refs: list[str] = Field(max_length=32)


class RecordCaseOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    outcome_id: UUID
    case_id: UUID
    lot_reference: str = Field(min_length=1, max_length=120)
    outcome: Literal["WON", "LOST", "UNKNOWN"]
    source_locator: str | None = Field(default=None, max_length=500)
    reservations: list[str] = Field(default_factory=list, max_length=32)
    unknown_reason: str | None = Field(default=None, max_length=1000)


class TransmitWonOutcomeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    transmission_id: UUID
    outcome_id: UUID
    case_id: UUID
    recipient: str = Field(min_length=1, max_length=120)


class RecordCaseOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    order_id: UUID
    outcome_id: UUID
    case_id: UUID
    decision: Literal["ACCEPTED", "REJECTED"]
    rationale: str = Field(min_length=1, max_length=1000)


class RecordCaseP6ControlRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    p6_control_id: UUID
    order_id: UUID
    case_id: UUID
    decision: Literal["APPROVED", "REJECTED"]
    reservations: list[str] = Field(default_factory=list, max_length=32)
    rationale: str = Field(min_length=1, max_length=1000)


class RecordCaseP7ResultRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    p7_result_id: UUID
    p6_control_id: UUID
    case_id: UUID
    result: Literal["COMPLETED", "UNKNOWN", "INTERRUPTED"]
    source_locator: str | None = Field(default=None, max_length=500)
    reason: str | None = Field(default=None, max_length=1000)
    reservations: list[str] = Field(default_factory=list, max_length=32)


class RecordCaseRexRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    rex_id: UUID
    p7_result_id: UUID
    case_id: UUID
    motif: Literal["KNOWN", "UNKNOWN"]
    scope: Literal["CASE_ONLY", "LOT_PATTERN", "ENTERPRISE_PATTERN"]
    validation: Literal["PENDING", "APPROVED"]
    observation: str = Field(min_length=1, max_length=2000)
    consequence: str = Field(min_length=1, max_length=2000)
    follow_up: str = Field(min_length=1, max_length=2000)
    source_locator: str | None = Field(default=None, max_length=500)


class RecordCaseDispositionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    disposition_id: UUID
    case_id: UUID
    state: Literal["SUSPENDED", "RESUMED", "CLOSED"]
    reason_code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Z0-9_]+$")
    rationale: str = Field(min_length=1, max_length=2000)
    p7_result_id: UUID | None = None
    source_locator: str | None = Field(default=None, max_length=500)


class RequestCaseExportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    export_request_id: UUID
    case_id: UUID
    artifact_kind: Literal["CASE_DOSSIER", "P7_RESULT", "REX", "AUDIT_TRAIL"]
    purpose: str = Field(min_length=1, max_length=2000)
    recipient_label: str | None = Field(default=None, max_length=240)
    source_locator: str | None = Field(default=None, max_length=500)


class RecordCaseRetentionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    retention_id: UUID
    case_id: UUID
    evidence_locator: str = Field(min_length=1, max_length=500)
    retention_basis: Literal["MARKET_RECORD", "OPEN_LITIGATION", "INTERNAL_POLICY"]
    retain_until: date
    rationale: str = Field(min_length=1, max_length=2000)


class TransitionPatronActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    transition_id: UUID
    expected_revision: int = Field(ge=1)
    target_state: Literal["IN_PROGRESS", "WAITING", "COMPLETED", "ABANDONED"]
    reason_code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Z0-9_]+$")


class PatronActionCommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["PATRON_ACTION_CREATED"]
    aggregate_id: UUID
    aggregate_revision: int = Field(ge=1)
    event_ids: list[UUID]
    replayed: bool = False


class PatronActionTransitionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["PATRON_ACTION_TRANSITIONED"]
    aggregate_id: UUID
    aggregate_revision: int = Field(ge=2)
    event_ids: list[UUID]
    replayed: bool = False


class PatronActionProjectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    action_id: UUID
    case_id: UUID | None
    functional_key: str
    action_type: str
    severity: Literal["URGENT", "BLOCKING", "AT_RISK", "MONITOR"]
    state: Literal["OPEN", "IN_PROGRESS", "WAITING", "COMPLETED", "ABANDONED"]
    title: str
    why_now: str
    impact: str
    recommended_action: str
    due_at: datetime | None
    source_refs: list[str]
    aggregate_revision: int = Field(ge=1)


class PatronActionQueueResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[PatronActionProjectionResponse]
    open_count: int = Field(ge=0)
