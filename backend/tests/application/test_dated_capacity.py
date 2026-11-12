from dataclasses import replace
from datetime import date
from uuid import UUID

import pytest
from app.modules.optimization.application.dated_capacity import (
    CapacityPeriod,
    CapacitySource,
    DatedCapacityOptimizer,
    DatedDemand,
    DatedSupply,
)
from app.modules.optimization.application.resource_assignment import SolverStatus


def uid(value: int) -> UUID:
    return UUID(int=value)


SOURCE = CapacitySource(reference="Planning équipe", revision="1", locator="ligne 2")
PERIOD = CapacityPeriod(start=date(2026, 11, 1), end=date(2026, 11, 3))
DEMAND = DatedDemand(uid(1), "Pose", "compagnons", 2, PERIOD, SOURCE)
SUPPLY = DatedSupply(
    uid(10),
    "Équipe A",
    "compagnons",
    2,
    CapacityPeriod(date(2026, 11, 1), date(2026, 12, 1)),
    SOURCE,
)


def test_successive_work_reuses_capacity_but_overlap_is_a_dated_conflict():
    optimizer = DatedCapacityOptimizer()
    second = replace(DEMAND, id=uid(2), period=CapacityPeriod(PERIOD.end, date(2026, 11, 5)))
    result = optimizer.solve(demands=(DEMAND, second), supplies=(SUPPLY,))
    assert result.status == SolverStatus.OPTIMAL
    assert result.assignments == {uid(1): uid(10), uid(2): uid(10)}
    overlap = optimizer.solve(demands=(DEMAND, replace(second, period=PERIOD)), supplies=(SUPPLY,))
    assert overlap.status == SolverStatus.INFEASIBLE
    assert overlap.assignments == {}
    assert overlap.conflicts[0].period == PERIOD
    assert overlap.conflicts[0].required_units == 4
    assert overlap.conflicts[0].available_units == 2


@pytest.mark.parametrize("field", ["period", "source", "required_units", "resource_type"])
def test_missing_evidence_is_unknown_not_an_assignment(field):
    result = DatedCapacityOptimizer().solve(
        demands=(replace(DEMAND, **{field: None}),), supplies=(SUPPLY,)
    )
    assert result.status == SolverStatus.UNKNOWN
    assert result.assignments == {}
    assert result.unknown_ids == (DEMAND.id,)


def test_compatibility_named_resource_and_whole_period_are_required():
    optimizer = DatedCapacityOptimizer()
    for supply in (
        replace(SUPPLY, resource_type="engin"),
        replace(SUPPLY, period=PERIOD),
        replace(SUPPLY, capacity_units=0),
    ):
        demand = replace(DEMAND, period=CapacityPeriod(PERIOD.start, date(2026, 11, 5)))
        assert (
            optimizer.solve(demands=(demand,), supplies=(supply,)).status == SolverStatus.INFEASIBLE
        )
    named = replace(DEMAND, named_supply_id=uid(20))
    assert optimizer.solve(demands=(named,), supplies=(SUPPLY,)).status == SolverStatus.INFEASIBLE


def test_empty_and_missing_are_distinct_and_invalid_inputs_are_refused():
    optimizer = DatedCapacityOptimizer()
    assert optimizer.solve(demands=None, supplies=()).status == SolverStatus.UNKNOWN
    assert optimizer.solve(demands=(), supplies=()).status == SolverStatus.OPTIMAL
    assert optimizer.solve(demands=(DEMAND,), supplies=()).status == SolverStatus.INFEASIBLE
    with pytest.raises(ValueError):
        CapacityPeriod(PERIOD.end, PERIOD.start)
    with pytest.raises(ValueError):
        optimizer.solve(demands=(DEMAND, DEMAND), supplies=(SUPPLY,))
    with pytest.raises(ValueError):
        replace(DEMAND, required_units=True)


def test_results_are_deterministic_and_supply_identity_cannot_double_capacity():
    optimizer = DatedCapacityOptimizer()
    inputs = dict(demands=(DEMAND,), supplies=(SUPPLY, replace(SUPPLY, id=uid(20))))
    assert optimizer.solve(**inputs) == optimizer.solve(**inputs)
    with pytest.raises(ValueError):
        optimizer.solve(demands=(DEMAND,), supplies=(SUPPLY, SUPPLY))


@pytest.mark.parametrize(
    "field,value",
    [("period", "2026-11-01"), ("source", "planning"), ("named_supply_id", "untyped-id")],
)
def test_untyped_evidence_is_rejected_at_the_boundary(field, value):
    with pytest.raises(ValueError):
        replace(DEMAND, **{field: value})


def test_single_supply_may_share_units_between_overlapping_demands():
    result = DatedCapacityOptimizer().solve(
        demands=(replace(DEMAND, required_units=1), replace(DEMAND, id=uid(2), required_units=1)),
        supplies=(SUPPLY,),
    )
    assert result.status == SolverStatus.OPTIMAL
    assert len(result.assignments) == 2


def test_named_resource_conflict_does_not_invent_a_total_shortage():
    result = DatedCapacityOptimizer().solve(
        demands=(replace(DEMAND, named_supply_id=uid(99)),), supplies=(SUPPLY,)
    )
    assert result.status == SolverStatus.INFEASIBLE
    assert result.conflicts == ()  # Aggregate availability alone cannot explain this refusal.


@pytest.mark.parametrize("limit", [float("inf"), float("nan"), 0, 31])
def test_solver_budget_is_bounded(limit):
    with pytest.raises(ValueError):
        DatedCapacityOptimizer(time_limit_seconds=limit)
