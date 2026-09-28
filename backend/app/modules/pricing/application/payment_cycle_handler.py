# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.payment_cycle_commands import (
    QualifyPaymentPostReceptionCycleCommand,
    RecordPaymentPostReceptionCycleCommand,
)
from app.modules.pricing.domain.payment_post_reception_cycle import build_payment_cost_qualification
from app.modules.pricing.domain.payment_unknown_audit import build_payment_unknown_audit
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

def payment_cycle_handlers() -> dict[str, CommandHandler]:
    return {RecordPaymentPostReceptionCycleCommand.command_type: RecordPaymentPostReceptionCycleHandler(), QualifyPaymentPostReceptionCycleCommand.command_type: QualifyPaymentPostReceptionCycleHandler()}

class QualifyPaymentPostReceptionCycleHandler(CommandHandler):
    def execute(self, *, session: Session, command: QualifyPaymentPostReceptionCycleCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        record = session.scalar(sa.select(PaymentPostReceptionCycleRecord).where(PaymentPostReceptionCycleRecord.tenant_id == tenant_id, PaymentPostReceptionCycleRecord.id == command.cycle_id))
        if record is None or record.case_id != command.case_id:
            raise CommandExecutionError("PAYMENT_CYCLE_NOT_FOUND")
        try:
            qualification = build_payment_cost_qualification(cash_assumption=command.cash_assumption, post_reception_cost_note=command.post_reception_cost_note)
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        record.cash_assumption = qualification.cash_assumption
        record.post_reception_cost_note = qualification.post_reception_cost_note
        return HandlerOutcome(result_code="PAYMENT_CYCLE_QUALIFIED", aggregate_refs=({"aggregate_type": "PAYMENT_POST_RECEPTION_CYCLE", "aggregate_id": str(command.cycle_id), "aggregate_revision": 2},), events=(PendingDomainEvent(aggregate_type="PAYMENT_POST_RECEPTION_CYCLE", aggregate_id=command.cycle_id, aggregate_revision=2, event_type="PAYMENT_CYCLE_QUALIFIED", payload={"case_id": str(command.case_id), "cash_assumption": qualification.cash_assumption, "post_reception_cost_note": qualification.post_reception_cost_note}),))

class PaymentCycleWriteService:
    def __init__(self, *, dispatcher, policy=None): self._dispatcher, self._policy = dispatcher, policy
    def execute(self, *, actor, command, now):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        from app.platform.events.dispatcher import CommandContext
        return self._dispatcher.dispatch(command=command, context=CommandContext(tenant_id=actor.tenant_id, actor_id=actor.actor_id, actor_kind=actor.actor_kind.value, received_at=now, identity_id=actor.identity_id, membership_id=actor.membership_id, session_id=actor.session_id, case_id=command.case_id, correlation_id=actor.correlation_id))

class PaymentCycleReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def list_for_case(self, *, actor, case_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(PaymentPostReceptionCycleRecord).where(PaymentPostReceptionCycleRecord.tenant_id == actor.tenant_id, PaymentPostReceptionCycleRecord.case_id == case_id).order_by(PaymentPostReceptionCycleRecord.created_at.asc())).all())
    def audit_for_case(self, *, actor, case_id):
        rows = self.list_for_case(actor=actor, case_id=case_id)
        return build_payment_unknown_audit({"status": row.status, "source_refs": tuple(row.source_refs_json), "cycle_id": row.id, "trigger_event": row.trigger_event} for row in rows)
