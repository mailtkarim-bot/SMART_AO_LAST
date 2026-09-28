# ruff: noqa: E501, I001
from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.payment_unknown_audit_owner_act_commands import RecordPaymentUnknownAuditOwnerActCommand
from app.modules.pricing.infrastructure.models.payment_unknown_audit_owner_act import PaymentUnknownAuditOwnerActRecord
from app.platform.events.dispatcher import CommandContext, CommandExecutionError, CommandHandler, HandlerOutcome, PendingDomainEvent

class RecordPaymentUnknownAuditOwnerActHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordPaymentUnknownAuditOwnerActCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(PaymentUnknownAuditOwnerActRecord.id).where(PaymentUnknownAuditOwnerActRecord.tenant_id == tenant_id, PaymentUnknownAuditOwnerActRecord.id == command.owner_act_id)) is not None:
            raise CommandExecutionError("PAYMENT_UNKNOWN_AUDIT_OWNER_ACT_ID_REUSED")
        session.add(PaymentUnknownAuditOwnerActRecord(id=command.owner_act_id, tenant_id=tenant_id, case_id=command.case_id, owner_id=UUID(str(context.actor_id)), approved=command.approved, rationale=command.rationale))
        return HandlerOutcome(result_code="PAYMENT_UNKNOWN_AUDIT_OWNER_ACT_RECORDED", aggregate_refs=({"aggregate_type": "PAYMENT_UNKNOWN_AUDIT_OWNER_ACT", "aggregate_id": str(command.owner_act_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="PAYMENT_UNKNOWN_AUDIT_OWNER_ACT", aggregate_id=command.owner_act_id, aggregate_revision=1, event_type="PAYMENT_UNKNOWN_AUDIT_OWNER_ACT_RECORDED", payload={"case_id": str(command.case_id), "approved": command.approved}),))

def payment_unknown_audit_owner_act_handlers() -> dict[str, RecordPaymentUnknownAuditOwnerActHandler]:
    return {RecordPaymentUnknownAuditOwnerActCommand.command_type: RecordPaymentUnknownAuditOwnerActHandler()}
