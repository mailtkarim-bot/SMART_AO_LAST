from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.pricing.application.commands import CreatePricingScenarioCommand
from app.modules.pricing.application.scenario_handler import pricing_scenario_handlers
from app.modules.pricing.application.service import PricingScenarioService
from app.modules.pricing.application.transition_commands import TransitionPricingScenarioCommand
from app.modules.pricing.application.transition_handler import pricing_scenario_transition_handlers
from app.modules.pricing.application.transition_service import PricingScenarioTransitionService
from app.modules.pricing.infrastructure.scenario_reader import SqlAlchemyPricingScenarioReader
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorKind
from app.platform.security.models import PricingScenarioTransitionRecord
from sqlalchemy.orm import Session, sessionmaker

from tests.application.test_financial_report_draft_lines import _seed_draft
from tests.application.test_pricing_scenarios import _declare_base_lines

NOW = datetime(2026, 8, 18, 10, 0, tzinfo=UTC)


@pytest.fixture
def services(session_factory: sessionmaker[Session]):
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            **pricing_scenario_handlers(),
            **pricing_scenario_transition_handlers(),
        },
    )
    policy = AuthorizationPolicy()
    reader = SqlAlchemyPricingScenarioReader(session_factory)
    return (
        PricingScenarioService(
            reader=reader,
            dispatcher=dispatcher,
            policy=policy,
        ),
        PricingScenarioTransitionService(
            reader=reader,
            dispatcher=dispatcher,
            policy=policy,
        ),
    )


def _published_snapshot(session_factory, snapshot_id):
    with session_factory.begin() as session:
        snapshot = session.get(
            __import__(
                "app.platform.security.models", fromlist=["FinancialReportSnapshotRecord"]
            ).FinancialReportSnapshotRecord,
            snapshot_id,
        )
        snapshot.sales_total_minor = 100_000
        snapshot.direct_cost_total_minor = 60_000
        snapshot.overhead_total_minor = 10_000
        snapshot.subcontracting_total_minor = 5_000
        snapshot.contingency_total_minor = 5_000
        snapshot.gross_margin_minor = 20_000
        snapshot.gross_margin_rate_bps = 2000
        snapshot.forecast_cashflow_minor = 15_000
        _declare_base_lines(session, snapshot)
        snapshot.state = "PUBLISHED"
        snapshot.published_at = NOW


def _create(pricing_service, actor, case_id, snapshot_id, key):
    command = CreatePricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        case_id=case_id,
        source_snapshot_id=snapshot_id,
        scenario_key=key,
        scenario_type=key,
        sales_adjustment_bps=0,
        cost_adjustment_bps=0,
        assumptions={},
    )
    pricing_service.execute(actor=actor, command=command, now=NOW)
    return command.scenario_id


def test_pricing_scenario_selection_and_archive_are_append_only_and_idempotent(
    services, session_factory
):
    pricing_service, transition_service = services
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    _published_snapshot(session_factory, snapshot_id)
    scenario_id = _create(pricing_service, actor, case_id, snapshot_id, "BASE")
    select = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        transition_id=uuid4(),
        scenario_id=scenario_id,
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )
    created = transition_service.execute(case_id=case_id, actor=actor, command=select, now=NOW)
    replay = transition_service.execute(case_id=case_id, actor=actor, command=select, now=NOW)
    assert created.result_code == "PRICING_SCENARIO_TRANSITIONED"
    assert replay.replayed is True
    selected = transition_service.list_for_case(actor=actor, case_id=case_id, now=NOW)[0]
    assert selected.state == "SELECTED"
    assert selected.source_snapshot_id == snapshot_id
    assert selected.source_basis_state == "DECLARED_COMPLETE"
    archive = select.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "transition_id": uuid4(),
            "expected_version": 2,
            "target_state": "ARCHIVED",
            "reason_code": "REPLACED",
        }
    )
    transition_service.execute(case_id=case_id, actor=actor, command=archive, now=NOW)
    archived = transition_service.list_for_case(actor=actor, case_id=case_id, now=NOW)[0]
    assert archived.state == "ARCHIVED"
    with session_factory() as session:
        record = session.get(PricingScenarioTransitionRecord, select.transition_id)
        assert record is not None
        with pytest.raises(sa.exc.DatabaseError), session.begin_nested():
            session.execute(
                sa.update(PricingScenarioTransitionRecord)
                .where(PricingScenarioTransitionRecord.id == select.transition_id)
                .values(to_state="SELECTED")
            )


def test_pricing_scenario_transition_requires_current_version_and_patron(services, session_factory):
    pricing_service, transition_service = services
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    _published_snapshot(session_factory, snapshot_id)
    scenario_id = _create(pricing_service, actor, case_id, snapshot_id, "BASE")
    first = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        transition_id=uuid4(),
        scenario_id=scenario_id,
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )
    transition_service.execute(case_id=case_id, actor=actor, command=first, now=NOW)
    stale = first.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "transition_id": uuid4(),
            "expected_version": 1,
            "target_state": "ARCHIVED",
        }
    )
    with pytest.raises(RuntimeError, match="VERSION_CONFLICT"):
        transition_service.execute(case_id=case_id, actor=actor, command=stale, now=NOW)
    collaborator = replace(
        actor,
        actor_id=uuid4(),
        identity_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        transition_service.execute(case_id=case_id, actor=collaborator, command=stale, now=NOW)


def test_pricing_scenario_selection_rejects_another_active_selection(services, session_factory):
    pricing_service, transition_service = services
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    _published_snapshot(session_factory, snapshot_id)
    first_id = _create(pricing_service, actor, case_id, snapshot_id, "BASE")
    second_id = _create(pricing_service, actor, case_id, snapshot_id, "PRUDENT")
    first = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        transition_id=uuid4(),
        scenario_id=first_id,
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )
    second = first.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "transition_id": uuid4(),
            "scenario_id": second_id,
        }
    )
    transition_service.execute(case_id=case_id, actor=actor, command=first, now=NOW)
    with pytest.raises(RuntimeError, match="SCENARIO_ALREADY_SELECTED"):
        transition_service.execute(case_id=case_id, actor=actor, command=second, now=NOW)


def test_two_concurrent_scenario_selections_have_one_winner(
    services, session_factory, database_engine
):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.platform.events.dispatcher import CommandExecutionError

    pricing_service, transition_service = services
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    _published_snapshot(session_factory, snapshot_id)
    ids = [
        _create(pricing_service, actor, case_id, snapshot_id, key) for key in ("BASE", "PRUDENT")
    ]
    started = Barrier(2)
    old_target_locks = Barrier(2)

    def expose_opposite_target_locks(connection, cursor, statement, parameters, context, many):
        # Force the former target-first path to overlap. Ordered Case-wide locking
        # has no target predicate and deliberately never waits at this barrier.
        if "FOR UPDATE" in statement and "pricing_scenarios.id =" in statement:
            old_target_locks.wait(timeout=5)

    def select(scenario_id):
        command = TransitionPricingScenarioCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            transition_id=uuid4(),
            scenario_id=scenario_id,
            expected_version=1,
            target_state="SELECTED",
            reason_code="SYNTHETIC_CONCURRENT_REVIEW",
        )
        started.wait(timeout=5)
        try:
            transition_service.execute(actor=actor, case_id=case_id, command=command, now=NOW)
            return "SUCCEEDED"
        except CommandExecutionError as error:
            return str(error)

    sa.event.listen(database_engine, "after_cursor_execute", expose_opposite_target_locks)
    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(select, ids))
    finally:
        sa.event.remove(database_engine, "after_cursor_execute", expose_opposite_target_locks)
    assert sorted(results) == ["SCENARIO_ALREADY_SELECTED", "SUCCEEDED"]
    rows = transition_service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert sorted(row.state for row in rows) == ["DRAFT", "SELECTED"]
    assert all(row.source_snapshot_revision == rows[0].source_snapshot_revision for row in rows)
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(PricingScenarioTransitionRecord)
                .where(PricingScenarioTransitionRecord.tenant_id == actor.tenant_id)
            )
            == 1
        )
