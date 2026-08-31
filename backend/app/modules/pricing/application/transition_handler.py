"""Transactional handlers for pricing scenario state transitions."""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.pricing.application.transition_commands import (
    ArchivePricingScenarioCommand,
    SelectPricingScenarioCommand,
    TransitionPricingScenarioCommand,
)
from app.modules.pricing.infrastructure.models import (
    PricingScenarioRecord,
    PricingScenarioTransitionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    HandlerOutcome,
    PendingDomainEvent,
)


class TransitionPricingScenarioHandler:
    def execute(self, *, session: Session, command, context: CommandContext) -> HandlerOutcome:
        scenario = session.scalar(
            sa.select(PricingScenarioRecord)
            .where(
                PricingScenarioRecord.tenant_id == context.tenant_id,
                PricingScenarioRecord.id == command.scenario_id,
            )
            .with_for_update()
        )
        if scenario is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        latest = session.scalar(
            sa.select(PricingScenarioTransitionRecord)
            .where(
                PricingScenarioTransitionRecord.tenant_id == context.tenant_id,
                PricingScenarioTransitionRecord.scenario_id == scenario.id,
            )
            .order_by(PricingScenarioTransitionRecord.version.desc())
            .limit(1)
        )
        current_state = latest.to_state if latest is not None else scenario.state
        current_version = latest.version if latest is not None else scenario.version
        if current_version != command.expected_version:
            raise CommandExecutionError("VERSION_CONFLICT")
        if current_state == "ARCHIVED":
            raise CommandExecutionError("SCENARIO_ALREADY_ARCHIVED")
        if command.target_state == current_state:
            raise CommandExecutionError("INVALID_STATE_TRANSITION")
        if command.target_state == "SELECTED":
            siblings = session.scalars(
                sa.select(PricingScenarioRecord)
                .where(
                    PricingScenarioRecord.tenant_id == context.tenant_id,
                    PricingScenarioRecord.case_id == scenario.case_id,
                    PricingScenarioRecord.id != scenario.id,
                )
                .with_for_update()
            ).all()
            for sibling in siblings:
                sibling_latest = session.scalar(
                    sa.select(PricingScenarioTransitionRecord)
                    .where(
                        PricingScenarioTransitionRecord.tenant_id == context.tenant_id,
                        PricingScenarioTransitionRecord.scenario_id == sibling.id,
                    )
                    .order_by(PricingScenarioTransitionRecord.version.desc())
                    .limit(1)
                )
                sibling_state = (
                    sibling_latest.to_state if sibling_latest is not None else sibling.state
                )
                if sibling_state == "SELECTED":
                    raise CommandExecutionError("SCENARIO_ALREADY_SELECTED")
        transition = PricingScenarioTransitionRecord(
            id=command.transition_id,
            tenant_id=context.tenant_id,
            scenario_id=scenario.id,
            from_state=current_state,
            to_state=command.target_state,
            reason_code=command.reason_code,
            version=current_version + 1,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(transition)
        return HandlerOutcome(
            result_code="PRICING_SCENARIO_TRANSITIONED",
            aggregate_refs=(
                {
                    "aggregate_type": "PricingScenario",
                    "aggregate_id": str(scenario.id),
                    "aggregate_revision": transition.version,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="PricingScenario",
                    aggregate_id=scenario.id,
                    aggregate_revision=transition.version,
                    event_type="PricingScenarioTransitioned",
                    payload={
                        "scenario_id": str(scenario.id),
                        "from_state": current_state,
                        "to_state": command.target_state,
                        "version": transition.version,
                    },
                ),
            ),
        )


def pricing_scenario_transition_handlers():
    handler = TransitionPricingScenarioHandler()
    return {
        TransitionPricingScenarioCommand.command_type: handler,
        SelectPricingScenarioCommand.command_type: handler,
        ArchivePricingScenarioCommand.command_type: handler,
    }
