"""Bounded read-only margin on explicitly declared base cost categories."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

from app.modules.pricing.domain.cost_basis import (
    CostBasisInput,
    CostBasisValidationError,
    calculate_cost_basis,
)

BASE_MARGIN_CATEGORIES = ("SALES", "DIRECT_COST", "OVERHEAD", "SUBCONTRACTING", "CONTINGENCY")


@dataclass(frozen=True, slots=True)
class DeclaredBaseMargin:
    state: Literal["CALCULATED", "UNKNOWN"] = "UNKNOWN"
    basis: Literal["DECLARED_BASE_CATEGORIES"] = "DECLARED_BASE_CATEGORIES"
    missing_categories: tuple[str, ...] = ()
    total_cost_minor: int | None = None
    gross_margin_minor: int | None = None
    gross_margin_rate_bps: int | None = None
    unknown_reason: str | None = None
    rate_unknown_reason: str | None = None


def calculate_declared_base_margin(lines: Sequence[tuple[str, int]]) -> DeclaredBaseMargin:
    """Missing categories remain unknown; an explicit zero is a declared input.

    This does not establish that all economic costs of an affair are covered.
    Stored human GROSS_MARGIN and FORECAST_CASHFLOW declarations are not inputs.
    """
    totals: dict[str, int] = {}
    for category, amount in lines:
        if category not in BASE_MARGIN_CATEGORIES:
            continue
        if isinstance(amount, bool) or not isinstance(amount, int):
            return DeclaredBaseMargin(unknown_reason="INVALID_BASE_AMOUNT")
        totals[category] = totals.get(category, 0) + amount
    missing = tuple(category for category in BASE_MARGIN_CATEGORIES if category not in totals)
    if missing:
        return DeclaredBaseMargin(
            missing_categories=missing, unknown_reason="MISSING_BASE_CATEGORY"
        )
    try:
        result = calculate_cost_basis(
            CostBasisInput(
                sales_total_minor=totals["SALES"],
                direct_cost_total_minor=totals["DIRECT_COST"],
                overhead_total_minor=totals["OVERHEAD"],
                subcontracting_total_minor=totals["SUBCONTRACTING"],
                contingency_total_minor=totals["CONTINGENCY"],
            )
        )
    except CostBasisValidationError:
        return DeclaredBaseMargin(unknown_reason="INVALID_BASE_AMOUNT")
    return DeclaredBaseMargin(
        state="CALCULATED",
        total_cost_minor=result.total_cost_minor,
        gross_margin_minor=result.gross_margin_minor,
        gross_margin_rate_bps=result.gross_margin_rate_bps if totals["SALES"] else None,
        rate_unknown_reason=None if totals["SALES"] else "ZERO_SALES",
    )


def qualify_declared_scenario_source(
    lines: Sequence[tuple[str, int]],
    snapshot_totals: Mapping[str, int],
    *,
    source_revision: int,
    expected_revision: int,
) -> str | None:
    """Qualify declared inputs only, never exhaustive economic coverage."""
    if source_revision != expected_revision:
        return "SOURCE_REVISION_MISMATCH"
    margin = calculate_declared_base_margin(lines)
    if margin.unknown_reason:
        return margin.unknown_reason
    if margin.rate_unknown_reason:
        return margin.rate_unknown_reason
    totals = {category: 0 for category in BASE_MARGIN_CATEGORIES}
    for category, amount in lines:
        if category in totals:
            totals[category] += amount
    if any(totals[category] != snapshot_totals.get(category) for category in totals):
        return "SOURCE_TOTAL_MISMATCH"
    return None
