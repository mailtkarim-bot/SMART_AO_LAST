from __future__ import annotations

from datetime import datetime

from app.modules.pricing.application.import_commands import CreatePricingImportPreviewCommand
from app.modules.pricing.application.ports import CaseExistenceReader
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


class PricingImportCreationService:
    """Authorize and persist one server-normalized pricing preview."""

    def __init__(
        self,
        *,
        case_reader: CaseExistenceReader,
        dispatcher: CommandDispatcher,
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._case_reader = case_reader
        self._dispatcher = dispatcher
        self._policy = policy

    def create(
        self,
        *,
        actor: ActorContext,
        command: CreatePricingImportPreviewCommand,
        now: datetime,
    ) -> DispatchResult:
        """Resolve tenant and Case server-side before dispatching financial data."""
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PRICING_IMPORT_PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.FINANCIAL_REPORT_LINE_WRITE,
                resource=AuthorizationResource(
                    resource_type="PRICING_IMPORT",
                    resource_id=command.case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
                    case_id=command.case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
        if not self._case_reader.exists(
            tenant_id=actor.tenant_id,
            case_id=command.case_id,
        ):
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
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
