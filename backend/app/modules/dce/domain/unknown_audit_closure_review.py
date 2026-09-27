from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True, slots=True)
class UnknownAuditClosureReview:
    reviewer_id: UUID
    evidence_count: int
    documentation_synced: bool
    public_go: bool
    rationale: str

    def validate(self) -> None:
        if self.evidence_count < 1:
            raise ValueError("CLOSURE_EVIDENCE_REQUIRED")
        if not self.documentation_synced:
            raise ValueError("DOCUMENTATION_SYNC_REQUIRED")
        if self.public_go:
            raise ValueError("PUBLIC_GO_FORBIDDEN")
        if not self.rationale.strip():
            raise ValueError("CLOSURE_RATIONALE_REQUIRED")
