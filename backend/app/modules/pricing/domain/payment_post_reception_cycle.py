# ruff: noqa: E501, I001
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

def build_external_payment_signal(*, case_id: UUID, source_refs: tuple[str, ...], trigger_event: str, post_reception_cost_note: str | None = None) -> PaymentPostReceptionCycle:
    cycle = PaymentPostReceptionCycle(case_id=case_id, source_refs=source_refs, trigger_event=trigger_event, status=PaymentCycleStatus.SOURCE_SIGNAL_ONLY, cash_assumption=None, post_reception_cost_note=post_reception_cost_note)
    cycle.validate()
    return cycle

@dataclass(frozen=True, slots=True)
class PaymentCostQualification:
    cash_assumption: str | None
    post_reception_cost_note: str | None

    def validate(self) -> None:
        if self.cash_assumption is not None and not self.cash_assumption.strip():
            raise ValueError("CASH_ASSUMPTION_NON_EMPTY")
        if self.post_reception_cost_note is not None and not self.post_reception_cost_note.strip():
            raise ValueError("POST_RECEPTION_COST_NOTE_NON_EMPTY")

def build_payment_cost_qualification(*, cash_assumption: str | None, post_reception_cost_note: str | None) -> PaymentCostQualification:
    qualification = PaymentCostQualification(cash_assumption=cash_assumption, post_reception_cost_note=post_reception_cost_note)
    qualification.validate()
    return qualification
