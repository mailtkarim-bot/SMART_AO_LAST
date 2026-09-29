# ruff: noqa: E501, I001
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.application.post_reception_obligation_commands import (
    RecordPostReceptionObligationCommand,
)
from app.modules.pricing.domain.post_reception_obligation import (
    PostReceptionObligationType,
    build_post_reception_obligation,
)
from app.modules.pricing.infrastructure.models.post_reception_obligation import (
    PostReceptionObligationRecord,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordPostReceptionObligationHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordPostReceptionObligationCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        case_exists = session.scalar(
            sa.select(CaseRecord.id).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == command.case_id,
            )
        )
        if case_exists is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(PostReceptionObligationRecord.id).where(
                    PostReceptionObligationRecord.tenant_id == tenant_id,
                    PostReceptionObligationRecord.id == command.obligation_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("POST_RECEPTION_OBLIGATION_ID_REUSED")
        if command.obligation_type == "RESERVES_LIFTING":
            source = (
                session.scalar(
                    sa.select(ContractExecutionEvidenceRecord).where(
                        ContractExecutionEvidenceRecord.tenant_id == tenant_id,
                        ContractExecutionEvidenceRecord.case_id == command.case_id,
                        ContractExecutionEvidenceRecord.id == command.origin_reception_act_id,
                        ContractExecutionEvidenceRecord.act_kind == "WORK_RECEPTION",
                    )
                )
                if command.origin_reception_act_id is not None
                else None
            )
            if source is None:
                raise CommandExecutionError("POST_RECEPTION_RECEIPT_NOT_FOUND_OR_FORBIDDEN")
            if source.reception_outcome not in {"WITH_RESERVATIONS", "UNDER_RESERVATIONS"}:
                raise CommandExecutionError("POST_RECEPTION_RECEIPT_NOT_ELIGIBLE")
        elif command.origin_reception_act_id is not None:
            raise CommandExecutionError("POST_RECEPTION_RECEIPT_SOURCE_NOT_APPLICABLE")
        try:
            obligation = build_post_reception_obligation(
                case_id=command.case_id,
                origin_reception_act_id=command.origin_reception_act_id,
                obligation_type=PostReceptionObligationType(command.obligation_type),
                summary=command.summary,
                source_refs=command.source_refs,
                due_date=command.due_date,
                resource_note=command.resource_note,
                cost_estimate_note=command.cost_estimate_note,
                fulfillment_proof_refs=command.fulfillment_proof_refs,
                sanction_ref=command.sanction_ref,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        session.add(
            PostReceptionObligationRecord(
                id=command.obligation_id,
                tenant_id=tenant_id,
                case_id=obligation.case_id,
                origin_reception_act_id=obligation.origin_reception_act_id,
                obligation_type=obligation.obligation_type.value,
                summary=obligation.summary,
                source_refs_json=list(obligation.source_refs),
                due_date=obligation.due_date,
                resource_note=obligation.resource_note,
                cost_estimate_note=obligation.cost_estimate_note,
                fulfillment_proof_refs_json=list(obligation.fulfillment_proof_refs),
                sanction_ref=obligation.sanction_ref,
                status=obligation.status,
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="POST_RECEPTION_OBLIGATION_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "POST_RECEPTION_OBLIGATION",
                    "aggregate_id": str(command.obligation_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="POST_RECEPTION_OBLIGATION",
                    aggregate_id=command.obligation_id,
                    aggregate_revision=1,
                    event_type="POST_RECEPTION_OBLIGATION_RECORDED",
                    payload={
                        "case_id": str(command.case_id),
                        "obligation_type": obligation.obligation_type.value,
                        "status": obligation.status,
                    },
                ),
            ),
        )


def post_reception_obligation_handlers() -> dict[str, RecordPostReceptionObligationHandler]:
    return {
        RecordPostReceptionObligationCommand.command_type: RecordPostReceptionObligationHandler()
    }
