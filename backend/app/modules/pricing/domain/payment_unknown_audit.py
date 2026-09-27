from collections import Counter
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True, slots=True)
class PaymentUnknownAudit:
    status_counts: dict[str, int]
    entries: tuple[dict[str, object], ...]

def build_payment_unknown_audit(entries: Iterable[dict[str, object]]) -> PaymentUnknownAudit:
    values = tuple(value for value in entries if value.get("status") in {"SOURCE_SIGNAL_ONLY", "REVIEW_REQUIRED", "UNKNOWN"})
    return PaymentUnknownAudit(status_counts=dict(Counter(str(value["status"]) for value in values)), entries=values)
