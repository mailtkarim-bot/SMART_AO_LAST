# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ExportVerificationOutcome(StrEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    UNAVAILABLE = "UNAVAILABLE"

@dataclass(frozen=True, slots=True)
class ExportProofVerificationRecord:
    export_id: UUID
    outcome: ExportVerificationOutcome
    calculated_sha256: str | None
    checked_by_actor_id: UUID

    def validate(self) -> None:
        if self.outcome is ExportVerificationOutcome.MATCH and (
            self.calculated_sha256 is None or len(self.calculated_sha256) != 64
        ):
            raise ValueError("MATCH_HASH_REQUIRED")
        if self.outcome is ExportVerificationOutcome.UNAVAILABLE and self.calculated_sha256 is not None:
            raise ValueError("UNAVAILABLE_HASH_FORBIDDEN")
