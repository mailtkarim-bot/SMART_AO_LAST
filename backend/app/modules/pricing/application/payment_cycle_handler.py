# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.payment_cycle_commands import (
    RecordPaymentPostReceptionCycleCommand,
)
from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordPaymentPostReceptionCycleHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordPaymentPostReceptionCycleCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(PaymentPostReceptionCycleRecord.id).where(PaymentPostReceptionCycleRecord.tenant_id == tenant_id, PaymentPostReceptionCycleRecord.id == command.cycle_id)) is not None:
            raise CommandExecutionError("PAYMENT_CYCLE_ID_REUSED")
        session.add(PaymentPostReceptionCycleRecord(id=command.cycle_id, tenant_id=tenant_id, case_id=command.case_id, source_refs_json=list(command.source_refs), trigger_event=command.trigger_event, status=command.status, cash_assumption=command.cash_assumption, post_reception_cost_note=command.post_reception_cost_note, actor_id=UUID(str(context.actor_id))))
        return HandlerOutcome(result_code="PAYMENT_CYCLE_RECORDED", aggregate_refs=({"aggregate_type": "PAYMENT_POST_RECEPTION_CYCLE", "aggregate_id": str(command.cycle_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="PAYMENT_POST_RECEPTION_CYCLE", aggregate_id=command.cycle_id, aggregate_revision=1, event_type="PAYMENT_CYCLE_RECORDED", payload={"case_id": str(command.case_id), "status": command.status}),))

def payment_cycle_handlers() -> dict[str, RecordPaymentPostReceptionCycleHandler]:
    return {RecordPaymentPostReceptionCycleCommand.command_type: RecordPaymentPostReceptionCycleHandler()}
