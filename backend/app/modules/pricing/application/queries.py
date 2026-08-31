from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PricingScenarioProjection:
    scenario_id: UUID
    case_id: UUID
    scenario_key: str
    scenario_type: str
    version: int
    state: str
    assumptions: dict[str, object]
    sales_total_minor: int
    total_cost_minor: int
    gross_margin_minor: int
    gross_margin_rate_bps: int
    penalty_reserve_minor: int
    retention_reserve_minor: int
    guarantee_reserve_minor: int
    floor_margin_rate_bps: int
    target_margin_rate_bps: int
    break_even_sales_minor: int
    floor_sales_minor: int
    target_sales_minor: int
    source_snapshot_revision: int


def project_pricing_scenario(
    *,
    scenario_id: UUID,
    case_id: UUID,
    scenario_key: str,
    scenario_type: str,
    version: int,
    state: str,
    assumptions: dict[str, object],
    sales_total_minor: int,
    total_cost_minor: int,
    gross_margin_minor: int,
    gross_margin_rate_bps: int,
    penalty_reserve_minor: int,
    retention_reserve_minor: int,
    guarantee_reserve_minor: int,
    floor_margin_rate_bps: int,
    target_margin_rate_bps: int,
    break_even_sales_minor: int,
    floor_sales_minor: int,
    target_sales_minor: int,
    source_snapshot_revision: int,
) -> PricingScenarioProjection:
    """Build a pricing scenario projection from primitive fields.

    The caller is responsible for supplying the current ``state`` and ``version``,
    which may be derived from append-only transitions rather than the immutable
    scenario row.
    """
    return PricingScenarioProjection(
        scenario_id=scenario_id,
        case_id=case_id,
        scenario_key=scenario_key,
        scenario_type=scenario_type,
        version=version,
        state=state,
        assumptions=assumptions,
        sales_total_minor=sales_total_minor,
        total_cost_minor=total_cost_minor,
        gross_margin_minor=gross_margin_minor,
        gross_margin_rate_bps=gross_margin_rate_bps,
        penalty_reserve_minor=penalty_reserve_minor,
        retention_reserve_minor=retention_reserve_minor,
        guarantee_reserve_minor=guarantee_reserve_minor,
        floor_margin_rate_bps=floor_margin_rate_bps,
        target_margin_rate_bps=target_margin_rate_bps,
        break_even_sales_minor=break_even_sales_minor,
        floor_sales_minor=floor_sales_minor,
        target_sales_minor=target_sales_minor,
        source_snapshot_revision=source_snapshot_revision,
    )


class PricingScenarioReader(Protocol):
    """Read tenant-scoped patron pricing projections."""

    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[PricingScenarioProjection, ...]: ...
