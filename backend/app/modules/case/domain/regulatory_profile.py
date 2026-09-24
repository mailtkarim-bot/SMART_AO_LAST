"""Pure contract for the first regulatory applicability profile slice."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class RegulatoryApplicabilityStatus(StrEnum):
    ACTIVE = "ACTIVE"
    FUTURE = "FUTURE"
    EXPIRED = "EXPIRED"
    UNKNOWN_APPLICABILITY = "UNKNOWN_APPLICABILITY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass(frozen=True, slots=True)
class RegulatoryProfile:
    """Sourced facts used to assess applicability without deciding legality."""

    case_id: UUID
    profile_version: int
    status: RegulatoryApplicabilityStatus
    facts: Mapping[str, object]
    source_refs: tuple[str, ...]
    effective_from: datetime | None = None
    effective_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.profile_version < 1:
            raise ValueError("profile_version must be positive")
        if not self.facts:
            raise ValueError("facts must not be empty")
        if not self.source_refs or any(not ref.strip() for ref in self.source_refs):
            raise ValueError("source_refs must contain at least one non-empty reference")
        if self.status is RegulatoryApplicabilityStatus.FUTURE and self.effective_from is None:
            raise ValueError("FUTURE profile requires effective_from")
        if self.status is RegulatoryApplicabilityStatus.EXPIRED and self.effective_until is None:
            raise ValueError("EXPIRED profile requires effective_until")
        if (
            self.effective_from is not None
            and self.effective_until is not None
            and self.effective_until < self.effective_from
        ):
            raise ValueError("effective_until must not precede effective_from")
