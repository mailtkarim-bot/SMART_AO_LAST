from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True, slots=True)
class ExportVerificationOwnerAct:
    export_id: UUID
    owner_id: UUID
    approved: bool
    rationale: str

    def validate(self) -> None:
        if not self.rationale.strip():
            raise ValueError("OWNER_RATIONALE_REQUIRED")
