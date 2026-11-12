"""Stable public HTTP contracts exported by the DCE module."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from app.modules.dce.application.commands import (
    AcknowledgeAssignmentCommand,
    AddFinancialReportLineCommand,
    AmendCaseAssignmentScopeCommand,
    AssignmentInteractionKind,
    AssignmentInteractionValidationCode,
    AssignmentScopeAction,
    AssignmentScopeClassification,
    CreateCaseAssignmentCommand,
    CreateConsultationCommand,
    CreateFinancialReportDraftCommand,
    EndCaseAssignmentCommand,
    EndReasonCode,
    PublishFinancialReportCommand,
    ReactivateCaseAssignmentCommand,
    ReactivationReasonCode,
    RecordDceRequirementConfirmationCommand,
    RegisterDceVersionCommand,
    ReportAssignmentUnavailabilityCommand,
    RequestAssignmentClarificationCommand,
    SuspendCaseAssignmentCommand,
    SuspensionReasonCode,
    ValidateAssignmentInteractionCommand,
)


class PublicResponseModel(BaseModel):
    """Closed response base that serializes only explicitly approved fields."""

    model_config = ConfigDict(extra="forbid")


class PublicRequestModel(BaseModel):
    """Closed HTTP intent model; server-owned actor and tenant stay outside it."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProjectionStatusResponse(PublicResponseModel):
    status: Literal["CURRENT", "REFRESH_PENDING", "PARTIAL"]
    refreshed_at: datetime | None = None
    tracking_correlation_id: UUID | None = None


class AggregateReferenceResponse(PublicResponseModel):
    aggregate_type: str
    aggregate_id: UUID
    aggregate_revision: int = Field(ge=0)


class CreateConsultationResponse(PublicResponseModel):
    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["CONSULTATION_CREATED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    projection: ProjectionStatusResponse
    replayed: bool = False


class PrepareDceStagingRequest(BaseModel):
    """Public intent; the server allocates the opaque storage object identity."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    consultation_id: UUID
    consultation_revision: int = Field(ge=0)
    original_filename: str = Field(min_length=1, max_length=500)
    expected_byte_size: int = Field(gt=0, le=2_000_000_000)
    source_channel: str = Field(pattern=r"^(BUYER_PLATFORM|EMAIL|MANUAL_UPLOAD|RECTIFICATION)$")
    expires_at: datetime


class DceStagingStatusResponse(PublicResponseModel):
    """Public staging state; intentionally excludes private storage locator data."""

    storage_object_id: UUID
    state: Literal["AWAITING_UPLOAD"]
    expires_at: datetime


class PrepareDceStagingResponse(PublicResponseModel):
    """DCE-STAGING-01 receipt for a server-keyed staging intent."""

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["DCE_STAGING_PREPARED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    staging: DceStagingStatusResponse
    replayed: bool = False


class UploadDceStagedObjectResponse(PublicResponseModel):
    """Safe DCE-UPLOAD-01 success response without storage or scanner internals."""

    storage_object_id: UUID
    state: Literal["CLEAN"]


class RegisterDceVersionResponse(PublicResponseModel):
    """DCE-ADMIT-HTTP-01 success receipt without document or storage metadata."""

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["DCE_VERSION_REGISTERED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


class DceVersionMetadataResponse(PublicResponseModel):
    """DCE-READ-01 metadata only; it deliberately excludes documents and provenance."""

    id: UUID
    consultation_id: UUID
    predecessor_dce_version_id: UUID | None
    source_received_at: datetime
    lifecycle: str
    integrity: str
    classification_readiness: str
    analysis_readiness: str
    aggregate_revision: int = Field(ge=0)


class DceDocumentInventoryItemResponse(PublicResponseModel):
    """One admitted original with its latest deterministic reading state."""

    document_id: UUID
    original_filename: str
    media_type: str
    byte_size: int = Field(gt=0)
    received_from: str
    processing_state: Literal[
        "RECEIVED",
        "READ",
        "REVIEW_REQUIRED",
        "UNSUPPORTED",
        "LIMIT_REACHED",
        "PROTECTED",
        "UNREADABLE",
    ]
    issue_code: str | None = None


class DceDocumentInventoryResponse(PublicResponseModel):
    """Closed per-file inventory; private storage and content stay hidden."""

    dce_version_id: UUID
    items: list[DceDocumentInventoryItemResponse]


class ConsultationProjectionResponse(PublicResponseModel):
    id: UUID
    buyer_legal_name: str
    external_reference: str | None
    object_label: str
    location_label: str | None
    lifecycle: str
    freshness: str
    aggregate_revision: int = Field(ge=0)
    lots: list[str]
    tranches: list[str]
    projection_status: Literal["CURRENT", "REFRESH_PENDING", "PARTIAL"]


class CaseDceReadingDceResponse(PublicResponseModel):
    dce_version_id: UUID
    lifecycle: str
    integrity: str
    classification_readiness: str
    analysis_readiness: str
    source_received_at: datetime


class CaseDceReadingCountersResponse(PublicResponseModel):
    total: int = Field(ge=0)
    pending_human_confirmation: int = Field(ge=0)
    confirmed: int = Field(ge=0)
    review_required: int = Field(ge=0)
    not_applicable: int = Field(ge=0)


class CaseDceSourceLocatorResponse(PublicResponseModel):
    kind: Literal[
        "pdf_page",
        "pymupdf_block",
        "ocr_page",
        "docx_paragraph",
        "docx_table_cell",
        "xlsx_cell",
        "text_line",
        "docling_markdown",
    ]
    coordinates: dict[str, object]


class CaseDceSourceAnchorResponse(PublicResponseModel):
    source_anchor_id: UUID
    dce_version_id: UUID
    dce_document_id: UUID
    extraction_id: UUID
    fragment_ordinal: int = Field(ge=1)
    source_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    extractor_id: str
    extractor_version: str
    fragment_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    locator_state: Literal["RESOLVED", "UNKNOWN"]
    locator: CaseDceSourceLocatorResponse | None


class CaseDceValueEvidenceResponse(PublicResponseModel):
    field: Literal["DOCUMENT", "DATE", "TIME", "TIMEZONE", "LOT"]
    value: str = Field(min_length=1, max_length=80)
    start_byte_offset: int = Field(ge=0)
    end_byte_offset: int = Field(gt=0)

    @model_validator(mode="after")
    def validate_region(self) -> CaseDceValueEvidenceResponse:
        if self.end_byte_offset <= self.start_byte_offset:
            raise ValueError("SOURCE_REGION_REQUIRED")
        return self


class CaseDceStructuredCandidateResponse(PublicResponseModel):
    projector_version: Literal["1"] = "1"
    state: Literal["UNKNOWN", "CANDIDATES_ONLY", "REVIEW_REQUIRED"] = "UNKNOWN"
    reason_code: str = Field(default="UNPROVEN_SOURCE", pattern=r"^[A-Z0-9_]{1,64}$")
    source_fragment_id: UUID | None = None
    documents: list[
        Literal["DC1", "DC2", "DC4", "DUME", "MEMOIRE_TECHNIQUE", "AE", "BPU", "DPGF"]
    ] = Field(default_factory=list, max_length=8)
    document_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    date_iso: str | None = Field(default=None, pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    date_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    time_local: str | None = Field(default=None, pattern=r"^[0-9]{2}:[0-9]{2}$")
    time_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    timezone: str | None = Field(default=None, pattern=r"^UTC(?:[+-][0-9]{2}:[0-9]{2})?$")
    timezone_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    lot_numbers: list[Annotated[int, Field(ge=1, le=999)]] = Field(
        default_factory=list, max_length=64
    )
    lot_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    evidence: list[CaseDceValueEvidenceResponse] = Field(default_factory=list, max_length=64)

    @model_validator(mode="after")
    def validate_candidate_states(self) -> CaseDceStructuredCandidateResponse:
        fields = (
            (self.document_state, bool(self.documents)),
            (self.date_state, self.date_iso is not None),
            (self.time_state, self.time_local is not None),
            (self.timezone_state, self.timezone is not None),
            (self.lot_state, bool(self.lot_numbers)),
        )
        if any((state == "CANDIDATE") != known for state, known in fields):
            raise ValueError("CANDIDATE_VALUE_STATE_MISMATCH")
        if self.state != "CANDIDATES_ONLY" and (self.evidence or any(known for _, known in fields)):
            raise ValueError("UNKNOWN_VALUES_MUST_REMAIN_UNKNOWN")
        if self.state == "CANDIDATES_ONLY" and (
            not self.evidence or self.source_fragment_id is None
        ):
            raise ValueError("CANDIDATE_SOURCE_REQUIRED")
        declared: set[tuple[str, str]] = {("DOCUMENT", code) for code in self.documents}
        declared.update(("LOT", str(number)) for number in self.lot_numbers)
        declared.update(
            (field, value)
            for field, value in (
                ("DATE", self.date_iso),
                ("TIME", self.time_local),
                ("TIMEZONE", self.timezone),
            )
            if value is not None
        )
        if declared != {(e.field, e.value) for e in self.evidence}:
            raise ValueError("CANDIDATE_VALUE_EVIDENCE_MISMATCH")
        return self


class CaseDceReadingRequirementResponse(PublicResponseModel):
    requirement_id: UUID
    confirmation_revision: int | None
    requirement_type: str
    directive_signal: str
    confirmation_outcome: str
    uncertainty_status: str
    document_family: str
    source_locator_label: str
    source_anchor: CaseDceSourceAnchorResponse | None = None
    structured_candidate: CaseDceStructuredCandidateResponse | None = None

    @model_validator(mode="after")
    def validate_structured_provenance(self) -> CaseDceReadingRequirementResponse:
        candidate = self.structured_candidate
        if (
            candidate is not None
            and candidate.state == "CANDIDATES_ONLY"
            and (
                self.source_anchor is None
                or self.source_anchor.locator_state != "RESOLVED"
                or candidate.source_fragment_id != self.source_anchor.source_anchor_id
            )
        ):
            raise ValueError("STRUCTURED_SOURCE_ANCHOR_REQUIRED")
        return self


class CaseDceDocumentCoverageResponse(PublicResponseModel):
    document_id: UUID
    extraction_id: UUID | None
    document_family: Literal[
        "RC",
        "CCAP",
        "CCTP",
        "AE",
        "BPU",
        "DPGF",
        "PLAN",
        "ANNEX",
        "RECTIFICATION",
        "SOURCE_UNCLASSIFIED",
    ]
    extraction_status: Literal[
        "NOT_STARTED",
        "COMPLETED",
        "REVIEW_REQUIRED",
        "UNSUPPORTED",
        "REJECTED_LIMIT",
        "FAILED_SAFE",
    ]


class CaseDceCoverageExceptionResponse(PublicResponseModel):
    observation_id: UUID
    kind: Literal["ARCHIVE_ENTRY", "DECLARED_MISSING"]
    state: Literal[
        "NOT_EXTRACTED",
        "NESTED_ARCHIVE",
        "DIRECTORY",
        "EXCLUDED_UNSAFE",
        "EXCLUDED_COMPRESSION",
        "EXCLUDED_SYMLINK",
        "EXCLUDED_ENCRYPTED",
        "EXCLUDED_LIMIT",
        "UNREADABLE",
        "INVENTORY_LIMIT",
        "DECLARED_MISSING",
    ]
    document_id: UUID | None
    extraction_id: UUID | None
    entry_path: list[int] = Field(max_length=4)
    document_family: str
    source_state: Literal["RESOLVED", "UNKNOWN"]
    lot_applicability: Literal["UNKNOWN"]
    criticality: Literal["UNKNOWN"]


class CaseDceAnnouncementAnchorResponse(PublicResponseModel):
    fragment_id: UUID
    fragment_ordinal: int = Field(ge=1)
    locator_label: str
    part: int = Field(ge=1)
    kind: Literal["HEADING", "BRIDGE", "SOURCE"]
    start_byte_offset: int = Field(ge=0)
    end_byte_offset: int = Field(gt=0)


class CaseDceAnnouncementResponse(PublicResponseModel):
    candidate_id: UUID
    document_family: str
    claim: Literal[
        "PROVIDED_SIGNAL",
        "NOT_PROVIDED_SIGNAL",
        "SUBMISSION_SIGNAL",
        "NOT_REQUIRED_SIGNAL",
        "PROHIBITED_SUBMISSION_SIGNAL",
        "AMBIGUOUS",
    ]
    lot_numbers: list[int]
    source_document_id: UUID
    source_extraction_id: UUID
    source_fragment_id: UUID
    source_locator_label: str
    source_locator_state: Literal["RESOLVED", "UNKNOWN"]
    start_byte_offset: int = Field(ge=0)
    end_byte_offset: int = Field(gt=0)
    context_fragment_id: UUID | None = None
    context_locator_label: str | None = None
    context_start_byte_offset: int | None = None
    context_end_byte_offset: int | None = None
    family_candidate_document_ids: list[UUID]
    presence_status: Literal["UNKNOWN"]
    applicability: Literal["UNKNOWN"]
    criticality: Literal["UNKNOWN"]
    conflict_state: Literal["UNKNOWN", "CONFLICTING_CANDIDATES"]
    rule_version: Literal["1", "2", "3"]
    anchor_chain: list[CaseDceAnnouncementAnchorResponse] = Field(
        default_factory=list, max_length=64
    )


class CaseDceCoverageResponse(PublicResponseModel):
    case_scope_kind: Literal["SINGLE_LOT", "MULTI_LOT", "TRANCHE", "VARIANT", "CUSTOM"]
    documents: list[CaseDceDocumentCoverageResponse]
    exceptions: list[CaseDceCoverageExceptionResponse] = Field(default_factory=list)
    announcements: list[CaseDceAnnouncementResponse] = Field(default_factory=list)
    announcement_scan_state: Literal[
        "UNKNOWN", "REVIEW_REQUIRED", "CANDIDATES_ONLY", "REJECTED_LIMIT"
    ] = "UNKNOWN"
    total_documents: int = Field(ge=0)
    completed_extractions: int = Field(ge=0)
    unread_documents: int = Field(ge=0)
    inventory_scope: Literal["ADMITTED_DOCUMENTS_ONLY"]
    inventory_completeness: Literal["UNKNOWN"]
    lot_applicability: Literal["UNKNOWN"]
    critical_unread_documents: None
    status: Literal["REVIEW_REQUIRED"]
    analysis_complete: Literal[False]


class CaseDceReadingResponse(PublicResponseModel):
    case_id: UUID
    work_label: str
    case_lifecycle: str
    commercial_stage: str
    dce_freshness: str
    availability: Literal["AVAILABLE"]
    dce: CaseDceReadingDceResponse
    counters: CaseDceReadingCountersResponse
    requirements: list[CaseDceReadingRequirementResponse]
    coverage: CaseDceCoverageResponse | None = None


class AssignedCaseResponse(PublicResponseModel):
    """Closed Case list item returned after server-side ReBAC filtering."""

    aggregate_revision: int = Field(default=0, ge=0)
    case_id: UUID
    work_label: str
    case_lifecycle: str
    commercial_stage: str
    dce_availability: str
    consultation_id: UUID | None
    applicable_dce_version_id: UUID | None


class AcknowledgeAssignmentRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    note: str | None = Field(default=None, max_length=500)

    def to_command(self, *, assignment_id: UUID) -> AcknowledgeAssignmentCommand:
        return AcknowledgeAssignmentCommand(
            **self.model_dump(),
            assignment_id=assignment_id,
        )


class RequestAssignmentClarificationRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    clarification_kind: Literal[
        "SCOPE",
        "PRIORITY",
        "DEADLINE",
        "DOCUMENT",
        "RESPONSIBILITY",
        "OTHER",
    ]
    subject: str = Field(min_length=1, max_length=160)
    question: str = Field(min_length=1, max_length=2_000)
    requested_scope: str | None = Field(default=None, max_length=500)
    priority: Literal["LOW", "NORMAL", "HIGH"] = "NORMAL"

    def to_command(
        self,
        *,
        assignment_id: UUID,
    ) -> RequestAssignmentClarificationCommand:
        return RequestAssignmentClarificationCommand(
            **self.model_dump(),
            assignment_id=assignment_id,
        )


class ReportAssignmentUnavailabilityRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    reason_kind: Literal[
        "SICKNESS",
        "LEAVE",
        "CAPACITY_CONFLICT",
        "SKILL_GAP",
        "ACCESS_PROBLEM",
        "OTHER",
    ]
    reason: str = Field(min_length=1, max_length=2_000)
    unavailable_from: datetime
    unavailable_until: datetime | None = None
    known_deadline_impact: bool = False
    impact_note: str | None = Field(default=None, max_length=500)

    def to_command(
        self,
        *,
        assignment_id: UUID,
    ) -> ReportAssignmentUnavailabilityCommand:
        return ReportAssignmentUnavailabilityCommand(
            **self.model_dump(),
            assignment_id=assignment_id,
        )


class AssignmentCommandResponse(PublicResponseModel):
    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal[
        "ASSIGNMENT_ACKNOWLEDGED",
        "ASSIGNMENT_CLARIFICATION_REQUESTED",
        "ASSIGNMENT_UNAVAILABILITY_REPORTED",
        "CASE_ASSIGNMENT_CREATED",
        "CASE_ASSIGNMENT_SCOPE_AMENDED",
        "CASE_ASSIGNMENT_SUSPENDED",
        "CASE_ASSIGNMENT_REACTIVATED",
        "CASE_ASSIGNMENT_ENDED",
        "INTERACTION_VALIDATED",
    ]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


class PublishFinancialReportRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)

    def to_command(self, *, case_id: UUID, report_id: UUID) -> PublishFinancialReportCommand:
        return PublishFinancialReportCommand(
            **self.model_dump(),
            case_id=case_id,
            report_id=report_id,
        )


class FinancialReportPublicationResponse(PublicResponseModel):
    """Closed receipt intentionally excluding every financial value and source."""

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["FINANCIAL_REPORT_PUBLISHED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


class CreateFinancialReportDraftRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    currency_code: str = Field(default="EUR", pattern=r"^[A-Z]{3}$")
    ruleset_version: int = Field(default=1, ge=1)

    def to_command(self, *, case_id: UUID) -> CreateFinancialReportDraftCommand:
        return CreateFinancialReportDraftCommand(**self.model_dump(), case_id=case_id)


class AddFinancialReportLineRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    category: Literal[
        "SALES",
        "DIRECT_COST",
        "OVERHEAD",
        "SUBCONTRACTING",
        "CONTINGENCY",
        "GROSS_MARGIN",
        "FORECAST_CASHFLOW",
    ]
    label: str = Field(min_length=1, max_length=160)
    quantity_decimal: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^(?:0|[1-9]\d*)(?:\.\d+)?$",
    )
    unit: str = Field(min_length=1, max_length=32)
    amount_minor: int

    def to_command(self, *, case_id: UUID, report_id: UUID) -> AddFinancialReportLineCommand:
        return AddFinancialReportLineCommand(
            **self.model_dump(),
            case_id=case_id,
            report_id=report_id,
        )


class FinancialReportLineAdditionResponse(PublicResponseModel):
    """Closed receipt intentionally excluding every financial value."""

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["FINANCIAL_REPORT_LINE_ADDED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


class FinancialReportDraftCreationResponse(PublicResponseModel):
    """Closed receipt intentionally excluding every financial value and source."""

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["FINANCIAL_REPORT_DRAFT_CREATED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


class PatronAssignmentScopeRequest(PublicRequestModel):
    """Closed operational scope intentionally excluding all pricing and decision actions."""

    scope_actions: list[AssignmentScopeAction] = Field(min_length=1, max_length=8)
    scope_classifications: list[AssignmentScopeClassification] = Field(min_length=1, max_length=1)

    @model_validator(mode="after")
    def validate_and_canonicalize_scope(self) -> PatronAssignmentScopeRequest:
        if len(self.scope_actions) != len(set(self.scope_actions)):
            raise ValueError("assignment scope actions must not contain duplicates")
        if len(self.scope_classifications) != len(set(self.scope_classifications)):
            raise ValueError("assignment scope classifications must not contain duplicates")
        self.scope_actions.sort()
        self.scope_classifications.sort()
        return self


class CreatePatronCaseAssignmentRequest(PatronAssignmentScopeRequest):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    assignment_id: UUID
    target_membership_id: UUID
    expected_case_revision: int = Field(ge=0)
    starts_at: AwareDatetime
    ends_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_period(self) -> CreatePatronCaseAssignmentRequest:
        if self.ends_at is not None and self.ends_at <= self.starts_at:
            raise ValueError("assignment period must be strictly ordered")
        return self

    def to_command(self, *, case_id: UUID) -> CreateCaseAssignmentCommand:
        return CreateCaseAssignmentCommand(**self.model_dump(), case_id=case_id)


class AmendPatronAssignmentScopeRequest(PatronAssignmentScopeRequest):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)

    def to_command(self, *, assignment_id: UUID) -> AmendCaseAssignmentScopeCommand:
        return AmendCaseAssignmentScopeCommand(**self.model_dump(), assignment_id=assignment_id)


class SuspendPatronCaseAssignmentRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    suspension_reason_code: SuspensionReasonCode

    def to_command(self, *, assignment_id: UUID) -> SuspendCaseAssignmentCommand:
        return SuspendCaseAssignmentCommand(**self.model_dump(), assignment_id=assignment_id)


class ReactivatePatronCaseAssignmentRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    reactivation_reason_code: ReactivationReasonCode

    def to_command(self, *, assignment_id: UUID) -> ReactivateCaseAssignmentCommand:
        return ReactivateCaseAssignmentCommand(**self.model_dump(), assignment_id=assignment_id)


class EndPatronCaseAssignmentRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    expected_revision: int = Field(ge=0)
    end_reason_code: EndReasonCode

    def to_command(self, *, assignment_id: UUID) -> EndCaseAssignmentCommand:
        return EndCaseAssignmentCommand(**self.model_dump(), assignment_id=assignment_id)


class ValidatePatronAssignmentInteractionRequest(PublicRequestModel):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    interaction_id: UUID
    interaction_kind: AssignmentInteractionKind
    validation_code: AssignmentInteractionValidationCode

    @model_validator(mode="after")
    def validate_kind_code_pair(self) -> ValidatePatronAssignmentInteractionRequest:
        expected = {
            "ACKNOWLEDGEMENT": "ACKNOWLEDGEMENT_NOTED",
            "CLARIFICATION_REQUEST": "CLARIFICATION_NOTED",
            "UNAVAILABILITY_REPORT": "UNAVAILABILITY_NOTED",
        }[self.interaction_kind]
        if self.validation_code != expected:
            raise ValueError("interaction validation code must match interaction kind")
        return self

    def to_command(self, *, assignment_id: UUID) -> ValidateAssignmentInteractionCommand:
        return ValidateAssignmentInteractionCommand(
            **self.model_dump(),
            assignment_id=assignment_id,
        )


class RecordDceRequirementConfirmationRequest(PublicResponseModel):
    """Untrusted HTTP intent; scope and actor stay server-resolved."""

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    confirmation_id: UUID
    expected_confirmation_revision: int = Field(ge=0)
    outcome: Literal["CONFIRMED", "REVIEW_REQUIRED", "NOT_APPLICABLE"]
    reason_code: Literal[
        "SOURCE_REVIEWED",
        "AMBIGUOUS_SOURCE",
        "CONTRADICTORY_DCE",
        "PATRON_NOT_APPLICABLE",
        "NEEDS_EXTERNAL_CLARIFICATION",
    ]

    def to_command(
        self,
        *,
        requirement_id: UUID,
    ) -> RecordDceRequirementConfirmationCommand:
        return RecordDceRequirementConfirmationCommand(
            **self.model_dump(),
            requirement_id=requirement_id,
        )


class RecordDceRequirementConfirmationResponse(PublicResponseModel):
    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["DCE_REQUIREMENT_CONFIRMED"]
    aggregate_refs: list[AggregateReferenceResponse]
    event_ids: list[UUID]
    replayed: bool = False


CreateConsultationRequest = CreateConsultationCommand
RegisterDceVersionRequest = RegisterDceVersionCommand


class DceContractRiskSignalResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    observation_id: UUID
    dce_version_id: UUID
    document_family: Literal["CCAP", "CCTP"]
    requirement_kind: Literal[
        "CCAP_PENALTIES",
        "CCAP_RETENTION_GUARANTEE",
        "CCAP_GUARANTEE",
        "CCAP_INSURANCE",
        "CCTP_VARIANTS",
        "CCAP_SUBCONTRACTING",
        "CCAP_QUALIFICATIONS",
    ]
    rule_id: str
    rule_version: str
    directive: Literal["REQUIRED_SIGNAL", "OPTIONAL_SIGNAL", "UNSPECIFIED"]
    fragment_id: UUID
    source_locator_label: str
    start_byte_offset: int
    end_byte_offset: int
    verification_status: Literal["REVIEW_REQUIRED"]


class DceContractRiskSignalPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_id: UUID
    items: list[DceContractRiskSignalResponse]


# ruff: noqa: E501
class ContractBaselineImpactResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    proof_id: UUID
    case_id: UUID
    baseline_observation_id: UUID
    dce_requirement_id: UUID | None = None
    dce_requirement_revision: int | None = None
    proof_revision: int
    baseline_source_refs: list[str]
    baseline_statement: str
    deviation_statement: str | None
    impact_statement: str | None
    status: Literal[
        "SOURCE_SIGNAL_ONLY", "HUMAN_REVIEW_REQUIRED", "CONFIRMED", "UNKNOWN", "SUPERSEDED"
    ]


class ContractBaselineImpactPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    items: list[ContractBaselineImpactResponse]


class RecordContractBaselineImpactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    proof_id: UUID
    dce_requirement_id: UUID
    dce_requirement_revision: int = Field(ge=1)
    baseline_source_refs: list[str] = Field(min_length=1, max_length=100)
    baseline_statement: str = Field(min_length=1, max_length=4_000)
    deviation_statement: str | None = Field(default=None, max_length=4_000)
    impact_statement: str = Field(min_length=1, max_length=4_000)


class RecordContractBaselineImpactResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    command_id: UUID
    idempotency_key: UUID
    proof_id: UUID
    proof_revision: int
    result_code: str
    status: Literal["HUMAN_REVIEW_REQUIRED"]
    replayed: bool


class ContractProofReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: UUID
    proof_id: UUID
    reviewer_id: UUID
    reviewed_revision: int
    decision: Literal["ACCEPTED", "REJECTED", "NEEDS_CLARIFICATION"]
    rationale: str


class ContractProofReviewPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    items: list[ContractProofReviewResponse]


class ContractProofTimelineEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: Literal["REVIEW"]
    event_id: UUID
    proof_id: UUID
    revision: int
    status: str
    rationale: str
    created_at: datetime


class ContractProofTimelineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    items: list[ContractProofTimelineEventResponse]


class ContractQueryReceiptResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    receipt_id: UUID
    case_id: UUID
    filters: dict[str, object]
    order_key: str
    limit_value: int
    offset_value: int
    actor_id: UUID
    created_at: datetime


class ContractQueryReceiptPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    items: list[ContractQueryReceiptResponse]


class ContractQueryExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    export_id: UUID
    case_id: UUID
    filters: dict[str, object]
    status: Literal["REQUESTED", "READY", "UNKNOWN", "REFUSED"]
    actor_id: UUID
    created_at: datetime


class ContractQueryExportPageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    items: list[ContractQueryExportResponse]


class ContractQueryExportTransitionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transition_id: UUID
    from_status: str
    to_status: str
    local_proof_ref: str | None
    created_at: datetime


class ContractQueryExportAuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    export: ContractQueryExportResponse
    transitions: list[ContractQueryExportTransitionResponse]


class ExportVerificationOwnerActResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    act_id: UUID
    export_id: UUID
    owner_id: UUID
    approved: bool
    rationale: str
    created_at: datetime


class ExportVerificationTimelineEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: Literal["VERIFICATION", "TRANSITION", "OWNER_ACT"]
    event_id: UUID
    status: str
    created_at: datetime


class ExportVerificationTimelineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    export_id: UUID
    items: list[ExportVerificationTimelineEventResponse]


class ExportOperationalHandoffResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    export_id: UUID
    current_status: str
    filters: dict[str, object]
    transition_count: int
    last_transition_at: datetime | None
    read_only: bool = True


class HumanResumptionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    act_id: UUID
    export_id: UUID
    actor_id: UUID
    state: Literal["ACKNOWLEDGED", "FOLLOW_UP_REQUIRED", "BLOCKED"]
    rationale: str
    created_at: datetime


class HumanResumptionTimelineEventResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_type: Literal["TRANSITION", "HUMAN_RESUMPTION"]
    event_id: UUID
    status: str
    created_at: datetime


class HumanResumptionTimelineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    export_id: UUID
    items: list[HumanResumptionTimelineEventResponse]


class UnknownAuditProvenanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provenance_id: UUID
    export_id: UUID
    source_type: Literal["TRANSITION", "HUMAN_RESUMPTION", "VERIFICATION"]
    source_event_id: UUID
    actor_id: UUID
    status: str
    occurred_at: datetime
    rationale: str | None


class PaymentCycleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cycle_id: UUID
    case_id: UUID
    source_refs: list[str]
    trigger_event: str
    status: Literal["SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"]
    cash_assumption: str | None
    post_reception_cost_note: str | None
