# ruff: noqa: E501, I001, UP035
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True, slots=True)
class PaymentUnknownAudit:
    status_counts: dict[str, int]
    entries: tuple[dict[str, object], ...]
    rejected_count: int = 0

def build_payment_unknown_audit(entries: Iterable[dict[str, object]], *, rejected_count: int = 0) -> PaymentUnknownAudit:
    values = tuple(value for value in entries if value.get("status") in {"SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"})
    if rejected_count < 0:
        raise ValueError("PAYMENT_REJECTED_COUNT_INVALID")
    return PaymentUnknownAudit(status_counts=dict(Counter(str(value["status"]) for value in values)), entries=values, rejected_count=rejected_count)
