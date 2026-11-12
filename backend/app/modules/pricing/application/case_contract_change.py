"""Patron use cases for sourced post-award contract changes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.modules.pricing.application.case_contract_change_commands import (
    ExpireCaseContractChangeEvidenceUploadCommand,
    PrepareCaseContractChangeEvidenceUploadCommand,
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeActionExecutionCommand,
    RecordCaseContractChangeActionImpactRelationCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEngagementLinkCommand,
    RecordCaseContractChangeEventCommand,
    RecordCaseContractChangeExternalConfirmationCommand,
    RecordCaseContractChangeImpactDeclarationCommand,
)
from app.modules.pricing.application.case_contract_change_handler import (
    CaseContractChangeHandler,
)
from app.modules.pricing.application.case_contract_change_queries import (
    CaseContractChangeReader,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandHandler,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    DataClassification,
    OperationalProfile,
)


class CaseContractChangeService:
    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        reader: CaseContractChangeReader,
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._reader = reader
        self._policy = policy

    def record(self, *, actor: ActorContext, command, now: datetime):
        self.authorize_case_write(actor=actor, case_id=command.case_id, now=now)
        if any(
            getattr(command, name, None) is not None
            for name in (
                "operational_context",
                "operational_review",
                "operational_details",
                "operational_publication",
            )
        ):
            self._authorize(
                actor=actor,
                case_id=command.case_id,
                action=Capability.PATRON_ACTION_WRITE,
                now=now,
                mfa_required=True,
            )
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
                correlation_id=command.correlation_id,
            ),
        )

    def authorize_case_write(self, *, actor: ActorContext, case_id: UUID, now: datetime) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(
            actor=actor, case_id=case_id, action=Capability.PATRON_ACTION_WRITE, now=now
        )

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> tuple[dict[str, object], ...]:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=case_id, action=Capability.PATRON_ACTION_READ, now=now)
        return self._reader.list_for_case(tenant_id=actor.tenant_id, case_id=case_id)

    def list_operational_for_case(self, *, actor, case_id, now):
        from app.modules.pricing.application.operational_change_projection import (
            public_change_projection,
        )

        if actor.actor_kind is ActorKind.COLLABORATEUR:
            if actor.operational_profile is not OperationalProfile.RESPONSABLE:
                raise PermissionError("RESPONSABLE_REQUIRED")
            decision = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=Capability.CASE_DCE_READ,
                    resource=AuthorizationResource(
                        resource_type="CASE_CONTRACT_CHANGE",
                        resource_id=case_id,
                        tenant_id=actor.tenant_id,
                        case_id=case_id,
                        classification=DataClassification.INTERNAL_OPERATIONAL,
                    ),
                    evaluated_at=now,
                ),
            )
            if not decision.allowed:
                raise PermissionError("FORBIDDEN")
        elif actor.actor_kind is ActorKind.PATRON_ADMIN:
            self._authorize(
                actor=actor, case_id=case_id, action=Capability.PATRON_ACTION_READ, now=now
            )
        else:
            raise PermissionError("FORBIDDEN")
        return tuple(
            value
            for row in self._reader.list_operational_for_case(
                tenant_id=actor.tenant_id, case_id=case_id
            )
            if (value := public_change_projection(row)) is not None
        )

    def _authorize(
        self,
        *,
        actor: ActorContext,
        case_id: UUID,
        action: Capability,
        now: datetime,
        mfa_required=False,
    ) -> None:
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="CASE_CONTRACT_CHANGE",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
                    case_id=case_id,
                ),
                evaluated_at=now,
                mfa_required=mfa_required,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)


def case_contract_change_handlers(*, storage=None) -> dict[str, CommandHandler]:
    handler = CaseContractChangeHandler(storage=storage)
    return {
        RecordCaseContractChangeEventCommand.command_type: handler,
        RecordCaseContractChangeApplicabilityCommand.command_type: handler,
        RecordCaseContractChangeActionCommand.command_type: handler,
        RecordCaseContractChangeActionImpactRelationCommand.command_type: handler,
        RecordCaseContractChangeActionExecutionCommand.command_type: handler,
        ExpireCaseContractChangeEvidenceUploadCommand.command_type: handler,
        PrepareCaseContractChangeEvidenceUploadCommand.command_type: handler,
        RecordCaseContractChangeExternalConfirmationCommand.command_type: handler,
        RecordCaseContractChangeEngagementLinkCommand.command_type: handler,
        RecordCaseContractChangeImpactDeclarationCommand.command_type: handler,
    }
