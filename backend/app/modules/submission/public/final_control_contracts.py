"""Bounded final control facts; none of these states grants conformity or a gate."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.preparation.public.contracts import ResponseCitedAnnex, ResponseCoverageRequirement
from app.modules.submission.public.signature_contracts import SubmissionSignatureProjection


class FinalControlFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    archive_path: str
    document_kind: str = "UNKNOWN"
    media_type: str | None = None
    validity: Literal["UNKNOWN"] = "UNKNOWN"
    document_id: UUID
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    byte_size: int | None = Field(default=None, ge=0)
    requirement_ids: list[UUID] = Field(default_factory=list)
    presence: Literal["VERIFIED_SOURCE", "UNKNOWN"]
    signature: Literal["UNKNOWN"] = "UNKNOWN"


class BuyerFileComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    source_excerpt: str | None
    source_locator: str
    source_anchor: dict | None
    confirmation: str
    scope: Literal["TECHNICAL_RESPONSE", "KBIS", "DELIVERY", "UNSPECIFIED"]
    requested: Literal["PDF", "DOCX", "PNG", "ZIP", "NO_ZIP", "INDIVIDUAL_FILES", "UNKNOWN"]
    files: list[FinalControlFile]
    state: Literal["OBSERVED_MATCH", "OBSERVED_MISMATCH", "UNKNOWN"]
    reason_code: str
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    conformity: Literal["UNKNOWN"] = "UNKNOWN"


class BuyerNameSizeComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")

    requirement_id: UUID
    source_excerpt: str | None
    source_locator: str
    source_anchor: dict | None
    confirmation: str
    scope: Literal["TECHNICAL_RESPONSE", "KBIS", "KNOWN_DOCUMENT_FILES", "UNSPECIFIED"]
    criterion: Literal["EXACT_NAME", "NO_WHITESPACE", "MAX_BYTES", "UNKNOWN"]
    requested_name: str | None = None
    max_bytes: int | None = Field(default=None, ge=0)
    files: list[FinalControlFile]
    state: Literal["OBSERVED_MATCH", "OBSERVED_MISMATCH", "UNKNOWN"]
    reason_code: str
    applicability: Literal["UNKNOWN"] = "UNKNOWN"
    conformity: Literal["UNKNOWN"] = "UNKNOWN"


class PublishedPricingReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_id: UUID
    revision: int = Field(ge=0)


class SubmissionPricingReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    state: Literal["CURRENT", "REVIEW_REQUIRED", "UNKNOWN", "NOT_APPLICABLE"] = "UNKNOWN"
    referenced: PublishedPricingReference | None = None
    latest_published: PublishedPricingReference | None = None
    reason_code: Literal[
        "REFERENCE_NOT_VERIFIED",
        "LATEST_PUBLISHED_REFERENCE",
        "NEWER_PUBLISHED_REPORT",
        "CANDIDATURE_ONLY",
    ] = "REFERENCE_NOT_VERIFIED"


class SubmissionFinalControlProjection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    submission_package_id: UUID
    package_version: int
    manifest_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    dce_version_id: UUID
    state: Literal["PARTIAL", "REVIEW_REQUIRED", "UNKNOWN"]
    source_state: Literal["CURRENT", "REVIEW_REQUIRED", "UNKNOWN"]
    pricing_reference: SubmissionPricingReference = Field(
        default_factory=SubmissionPricingReference
    )
    local_delivery_mode: Literal["LOCAL_ZIP", "UNKNOWN"] = "UNKNOWN"
    buyer_formats_state: Literal["OBSERVATIONS_AVAILABLE", "UNKNOWN"] = "UNKNOWN"
    format_comparisons: list[BuyerFileComparison] = Field(default_factory=list)
    buyer_names_sizes_state: Literal["OBSERVATIONS_AVAILABLE", "UNKNOWN"] = "UNKNOWN"
    name_size_comparisons: list[BuyerNameSizeComparison] = Field(default_factory=list)
    files: list[FinalControlFile]
    requirements: list[ResponseCoverageRequirement]
    missing_cited_annexes: list[ResponseCitedAnnex]
    entries_without_exported_file: list[str]
    patron_review_ids: list[UUID]
    p5_authorization_status: Literal["RECORDED", "NOT_RECORDED"]
    p5_authorization_id: UUID | None
    signature_visibility: Literal["RESTRICTED"] = "RESTRICTED"
    signature_records: list[SubmissionSignatureProjection] = Field(
        default_factory=list, max_length=0
    )
    inventory: Literal["CURRENT_NON_FINANCIAL_SIGNALS_ONLY"] = "CURRENT_NON_FINANCIAL_SIGNALS_ONLY"
    signature_requirement: Literal["UNKNOWN"] = "UNKNOWN"
    signature_verification: Literal["UNKNOWN"] = "UNKNOWN"
    signer_authority: Literal["UNKNOWN"] = "UNKNOWN"
    conformity: Literal["UNKNOWN"] = "UNKNOWN"
    external_submission: Literal["NOT_PERFORMED"] = "NOT_PERFORMED"
