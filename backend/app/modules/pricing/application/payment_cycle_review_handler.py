# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.pricing.application.payment_cycle_review_commands import (
    RecordPaymentCycleReviewCommand,
)
from app.modules.pricing.infrastructure.models.payment_cycle_review import PaymentCycleReviewRecord
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


class RecordPaymentCycleReviewHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordPaymentCycleReviewCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(PaymentPostReceptionCycleRecord.id).where(PaymentPostReceptionCycleRecord.tenant_id == tenant_id, PaymentPostReceptionCycleRecord.id == command.cycle_id)) is None:
            raise CommandExecutionError("PAYMENT_CYCLE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(PaymentCycleReviewRecord.id).where(PaymentCycleReviewRecord.tenant_id == tenant_id, PaymentCycleReviewRecord.id == command.review_id)) is not None:
            raise CommandExecutionError("PAYMENT_REVIEW_ID_REUSED")
        session.add(PaymentCycleReviewRecord(id=command.review_id, tenant_id=tenant_id, cycle_id=command.cycle_id, reviewer_id=UUID(str(context.actor_id)), decision=command.decision, rationale=command.rationale))
        return HandlerOutcome(result_code="PAYMENT_CYCLE_REVIEW_RECORDED", aggregate_refs=({"aggregate_type": "PAYMENT_CYCLE_REVIEW", "aggregate_id": str(command.review_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="PAYMENT_CYCLE_REVIEW", aggregate_id=command.review_id, aggregate_revision=1, event_type="PAYMENT_CYCLE_REVIEW_RECORDED", payload={"cycle_id": str(command.cycle_id), "decision": command.decision}),))

def payment_cycle_review_handlers() -> dict[str, RecordPaymentCycleReviewHandler]:
    return {RecordPaymentCycleReviewCommand.command_type: RecordPaymentCycleReviewHandler()}
