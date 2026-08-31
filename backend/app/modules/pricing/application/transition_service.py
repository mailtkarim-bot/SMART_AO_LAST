from datetime import datetime

from app.modules.pricing.application.queries import PricingScenarioReader
from app.modules.pricing.application.transition_commands import TransitionPricingScenarioCommand
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


class PricingScenarioTransitionService:
    def __init__(
        self,
        *,
        reader: PricingScenarioReader,
        dispatcher: CommandDispatcher,
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._reader = reader
        self._dispatcher = dispatcher
        self._policy = policy

    def execute(
        self, *, actor: ActorContext, command: TransitionPricingScenarioCommand, now: datetime
    ) -> DispatchResult:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PRICING_WRITE,
                resource=AuthorizationResource(
                    resource_type="PRICING_SCENARIO",
                    resource_id=command.scenario_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
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
                correlation_id=actor.correlation_id,
            ),
        )

    def list_for_case(self, *, actor: ActorContext, case_id, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        return self._reader.list_for_case(tenant_id=actor.tenant_id, case_id=case_id)
