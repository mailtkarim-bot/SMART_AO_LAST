from collections.abc import Iterable
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class ConsolidatedUnknownAudit:
    unknown_statuses: tuple[str, ...]
    blocking_statuses: tuple[str, ...]

def audit_consolidated_statuses(statuses: Iterable[str]) -> ConsolidatedUnknownAudit:
    values = tuple(statuses)
    return ConsolidatedUnknownAudit(
        unknown_statuses=tuple(value for value in values if value in {"UNKNOWN", "UNAVAILABLE", "MISMATCH"}),
        blocking_statuses=tuple(value for value in values if value in {"BLOCKED", "FOLLOW_UP_REQUIRED"}),
    )
