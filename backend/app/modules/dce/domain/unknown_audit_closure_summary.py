from collections import Counter
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True, slots=True)
class UnknownAuditClosureSummary:
    status_counts: dict[str, int]
    source_counts: dict[str, int]
    open_entries: tuple[dict[str, object], ...]

def build_unknown_audit_closure_summary(entries: Iterable[dict[str, object]]) -> UnknownAuditClosureSummary:
    values = tuple(entries)
    open_entries = tuple(value for value in values if value.get("status") in {"UNKNOWN", "MISMATCH", "BLOCKED", "FOLLOW_UP_REQUIRED"})
    return UnknownAuditClosureSummary(
        status_counts=dict(Counter(str(value["status"]) for value in open_entries)),
        source_counts=dict(Counter(str(value["source_type"]) for value in open_entries)),
        open_entries=open_entries,
    )
