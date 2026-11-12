"""Conservative query lot evidence, independent from ranking and business applicability."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from app.modules.knowledge.application.rc_candidate_conflicts import (
    RcClauseEvidence,
    RcConflictProjection,
)


@dataclass(frozen=True, slots=True)
class RcQueryLot:
    state: Literal["CANDIDATE", "UNKNOWN"] = "UNKNOWN"
    lot: int | None = None
    start_byte: int | None = None
    end_byte: int | None = None


_LOT = re.compile(r"\blot\s+(?:n[°o]\s*)?([0-9]{1,3})(?!\w)", re.I)
_CONDITION = re.compile(
    r"\b(?:si|sauf|sans|hors|excepté|lorsque|selon|sous\s+réserve|en\s+cas|à\s+condition"
    r"|à\s+défaut|à\s+l['’]exclusion|en\s+dehors)\b",
    re.I,
)
_CONTINUATION = re.compile(
    r"^\s*(?:[\W_]*[0-9]|bis\b|ter\b|quater\b|[-‐‑‒–—―−/]\s*\w"
    r"|non\s+(?:compris|concerné|visé)\b"
    r"|(?:et|ou|à|a|jusqu['’][àa])\s*(?:le\s+)?(?:lot\s+)?[0-9])",
    re.I,
)


def parse_query_lot(query: str) -> RcQueryLot:
    if not query.strip() or len(query) > 2000:
        raise ValueError("invalid candidate query budget")
    matches = list(_LOT.finditer(query))
    if len(matches) != 1 or len(re.findall(r"\blots?\b", query, re.I)) != 1:
        return RcQueryLot()
    match = matches[0]
    if (
        int(match[1]) == 0
        or _CONDITION.search(query)
        or _CONTINUATION.search(query[match.end() :])
        or re.search(r"\b(?:pas|autre\s+que)\s+(?:le\s+)?$", query[: match.start()], re.I)
    ):
        return RcQueryLot()
    return RcQueryLot(
        "CANDIDATE",
        int(match[1]),
        len(query[: match.start()].encode()),
        len(query[: match.end()].encode()),
    )


def scope_rc_projection(
    projection: RcConflictProjection,
    query_lot: RcQueryLot,
) -> tuple[RcConflictProjection, tuple[RcClauseEvidence, ...]]:
    """Preserve unassigned evidence; no lot is inferred from a source's rank."""
    if query_lot.state == "UNKNOWN":
        return RcConflictProjection(unknown_regions=projection.unknown_regions), projection.clauses
    clauses = tuple(c for c in projection.clauses if c.lot == query_lot.lot)
    unknown = tuple(c for c in projection.unknown_regions if c.lot in (None, query_lot.lot))
    unscoped = tuple(
        c
        for c in (*projection.clauses, *projection.unknown_regions)
        if c.lot is not None and c.lot != query_lot.lot
    )
    links = tuple(
        link
        for link in projection.links
        if link.left.lot == query_lot.lot and link.right.lot == query_lot.lot
    )
    return RcConflictProjection(clauses, links, unknown), unscoped
