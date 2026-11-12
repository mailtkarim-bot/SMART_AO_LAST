from app.modules.pricing.application.case_closure_commands import RecordPaymentFactCommand
from app.modules.pricing.application.case_closure_handler import RecordPaymentFactHandler
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
)
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


def closure_handlers():
    from app.modules.patron_action.application.case_interview_handler import case_interview_handlers
    from app.modules.patron_action.application.execution_rex_handler import (
        RecordExecutionRexHandler,
    )
    from app.modules.patron_action.application.teaching_applicability_handler import (
        RecordCaseTeachingApplicabilityHandler,
    )
    from app.modules.pricing.application.case_closure_commands import (
        RecordClosureActCommand,
        RecordClosureObligationCommand,
        RecordExecutionRexCommand,
        RecordExecutionTeachingReuseCommand,
    )
    from app.modules.pricing.application.contract_execution_evidence_handler import (
        RecordContractExecutionEvidenceHandler,
    )
    from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
    from app.modules.pricing.application.post_reception_obligation_handler import (
        RecordPostReceptionObligationHandler,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_handler import (
        post_reception_obligation_transition_handlers,
    )

    return {
        **payment_cycle_handlers(),
        **post_reception_obligation_transition_handlers(),
        **case_interview_handlers(),
        RecordExecutionTeachingReuseCommand.command_type: RecordCaseTeachingApplicabilityHandler(),
        RecordPaymentFactCommand.command_type: RecordPaymentFactHandler(),
        RecordClosureActCommand.command_type: RecordContractExecutionEvidenceHandler(),
        RecordClosureObligationCommand.command_type: RecordPostReceptionObligationHandler(),
        RecordExecutionRexCommand.command_type: RecordExecutionRexHandler(),
    }


class CaseClosureService:
    def __init__(self, *, reader, dispatcher, policy):
        self._reader, self._dispatcher, self._policy = reader, dispatcher, policy

    def _authorize(self, actor, case_id, now, write=False):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FORBIDDEN")
        if (
            Capability.PRICING_WRITE.value if write else Capability.PRICING_READ.value
        ) not in actor.capabilities:
            raise PermissionError("FORBIDDEN")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PATRON_ACTION_WRITE if write else Capability.PATRON_ACTION_READ,
                resource=AuthorizationResource(
                    resource_type="CASE_CLOSURE",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    case_id=case_id,
                    classification=DataClassification.FINANCIAL_PRIVATE,
                ),
                evaluated_at=now,
                mfa_required=write,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)

    def read(self, *, actor, case_id, now):
        self._authorize(actor, case_id, now)
        result = self._reader.read(tenant_id=actor.tenant_id, case_id=case_id)
        if result is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        return result

    def record(self, *, actor, command, now):
        self._authorize(actor, command.case_id, now, write=True)
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
