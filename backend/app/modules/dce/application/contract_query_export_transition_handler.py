# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.application.contract_query_export_transition_commands import (
    TransitionContractQueryExportCommand,
)
from app.modules.dce.infrastructure.models.contract_query_export import ContractQueryExportRecord
from app.modules.dce.infrastructure.models.contract_query_export_transition import (
    ContractQueryExportTransitionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class TransitionContractQueryExportHandler(CommandHandler):
    def execute(self, *, session: Session, command: TransitionContractQueryExportCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        export = session.scalar(sa.select(ContractQueryExportRecord).where(ContractQueryExportRecord.tenant_id == tenant_id, ContractQueryExportRecord.id == command.export_id))
        if export is None or export.status != command.from_status:
            raise CommandExecutionError("CONTRACT_QUERY_EXPORT_NOT_FOUND_OR_STALE")
        if command.to_status == "READY" and not command.local_proof_ref:
            raise CommandExecutionError("LOCAL_EXPORT_PROOF_REQUIRED")
        session.add(ContractQueryExportTransitionRecord(id=command.transition_id, tenant_id=tenant_id, export_id=command.export_id, from_status=command.from_status, to_status=command.to_status, local_proof_ref=command.local_proof_ref, actor_id=UUID(str(context.actor_id))))
        export.status = command.to_status
        return HandlerOutcome(result_code="CONTRACT_QUERY_EXPORT_TRANSITIONED", aggregate_refs=({"aggregate_type": "CONTRACT_QUERY_EXPORT", "aggregate_id": str(command.export_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="CONTRACT_QUERY_EXPORT", aggregate_id=command.export_id, aggregate_revision=1, event_type="CONTRACT_QUERY_EXPORT_TRANSITIONED", payload={"from_status": command.from_status, "to_status": command.to_status}),))

def contract_query_export_transition_handlers() -> dict[str, TransitionContractQueryExportHandler]:
    return {TransitionContractQueryExportCommand.command_type: TransitionContractQueryExportHandler()}

class ContractQueryExportAuditReadService:
    def __init__(self, *, session_factory, policy) -> None:
        self._session_factory, self._policy = session_factory, policy

    def get_for_case(self, *, actor, case_id, export_id):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            export = session.scalar(sa.select(ContractQueryExportRecord).where(ContractQueryExportRecord.tenant_id == actor.tenant_id, ContractQueryExportRecord.case_id == case_id, ContractQueryExportRecord.id == export_id))
            if export is None:
                return None
            transitions = tuple(session.scalars(sa.select(ContractQueryExportTransitionRecord).where(ContractQueryExportTransitionRecord.tenant_id == actor.tenant_id, ContractQueryExportTransitionRecord.export_id == export_id).order_by(ContractQueryExportTransitionRecord.created_at.asc())).all())
            return export, transitions
