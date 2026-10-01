"""Publish, read and adopt immutable, tenant-owned business-method profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.business_method_profile_adoption import (
    CaseBusinessMethodProfileAdoptionRecord,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.enterprise.application.business_method_profile_commands import (
    AdoptBusinessMethodProfileCommand,
    PublishBusinessMethodProfileCommand,
)
from app.modules.enterprise.domain.business_method_profile import profile_content_hash
from app.modules.enterprise.infrastructure.models.business_method_profile import (
    EnterpriseBusinessMethodProfileVersionRecord,
)
from app.modules.enterprise.infrastructure.models.enterprise import EnterpriseCompanyRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
    CommandHandler,
    DispatchResult,
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


@dataclass(frozen=True, slots=True)
class BusinessMethodProfileVersionProjection:
    profile_version_id: UUID
    version: int
    schema_version: int
    profile: dict[str, Any]
    content_sha256: str


@dataclass(frozen=True, slots=True)
class BusinessMethodProfileAdoptionProjection:
    adoption_id: UUID
    case_id: UUID
    adoption_revision: int
    profile_version_id: UUID
    profile_version: int
    profile_content_sha256: str


class BusinessMethodProfileService:
    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def publish(
        self,
        *,
        actor: ActorContext,
        command: PublishBusinessMethodProfileCommand,
        now,
    ) -> DispatchResult:
        self._authorize_company(actor=actor, company_id=command.company_id, now=now, write=True)
        return self._dispatcher.dispatch(
            command=command, context=self._context(actor=actor, now=now)
        )

    def adopt(
        self,
        *,
        actor: ActorContext,
        command: AdoptBusinessMethodProfileCommand,
        now,
    ) -> DispatchResult:
        self._authorize_case(actor=actor, case_id=command.case_id, now=now, write=True)
        return self._dispatcher.dispatch(
            command=command,
            context=self._context(actor=actor, now=now, case_id=command.case_id),
        )

    def versions(
        self, *, actor: ActorContext, company_id: UUID, now
    ) -> tuple[BusinessMethodProfileVersionProjection, ...]:
        self._authorize_company(actor=actor, company_id=company_id, now=now, write=False)
        with self._session_factory() as session:
            company = session.scalar(
                sa.select(EnterpriseCompanyRecord.id).where(
                    EnterpriseCompanyRecord.tenant_id == actor.tenant_id,
                    EnterpriseCompanyRecord.id == company_id,
                )
            )
            if company is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            rows = session.scalars(
                sa.select(EnterpriseBusinessMethodProfileVersionRecord)
                .where(
                    EnterpriseBusinessMethodProfileVersionRecord.tenant_id == actor.tenant_id,
                    EnterpriseBusinessMethodProfileVersionRecord.company_id == company_id,
                )
                .order_by(EnterpriseBusinessMethodProfileVersionRecord.version_number)
            ).all()
        return tuple(
            BusinessMethodProfileVersionProjection(
                profile_version_id=row.id,
                version=row.version_number,
                schema_version=row.schema_version,
                profile=row.profile_json,
                content_sha256=row.content_sha256,
            )
            for row in rows
        )

    def current_adoption(
        self, *, actor: ActorContext, case_id: UUID, now
    ) -> BusinessMethodProfileAdoptionProjection | None:
        self._authorize_case(actor=actor, case_id=case_id, now=now, write=False)
        with self._session_factory() as session:
            case_exists = session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == actor.tenant_id,
                    CaseRecord.id == case_id,
                )
            )
            if case_exists is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            row = session.scalar(
                sa.select(CaseBusinessMethodProfileAdoptionRecord)
                .where(
                    CaseBusinessMethodProfileAdoptionRecord.tenant_id == actor.tenant_id,
                    CaseBusinessMethodProfileAdoptionRecord.case_id == case_id,
                )
                .order_by(
                    CaseBusinessMethodProfileAdoptionRecord.adoption_revision.desc(),
                    CaseBusinessMethodProfileAdoptionRecord.id.desc(),
                )
                .limit(1)
            )
        if row is None:
            return None
        return BusinessMethodProfileAdoptionProjection(
            adoption_id=row.id,
            case_id=row.case_id,
            adoption_revision=row.adoption_revision,
            profile_version_id=row.profile_version_id,
            profile_version=row.profile_version,
            profile_content_sha256=row.profile_content_sha256,
        )

    def _authorize_company(
        self, *, actor: ActorContext, company_id: UUID, now, write: bool
    ) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=(
                    Capability.ENTERPRISE_CAPABILITY_WRITE
                    if write
                    else Capability.ENTERPRISE_CAPABILITY_READ
                ),
                resource=AuthorizationResource(
                    resource_type="BUSINESS_METHOD_PROFILE",
                    resource_id=company_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)

    def _authorize_case(self, *, actor: ActorContext, case_id: UUID, now, write: bool) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.DECISION_MANAGE,
                resource=AuthorizationResource(
                    resource_type="BUSINESS_METHOD_PROFILE_ADOPTION",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    case_id=case_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)

    @staticmethod
    def _context(*, actor: ActorContext, now, case_id: UUID | None = None) -> CommandContext:
        return CommandContext(
            tenant_id=actor.tenant_id,
            actor_id=actor.actor_id,
            actor_kind=actor.actor_kind.value,
            received_at=now,
            identity_id=actor.identity_id,
            membership_id=actor.membership_id,
            session_id=actor.session_id,
            case_id=case_id,
            correlation_id=actor.correlation_id,
        )


class PublishBusinessMethodProfileHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: PublishBusinessMethodProfileCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        company = session.scalar(
            sa.select(EnterpriseCompanyRecord)
            .where(
                EnterpriseCompanyRecord.tenant_id == context.tenant_id,
                EnterpriseCompanyRecord.id == command.company_id,
            )
            .with_for_update()
        )
        if company is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        latest_version = session.scalar(
            sa.select(sa.func.max(EnterpriseBusinessMethodProfileVersionRecord.version_number)).where(
                EnterpriseBusinessMethodProfileVersionRecord.tenant_id == context.tenant_id,
                EnterpriseBusinessMethodProfileVersionRecord.company_id == company.id,
            )
        ) or 0
        if command.expected_version != latest_version:
            raise CommandExecutionError("STALE_PROFILE_VERSION")
        version = latest_version + 1
        profile_json = command.profile.model_dump(mode="json")
        content_hash = profile_content_hash(profile_json)
        session.add(
            EnterpriseBusinessMethodProfileVersionRecord(
                id=command.profile_version_id,
                tenant_id=context.tenant_id,
                company_id=company.id,
                version_number=version,
                schema_version=1,
                profile_json=profile_json,
                content_sha256=content_hash,
                created_by_actor_id=context.actor_id,
                created_by_membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return HandlerOutcome(
            result_code="BUSINESS_METHOD_PROFILE_PUBLISHED",
            aggregate_refs=(
                {
                    "aggregate_type": "BusinessMethodProfile",
                    "aggregate_id": str(command.profile_version_id),
                    "aggregate_revision": version,
                    "content_hash": content_hash,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="BusinessMethodProfile",
                    aggregate_id=command.profile_version_id,
                    aggregate_revision=version,
                    event_type="BusinessMethodProfilePublished",
                    payload={
                        "company_id": str(company.id),
                        "version": version,
                        "content_sha256": content_hash,
                    },
                ),
            ),
        )


class AdoptBusinessMethodProfileHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: AdoptBusinessMethodProfileCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == context.tenant_id, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        profile = session.scalar(
            sa.select(EnterpriseBusinessMethodProfileVersionRecord).where(
                EnterpriseBusinessMethodProfileVersionRecord.tenant_id == context.tenant_id,
                EnterpriseBusinessMethodProfileVersionRecord.id == command.profile_version_id,
                EnterpriseBusinessMethodProfileVersionRecord.version_number
                == command.profile_version,
                EnterpriseBusinessMethodProfileVersionRecord.content_sha256
                == command.profile_content_sha256,
            )
        )
        if profile is None:
            raise CommandExecutionError("PROFILE_VERSION_NOT_FOUND_OR_FORBIDDEN")
        latest_revision = session.scalar(
            sa.select(sa.func.max(CaseBusinessMethodProfileAdoptionRecord.adoption_revision)).where(
                CaseBusinessMethodProfileAdoptionRecord.tenant_id == context.tenant_id,
                CaseBusinessMethodProfileAdoptionRecord.case_id == case.id,
            )
        ) or 0
        if command.expected_adoption_revision != latest_revision:
            raise CommandExecutionError("STALE_PROFILE_ADOPTION")
        revision = latest_revision + 1
        session.add(
            CaseBusinessMethodProfileAdoptionRecord(
                id=command.adoption_id,
                tenant_id=context.tenant_id,
                case_id=case.id,
                profile_version_id=profile.id,
                profile_version=profile.version_number,
                profile_content_sha256=profile.content_sha256,
                adoption_revision=revision,
                created_by_actor_id=context.actor_id,
                created_by_membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return HandlerOutcome(
            result_code="BUSINESS_METHOD_PROFILE_ADOPTED",
            aggregate_refs=(
                {
                    "aggregate_type": "BusinessMethodProfileAdoption",
                    "aggregate_id": str(command.adoption_id),
                    "aggregate_revision": revision,
                },
                {
                    "aggregate_type": "BusinessMethodProfile",
                    "aggregate_id": str(profile.id),
                    "aggregate_revision": profile.version_number,
                    "content_hash": profile.content_sha256,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="BusinessMethodProfileAdoption",
                    aggregate_id=command.adoption_id,
                    aggregate_revision=revision,
                    event_type="BusinessMethodProfileAdoptedByCase",
                    payload={
                        "case_id": str(case.id),
                        "profile_version_id": str(profile.id),
                        "profile_version": profile.version_number,
                        "content_sha256": profile.content_sha256,
                    },
                ),
            ),
        )


def business_method_profile_handlers() -> dict[str, CommandHandler]:
    return {
        PublishBusinessMethodProfileCommand.command_type: PublishBusinessMethodProfileHandler(),
        AdoptBusinessMethodProfileCommand.command_type: AdoptBusinessMethodProfileHandler(),
    }
