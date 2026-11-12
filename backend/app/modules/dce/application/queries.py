"""Read ports and closed projections for DCE application views."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID

from app.modules.dce.application.requirement_values import RcStructuredCandidate
from app.modules.dce.application.source_anchor_projection import DceSourceAnchorProjection


@dataclass(frozen=True, slots=True)
class ConsultationProjection:
    """Read-only Consultation situation safe for the first public API path."""

    id: UUID
    buyer_legal_name: str
    external_reference: str | None
    object_label: str
    location_label: str | None
    lifecycle: str
    freshness: str
    aggregate_revision: int
    lots: tuple[str, ...]
    tranches: tuple[str, ...]
    projection_status: str = "CURRENT"


class ConsultationProjectionReader(Protocol):
    """Read-only, tenant-scoped query port for Consultation."""

    def get(
        self,
        *,
        tenant_id: UUID | str,
        consultation_id: UUID | str,
    ) -> ConsultationProjection | None: ...


class CaseDceReadingAvailability(StrEnum):
    """Closed availability states for one server-resolved Case reading."""

    AVAILABLE = "AVAILABLE"
    NO_APPLICABLE_DCE = "NO_APPLICABLE_DCE"
    DCE_REFERENCE_BROKEN = "DCE_REFERENCE_BROKEN"


@dataclass(frozen=True, slots=True)
class CaseDceReadingCounters:
    """Counters derived exclusively from the final closed requirement collection."""

    total: int
    pending_human_confirmation: int
    confirmed: int
    review_required: int
    not_applicable: int


@dataclass(frozen=True, slots=True)
class CaseDceReadingRequirementProjection:
    """One immutable DCE signal and its optional source provenance projection."""

    requirement_id: UUID
    confirmation_revision: int | None
    requirement_type: str
    directive_signal: str
    confirmation_outcome: str
    uncertainty_status: str
    document_family: str
    source_locator_label: str
    source_anchor: DceSourceAnchorProjection | None = None
    structured_candidate: RcStructuredCandidate | None = None
    source_proof_state: str = "UNKNOWN"
    source_start_byte_offset: int | None = None
    source_end_byte_offset: int | None = None


@dataclass(frozen=True, slots=True)
class CaseDceDocumentCoverage:
    """Safe admitted-piece metadata; extraction is not semantic completeness."""

    document_id: UUID
    extraction_id: UUID | None
    document_family: str
    extraction_status: str


@dataclass(frozen=True, slots=True)
class CaseDceCoverageException:
    """Closed structural provenance or an explicitly unverified declaration."""

    observation_id: UUID
    kind: str
    state: str
    document_id: UUID | None
    extraction_id: UUID | None
    entry_path: tuple[int, ...]
    document_family: str
    source_state: str
    lot_applicability: str = "UNKNOWN"
    criticality: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CaseDceAnnouncementAnchor:
    fragment_id: UUID
    fragment_ordinal: int
    locator_label: str
    part: int
    kind: str
    start_byte_offset: int
    end_byte_offset: int


@dataclass(frozen=True, slots=True)
class CaseDceAnnouncementProjection:
    candidate_id: UUID
    document_family: str
    claim: str
    lot_numbers: tuple[int, ...]
    source_document_id: UUID
    source_extraction_id: UUID
    source_fragment_id: UUID
    source_locator_label: str
    source_locator_state: str
    start_byte_offset: int
    end_byte_offset: int
    family_candidate_document_ids: tuple[UUID, ...]
    context_fragment_id: UUID | None = None
    context_locator_label: str | None = None
    context_start_byte_offset: int | None = None
    context_end_byte_offset: int | None = None
    presence_status: str = "UNKNOWN"
    applicability: str = "UNKNOWN"
    criticality: str = "UNKNOWN"
    conflict_state: str = "UNKNOWN"
    rule_version: str = "1"
    anchor_chain: tuple[CaseDceAnnouncementAnchor, ...] = ()


@dataclass(frozen=True, slots=True)
class CaseDceCoverageProjection:
    """Known extraction coverage, with unrecorded inventory/lot facts explicit."""

    case_scope_kind: str
    documents: tuple[CaseDceDocumentCoverage, ...]
    total_documents: int
    completed_extractions: int
    unread_documents: int
    exceptions: tuple[CaseDceCoverageException, ...] = ()
    announcements: tuple[CaseDceAnnouncementProjection, ...] = ()
    announcement_scan_state: str = "UNKNOWN"
    inventory_scope: str = "ADMITTED_DOCUMENTS_ONLY"
    inventory_completeness: str = "UNKNOWN"
    lot_applicability: str = "UNKNOWN"
    critical_unread_documents: None = None
    status: str = "REVIEW_REQUIRED"
    analysis_complete: bool = False


@dataclass(frozen=True, slots=True)
class CaseDceReadingProjection:
    """Closed DCE situation applicable to one Case at one point in time."""

    dce_version_id: UUID
    lifecycle: str
    integrity: str
    classification_readiness: str
    analysis_readiness: str
    source_received_at: datetime
    requirements: tuple[CaseDceReadingRequirementProjection, ...]
    counters: CaseDceReadingCounters
    coverage: CaseDceCoverageProjection | None = None


@dataclass(frozen=True, slots=True)
class CaseDceReadingLookup:
    """Tenant-scoped Case lookup with an explicitly unavailable DCE state."""

    case_id: UUID
    work_label: str
    case_lifecycle: str
    commercial_stage: str
    dce_freshness: str
    availability: CaseDceReadingAvailability
    reading: CaseDceReadingProjection | None


class CaseDceReadingReader(Protocol):
    """Read-only port for the DCE applicable to one Case in one tenant."""

    def get(
        self,
        *,
        tenant_id: UUID | str,
        case_id: UUID | str,
    ) -> CaseDceReadingLookup | None: ...


@dataclass(frozen=True, slots=True)
class DceContractRiskSignalProjection:
    """Closed provenance metadata for one CCAP/CCTP contract-risk signal."""

    observation_id: UUID
    dce_version_id: UUID
    document_family: str
    requirement_kind: str
    rule_id: str
    rule_version: str
    directive: str
    fragment_id: UUID
    source_locator_label: str
    start_byte_offset: int
    end_byte_offset: int
    verification_status: str


class DceContractRiskSignalReader(Protocol):
    """Read-only tenant/case reader for detected CCAP/CCTP contract-risk signals."""

    def list_for_case(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        limit: int,
    ) -> tuple[DceContractRiskSignalProjection, ...]: ...


@dataclass(frozen=True, slots=True)
class AssignedCaseProjection:
    """Closed Case summary candidate; authorization remains a route concern."""

    case_id: UUID
    work_label: str
    case_lifecycle: str
    commercial_stage: str
    dce_availability: str
    consultation_id: UUID | None
    applicable_dce_version_id: UUID | None
    aggregate_revision: int = 0


class AssignedCaseReader(Protocol):
    """Tenant-scoped candidate reader for the server-filtered Case collection."""

    def list(self, *, tenant_id: UUID | str) -> tuple[AssignedCaseProjection, ...]: ...
