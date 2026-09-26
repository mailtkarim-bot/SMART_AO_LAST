# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.application.human_resumption_commands import RecordHumanResumptionCommand
from app.modules.dce.infrastructure.models.contract_query_export import ContractQueryExportRecord
from app.modules.dce.infrastructure.models.human_resumption_act import HumanResumptionActRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordHumanResumptionHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordHumanResumptionCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(ContractQueryExportRecord.id).where(ContractQueryExportRecord.tenant_id == tenant_id, ContractQueryExportRecord.id == command.export_id)) is None:
            raise CommandExecutionError("CONTRACT_QUERY_EXPORT_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(HumanResumptionActRecord.id).where(HumanResumptionActRecord.tenant_id == tenant_id, HumanResumptionActRecord.id == command.act_id)) is not None:
            raise CommandExecutionError("HUMAN_RESUMPTION_ID_REUSED")
        session.add(HumanResumptionActRecord(id=command.act_id, tenant_id=tenant_id, export_id=command.export_id, actor_id=UUID(str(context.actor_id)), state=command.state, rationale=command.rationale))
        return HandlerOutcome(result_code="HUMAN_RESUMPTION_RECORDED", aggregate_refs=({"aggregate_type": "HUMAN_RESUMPTION", "aggregate_id": str(command.act_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="HUMAN_RESUMPTION", aggregate_id=command.act_id, aggregate_revision=1, event_type="HUMAN_RESUMPTION_RECORDED", payload={"export_id": str(command.export_id), "state": command.state}),))

def human_resumption_handlers() -> dict[str, RecordHumanResumptionHandler]:
    return {RecordHumanResumptionCommand.command_type: RecordHumanResumptionHandler()}
