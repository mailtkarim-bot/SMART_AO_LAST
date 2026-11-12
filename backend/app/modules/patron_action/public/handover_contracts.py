from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.membership.public.text_safety import contains_forbidden_text


class HandoverOperationalPoint(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    point_id: UUID
    kind: Literal[
        "ENGAGEMENT",
        "EXCLUSION",
        "CONDITION",
        "INTERFACE",
        "PARTNER",
        "PLANNING",
        "GUARANTEE",
        "PENALTY",
        "PAYMENT",
        "HSE",
        "POST_AWARD_DOCUMENT",
        "RESIDUAL_RISK",
        "RIGHT_PRESERVATION",
    ]
    statement: str = Field(min_length=1, max_length=2000)
    offer_excerpt: str | None = Field(default=None, min_length=1, max_length=4000)
    offer_locator: str | None = Field(default=None, min_length=1, max_length=500)
    contract_locator: str | None = Field(default=None, min_length=1, max_length=500)
    difference_state: Literal["DECLARED_EQUIVALENT", "DECLARED_DIFFERENCE", "UNKNOWN"] = "UNKNOWN"
    difference_note: str | None = Field(default=None, min_length=1, max_length=2000)
    responsible: str | None = Field(default=None, min_length=1, max_length=300)
    action: str | None = Field(default=None, min_length=1, max_length=2000)
    expected_evidence: str | None = Field(default=None, min_length=1, max_length=2000)
    due_date: date | None = None
    criticality: Literal["CRITICAL", "IMPORTANT", "UNKNOWN"] = "UNKNOWN"
    condition_id: UUID | None = None

    @field_validator(
        "statement",
        "offer_excerpt",
        "offer_locator",
        "contract_locator",
        "difference_note",
        "responsible",
        "action",
        "expected_evidence",
    )
    @classmethod
    def operational_only(cls, value):
        if value is not None and contains_forbidden_text(value):
            raise ValueError("FINANCIAL_DATA_FORBIDDEN")
        return value

    @model_validator(mode="after")
    def explicit_difference(self):
        if self.difference_state != "UNKNOWN" and (
            not self.offer_locator or not self.contract_locator
        ):
            raise ValueError("COMPARISON_SOURCES_REQUIRED")
        if self.difference_state == "DECLARED_DIFFERENCE" and not self.difference_note:
            raise ValueError("DIFFERENCE_NOTE_REQUIRED")
        return self


class HandoverOperationalReview(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    expected_source_context_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_handover_revision: int = Field(ge=0)
    expected_offer_manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    contract_instrument_version_id: UUID | None = None
    expected_contract_record_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]
    points: list[HandoverOperationalPoint] = Field(min_length=1, max_length=64)

    @field_validator("justification")
    @classmethod
    def non_private_justification(cls, value):
        if contains_forbidden_text(value):
            raise ValueError("FINANCIAL_DATA_FORBIDDEN")
        return value

    @model_validator(mode="after")
    def exact_sources_and_unique_points(self):
        if (self.contract_instrument_version_id is None) != (
            self.expected_contract_record_sha256 is None
        ):
            raise ValueError("CONTRACT_REFERENCE_INCOMPLETE")
        if len({point.point_id for point in self.points}) != len(self.points):
            raise ValueError("HANDOVER_POINT_DUPLICATE")
        if self.contract_instrument_version_id is None and any(
            point.difference_state != "UNKNOWN" for point in self.points
        ):
            raise ValueError("CONTRACT_REQUIRED_FOR_COMPARISON")
        return self


class RecordCaseHandoverRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID
    snapshot_id: UUID
    outcome_id: UUID
    submission_package_id: UUID
    operational_review: HandoverOperationalReview | None = None


class CaseHandoverOfferOptionResponse(BaseModel):
    outcome_id: UUID
    lot_reference: str
    submission_package_id: UUID
    package_version: int
    manifest_sha256: str
    dce_version_id: UUID
    technical_document_id: UUID
    technical_document_version: int
    technical_document_kind: str
    technical_document_sha256: str


class CaseHandoverOfferOptionsResponse(BaseModel):
    case_id: UUID
    items: list[CaseHandoverOfferOptionResponse]


class CaseHandoverSnapshotResponse(BaseModel):
    snapshot_id: UUID
    outcome_id: UUID
    lot_reference: str
    submission_package_id: UUID
    package_version: int
    manifest_sha256: str
    revision: int
    created_at: str
    snapshot: dict[str, object]
    view_sha256: str | None = None
    source_state: str = "UNKNOWN"
    source_reasons: list[str] = Field(default_factory=list)
    receipts: list[dict[str, object]] = Field(default_factory=list)
    receipts_truncated: bool = False


class CaseHandoverSnapshotsResponse(BaseModel):
    case_id: UUID
    items: list[CaseHandoverSnapshotResponse] = Field(default_factory=list)
    next_cursor: UUID | None = None
    truncated: bool = False


class RecordCaseHandoverResponse(BaseModel):
    command_id: UUID
    idempotency_key: UUID
    status: str
    result_code: str
    replayed: bool


class HandoverReceiptFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    receipt_id: UUID
    expected_snapshot_revision: int = Field(gt=0)
    expected_view_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    receipt_kind: Literal["RECEIVED", "RECEIVED_WITH_GAPS"]
    note: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]

    @field_validator("note")
    @classmethod
    def operational_note(cls, value):
        if contains_forbidden_text(value):
            raise ValueError("FINANCIAL_DATA_FORBIDDEN")
        return value


class AcknowledgeHandoverRequest(HandoverReceiptFields):
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID


class HandoverContractOptionResponse(BaseModel):
    instrument_version_id: UUID
    instrument_kind: str
    version_reference: str
    record_sha256: str
    state: str


class HandoverContractOptionsResponse(BaseModel):
    source_context_sha256: str
    case_id: UUID
    items: list[HandoverContractOptionResponse]
    condition_options: list[dict[str, object]] = Field(default_factory=list)
    truncated: bool = False
