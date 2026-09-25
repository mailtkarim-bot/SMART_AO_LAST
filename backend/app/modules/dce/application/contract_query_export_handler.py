# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.contract_query_export_commands import (
    RequestContractQueryExportCommand,
)
from app.modules.dce.infrastructure.models.contract_query_export import ContractQueryExportRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RequestContractQueryExportHandler(CommandHandler):
    def execute(self, *, session: Session, command: RequestContractQueryExportCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(ContractQueryExportRecord.id).where(ContractQueryExportRecord.tenant_id == tenant_id, ContractQueryExportRecord.id == command.export_id)) is not None:
            raise CommandExecutionError("CONTRACT_QUERY_EXPORT_ID_REUSED")
        session.add(ContractQueryExportRecord(id=command.export_id, tenant_id=tenant_id, case_id=command.case_id, filters_json=command.filters, status="REQUESTED", actor_id=UUID(str(context.actor_id))))
        return HandlerOutcome(result_code="CONTRACT_QUERY_EXPORT_REQUESTED", aggregate_refs=({"aggregate_type": "CONTRACT_QUERY_EXPORT", "aggregate_id": str(command.export_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="CONTRACT_QUERY_EXPORT", aggregate_id=command.export_id, aggregate_revision=1, event_type="CONTRACT_QUERY_EXPORT_REQUESTED", payload={"case_id": str(command.case_id), "status": "REQUESTED"}),))

def contract_query_export_handlers() -> dict[str, RequestContractQueryExportHandler]:
    return {RequestContractQueryExportCommand.command_type: RequestContractQueryExportHandler()}
