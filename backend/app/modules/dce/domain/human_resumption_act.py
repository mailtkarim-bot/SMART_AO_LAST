from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

class HumanResumptionState(StrEnum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    BLOCKED = "BLOCKED"

@dataclass(frozen=True, slots=True)
class HumanResumptionAct:
    export_id: UUID
    actor_id: UUID
    state: HumanResumptionState
    rationale: str

    def validate(self) -> None:
        if not self.rationale.strip():
            raise ValueError("RESUMPTION_RATIONALE_REQUIRED")
