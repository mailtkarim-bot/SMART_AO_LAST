# ruff: noqa: E501, I001
from __future__ import annotations
from uuid import UUID
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.payment_collection_rejection_review_commands import RecordPaymentCollectionRejectionReviewCommand
from app.modules.pricing.infrastructure.models.payment_collection_rejection_review import PaymentCollectionRejectionReviewRecord
from app.platform.events.dispatcher import CommandContext, CommandExecutionError, CommandHandler, HandlerOutcome, PendingDomainEvent

class RecordPaymentCollectionRejectionReviewHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordPaymentCollectionRejectionReviewCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(PaymentCollectionRejectionReviewRecord.id).where(PaymentCollectionRejectionReviewRecord.tenant_id == tenant_id, PaymentCollectionRejectionReviewRecord.id == command.review_id)) is not None:
            raise CommandExecutionError("PAYMENT_COLLECTION_REJECTION_REVIEW_ID_REUSED")
        session.add(PaymentCollectionRejectionReviewRecord(id=command.review_id, tenant_id=tenant_id, case_id=command.case_id, reviewer_id=UUID(str(context.actor_id)), rejected_count=command.rejected_count, decision=command.decision, rationale=command.rationale))
        return HandlerOutcome(result_code="PAYMENT_COLLECTION_REJECTION_REVIEW_RECORDED", aggregate_refs=({"aggregate_type": "PAYMENT_COLLECTION_REJECTION_REVIEW", "aggregate_id": str(command.review_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="PAYMENT_COLLECTION_REJECTION_REVIEW", aggregate_id=command.review_id, aggregate_revision=1, event_type="PAYMENT_COLLECTION_REJECTION_REVIEW_RECORDED", payload={"case_id": str(command.case_id), "decision": command.decision, "rejected_count": command.rejected_count}),))

def payment_collection_rejection_review_handlers() -> dict[str, RecordPaymentCollectionRejectionReviewHandler]:
    return {RecordPaymentCollectionRejectionReviewCommand.command_type: RecordPaymentCollectionRejectionReviewHandler()}
