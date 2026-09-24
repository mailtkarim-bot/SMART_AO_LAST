from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.application.regulatory_profile_commands import RecordRegulatoryProfileCommand
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.case.infrastructure.models.regulatory_profile import RegulatoryProfileRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification


class RegulatoryProfileService:
    """Authorize and dispatch a sourced profile without evaluating legal rules."""

    def __init__(self, *, dispatcher, policy: AuthorizationPolicyPort) -> None:
        self._dispatcher = dispatcher
        self._policy = policy

    def execute(
        self,
        *,
        actor: ActorContext,
        command: RecordRegulatoryProfileCommand,
        now: datetime,
    ):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.REGULATORY_PROFILE_WRITE,
                resource=AuthorizationResource(
                    resource_type="REGULATORY_PROFILE",
                    resource_id=command.profile_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=command.case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                received_at=now,
                identity_id=actor.identity_id,
                membership_id=actor.membership_id,
                session_id=actor.session_id,
                case_id=command.case_id,
                correlation_id=actor.correlation_id,
            ),
        )


class RegulatoryProfileReadService:
    """Read Patron-owned profiles without evaluating their legal meaning."""

    def __init__(self, *, session_factory: sessionmaker[Session], policy: AuthorizationPolicyPort):
        self._session_factory = session_factory
        self._policy = policy

    def list_for_case(self, *, actor: ActorContext, case_id: UUID, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.REGULATORY_PROFILE_READ,
                resource=AuthorizationResource(
                    resource_type="REGULATORY_PROFILE",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
        with self._session_factory() as session:
            return tuple(
                session.scalars(
                    sa.select(RegulatoryProfileRecord)
                    .where(
                        RegulatoryProfileRecord.tenant_id == actor.tenant_id,
                        RegulatoryProfileRecord.case_id == case_id,
                    )
                    .order_by(RegulatoryProfileRecord.profile_version.desc())
                ).all()
            )


class RecordRegulatoryProfileHandler(CommandHandler):
    """Persist one profile version only after tenant-scoped Case lookup."""

    def execute(
        self,
        *,
        session: Session,
        command: RecordRegulatoryProfileCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == command.case_id,
            )
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        existing = session.scalar(
            sa.select(RegulatoryProfileRecord).where(
                RegulatoryProfileRecord.tenant_id == tenant_id,
                RegulatoryProfileRecord.id == command.profile_id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("REGULATORY_PROFILE_ID_REUSED")
        record = RegulatoryProfileRecord(
            id=command.profile_id,
            tenant_id=tenant_id,
            case_id=case.id,
            profile_version=command.profile_version,
            status=command.status,
            facts_json=command.facts,
            source_refs_json=list(command.source_refs),
            effective_from=command.effective_from,
            effective_until=command.effective_until,
            created_by_actor_id=UUID(str(context.actor_id)),
        )
        session.add(record)
        return HandlerOutcome(
            result_code="REGULATORY_PROFILE_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "REGULATORY_PROFILE",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": record.profile_version,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="REGULATORY_PROFILE",
                    aggregate_id=record.id,
                    aggregate_revision=record.profile_version,
                    event_type="REGULATORY_PROFILE_RECORDED",
                    payload={
                        "case_id": str(record.case_id),
                        "profile_version": record.profile_version,
                        "status": record.status,
                    },
                ),
            ),
        )


def regulatory_profile_handlers() -> dict[str, RecordRegulatoryProfileHandler]:
    return {RecordRegulatoryProfileCommand.command_type: RecordRegulatoryProfileHandler()}
