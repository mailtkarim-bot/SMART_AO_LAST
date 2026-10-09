"""Application ports for preparation read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class PreparationRequirementInput:
    """Minimal DCE requirement facts used by deterministic readiness and generation."""

    requirement_id: UUID
    requirement_type: str
    directive_signal: str
    confirmation_outcome: str | None


@dataclass(frozen=True, slots=True)
class PreparationDceInput:
    """Minimal DCE projection exposed to preparation application logic."""

    analysis_readiness: str
    requirements: tuple[PreparationRequirementInput, ...]


class PreparationDceReader(Protocol):
    """Read-only DCE projection port owned by the preparation application."""

    def read(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        dce_version_id: UUID,
        as_of: datetime,
    ) -> PreparationDceInput | None: ...


PreparationRequirementState = Literal["CONFIRMED", "REVIEW_REQUIRED", "NOT_APPLICABLE", "UNKNOWN"]
PreparationSourceState = Literal["CURRENT", "EXPIRED", "UNKNOWN"]


@dataclass(frozen=True, slots=True)
class PreparationResponsePlanFact:
    proposal_id: UUID
    requirement_id: UUID | None
    task_id: UUID | None
    capability_version_id: UUID
    validity_state: PreparationSourceState
    evidence_state: PreparationSourceState
    proof_refs: tuple[tuple[UUID, str], ...]


@dataclass(frozen=True, slots=True)
class PreparationResponsePlanSources:
    dce_current: bool
    requirement_states: dict[UUID, PreparationRequirementState]
    facts: dict[UUID, PreparationResponsePlanFact]


class PreparationResponsePlanSourceReader(Protocol):
    """Resolve exact Case/DCE requirements and existing reusable capability proofs."""

    def read(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        case_id: UUID,
        assignment_id: UUID,
        dce_version_id: UUID,
        requirement_ids: set[UUID],
        proposal_ids: set[UUID],
        evaluated_at: datetime,
    ) -> PreparationResponsePlanSources: ...


class PreparationPrivateSourceDigestReader(Protocol):
    """Re-read one authorized private source without returning its bytes to the command."""

    def read_digest(self, *, storage_key: str, max_bytes: int) -> tuple[int, str]: ...
