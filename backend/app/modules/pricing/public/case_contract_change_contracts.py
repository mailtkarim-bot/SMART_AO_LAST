from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RecordCaseContractChangeEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    event_id: UUID
    handover_snapshot_id: UUID
    change_kind: Literal["ORDER_OF_SERVICE", "CHANGE_REQUEST", "ADDENDUM", "SCHEDULE_CHANGE"]
    contract_instrument_version_id: UUID | None = None
    issuer: str | None = Field(default=None, max_length=240)
    summary: str = Field(min_length=1, max_length=2_000)
    scope_note: str = Field(min_length=1, max_length=2_000)
    source_refs: list[str] = Field(min_length=1, max_length=32)
    evidence_refs: list[str] = Field(min_length=1, max_length=32)
    declared_received_at: datetime


class RecordCaseContractChangeApplicabilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    review_id: UUID
    handover_snapshot_id: UUID
    contract_instrument_version_id: UUID
    expected_revision: int = Field(ge=0)
    decision: Literal["APPLICABLE_TO_HANDOVER", "NOT_APPLICABLE", "NEEDS_CLARIFICATION"]
    delta_state: Literal["UNKNOWN", "DECLARED"] = "UNKNOWN"
    delta_note: str | None = Field(default=None, max_length=2_000)
    rationale: str = Field(min_length=1, max_length=2_000)
    evidence_refs: list[str] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def delta_note_matches_state(self):
        if self.delta_state == "DECLARED" and not (self.delta_note and self.delta_note.strip()):
            raise ValueError("DECLARED_DELTA_NOTE_REQUIRED")
        if self.delta_state == "UNKNOWN" and self.delta_note is not None:
            raise ValueError("UNKNOWN_DELTA_NOTE_MUST_BE_EMPTY")
        return self


class RecordCaseContractChangeActionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    action_id: UUID
    applicability_review_id: UUID
    expected_revision: int = Field(ge=0)
    action_summary: str = Field(min_length=1, max_length=2_000)
    evidence_refs: list[str] = Field(min_length=1, max_length=32)
    due_at: datetime | None = None
    due_date_absence_reason: str | None = Field(default=None, max_length=500)


class ContractChangeInstrumentResponse(BaseModel):
    contract_instrument_version_id: UUID
    instrument_kind: Literal["SIGNED_CONTRACT", "AMENDMENT"]
    version_reference: str
    source_refs: list[str]
    evidence_refs: list[str]


class ContractChangeApplicabilityResponse(BaseModel):
    review_id: UUID
    revision: int
    contract_instrument_version_id: UUID
    decision: Literal["APPLICABLE_TO_HANDOVER", "NOT_APPLICABLE", "NEEDS_CLARIFICATION"]
    delta_state: Literal["UNKNOWN", "DECLARED"]
    delta_note: str | None
    rationale: str
    evidence_refs: list[str]
    recorded_at: str
    contract_instrument: ContractChangeInstrumentResponse | None


class ContractChangeActionResponse(BaseModel):
    action_id: UUID
    revision: int
    applicability_review_id: UUID
    summary: str
    evidence_refs: list[str]
    due_at: str | None
    due_date_absence_reason: str | None
    state: Literal["RECORDED"]
    recorded_at: str


class ContractChangeEventResponse(BaseModel):
    event_id: UUID
    case_id: UUID
    handover_snapshot_id: UUID
    outcome_id: UUID | None
    lot_reference: str
    offer_package_id: UUID | None
    offer_package_version: int | None
    offer_manifest_sha256: str | None
    offer_source_locator: str | None
    change_kind: Literal["ORDER_OF_SERVICE", "CHANGE_REQUEST", "ADDENDUM", "SCHEDULE_CHANGE"]
    issuer: str | None
    summary: str
    scope_note: str
    source_refs: list[str]
    evidence_refs: list[str]
    declared_received_at: str
    declared_instrument: ContractChangeInstrumentResponse | None
    applicability_state: Literal[
        "UNKNOWN", "APPLICABLE_TO_HANDOVER", "NOT_APPLICABLE", "NEEDS_CLARIFICATION"
    ]
    applicability_history: list[ContractChangeApplicabilityResponse]
    actions: list[ContractChangeActionResponse]


class CaseContractChangeEventListResponse(BaseModel):
    case_id: UUID
    events: list[ContractChangeEventResponse] = Field(default_factory=list)


class RecordCaseContractChangeResponse(BaseModel):
    status: str
    result_code: str
    replayed: bool
