"""Patron use cases for sourced post-award contract changes."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.modules.pricing.application.case_contract_change_commands import (
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEventCommand,
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
from app.platform.security.context import ActorContext, ActorKind, DataClassification


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
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.PATRON_ACTION_WRITE, now=now
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

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> tuple[dict[str, object], ...]:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=case_id, action=Capability.PATRON_ACTION_READ, now=now)
        return self._reader.list_for_case(tenant_id=actor.tenant_id, case_id=case_id)

    def _authorize(
        self, *, actor: ActorContext, case_id: UUID, action: Capability, now: datetime
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
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)


def case_contract_change_handlers() -> dict[str, CommandHandler]:
    handler = CaseContractChangeHandler()
    return {
        RecordCaseContractChangeEventCommand.command_type: handler,
        RecordCaseContractChangeApplicabilityCommand.command_type: handler,
        RecordCaseContractChangeActionCommand.command_type: handler,
    }
