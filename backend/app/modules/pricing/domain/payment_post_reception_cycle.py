from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

class PaymentCycleStatus(StrEnum):
    SOURCE_SIGNAL_ONLY = "SOURCE_SIGNAL_ONLY"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True, slots=True)
class PaymentPostReceptionCycle:
    case_id: UUID
    source_refs: tuple[str, ...]
    trigger_event: str
    status: PaymentCycleStatus
    cash_assumption: str | None
    post_reception_cost_note: str | None

    def validate(self) -> None:
        if not self.source_refs:
            raise ValueError("PAYMENT_SOURCE_REQUIRED")
        if not self.trigger_event.strip():
            raise ValueError("PAYMENT_TRIGGER_REQUIRED")
        if self.cash_assumption is not None and not self.cash_assumption.strip():
            raise ValueError("CASH_ASSUMPTION_NON_EMPTY")
        if self.post_reception_cost_note is not None and not self.post_reception_cost_note.strip():
            raise ValueError("POST_RECEPTION_COST_NOTE_NON_EMPTY")
