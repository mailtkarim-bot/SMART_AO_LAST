from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.modules.pricing.application.commands import CreatePricingScenarioCommand
from app.modules.pricing.application.scenario_handler import pricing_scenario_handlers
from app.modules.pricing.application.service import PricingScenarioService
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    PricingScenarioRecord,
)
from app.modules.pricing.infrastructure.scenario_reader import SqlAlchemyPricingScenarioReader
from app.modules.pricing.public.declared_margin import BASE_MARGIN_CATEGORIES
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.models import FinancialReportSnapshotRecord
from sqlalchemy.orm import Session, sessionmaker

from tests.application.test_financial_report_draft_lines import _seed_draft

NOW = datetime(2026, 8, 18, 12, 0, tzinfo=UTC)


def _declare_base_lines(session, snapshot):
    session.add_all(
        [
            FinancialReportLineRecord(
                id=uuid4(),
                tenant_id=snapshot.tenant_id,
                snapshot_id=snapshot.id,
                category=category,
                label="Synthetic " + category,
                quantity_decimal="1",
                unit="forfait",
                amount_minor=getattr(snapshot, f"{category.lower()}_total_minor"),
            )
            for category in BASE_MARGIN_CATEGORIES
        ]
    )
    session.flush()


@pytest.fixture
def pricing_service(session_factory: sessionmaker[Session]) -> PricingScenarioService:
    return PricingScenarioService(
        reader=SqlAlchemyPricingScenarioReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=pricing_scenario_handlers(),
        ),
        policy=AuthorizationPolicy(),
    )


def test_pricing_scenario_is_deterministic_idempotent_and_private(
    pricing_service: PricingScenarioService, session_factory: sessionmaker[Session]
) -> None:
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    with session_factory.begin() as session:
        snapshot = session.get(FinancialReportSnapshotRecord, snapshot_id)
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

    command = CreatePricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        case_id=case_id,
        source_snapshot_id=snapshot_id,
        scenario_key="PRUDENT",
        scenario_type="PRUDENT",
        sales_adjustment_bps=0,
        cost_adjustment_bps=800,
        assumptions={"supplier_buffer_bps": 800},
    )
    created = pricing_service.execute(actor=actor, command=command, now=NOW)
    replay = pricing_service.execute(actor=actor, command=command, now=NOW)
    assert created.result_code == "PRICING_SCENARIO_CREATED"
    assert replay.replayed is True
    projection = pricing_service.list_for_case(actor=actor, case_id=case_id, now=NOW)[0]
    assert projection.sales_total_minor == 100_000
    assert projection.total_cost_minor == 86_400
    assert projection.gross_margin_minor == 13_600
    assert projection.gross_margin_rate_bps == 1360
    assert "supplier_buffer_bps" in projection.assumptions
    assert projection.source_snapshot_id == snapshot_id
    assert projection.source_snapshot_revision == 0
    assert projection.source_basis_state == "DECLARED_COMPLETE"
    assert projection.source_basis_reason is None
    assert projection.currency_code == "EUR"


def test_pricing_scenario_requires_published_snapshot(
    pricing_service: PricingScenarioService, session_factory: sessionmaker[Session]
) -> None:
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    with pytest.raises(CommandExecutionError, match="OFFICIAL_PRICE_NOT_PUBLISHED"):
        pricing_service.execute(
            actor=actor,
            command=CreatePricingScenarioCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
                scenario_id=uuid4(),
                case_id=case_id,
                source_snapshot_id=snapshot_id,
                scenario_key="BASE",
                scenario_type="BASE",
                sales_adjustment_bps=0,
                cost_adjustment_bps=0,
                assumptions={},
            ),
            now=NOW,
        )


@pytest.mark.parametrize("sales", [0, 100_000])
def test_pricing_scenario_refuses_undeclared_published_base(
    pricing_service, session_factory, sales
):
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    with session_factory.begin() as session:
        snapshot = session.get(FinancialReportSnapshotRecord, snapshot_id)
        snapshot.state = "PUBLISHED"
        snapshot.published_at = NOW
        snapshot.sales_total_minor = sales
    command = CreatePricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        case_id=case_id,
        source_snapshot_id=snapshot_id,
        scenario_key="BASE",
        scenario_type="BASE",
        sales_adjustment_bps=0,
        cost_adjustment_bps=0,
        assumptions={},
    )
    with pytest.raises(CommandExecutionError, match="SCENARIO_SOURCE_UNKNOWN"):
        pricing_service.execute(actor=actor, command=command, now=NOW)


@pytest.mark.parametrize(
    "kind,error",
    [
        ("mismatch", "SCENARIO_SOURCE_UNKNOWN"),
        ("zero", "SCENARIO_SOURCE_UNKNOWN"),
        ("rounded_zero", "SCENARIO_RATE_UNKNOWN"),
    ],
)
def test_pricing_refuses_discordant_or_undefined_declared_source(
    pricing_service, session_factory, kind, error
):
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    with session_factory.begin() as session:
        snapshot = session.get(FinancialReportSnapshotRecord, snapshot_id)
        snapshot.sales_total_minor = 0 if kind == "zero" else 1
        _declare_base_lines(session, snapshot)
        if kind == "mismatch":
            snapshot.overhead_total_minor = 1
        snapshot.state = "PUBLISHED"
        snapshot.published_at = NOW
    command = CreatePricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        case_id=case_id,
        source_snapshot_id=snapshot_id,
        scenario_key="BASE",
        scenario_type="BASE",
        sales_adjustment_bps=-5000 if kind == "rounded_zero" else 0,
        cost_adjustment_bps=0,
        assumptions={},
    )
    for _ in range(2):
        with pytest.raises(CommandExecutionError, match=error):
            pricing_service.execute(actor=actor, command=command, now=NOW)
    with session_factory() as session:
        assert session.get(PricingScenarioRecord, command.scenario_id) is None


@pytest.mark.parametrize(
    "kind,reason",
    [
        ("missing", "MISSING_BASE_CATEGORY"),
        ("revision", "SOURCE_REVISION_MISMATCH"),
        ("wrong_case", "SOURCE_NOT_RESOLVED"),
        ("zero", "ZERO_SALES"),
        ("scenario_zero", "SCENARIO_RATE_UNKNOWN"),
    ],
)
def test_legacy_scenario_projection_is_unknown_without_mutation(
    pricing_service, session_factory, kind, reason
):
    actor, case_id, snapshot_id, _ = _seed_draft(session_factory)
    scenario_id = uuid4()
    if kind == "wrong_case":
        case_id = uuid4()
    with session_factory.begin() as session:
        snapshot = session.get(FinancialReportSnapshotRecord, snapshot_id)
        snapshot.sales_total_minor = 0 if kind == "zero" else 100
        if kind != "missing":
            _declare_base_lines(session, snapshot)
        snapshot.state = "PUBLISHED"
        snapshot.published_at = NOW
        session.add(
            PricingScenarioRecord(
                id=scenario_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                source_snapshot_id=snapshot_id,
                source_snapshot_revision=7 if kind == "revision" else 0,
                scenario_key="HISTORY",
                scenario_type="BASE",
                version=1,
                state="DRAFT",
                assumptions_json={},
                sales_total_minor=0 if kind == "scenario_zero" else 100,
                total_cost_minor=0,
                gross_margin_minor=100,
                gross_margin_rate_bps=10000,
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
    projection = pricing_service.list_for_case(actor=actor, case_id=case_id, now=NOW)[0]
    assert projection.source_basis_state == "UNKNOWN" and projection.source_basis_reason == reason
    assert projection.source_snapshot_id == (
        None if kind in {"wrong_case", "revision"} else snapshot_id
    )
    if kind in {"wrong_case", "revision"}:
        assert projection.currency_code is None
    with session_factory() as session:
        stored = session.get(PricingScenarioRecord, scenario_id)
        assert stored.version == 1 and stored.state == "DRAFT" and stored.gross_margin_minor == 100
