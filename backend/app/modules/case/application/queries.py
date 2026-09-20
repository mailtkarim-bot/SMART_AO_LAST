"""Read-only Case projections assembled from existing source registers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CaseResolutionItemProjection:
    """One open point while preserving its native source and state."""

    item_id: UUID
    item_kind: str
    native_state: str
    source_refs: tuple[str, ...]
    resolution_owner: str | None
    next_action: str
    due_at: datetime | None
    impact: str | None = None


@dataclass(frozen=True, slots=True)
class CaseResolutionIndexProjection:
    """Closed, deliberately partial read model for one Case."""

    case_id: UUID
    work_label: str
    coverage: str
    items: tuple[CaseResolutionItemProjection, ...]
    economic_coverage: CaseEconomicCoverageProjection | None = None


@dataclass(frozen=True, slots=True)
class CaseEconomicCoverageStatusProjection:
    """One Patron-only evidence status without exposing monetary values."""

    state: str
    source_refs: tuple[str, ...]
    note: str


@dataclass(frozen=True, slots=True)
class CaseEconomicCoverageProjection:
    """Small read-only view of the four EXP-05 evidence boundaries."""

    assumptions: CaseEconomicCoverageStatusProjection
    quote_validity: CaseEconomicCoverageStatusProjection
    capacity: CaseEconomicCoverageStatusProjection
    financing: CaseEconomicCoverageStatusProjection


@dataclass(frozen=True, slots=True)
class CaseResolutionUnknownProjection:
    """One source-owned unknown attached to an opportunity Case."""

    unknown_id: UUID
    native_state: str
    source_refs: tuple[str, ...]
    next_action: str
    due_at: datetime | None
    impact: str | None = None


class CaseResolutionUnknownReader(Protocol):
    """Reads source-owned unknowns for an opportunity-origin Case."""

    def list_for_case(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        limit: int,
    ) -> tuple[CaseResolutionUnknownProjection, ...]: ...


class CaseResolutionReader(Protocol):
    """Tenant and assignment-scoped reader for open Case points."""

    def get(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        membership_id: UUID | None,
    ) -> CaseResolutionIndexProjection | None: ...
