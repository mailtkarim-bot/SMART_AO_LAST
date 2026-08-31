from __future__ import annotations

from datetime import datetime

from app.modules.pricing.application.import_commands import CommitPricingImportCommand
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    DispatchResult,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification


class PricingImportService:
    """Authorize and dispatch one patronal application of normalized import rows."""

    def __init__(
        self,
        *,
        dispatcher: CommandDispatcher,
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._policy = policy

    def commit(
        self,
        *,
        actor: ActorContext,
        command: CommitPricingImportCommand,
        now: datetime,
    ) -> DispatchResult:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FINANCIAL_REPORT_PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.FINANCIAL_REPORT_LINE_WRITE,
                resource=AuthorizationResource(
                    resource_type="PRICING_IMPORT",
                    resource_id=command.batch_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
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
