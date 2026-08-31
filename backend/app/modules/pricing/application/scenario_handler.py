"""Transactional handler for pricing scenario creation."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.pricing.application.commands import CreatePricingScenarioCommand
from app.modules.pricing.domain.cost_basis import (
    CostBasisInput,
    CostBasisValidationError,
    calculate_cost_basis,
)
from app.modules.pricing.domain.scenario import calculate_pricing_scenario_amounts
from app.modules.pricing.infrastructure.models import (
    FinancialReportSnapshotRecord,
    PricingScenarioRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.security.context import ActorKind


class PricingScenarioHandler:
    def execute(self, *, session: Session, command, context: CommandContext) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        snapshot = session.scalar(
            sa.select(FinancialReportSnapshotRecord).where(
                FinancialReportSnapshotRecord.tenant_id == context.tenant_id,
                FinancialReportSnapshotRecord.id == command.source_snapshot_id,
                FinancialReportSnapshotRecord.case_id == command.case_id,
                FinancialReportSnapshotRecord.state == "PUBLISHED",
            )
        )
        if snapshot is None:
            raise CommandExecutionError("OFFICIAL_PRICE_NOT_PUBLISHED")
        version = (
            session.scalar(
                sa.select(sa.func.coalesce(sa.func.max(PricingScenarioRecord.version), 0)).where(
                    PricingScenarioRecord.tenant_id == context.tenant_id,
                    PricingScenarioRecord.case_id == command.case_id,
                    PricingScenarioRecord.scenario_key == command.scenario_key,
                )
            )
            + 1
        )
        amounts = calculate_pricing_scenario_amounts(
            sales_total_minor=snapshot.sales_total_minor,
            direct_cost_total_minor=snapshot.direct_cost_total_minor,
            overhead_total_minor=snapshot.overhead_total_minor,
            subcontracting_total_minor=snapshot.subcontracting_total_minor,
            contingency_total_minor=snapshot.contingency_total_minor,
            sales_adjustment_bps=command.sales_adjustment_bps,
            cost_adjustment_bps=command.cost_adjustment_bps,
        )
        try:
            cost_basis = calculate_cost_basis(
                CostBasisInput(
                    sales_total_minor=amounts.sales_total_minor,
                    direct_cost_total_minor=amounts.total_cost_minor,
                    overhead_total_minor=0,
                    subcontracting_total_minor=0,
                    contingency_total_minor=0,
                    penalty_reserve_minor=command.penalty_reserve_minor,
                    retention_reserve_minor=command.retention_reserve_minor,
                    guarantee_reserve_minor=command.guarantee_reserve_minor,
                    floor_margin_rate_bps=command.floor_margin_rate_bps,
                    target_margin_rate_bps=command.target_margin_rate_bps,
                )
            )
        except CostBasisValidationError as error:
            raise CommandExecutionError("INVALID_COST_BASIS") from error
        record = PricingScenarioRecord(
            id=command.scenario_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            source_snapshot_id=snapshot.id,
            scenario_key=command.scenario_key,
            scenario_type=command.scenario_type,
            version=version,
            state="DRAFT",
            assumptions_json=command.assumptions,
            sales_total_minor=cost_basis.sales_total_minor,
            total_cost_minor=cost_basis.total_cost_minor,
            gross_margin_minor=cost_basis.gross_margin_minor,
            gross_margin_rate_bps=cost_basis.gross_margin_rate_bps,
            penalty_reserve_minor=cost_basis.penalty_reserve_minor,
            retention_reserve_minor=cost_basis.retention_reserve_minor,
            guarantee_reserve_minor=cost_basis.guarantee_reserve_minor,
            floor_margin_rate_bps=command.floor_margin_rate_bps,
            target_margin_rate_bps=command.target_margin_rate_bps,
            break_even_sales_minor=cost_basis.break_even_sales_minor,
            floor_sales_minor=cost_basis.floor_sales_minor,
            target_sales_minor=cost_basis.target_sales_minor,
            source_snapshot_revision=snapshot.aggregate_revision,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="PRICING_SCENARIO_CREATED",
            aggregate_refs=(
                {
                    "aggregate_type": "PricingScenario",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": record.version,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PricingScenario",
                    aggregate_id=record.id,
                    aggregate_revision=record.version,
                    event_type="PricingScenarioCreated",
                    payload={
                        "scenario_id": str(record.id),
                        "case_id": str(record.case_id),
                        "version": record.version,
                    },
                ),
            ),
        )


def pricing_scenario_handlers():
    handler = PricingScenarioHandler()
    return {CreatePricingScenarioCommand.command_type: handler}
