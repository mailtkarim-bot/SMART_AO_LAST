from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.pricing.application.case_contract_change_commands import (
    A1EngagementSourceInput,
    validate_impact_declaration_payload,
)


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


class RecordCaseContractChangeActionImpactRelationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    relation_id: UUID
    expected_revision: int = Field(ge=0)
    state: Literal["LINKED", "UNKNOWN", "NOT_APPLICABLE"]
    declaration_ids: list[UUID] = Field(default_factory=list, max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)
    unknown_reason: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def state_matches_declarations(self):
        if len(set(self.declaration_ids)) != len(self.declaration_ids):
            raise ValueError("C4_DECLARATION_IDS_MUST_BE_UNIQUE")
        if self.state == "LINKED":
            if not self.declaration_ids or self.unknown_reason is not None:
                raise ValueError("C4_LINKED_REQUIRES_DECLARATIONS")
        elif self.declaration_ids or not (self.unknown_reason and self.unknown_reason.strip()):
            raise ValueError("C4_NON_LINKED_REQUIRES_REASON_AND_NO_DECLARATIONS")
        return self


class RecordCaseContractChangeEngagementLinkRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    linkage_id: UUID
    expected_revision: int = Field(ge=0)
    state: Literal["LINKED", "UNKNOWN"]
    selected_sources: list[A1EngagementSourceInput] = Field(max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)
    unknown_reason: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def state_matches_sources(self):
        if self.state == "LINKED" and (
            not self.selected_sources or self.unknown_reason is not None
        ):
            raise ValueError("LINKED_REQUIRES_SELECTED_SOURCES")
        if self.state == "UNKNOWN" and (
            self.selected_sources or not (self.unknown_reason and self.unknown_reason.strip())
        ):
            raise ValueError("UNKNOWN_REQUIRES_REASON_AND_NO_SELECTION")
        return self


class RecordCaseContractChangeImpactDeclarationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    declaration_id: UUID
    linkage_id: UUID
    source: A1EngagementSourceInput
    expected_revision: int = Field(ge=0)
    axis: Literal["SCOPE", "COST", "CASH", "SCHEDULE", "CAPACITY"]
    impact_state: Literal["DECLARED", "UNKNOWN"]
    impact_summary: str | None = Field(default=None, max_length=2_000)
    impact_unknown_reason: str | None = Field(default=None, max_length=1_000)
    measurement_state: Literal["DECLARED", "UNKNOWN", "NOT_APPLICABLE"]
    value_as_declared: str | None = Field(
        default=None,
        max_length=80,
        pattern=r"^-?[0-9]+([,.][0-9]{1,6})?$",
    )
    currency_code: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    unit: str | None = Field(default=None, max_length=32)
    measurement_unknown_reason: str | None = Field(default=None, max_length=1_000)
    assumptions: list[str] = Field(default_factory=list, max_length=32)
    source_refs: list[str] = Field(min_length=1, max_length=32)
    evidence_refs: list[str] = Field(default_factory=list, max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)

    @model_validator(mode="after")
    def validate_declared_impact(self):
        validate_impact_declaration_payload(
            axis=self.axis,
            impact_state=self.impact_state,
            impact_summary=self.impact_summary,
            impact_unknown_reason=self.impact_unknown_reason,
            measurement_state=self.measurement_state,
            value_as_declared=self.value_as_declared,
            currency_code=self.currency_code,
            unit=self.unit,
            measurement_unknown_reason=self.measurement_unknown_reason,
            evidence_refs=self.evidence_refs,
        )
        return self


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


class ContractChangeEngagementLinkResponse(BaseModel):
    linkage_id: UUID
    revision: int
    state: Literal["LINKED", "UNKNOWN"]
    selected_sources: list[dict[str, object]]
    rationale: str
    unknown_reason: str | None
    recorded_at: str


class ContractChangeImpactDeclarationResponse(BaseModel):
    declaration_id: UUID
    linkage_id: UUID
    source: dict[str, object]
    axis: Literal["SCOPE", "COST", "CASH", "SCHEDULE", "CAPACITY"]
    revision: int
    impact_state: Literal["DECLARED", "UNKNOWN"]
    impact_summary: str | None
    impact_unknown_reason: str | None
    measurement_state: Literal["DECLARED", "UNKNOWN", "NOT_APPLICABLE"]
    value_as_declared: str | None
    currency_code: str | None
    unit: str | None
    measurement_unknown_reason: str | None
    assumptions: list[str]
    source_refs: list[str]
    evidence_refs: list[str]
    rationale: str
    linkage_state: Literal["CURRENT", "REVIEW_REQUIRED"]
    recorded_at: str


class ContractChangeActionImpactRelationResponse(BaseModel):
    relation_id: UUID
    action_id: UUID
    applicability_review_id: UUID
    revision: int
    state: Literal["LINKED", "UNKNOWN", "NOT_APPLICABLE"]
    declaration_ids: list[UUID]
    rationale: str
    unknown_reason: str | None
    projection_state: Literal["CURRENT", "REVIEW_REQUIRED"]
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
    a1_engagements_state: Literal["KNOWN", "UNKNOWN"]
    a1_engagements: list[dict[str, object]]
    engagement_linkage_state: Literal["LINKED", "UNKNOWN"]
    engagement_linkage_history: list[ContractChangeEngagementLinkResponse]
    impact_declarations: list[ContractChangeImpactDeclarationResponse]
    action_impact_relations: list[ContractChangeActionImpactRelationResponse]


class CaseContractChangeEventListResponse(BaseModel):
    case_id: UUID
    events: list[ContractChangeEventResponse] = Field(default_factory=list)


class RecordCaseContractChangeResponse(BaseModel):
    status: str
    result_code: str
    replayed: bool
