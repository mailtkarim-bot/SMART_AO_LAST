"""Closed patron-only analysis dossier response; no mutation contract."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.case.application.analysis_dossier import AnalysisTreatment, DossierAxisReview
from app.modules.dce.public.contracts import CaseDceCoverageResponse, CaseDceSourceAnchorResponse
from app.modules.pricing.public.contracts import PricingScenarioResponse


class CaseAnalysisFollowUpResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["ACTION", "CONTRACT_IMPACT", "CONDITION"]
    record_id: UUID
    revision: int = Field(ge=1)
    state: str
    relation_id: UUID | None = None
    risk_requirement_link_id: UUID | None = None
    contract_impact_id: UUID | None = None
    contract_impact_revision: int | None = Field(default=None, ge=1)
    decision_id: UUID | None = None
    context_id: UUID | None = None
    risk_id: UUID | None = None
    requirement_id: UUID | None = None
    description: str
    consequence: str | None = None
    responsible_actor_id: UUID | None = None
    due_at: datetime | None = None
    scope: Literal["EXACT_RECORDED_RELATION"] = "EXACT_RECORDED_RELATION"


class AnalysisAssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assessment_id: UUID
    revision: int = Field(ge=1)
    previous_assessment_id: UUID | None
    state: Literal["CURRENT", "REVIEW_REQUIRED"]
    source_context_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    actor_id: UUID | None
    created_at: datetime
    expected_evidence_state: Literal["DECLARED", "UNKNOWN"]
    expected_evidence: str | None
    residual_risk_state: Literal["DECLARED", "UNKNOWN"]
    residual_risk: str | None
    unknown_reason: str | None
    justification: str | None
    treatment: AnalysisTreatment | None = None

    @model_validator(mode="after")
    def declaration_consistency(self):
        if self.state == "REVIEW_REQUIRED":
            if any(
                v is not None
                for v in (
                    self.expected_evidence,
                    self.residual_risk,
                    self.justification,
                    self.unknown_reason,
                    self.actor_id,
                    self.treatment,
                )
            ):
                raise ValueError("STALE_ASSESSMENT_DETAILS")
        else:
            for state, value in [
                (self.expected_evidence_state, self.expected_evidence),
                (self.residual_risk_state, self.residual_risk),
            ]:
                if (state == "DECLARED") != bool(value and value.strip()):
                    raise ValueError("ASSESSMENT_DECLARATION_MISMATCH")
            if (
                self.actor_id is None
                or not self.justification
                or (
                    "UNKNOWN" in (self.expected_evidence_state, self.residual_risk_state)
                    and not self.unknown_reason
                )
            ):
                raise ValueError("HUMAN_ASSESSMENT_INCOMPLETE")
        return self


class AnalysisTableCellResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=8000)
    source_anchor: CaseDceSourceAnchorResponse


class AnalysisTableContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    state: Literal["EXACT_SOURCE", "UNKNOWN"]
    applicability: Literal["UNKNOWN"]
    unknown_reason: Literal["SOURCE_UNPROVEN", "READ_BUDGET_EXCEEDED"] | None
    cells: list[AnalysisTableCellResponse] = Field(max_length=64)

    @model_validator(mode="after")
    def evidence_consistency(self):
        if (self.state == "EXACT_SOURCE") != bool(self.cells):
            raise ValueError("TABLE_CONTEXT_STATE_MISMATCH")
        if (self.state == "UNKNOWN") != (self.unknown_reason is not None):
            raise ValueError("TABLE_CONTEXT_REASON_MISMATCH")
        if sum(len(c.text.encode()) for c in self.cells) > 16000:
            raise ValueError("TABLE_CONTEXT_BUDGET_EXCEEDED")
        return self


class CaseAnalysisItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    item_id: UUID
    native_revision: int = Field(default=0, ge=0)
    source_context_sha256: str | None = None
    human_assessment: AnalysisAssessmentResponse | None = None
    kind: Literal["REQUIREMENT", "RISK"]
    native_type: str = Field(max_length=64)
    native_state: str = Field(max_length=64)
    title: str | None = Field(default=None, max_length=240)
    source_excerpt: str | None = Field(default=None, min_length=1, max_length=8000)
    source_excerpt_state: Literal["EXACT_SOURCE", "UNKNOWN"] = "UNKNOWN"
    source_excerpt_unknown_reason: Literal["SOURCE_UNPROVEN", "READ_BUDGET_EXCEEDED"] | None = None
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"] = "UNKNOWN"
    expected_evidence: Literal["UNKNOWN"] = "UNKNOWN"
    residual_risk: Literal["UNKNOWN"] = "UNKNOWN"
    source_state: Literal["CURRENT_SOURCE", "UNKNOWN"]
    source_anchor: CaseDceSourceAnchorResponse | None = None
    table_context: AnalysisTableContextResponse | None = None
    start_byte_offset: int | None = Field(default=None, ge=0)
    end_byte_offset: int | None = Field(default=None, gt=0)
    lot_numbers: list[Annotated[int, Field(ge=1, le=999)]] = Field(
        default_factory=list, max_length=64
    )
    lot_state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    follow_ups: list[CaseAnalysisFollowUpResponse] = Field(default_factory=list, max_length=300)
    follow_up_state: Literal["RECORDED", "UNKNOWN"] = "UNKNOWN"
    responsible: None = None
    action: None = None
    consequences: Literal["UNKNOWN"] = "UNKNOWN"

    @model_validator(mode="after")
    def source_consistency(self):
        if self.table_context is not None:
            source = self.source_anchor
            if (
                self.source_state != "CURRENT_SOURCE"
                or source is None
                or source.locator is None
                or source.locator.kind != "docx_table_cell"
            ):
                raise ValueError("UNPROVEN_TABLE_CONTEXT")
            for cell in self.table_context.cells:
                anchor = cell.source_anchor
                if (
                    anchor.locator_state != "RESOLVED"
                    or anchor.locator is None
                    or anchor.locator.kind != "docx_table_cell"
                    or anchor.locator.coordinates.get("table")
                    != source.locator.coordinates.get("table")
                    or (
                        anchor.dce_version_id,
                        anchor.dce_document_id,
                        anchor.extraction_id,
                        anchor.source_sha256,
                    )
                    != (
                        source.dce_version_id,
                        source.dce_document_id,
                        source.extraction_id,
                        source.source_sha256,
                    )
                ):
                    raise ValueError("TABLE_CONTEXT_SOURCE_MISMATCH")
        if (
            self.human_assessment
            and self.human_assessment.state == "CURRENT"
            and (
                self.source_state != "CURRENT_SOURCE"
                or not self.source_context_sha256
                or self.human_assessment.source_context_sha256 != self.source_context_sha256
            )
        ):
            raise ValueError("HUMAN_ASSESSMENT_SOURCE_MISMATCH")
        if (self.source_excerpt is not None) != (self.source_excerpt_state == "EXACT_SOURCE"):
            raise ValueError("EXCERPT_STATE_MISMATCH")
        if self.source_state != "CURRENT_SOURCE" and (
            self.source_excerpt is not None or self.severity != "UNKNOWN"
        ):
            raise ValueError("UNPROVEN_ANATOMY")
        if self.source_excerpt is not None and (
            self.source_excerpt_unknown_reason is not None
            or self.start_byte_offset is None
            or self.end_byte_offset is None
            or len(self.source_excerpt.encode("utf-8"))
            != self.end_byte_offset - self.start_byte_offset
        ):
            raise ValueError("EXCERPT_REGION_MISMATCH")
        if bool(self.follow_ups) != (self.follow_up_state == "RECORDED"):
            raise ValueError("FOLLOW_UP_STATE_MISMATCH")
        if self.follow_ups and self.source_state != "CURRENT_SOURCE":
            raise ValueError("UNPROVEN_FOLLOW_UP_SOURCE")
        if (self.source_state == "CURRENT_SOURCE") != (self.source_anchor is not None):
            raise ValueError("SOURCE_STATE_MISMATCH")
        if self.source_state == "CURRENT_SOURCE" and (
            self.start_byte_offset is None
            or self.end_byte_offset is None
            or self.end_byte_offset <= self.start_byte_offset
        ):
            raise ValueError("SOURCE_REGION_REQUIRED")
        if self.source_state == "UNKNOWN" and (
            self.start_byte_offset is not None or self.end_byte_offset is not None
        ):
            raise ValueError("UNPROVEN_SOURCE_REGION")
        if self.source_state == "UNKNOWN" and (self.title is not None or self.lot_numbers):
            raise ValueError("UNPROVEN_SOURCE_DETAILS")
        if (self.lot_state == "CANDIDATE") != bool(self.lot_numbers):
            raise ValueError("LOT_STATE_MISMATCH")
        return self


class CaseAnalysisPricingResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario_id: UUID
    revision: int = Field(ge=1)
    state: Literal["RECORDED", "UNKNOWN"]
    unknown_reason: str | None
    dce_applicability: Literal["UNKNOWN"]
    details: "PricingScenarioResponse | None"

    @model_validator(mode="after")
    def qualified_details(self):
        if self.state == "UNKNOWN":
            if self.details is not None or not self.unknown_reason:
                raise ValueError("UNPROVEN_PRICING_DETAILS")
        elif (
            self.details is None
            or self.unknown_reason is not None
            or self.details.scenario_id != self.scenario_id
            or self.details.version != self.revision
            or self.details.state == "ARCHIVED"
            or self.details.source_basis_state != "DECLARED_COMPLETE"
            or self.details.source_snapshot_id is None
        ):
            raise ValueError("PRICING_PROVENANCE_REQUIRED")
        return self


class CaseAnalysisCashLineResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_id: UUID
    label: str
    amount_minor: int


class CaseAnalysisCashDetailsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    currency_code: str = Field(pattern=r"^[A-Z]{3}$")
    calculated_at: datetime
    ruleset_version: int = Field(ge=1)
    forecast_cashflow_minor: int
    lines: list[CaseAnalysisCashLineResponse] = Field(min_length=1)


class CaseAnalysisCashResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    report_id: UUID
    revision: int = Field(ge=0)
    state: Literal["DECLARED", "UNKNOWN"]
    unknown_reason: str | None
    schedule_state: Literal["UNKNOWN"]
    funding_peak_state: Literal["UNKNOWN"]
    scope_state: Literal["UNKNOWN"]
    details: CaseAnalysisCashDetailsResponse | None

    @model_validator(mode="after")
    def declaration_consistency(self):
        if self.state == "UNKNOWN":
            if self.details is not None or not self.unknown_reason:
                raise ValueError("UNPROVEN_CASH_DETAILS")
        elif (
            self.details is None
            or self.unknown_reason is not None
            or sum(line.amount_minor for line in self.details.lines)
            != self.details.forecast_cashflow_minor
        ):
            raise ValueError("CASH_DECLARATION_MISMATCH")
        return self


class CaseAnalysisCapacityDetailsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    status: str
    inputs: dict[str, object]
    result: dict[str, object]
    reservation_state: Literal["NOT_RESERVED"]
    coverage_state: Literal["UNKNOWN"]


class CaseAnalysisCapacityResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    run_id: UUID
    revision: int = Field(ge=1)
    input_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    state: Literal["RECORDED", "REVIEW_REQUIRED"]
    unknown_reason: str | None
    lot_state: Literal["UNKNOWN"]
    dce_applicability: Literal["UNKNOWN"]
    details: CaseAnalysisCapacityDetailsResponse | None


class CaseAnalysisAxisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Literal[
        "COMMERCIAL",
        "CANDIDATURE",
        "TECHNICAL",
        "CONSTRUCTIBILITY",
        "CONTRACT",
        "PRICE",
        "CASH",
        "CAPACITY",
        "PARTNERS",
        "HSE",
        "DOCUMENTS",
        "RIGHTS",
    ]
    label: str
    status: Literal["NON_EVALUATED", "REVIEW_REQUIRED"]
    mapping_basis: Literal["NATIVE_REGISTER_TYPE_ONLY"]
    items: list[CaseAnalysisItemResponse] = Field(max_length=300)
    cash_reports: list[CaseAnalysisCashResponse] = Field(default_factory=list, max_length=20)
    capacity_plans: list[CaseAnalysisCapacityResponse] = Field(default_factory=list, max_length=20)
    pricing_scenarios: list[CaseAnalysisPricingResponse] = Field(
        default_factory=list, max_length=100
    )


class AnalysisDossierReviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: UUID
    revision: int = Field(ge=1)
    phase: Literal["PREPARED", "REVIEWED"]
    state: Literal["CURRENT", "REVIEW_REQUIRED"]
    dossier_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    actor_id: UUID | None
    created_at: datetime
    axes: list[DossierAxisReview] = Field(max_length=12)
    justification: str | None

    @model_validator(mode="after")
    def stale_private_details(self):
        if self.state == "REVIEW_REQUIRED" and (
            self.axes or self.justification is not None or self.actor_id is not None
        ):
            raise ValueError("STALE_DOSSIER_DETAILS")
        if self.state == "CURRENT" and (
            len({a.code for a in self.axes}) != 12
            or self.actor_id is None
            or not self.justification
        ):
            raise ValueError("INCOMPLETE_DOSSIER_REVIEW")
        return self


class CaseAnalysisSummaryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    dce_version_id: UUID
    case_scope_kind: Literal["SINGLE_LOT", "MULTI_LOT", "TRANCHE", "VARIANT", "CUSTOM"]
    status: Literal["REVIEW_REQUIRED"]
    analysis_complete: Literal[False]
    coverage_scope: Literal["CURRENT_DCE_ONLY"]
    truncated: bool
    source_context_state: Literal["CURRENT", "REVIEW_REQUIRED", "UNKNOWN"]
    axes: list[CaseAnalysisAxisResponse] = Field(min_length=12, max_length=12)
    case_scope_fingerprint: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    dossier_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    dossier_review: AnalysisDossierReviewResponse | None = None
    coverage: CaseDceCoverageResponse | None

    @model_validator(mode="after")
    def pricing_scope(self):
        for axis in self.axes:
            for plan in axis.capacity_plans:
                if axis.code != "CAPACITY" or (
                    plan.details is not None
                    and (
                        plan.details.case_id != self.case_id
                        or self.source_context_state != "CURRENT"
                    )
                ):
                    raise ValueError("CAPACITY_CONTEXT_MISMATCH")
            for report in axis.cash_reports:
                if axis.code != "CASH" or (
                    report.details is not None
                    and (
                        report.details.case_id != self.case_id
                        or self.source_context_state != "CURRENT"
                    )
                ):
                    raise ValueError("CASH_CONTEXT_MISMATCH")
            for item in axis.pricing_scenarios:
                if axis.code not in {"PRICE", "CASH"} or (
                    item.details is not None
                    and (
                        item.details.case_id != self.case_id
                        or self.source_context_state != "CURRENT"
                    )
                ):
                    raise ValueError("PRICING_CONTEXT_MISMATCH")
        return self

    @model_validator(mode="after")
    def context_consistency(self):
        if (
            self.dossier_review
            and self.dossier_review.state == "CURRENT"
            and self.dossier_review.dossier_sha256 != self.dossier_sha256
        ):
            raise ValueError("DOSSIER_CONTEXT_MISMATCH")
        if len({a.code for a in self.axes}) != 12:
            raise ValueError("AXIS_IDENTITY_MISMATCH")
        if self.source_context_state != "CURRENT" and any(
            i.source_state == "CURRENT_SOURCE" for a in self.axes for i in a.items
        ):
            raise ValueError("SOURCE_CONTEXT_MISMATCH")
        return self


class AnalysisDossierHistoricalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    review_id: UUID
    revision: int = Field(ge=1)
    phase: Literal["PREPARED", "REVIEWED"]
    state: Literal["HISTORICAL"]
    dossier_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    dce_version_id: UUID
    actor_id: UUID
    created_at: datetime
    axes: list[DossierAxisReview] = Field(min_length=12, max_length=12)
    justification: str
    snapshot: dict


class AnalysisDossierHistoryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    case_id: UUID
    entries: list[AnalysisDossierHistoricalEntry] = Field(max_length=20)
    next_before_revision: int | None = Field(default=None, ge=1)
