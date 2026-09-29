from datetime import date, datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

ContractExecutionActKindValue = Literal["WORK_RECEPTION", "RIGHTS_PRESERVATION", "CONTRACT_EXIT"]
ContractReceptionOutcomeValue = Literal[
    "WITH_RESERVATIONS", "UNDER_RESERVATIONS", "WITHOUT_RESERVATIONS"
]
ContractExecutionVersionRelation = Literal["MATCHES_CASE_CURRENT", "REVIEW_REQUIRED", "UNKNOWN"]
ContractInstrumentVersionRelation = Literal["DECLARED", "REVIEW_REQUIRED", "UNKNOWN"]
ContractInstrumentKindValue = Literal["SIGNED_CONTRACT", "AMENDMENT"]
ContractExecutionEvidenceRequalificationDecisionValue = Literal[
    "RETAINED_AS_DECLARED", "RELINKED_TO_DECLARED_VERSION", "NEEDS_CLARIFICATION"
]


class RecordContractExecutionEvidenceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    act_id: UUID
    act_kind: ContractExecutionActKindValue
    reception_outcome: ContractReceptionOutcomeValue | None = None
    summary: str = Field(min_length=1, max_length=2000)
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    declared_event_date: date | None = None
    contract_instrument_version_id: UUID | None = None


class RecordContractInstrumentVersionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    contract_instrument_version_id: UUID
    instrument_kind: ContractInstrumentKindValue
    version_reference: str = Field(min_length=1, max_length=500)
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1000)], ...] = Field(
        min_length=1, max_length=32
    )


class DeclareContractInstrumentSupersessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    supersession_id: UUID
    replacing_contract_instrument_version_id: UUID
    replaced_contract_instrument_version_id: UUID
    rationale: str = Field(min_length=1, max_length=2000)


class RecordContractExecutionEvidenceRequalificationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    requalification_id: UUID
    act_id: UUID
    supersession_id: UUID
    expected_revision: int = Field(ge=0)
    decision: ContractExecutionEvidenceRequalificationDecisionValue
    resulting_contract_instrument_version_id: UUID | None = None
    rationale: str = Field(min_length=1, max_length=2000)


class RecordContractExecutionEvidenceResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    act_id: UUID
    result_code: Literal["CONTRACT_EXECUTION_EVIDENCE_RECORDED"]
    replayed: bool


class RecordContractInstrumentVersionResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    contract_instrument_version_id: UUID
    result_code: Literal["CONTRACT_INSTRUMENT_VERSION_RECORDED"]
    replayed: bool


class DeclareContractInstrumentSupersessionResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    supersession_id: UUID
    result_code: Literal["CONTRACT_INSTRUMENT_SUPERSESSION_DECLARED"]
    replayed: bool


class RecordContractExecutionEvidenceRequalificationResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    requalification_id: UUID
    revision: int
    result_code: Literal["CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION_RECORDED"]
    replayed: bool


class ContractInstrumentVersionResponse(BaseModel):
    contract_instrument_version_id: UUID
    case_id: UUID
    instrument_kind: ContractInstrumentKindValue
    version_reference: str
    source_refs: list[str]
    evidence_refs: list[str]
    actor_id: UUID
    recorded_at: datetime


class ContractInstrumentVersionSummary(BaseModel):
    contract_instrument_version_id: UUID
    instrument_kind: ContractInstrumentKindValue
    version_reference: str
    source_refs: list[str]
    evidence_refs: list[str]


class ContractInstrumentSupersessionResponse(BaseModel):
    supersession_id: UUID
    case_id: UUID
    replacing_contract_instrument_version_id: UUID
    replacing_instrument_kind: ContractInstrumentKindValue
    replacing_version_reference: str
    replaced_contract_instrument_version_id: UUID
    replaced_instrument_kind: ContractInstrumentKindValue
    replaced_version_reference: str
    rationale: str
    actor_id: UUID
    recorded_at: datetime


class ContractExecutionEvidenceRequalificationResponse(BaseModel):
    requalification_id: UUID
    case_id: UUID
    act_id: UUID
    act_kind: ContractExecutionActKindValue
    act_summary: str
    supersession_id: UUID
    review_revision: int
    decision: ContractExecutionEvidenceRequalificationDecisionValue
    resulting_contract_instrument_version_id: UUID | None
    resulting_instrument_kind: ContractInstrumentKindValue | None
    resulting_version_reference: str | None
    rationale: str
    actor_id: UUID
    recorded_at: datetime


class ContractExecutionEvidenceTimelineAct(BaseModel):
    act_id: UUID
    act_kind: ContractExecutionActKindValue
    reception_outcome: ContractReceptionOutcomeValue | Literal["UNKNOWN"]
    summary: str
    declared_event_date: date | None
    source_refs: list[str]
    evidence_refs: list[str]
    case_dce_version_id_at_recording: UUID | None
    current_dce_relation: ContractExecutionVersionRelation
    contract_instrument_version_id: UUID | None
    current_instrument_relation: ContractInstrumentVersionRelation
    contract_instrument_version: ContractInstrumentVersionSummary | None


class ContractExecutionEvidenceTimelineActEvent(BaseModel):
    event_type: Literal["EXECUTION_EVIDENCE"]
    event_id: UUID
    case_id: UUID
    revision: Literal[1]
    status: Literal["RECORDED"]
    status_origin: Literal["HUMAN_ACT"]
    actor_id: UUID
    recorded_at: datetime
    act: ContractExecutionEvidenceTimelineAct


class ContractExecutionEvidenceTimelineSupersessionEvent(BaseModel):
    event_type: Literal["INSTRUMENT_SUPERSESSION"]
    event_id: UUID
    case_id: UUID
    revision: Literal[1]
    status: Literal["SUPERSEDED"]
    status_origin: Literal["PATRON_DECLARATION"]
    actor_id: UUID
    recorded_at: datetime
    supersession_id: UUID
    rationale: str
    replacing: ContractInstrumentVersionSummary
    replaced: ContractInstrumentVersionSummary


class ContractExecutionEvidenceTimelineRequalificationEvent(BaseModel):
    event_type: Literal["EVIDENCE_REQUALIFICATION"]
    event_id: UUID
    case_id: UUID
    revision: int
    status: ContractExecutionEvidenceRequalificationDecisionValue
    status_origin: Literal["PATRON_DECISION"]
    actor_id: UUID
    recorded_at: datetime
    requalification_id: UUID
    act_id: UUID
    supersession_id: UUID
    act_kind: ContractExecutionActKindValue
    act_summary: str
    act_source_refs: list[str]
    act_evidence_refs: list[str]
    resulting_contract_instrument_version_id: UUID | None
    resulting_instrument_kind: ContractInstrumentKindValue | None
    resulting_version_reference: str | None
    rationale: str


ContractExecutionEvidenceTimelineEvent = Annotated[
    ContractExecutionEvidenceTimelineActEvent
    | ContractExecutionEvidenceTimelineSupersessionEvent
    | ContractExecutionEvidenceTimelineRequalificationEvent,
    Field(discriminator="event_type"),
]


class ContractExecutionEvidenceResponse(BaseModel):
    act_id: UUID
    case_id: UUID
    act_kind: ContractExecutionActKindValue
    reception_outcome: ContractReceptionOutcomeValue | Literal["UNKNOWN"]
    summary: str
    source_refs: list[str]
    evidence_refs: list[str]
    declared_event_date: date | None
    case_dce_version_id_at_recording: UUID | None
    version_relation: ContractExecutionVersionRelation
    contract_instrument_version_relation: ContractInstrumentVersionRelation
    contract_instrument_version_id: UUID | None
    contract_instrument_version: ContractInstrumentVersionSummary | None
    actor_id: UUID
    recorded_at: datetime
