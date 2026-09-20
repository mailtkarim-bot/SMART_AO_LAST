from __future__ import annotations

from typing import Literal
from uuid import UUID

from app.modules.opportunity.application.boamp_qualification import (
    BoampDeadlineState,
    BoampLotScopeState,
    BoampP0State,
    BoampP1State,
    BoampUnknownCode,
    QualificationDecision,
    QualificationReason,
)
from pydantic import BaseModel, ConfigDict, Field


class BoampUnknownResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: BoampUnknownCode
    missing: str
    why_it_matters: str
    possible_impact: str
    responsible: str | None
    next_action: str
    due_at: str | None
    state: Literal["OPEN"]
    source_ref: str


class BoampObservationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: UUID
    source_notice_id: str
    title: str | None
    observed_at: str
    publication_date: str | None
    response_deadline: str | None
    department_codes: list[str]
    market_types: list[str]
    source_status: str | None
    score_version: str
    score: int = Field(ge=0, le=100)
    score_explanation: dict[str, object]
    fingerprint_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    p0_state: BoampP0State
    p0_decision: QualificationDecision | None
    p0_reason_code: QualificationReason | None
    p0_qualification_id: UUID | None
    p0_decided_at: str | None
    p1_state: BoampP1State
    p1_case_id: UUID | None
    p1_opened_at: str | None
    lot_scope_state: BoampLotScopeState
    lot_references: list[str]
    lot_scope_source: str | None
    deadline_state: BoampDeadlineState
    deadline_source: str | None
    deadline_source_timezone: str | None
    deadline_normalized_timezone: str | None
    unknowns: list[BoampUnknownResponse]


class BoampSourceStatusResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Literal["BOAMP"] = "BOAMP"
    state: Literal["AVAILABLE", "UNAVAILABLE", "UNKNOWN"]
    checked_at: str
    last_success_at: str | None
    retryable: bool = True
    manual_entry_available: bool = True


class BoampObservationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observations: list[BoampObservationResponse]
    source_status: BoampSourceStatusResponse


class BoampObservationQualificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: QualificationDecision
    reason_code: QualificationReason
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


class BoampQualificationReceiptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    qualification_id: UUID
    event_id: UUID
    replayed: bool


class BoampObservationCreateCaseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


class BoampCaseCreationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: str = "CASE_CREATED"
    case_id: UUID
    version: int = Field(ge=0)
    event_ids: list[UUID]
    replayed: bool
