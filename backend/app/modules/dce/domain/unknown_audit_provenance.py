from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

class UnknownAuditSource(StrEnum):
    TRANSITION = "TRANSITION"
    HUMAN_RESUMPTION = "HUMAN_RESUMPTION"
    VERIFICATION = "VERIFICATION"

@dataclass(frozen=True, slots=True)
class UnknownAuditProvenance:
    export_id: UUID
    source_type: UnknownAuditSource
    source_event_id: UUID
    actor_id: UUID
    status: str
    occurred_at: datetime
    rationale: str | None

    def validate(self) -> None:
        if not self.status.strip():
            raise ValueError("PROVENANCE_STATUS_REQUIRED")
        if self.rationale is not None and not self.rationale.strip():
            raise ValueError("PROVENANCE_RATIONALE_NON_EMPTY")
