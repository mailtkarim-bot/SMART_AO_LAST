# ruff: noqa: E501, I001
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.application.case_interview_commands import RecordCaseInterviewCommand
from app.modules.patron_action.domain.case_interview import build_case_interview
from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord
from app.platform.events.dispatcher import CommandContext, CommandExecutionError, CommandHandler, HandlerOutcome, PendingDomainEvent
from app.platform.security.authorization import AuthorizationPolicyPort, AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification

class RecordCaseInterviewHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordCaseInterviewCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id)) is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(CaseInterviewRecord.id).where(CaseInterviewRecord.tenant_id == tenant_id, CaseInterviewRecord.id == command.interview_id)) is not None:
            raise CommandExecutionError("CASE_INTERVIEW_ID_REUSED")
        try:
            interview = build_case_interview(case_id=command.case_id, held_on=command.held_on, source_locator=command.source_locator, rationale=command.rationale, expires_on=command.expires_on)
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        rex_rows = session.scalars(sa.select(CaseRexRecord).where(CaseRexRecord.tenant_id == tenant_id, CaseRexRecord.case_id == command.case_id).order_by(CaseRexRecord.created_at.asc(), CaseRexRecord.id.asc())).all()
        snapshot = {
            "captured_at": datetime.now(tz=UTC).isoformat(),
            "rex": [
                {
                    "rex_id": str(row.id),
                    "lot_reference": row.lot_reference,
                    "motif": row.motif,
                    "scope": row.scope,
                    "validation": row.validation,
                    "observation": row.observation,
                    "consequence": row.consequence,
                    "follow_up": row.follow_up,
                    "source_locator": row.source_locator,
                }
                for row in rex_rows
            ],
        }
        session.add(CaseInterviewRecord(id=command.interview_id, tenant_id=tenant_id, case_id=command.case_id, held_on=interview.held_on, source_locator=interview.source_locator, rationale=interview.rationale, expires_on=interview.expires_on, snapshot_json=snapshot, actor_id=UUID(str(context.actor_id)), membership_id=UUID(str(context.membership_id)), command_id=command.command_id, idempotency_key=command.idempotency_key, correlation_id=command.correlation_id))
        return HandlerOutcome(result_code="CASE_INTERVIEW_RECORDED", aggregate_refs=({"aggregate_type": "CASE_INTERVIEW", "aggregate_id": str(command.interview_id), "aggregate_revision": 1},), events=(PendingDomainEvent(aggregate_type="CASE_INTERVIEW", aggregate_id=command.interview_id, aggregate_revision=1, event_type="CASE_INTERVIEW_RECORDED", payload={"case_id": str(command.case_id), "expires_on": interview.expires_on.isoformat(), "rex_count": len(rex_rows)}),))

def case_interview_handlers() -> dict[str, CommandHandler]:
    return {RecordCaseInterviewCommand.command_type: RecordCaseInterviewHandler()}

@dataclass(frozen=True, slots=True)
class CaseInterviewProjection:
    record: CaseInterviewRecord
    status: str  # "USABLE" | "EXPIRED"

class CaseInterviewReadService:
    def __init__(self, *, session_factory): self._session_factory = session_factory
    def list_for_case(self, *, actor, case_id, now):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        with self._session_factory() as session:
            if session.scalar(sa.select(CaseRecord.id).where(CaseRecord.tenant_id == actor.tenant_id, CaseRecord.id == case_id)) is None:
                return ()
            rows = tuple(session.scalars(sa.select(CaseInterviewRecord).where(CaseInterviewRecord.tenant_id == actor.tenant_id, CaseInterviewRecord.case_id == case_id).order_by(CaseInterviewRecord.held_on.asc(), CaseInterviewRecord.id.asc())).all())
            today = now.date() if isinstance(now, datetime) else now
            return tuple(CaseInterviewProjection(record=row, status="USABLE" if row.expires_on >= today else "EXPIRED") for row in rows)

class CaseInterviewService:
    def __init__(self, *, dispatcher, session_factory, policy: AuthorizationPolicyPort) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def record_interview(self, *, actor: ActorContext, command: RecordCaseInterviewCommand, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(context=actor, request=AuthorizationRequest(action=Capability.PATRON_ACTION_WRITE, resource=AuthorizationResource(resource_type="CASE_INTERVIEW", resource_id=command.case_id, tenant_id=actor.tenant_id, classification=DataClassification.INTERNAL_OPERATIONAL, case_id=command.case_id), evaluated_at=now))
        if not decision.allowed:
            raise PermissionError(decision.code)
        return self._dispatcher.dispatch(command=command, context=CommandContext(tenant_id=actor.tenant_id, actor_id=actor.actor_id, actor_kind=actor.actor_kind.value, received_at=now, identity_id=actor.identity_id, membership_id=actor.membership_id, session_id=actor.session_id, case_id=command.case_id, correlation_id=actor.correlation_id))

    def list_interviews(self, *, actor: ActorContext, case_id: UUID, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(context=actor, request=AuthorizationRequest(action=Capability.PATRON_ACTION_READ, resource=AuthorizationResource(resource_type="CASE_INTERVIEW", resource_id=case_id, tenant_id=actor.tenant_id, classification=DataClassification.INTERNAL_OPERATIONAL, case_id=case_id), evaluated_at=now))
        if not decision.allowed:
            raise PermissionError(decision.code)
        with self._session_factory() as session:
            rows = tuple(session.scalars(sa.select(CaseInterviewRecord).where(CaseInterviewRecord.tenant_id == actor.tenant_id, CaseInterviewRecord.case_id == case_id).order_by(CaseInterviewRecord.held_on.asc(), CaseInterviewRecord.id.asc())).all())
            today = now.date()
            return tuple(CaseInterviewProjection(record=row, status="USABLE" if row.expires_on >= today else "EXPIRED") for row in rows)
