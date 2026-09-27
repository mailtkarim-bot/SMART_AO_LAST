from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True, slots=True)
class FinalUnknownAudit:
    counts: dict[str, int]
    entries: tuple[dict[str, object], ...]

def build_final_unknown_audit(entries: Iterable[dict[str, object]]) -> FinalUnknownAudit:
    values = tuple(entries)
    difficult = tuple(value for value in values if value.get("status") in {"UNKNOWN", "UNAVAILABLE", "MISMATCH", "BLOCKED", "FOLLOW_UP_REQUIRED"})
    return FinalUnknownAudit(counts=dict(Counter(str(value["status"]) for value in difficult)), entries=difficult)
