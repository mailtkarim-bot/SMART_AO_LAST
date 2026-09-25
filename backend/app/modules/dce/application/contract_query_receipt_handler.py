# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.contract_query_receipt_commands import (
    RecordContractQueryReceiptCommand,
)
from app.modules.dce.infrastructure.models.contract_query_receipt import ContractQueryReceiptRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordContractQueryReceiptHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordContractQueryReceiptCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(ContractQueryReceiptRecord.id).where(ContractQueryReceiptRecord.tenant_id == tenant_id, ContractQueryReceiptRecord.id == command.receipt_id)) is not None:
            raise CommandExecutionError("CONTRACT_QUERY_RECEIPT_ID_REUSED")
        session.add(ContractQueryReceiptRecord(id=command.receipt_id, tenant_id=tenant_id, case_id=command.case_id, filters_json=command.filters, order_key=command.order_key, limit_value=command.limit_value, offset_value=command.offset_value, actor_id=UUID(str(context.actor_id))))
        return HandlerOutcome(result_code="CONTRACT_QUERY_RECEIPT_RECORDED", aggregate_refs=({"aggregate_type": "CONTRACT_QUERY_RECEIPT", "aggregate_id": str(command.receipt_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="CONTRACT_QUERY_RECEIPT", aggregate_id=command.receipt_id, aggregate_revision=1, event_type="CONTRACT_QUERY_RECEIPT_RECORDED", payload={"case_id": str(command.case_id), "limit": command.limit_value, "offset": command.offset_value}),))

def contract_query_receipt_handlers() -> dict[str, RecordContractQueryReceiptHandler]:
    return {RecordContractQueryReceiptCommand.command_type: RecordContractQueryReceiptHandler()}

class ContractQueryReceiptReadService:
    def __init__(self, *, session_factory, policy) -> None:
        self._session_factory = session_factory
        self._policy = policy

    def list_for_case(self, *, actor, case_id, limit=50, offset=0):
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        if not 1 <= limit <= 100 or offset < 0:
            raise ValueError("INVALID_PAGINATION")
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(ContractQueryReceiptRecord).where(ContractQueryReceiptRecord.tenant_id == actor.tenant_id, ContractQueryReceiptRecord.case_id == case_id).order_by(ContractQueryReceiptRecord.created_at.desc()).limit(limit).offset(offset)).all())
