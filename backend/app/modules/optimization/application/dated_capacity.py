"""Advisory daily capacity assignments; no reservation or financial effect."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from ortools.sat.python import cp_model

from app.modules.optimization.application.resource_assignment import SolverStatus, _map_status


@dataclass(frozen=True, slots=True)
class CapacityPeriod:
    start: date
    end: date

    def __post_init__(self) -> None:
        if type(self.start) is not date or type(self.end) is not date or self.end <= self.start:
            raise ValueError("period requires dates with start < end (end excluded)")


@dataclass(frozen=True, slots=True)
class CapacitySource:
    reference: str
    revision: str
    locator: str

    def __post_init__(self) -> None:
        for value in (self.reference, self.revision, self.locator):
            if not isinstance(value, str) or not value.strip() or len(value) > 500:
                raise ValueError("source reference, revision and locator must be explicit")


@dataclass(frozen=True, slots=True)
class DatedDemand:
    id: UUID
    label: str
    resource_type: str | None
    required_units: int | None
    period: CapacityPeriod | None
    source: CapacitySource | None
    named_supply_id: UUID | None = None

    def __post_init__(self) -> None:
        _validate_row(self.id, self.label, self.resource_type, self.required_units, minimum=1)
        _validate_evidence(self.period, self.source)
        if self.named_supply_id is not None and not isinstance(self.named_supply_id, UUID):
            raise ValueError("named supply must be an explicit UUID")


@dataclass(frozen=True, slots=True)
class DatedSupply:
    id: UUID
    label: str
    resource_type: str | None
    capacity_units: int | None
    period: CapacityPeriod | None
    source: CapacitySource | None

    def __post_init__(self) -> None:
        _validate_row(self.id, self.label, self.resource_type, self.capacity_units, minimum=0)
        _validate_evidence(self.period, self.source)


def _validate_evidence(period: CapacityPeriod | None, source: CapacitySource | None) -> None:
    if period is not None and not isinstance(period, CapacityPeriod):
        raise ValueError("period must be qualified or unknown")
    if source is not None and not isinstance(source, CapacitySource):
        raise ValueError("source must be qualified or unknown")


def _validate_row(
    id: UUID, label: str, kind: str | None, units: int | None, *, minimum: int
) -> None:
    if (
        not isinstance(id, UUID)
        or not isinstance(label, str)
        or not label.strip()
        or len(label) > 200
    ):
        raise ValueError("explicit resource id and label required")
    if kind is not None and (not isinstance(kind, str) or not kind.strip() or len(kind) > 100):
        raise ValueError("resource_type must be explicit or unknown")
    if units is not None and (type(units) is not int or not minimum <= units <= 10000):
        raise ValueError("capacity units outside integer bounds")


@dataclass(frozen=True, slots=True)
class CapacityConflict:
    """Aggregate shortage diagnostic; not a minimal infeasible subset proof."""

    period: CapacityPeriod
    resource_type: str
    required_units: int
    available_units: int
    demand_ids: tuple[UUID, ...]


@dataclass(frozen=True, slots=True)
class DatedCapacityResult:
    status: SolverStatus
    assignments: dict[UUID, UUID]
    unknown_ids: tuple[UUID, ...] = ()
    conflicts: tuple[CapacityConflict, ...] = ()


class DatedCapacityOptimizer:
    solver_id = "google-ortools-cp-sat-dated-v1"

    def __init__(self, *, time_limit_seconds: float = 5.0) -> None:
        if not math.isfinite(time_limit_seconds) or not 0 < time_limit_seconds <= 30:
            raise ValueError("time limit must be finite and bounded")
        self._time_limit_seconds = time_limit_seconds

    def solve(
        self, *, demands: tuple[DatedDemand, ...] | None, supplies: tuple[DatedSupply, ...] | None
    ) -> DatedCapacityResult:
        for rows in (demands or (), supplies or ()):
            if len(rows) > 100 or len({row.id for row in rows}) != len(rows):
                raise ValueError("at most 100 distinct rows per input")
        rows_typed: tuple[DatedDemand | DatedSupply, ...] = (*(demands or ()), *(supplies or ()))
        unknown = tuple(
            row.id
            for row in rows_typed
            if row.period is None
            or row.source is None
            or row.resource_type is None
            or (row.required_units if isinstance(row, DatedDemand) else row.capacity_units) is None
        )
        if demands is None or supplies is None or unknown:
            return DatedCapacityResult(SolverStatus.UNKNOWN, {}, unknown)
        if not demands:
            return DatedCapacityResult(SolverStatus.OPTIMAL, {})
        # Missing fields were refused above; keep types explicit at the solver boundary.
        model = cp_model.CpModel()
        decisions: dict[tuple[UUID, UUID], cp_model.IntVar] = {}
        for supply in supplies:
            assert supply.period is not None and supply.capacity_units is not None
            intervals = []
            quantities = []
            for demand in demands:
                assert demand.period is not None and demand.required_units is not None
                if (
                    demand.resource_type != supply.resource_type
                    or demand.named_supply_id not in (None, supply.id)
                    or demand.period.start < supply.period.start
                    or demand.period.end > supply.period.end
                ):
                    continue
                present = model.new_bool_var(f"assign_{demand.id}_{supply.id}")
                decisions[demand.id, supply.id] = present
                intervals.append(
                    model.new_optional_fixed_size_interval_var(
                        demand.period.start.toordinal(),
                        (demand.period.end - demand.period.start).days,
                        present,
                        f"period_{demand.id}_{supply.id}",
                    )
                )
                quantities.append(demand.required_units)
            model.add_cumulative(intervals, quantities, supply.capacity_units)
        for demand in demands:
            model.add(sum(var for (did, _), var in decisions.items() if did == demand.id) == 1)
        model.minimize(sum((index + 1) * var for index, var in enumerate(decisions.values())))
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self._time_limit_seconds
        solver.parameters.num_search_workers = 1
        status = _map_status(solver.solve(model))
        if status not in (SolverStatus.OPTIMAL, SolverStatus.FEASIBLE):
            return DatedCapacityResult(
                status,
                {},
                conflicts=_shortages(demands, supplies)
                if status == SolverStatus.INFEASIBLE
                else (),
            )
        return DatedCapacityResult(
            status, {did: sid for (did, sid), var in decisions.items() if solver.value(var)}
        )


def _shortages(
    demands: tuple[DatedDemand, ...], supplies: tuple[DatedSupply, ...]
) -> tuple[CapacityConflict, ...]:
    # Event boundaries avoid an unbounded expansion into individual calendar days.
    rows_typed: tuple[DatedDemand | DatedSupply, ...] = (*demands, *supplies)
    boundaries = sorted(
        {
            day
            for row in rows_typed
            if row.period is not None
            for day in (row.period.start, row.period.end)
        }
    )
    result = []
    for start, end in zip(boundaries, boundaries[1:], strict=False):
        for kind in sorted({row.resource_type for row in demands if row.resource_type is not None}):
            active = tuple(
                row
                for row in demands
                if row.period is not None
                and row.resource_type == kind
                and row.period.start <= start < row.period.end
            )
            required = sum(row.required_units or 0 for row in active)
            available = sum(
                row.capacity_units or 0
                for row in supplies
                if row.period is not None
                and row.resource_type == kind
                and row.period.start <= start < row.period.end
            )
            if required > available:
                result.append(
                    CapacityConflict(
                        CapacityPeriod(start, end),
                        kind,
                        required,
                        available,
                        tuple(row.id for row in active),
                    )
                )
    return tuple(result)
