from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.membership.public.text_safety import contains_forbidden_text


class PreparationCommandRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


class EvaluatePreparationReadinessRequest(PreparationCommandRequest):
    expected_revision: int = Field(ge=0)
    package_id: UUID
    assignment_id: UUID
    dce_version_id: UUID


class GenerateTechnicalDocumentRequest(PreparationCommandRequest):
    expected_revision: int = Field(ge=0)
    readiness_revision: int = Field(ge=1)
    document_kind: Literal["TECHNICAL_RESPONSE", "DC1", "DC2", "DC4"]


class RequestPreparationReviewRequest(PreparationCommandRequest):
    expected_package_revision: int = Field(ge=0)
    review_id: UUID
    target_document_id: UUID | None = None
    target_version: int | None = Field(default=None, gt=0)
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")

    @model_validator(mode="after")
    def exact_target(self):
        if self.target_draft_id is not None:
            if self.target_draft_version is None or self.target_content_sha256 is None:
                raise ValueError("REVIEW_TARGET_INCOMPLETE")
        elif self.target_document_id is None or self.target_version is None:
            raise ValueError("REVIEW_TARGET_INCOMPLETE")
        return self


class DecidePreparationReviewRequest(PreparationCommandRequest):
    expected_review_revision: int = Field(ge=1)
    review_id: UUID
    target_document_id: UUID | None = None
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    decision_code: Literal["ACCEPTED", "CORRECTIONS_REQUIRED", "REJECTED"]
    decision_note: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def exact_target(self):
        if self.target_draft_id is not None:
            if self.target_draft_version is None or self.target_content_sha256 is None:
                raise ValueError("REVIEW_TARGET_INCOMPLETE")
        elif self.target_document_id is None:
            raise ValueError("REVIEW_TARGET_INCOMPLETE")
        return self


class AddPreparationCorrectionRequest(PreparationCommandRequest):
    review_id: UUID
    target_document_id: UUID | None = None
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    correction_code: Literal[
        "SOURCE_MISSING", "SOURCE_WRONG", "SECTION_INCOMPLETE", "WORDING_UNCLEAR"
    ]
    instruction: str = Field(min_length=1, max_length=2000)
    source_locator: str | None = Field(default=None, max_length=500)
    corrected_content: str | None = Field(default=None, min_length=1, max_length=100_000)

    @model_validator(mode="after")
    def exact_target(self):
        if self.target_draft_id is not None:
            if self.target_draft_version is None or self.target_content_sha256 is None:
                raise ValueError("REVIEW_TARGET_INCOMPLETE")
        elif self.target_document_id is None:
            raise ValueError("REVIEW_TARGET_INCOMPLETE")
        return self


class SelectedResponseDraft(BaseModel):
    """One explicitly chosen immutable assembled response, never a review approval."""

    model_config = ConfigDict(extra="forbid")
    draft_id: UUID
    version: int = Field(ge=1)
    content_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class ResponseCoveragePiece(BaseModel):
    section_code: str
    locator: str
    sha256: str
    start_byte: int | None = None
    end_byte: int | None = None
    text_present: bool
    missing: str


class ResponseCoverageRequirement(BaseModel):
    requirement_id: UUID
    document_family: str
    source_state: str
    confirmation: str
    source_locator: str
    source_anchor: dict | None = None
    source_excerpt: str | None = None
    lot_candidates: list[int]
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    coverage: Literal["UNKNOWN"] = "UNKNOWN"
    signature: Literal["UNKNOWN"] = "UNKNOWN"
    response_state: Literal["TEXT_PRESENT", "TEXT_WITH_GAPS", "MISSING", "UNKNOWN"]
    pieces: list[ResponseCoveragePiece]


class ResponseCitedAnnex(BaseModel):
    requirement_id: UUID
    section_code: str
    document_id: UUID
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    inclusion: Literal["UNKNOWN"] = "UNKNOWN"


class ResponseCoverageProjection(BaseModel):
    content_byte_size: int | None = Field(default=None, ge=0)
    package_id: UUID
    dce_version_id: UUID
    selected_response: SelectedResponseDraft
    content_format: Literal["MARKDOWN", "DOCX"]
    requirements: list[ResponseCoverageRequirement]
    cited_annexes: list[ResponseCitedAnnex] = Field(default_factory=list)
    coverage: Literal["UNKNOWN"] = "UNKNOWN"
    signature: Literal["UNKNOWN"] = "UNKNOWN"
    annexes: Literal["UNKNOWN"] = "UNKNOWN"
    inventory: Literal["CURRENT_NON_FINANCIAL_SIGNALS_ONLY"] = "CURRENT_NON_FINANCIAL_SIGNALS_ONLY"


class SelectedResponseAnnex(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requirement_id: UUID
    document_id: UUID
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def validate_annex_selection(response, annexes, justification=None):
    if justification and (
        contains_forbidden_text(justification) or "devis" in justification.casefold()
    ):
        raise ValueError("FINANCIAL_DATA_FORBIDDEN")
    if annexes and not (justification and justification.strip()):
        raise ValueError("ANNEX_JUSTIFICATION_REQUIRED")
    if annexes and response is None:
        raise ValueError("ANNEX_RESPONSE_SELECTION_REQUIRED")
    identities = [(item.requirement_id, item.document_id) for item in annexes]
    if len(identities) != len(set(identities)):
        raise ValueError("ANNEX_SELECTION_DUPLICATE")


class CreatePreparationSnapshotRequest(PreparationCommandRequest):
    selected_response_draft: SelectedResponseDraft | None = None
    selected_annexes: list[SelectedResponseAnnex] = Field(default_factory=list, max_length=64)
    annex_justification: str | None = Field(default=None, min_length=1, max_length=2000)
    expected_package_revision: int = Field(ge=0)
    package_id: UUID
    snapshot_id: UUID

    @model_validator(mode="after")
    def exact_annex_selection(self):
        validate_annex_selection(
            self.selected_response_draft, self.selected_annexes, self.annex_justification
        )
        return self


class TransmitPreparationSnapshotRequest(PreparationCommandRequest):
    expected_package_revision: int = Field(ge=0)
    package_id: UUID
    snapshot_id: UUID
    transmission_id: UUID


class ResponseContribution(BaseModel):
    """Human wording for one exact response-plan item, never a coverage approval."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    requirement_id: UUID
    section_code: Literal[
        "COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"
    ]
    content: str = Field(default="", max_length=12000)
    missing: str = Field(default="", max_length=2000)

    @field_validator("content", "missing")
    @classmethod
    def non_financial(cls, value):
        if contains_forbidden_text(value) or "devis" in value.casefold():
            raise ValueError("FINANCIAL_DATA_FORBIDDEN")
        return value

    @model_validator(mode="after")
    def explicit_content_or_missing(self):
        if not self.content and not self.missing:
            raise ValueError("CONTRIBUTION_CONTENT_OR_MISSING_REQUIRED")
        return self


class CreateTechnicalResponseDraftRequest(PreparationCommandRequest):
    expected_package_revision: int = Field(ge=0)
    draft_id: UUID
    source_document_id: UUID
    section_codes: list[str] = Field(min_length=1, max_length=32)
    source_refs: list[UUID] = Field(min_length=1, max_length=64)

    contributions: list[ResponseContribution] | None = Field(
        default=None, min_length=1, max_length=64
    )


class PreparationResponsePlanItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    section_code: Literal[
        "COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"
    ]
    source_proposal_id: UUID | None = None


class CreatePreparationResponsePlanRequest(PreparationCommandRequest):
    expected_package_revision: int = Field(ge=0)
    plan_id: UUID
    items: list[PreparationResponsePlanItemRequest] = Field(min_length=1, max_length=64)

    @field_validator("items")
    @classmethod
    def unique_requirement_sections(
        cls, items: list[PreparationResponsePlanItemRequest]
    ) -> list[PreparationResponsePlanItemRequest]:
        identities = [(item.requirement_id, item.section_code) for item in items]
        if len(identities) != len(set(identities)):
            raise ValueError("RESPONSE_PLAN_ITEM_DUPLICATE")
        return items


class PreparationAggregateReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aggregate_type: Literal[
        "PreparationPackage",
        "GeneratedTechnicalDocument",
        "PreparationReview",
        "TechnicalResponseDraft",
        "PreparationResponsePlan",
        "PreparationSnapshot",
        "PreparationTransmission",
    ]
    aggregate_id: UUID
    aggregate_revision: int = Field(ge=0)


class PreparationCommandResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"] = "SUCCEEDED"
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal[
        "PREPARATION_READINESS_EVALUATED",
        "TECHNICAL_DOCUMENT_GENERATED",
        "CONTROLLED_DRAFT_GENERATED",
        "PREPARATION_REVIEW_REQUESTED",
        "PREPARATION_REVIEW_DECIDED",
        "PREPARATION_CORRECTION_ADDED",
        "TECHNICAL_RESPONSE_DRAFT_CREATED",
        "BUYER_DOCX_RESPONSE_DRAFT_CREATED",
        "PREPARATION_RESPONSE_PLAN_CREATED",
        "PREPARATION_SNAPSHOT_CREATED",
        "PREPARATION_TRANSMITTED_TO_PATRON",
    ]
    aggregate_refs: list[PreparationAggregateReference]
    event_ids: list[UUID]
    replayed: bool = False


class PreparationStoredCommandReceipt(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["SUCCEEDED"]
    command_id: UUID
    idempotency_key: UUID
    result_code: Literal["PREPARATION_SNAPSHOT_CREATED", "PREPARATION_TRANSMITTED_TO_PATRON"]
    aggregate_refs: list[PreparationAggregateReference]
    event_ids: list[UUID]


class PreparationTransmissionDeliveryProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    snapshot_id: UUID
    snapshot_version: int = Field(ge=1)
    snapshot_state: Literal["READY_FOR_PATRON_REVIEW"]
    snapshot_created_at: datetime
    snapshot_manifest_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    snapshot_manifest: dict[str, object]
    snapshot_receipt: PreparationStoredCommandReceipt
    transmission_id: UUID
    transmission_state: Literal["TRANSMITTED_TO_PATRON"]
    transmitted_at: datetime
    transmission_receipt: PreparationStoredCommandReceipt


class PreparationTransmissionListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    deliveries: list[PreparationTransmissionDeliveryProjection]


class PreparationReviewCorrectionProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    correction_id: UUID
    review_revision: int = Field(ge=1)
    revision: int = Field(ge=1)
    target_document_id: UUID
    target_draft_id: UUID | None = None
    target_draft_version: int | None = None
    target_content_sha256: str | None = None
    correction_code: Literal[
        "SOURCE_MISSING", "SOURCE_WRONG", "SECTION_INCOMPLETE", "WORDING_UNCLEAR"
    ]
    instruction: str
    source_locator: str | None


class PreparationReviewProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    review_id: UUID
    package_id: UUID
    target_document_id: UUID
    target_version: int = Field(gt=0)
    target_draft_id: UUID | None = None
    target_draft_version: int | None = None
    target_content_sha256: str | None = None
    revision: int = Field(ge=1)
    state: Literal["REQUESTED", "ACCEPTED", "RETURNED_WITH_CORRECTIONS", "REJECTED"]
    decision_code: Literal["ACCEPTED", "CORRECTIONS_REQUIRED", "REJECTED"] | None
    decision_note: str | None
    corrections: list[PreparationReviewCorrectionProjection]


class PreparationReviewListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    reviews: list[PreparationReviewProjection]


class PreparationResponseDraftListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    package_revision: int = Field(ge=0)
    drafts: list[TechnicalResponseDraftProjection]


class PreparationResponsePlanItemProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    requirement_state: Literal["CONFIRMED", "REVIEW_REQUIRED", "NOT_APPLICABLE", "UNKNOWN"]
    section_code: Literal[
        "COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"
    ]
    source_proposal_id: UUID | None
    source_capability_version_id: UUID | None
    source_validity_state: Literal["CURRENT", "EXPIRED", "UNKNOWN"]
    source_evidence_state: Literal["CURRENT", "EXPIRED", "UNKNOWN"]


class PreparationResponsePlanContentProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1]
    case_id: UUID
    package_id: UUID
    dce_version_id: UUID
    items: list[PreparationResponsePlanItemProjection]


class PreparationResponsePlanProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: UUID
    version: int = Field(ge=1)
    package_id: UUID
    dce_version_id: UUID
    state: Literal["UNKNOWN", "SOURCES_CURRENT"]
    plan_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    content: PreparationResponsePlanContentProjection


class PreparationResponsePlanListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    plans: list[PreparationResponsePlanProjection]


class PreparationReadinessProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    readiness_id: UUID
    revision: int = Field(ge=1)
    state: Literal["READY", "READY_WITH_WARNINGS", "BLOCKED"]
    blocker_codes: list[str]
    warning_codes: list[str]
    checked_requirement_count: int = Field(ge=0)
    checked_task_count: int = Field(ge=0)


class GeneratedDocumentProjection(BaseModel):
    content_format: Literal["MARKDOWN", "DOCX"] = "MARKDOWN"
    model_config = ConfigDict(extra="forbid")

    document_id: UUID
    version: int = Field(ge=1)
    document_kind: Literal["TECHNICAL_RESPONSE", "DC1", "DC2", "DC4"]
    state: Literal["GENERATED", "FAILED_SAFE"]
    readiness_revision: int = Field(ge=1)


class TechnicalResponseDraftProjection(BaseModel):
    content_format: Literal["MARKDOWN", "DOCX"] = "MARKDOWN"
    content_provenance: dict | None = None
    model_config = ConfigDict(extra="forbid")

    draft_id: UUID
    version: int = Field(ge=1)
    state: Literal[
        "DRAFT", "SUBMITTED_FOR_REVIEW", "RETURNED_WITH_CORRECTIONS", "ACCEPTED_CANDIDATE"
    ]
    section_codes: list[str]
    source_refs: list[str]
    responsible_role: Literal["COLLABORATEUR", "PATRON_REVIEWER"]
    content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    response_plan_id: UUID | None = None
    response_plan_version: int | None = None
    content: str | None = None


class PreparationPackageProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    package_id: UUID
    case_id: UUID
    assignment_id: UUID
    dce_version_id: UUID
    state: Literal["IN_PREPARATION", "A_REVIEW", "READY", "BLOCKED", "GENERATED"]
    aggregate_revision: int = Field(ge=0)
    latest_readiness: PreparationReadinessProjection | None
    generated_documents: list[GeneratedDocumentProjection]
    response_drafts: list[TechnicalResponseDraftProjection]


class BuyerDocxTemplateReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: UUID
    dce_version_id: UUID
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class BuyerDocxFieldMapping(BaseModel):
    model_config = ConfigDict(extra="forbid")
    locator: str = Field(min_length=1, max_length=160)
    expected_xml_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    requirement_id: UUID
    section_code: Literal[
        "COVER", "UNDERSTANDING", "METHOD", "RESOURCES", "SCHEDULE", "RISKS", "SOURCES"
    ]


class CreateBuyerDocxResponseDraftRequest(PreparationCommandRequest):
    expected_package_revision: int = Field(ge=0)
    draft_id: UUID
    source_response: SelectedResponseDraft
    template: BuyerDocxTemplateReference
    fields: list[BuyerDocxFieldMapping] = Field(min_length=1, max_length=64)

    @model_validator(mode="after")
    def distinct_output_and_regions(self):
        if self.draft_id == self.source_response.draft_id:
            raise ValueError("BUYER_DOCX_DISTINCT_DRAFT_REQUIRED")
        if len({f.locator for f in self.fields}) != len(self.fields):
            raise ValueError("BUYER_DOCX_DUPLICATE_REGION")
        return self


class BuyerDocxInputsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    source_response: SelectedResponseDraft
