# ruff: noqa: I001
from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ObligationType = Literal[
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


class RecordPostReceptionObligationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    obligation_id: UUID
    obligation_type: ObligationType
    origin_reception_act_id: UUID | None = None
    summary: str = Field(min_length=1, max_length=2000)
    source_refs: tuple[str, ...] = Field(min_length=1, max_length=32)
    due_date: date | None = None
    resource_note: str | None = Field(default=None, max_length=2000)
    cost_estimate_note: str | None = Field(default=None, max_length=2000)
    fulfillment_proof_refs: tuple[str, ...] = Field(default=(), max_length=32)
    sanction_ref: str | None = Field(default=None, max_length=500)


class RecordPostReceptionObligationResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    obligation_id: UUID
    result_code: str
    replayed: bool


class PostReceptionObligationResponse(BaseModel):
    obligation_id: UUID
    case_id: UUID
    obligation_type: ObligationType
    origin_reception_act_id: UUID | None
    origin_reception_summary: str | None
    origin_reception_outcome: Literal[
        "WITH_RESERVATIONS", "UNDER_RESERVATIONS", "WITHOUT_RESERVATIONS", "UNKNOWN"
    ]
    summary: str
    source_refs: list[str]
    due_date: date | None
    resource_note: str | None
    cost_estimate_note: str | None
    fulfillment_proof_refs: list[str]
    sanction_ref: str | None
    status: Literal["REVIEW_REQUIRED", "IN_PROGRESS", "FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"]
    revision: int
    latest_transition_id: UUID | None = None
    latest_transition_actor_id: UUID | None = None
    latest_transition_at: datetime | None = None
    latest_transition_rationale: str | None = None
    completion_proof_refs: list[str] = Field(default_factory=list)
    actor_id: UUID
    created_at: datetime


class TransitionPostReceptionObligationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    transition_id: UUID
    expected_revision: int = Field(ge=0)
    resulting_status: Literal["IN_PROGRESS", "FOLLOW_UP_REQUIRED", "UNKNOWN", "COMPLETED"]
    rationale: str = Field(min_length=1, max_length=2000)
    evidence_refs: tuple[str, ...] = Field(default=(), max_length=32)


class TransitionPostReceptionObligationResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    transition_id: UUID
    result_code: str
    aggregate_revision: int
    replayed: bool
