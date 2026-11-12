from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.decision.infrastructure.analysis_reference import assessment_reference_is_current
from app.modules.decision.infrastructure.commitment_reader import read_commitment_card
from app.modules.decision.infrastructure.models.assessment_link import (
    DecisionConditionAssessmentLinkRecord as Link,
)
from app.modules.decision.infrastructure.models.decision import (
    DecisionConditionRecord,
    DecisionContextReferenceRecord,
    DecisionRecord,
)
from app.modules.decision.infrastructure.repositories import SqlAlchemyDecisionRepository
from app.platform.events.dispatcher import CommandContext, CommandExecutionError, HandlerOutcome
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


class CommitmentCardService:
    def __init__(self, *, session_factory, dispatcher, policy):
        self._factory = session_factory
        self._dispatcher = dispatcher
        self._policy = policy

    def _authorize(self, actor, case_id, now, write=False):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("FORBIDDEN")
        for cap, classification in [
            (Capability.CASE_DCE_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.DECISION_RISK_READ, DataClassification.INTERNAL_OPERATIONAL),
            (Capability.PRICING_READ, DataClassification.FINANCIAL_PRIVATE),
            *(
                ([(Capability.DECISION_MANAGE, DataClassification.FINANCIAL_PRIVATE)])
                if write
                else []
            ),
        ]:
            result = self._policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=cap,
                    resource=AuthorizationResource(
                        resource_type="COMMITMENT_CARD",
                        resource_id=case_id,
                        case_id=case_id,
                        tenant_id=actor.tenant_id,
                        classification=classification,
                    ),
                    evaluated_at=now,
                    mfa_required=write,
                ),
            )
            if not result.allowed:
                raise PermissionError("FORBIDDEN")

    def read(self, *, actor, case_id, now):
        self._authorize(actor, case_id, now)
        with self._factory() as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            return read_commitment_card(
                session, tenant_id=actor.tenant_id, case_id=case_id, session_factory=self._factory
            )

    def link(self, *, actor, command, now):
        self._authorize(actor, command.case_id, now, write=True)
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                case_id=command.case_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                membership_id=actor.membership_id,
                identity_id=actor.identity_id,
                session_id=actor.session_id,
                received_at=now,
                correlation_id=actor.correlation_id,
            ),
        )

    def history(self, *, actor, case_id, now, decision_id=None, before_decision_id=None):
        from app.modules.decision.infrastructure.commitment_reader import read_commitment_decisions

        self._authorize(actor, case_id, now)
        with self._factory() as session:
            session.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            case = session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == actor.tenant_id, CaseRecord.id == case_id
                )
            )
            if case is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            records, more = read_commitment_decisions(
                session,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                decision_id=decision_id,
                before_decision_id=before_decision_id,
            )
            if decision_id is not None:
                if not records:
                    raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
                return dict(case_id=str(case_id), decision=records[0])
            return dict(
                case_id=str(case_id),
                history=records,
                next_before_decision_id=records[-1]["decision_id"] if more and records else None,
            )


class LinkConditionAssessmentHandler:
    def execute(self, *, session, command, context):
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("FORBIDDEN")
        tenant = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if not assessment_reference_is_current(
            session,
            tenant_id=tenant,
            case_id=case.id,
            aggregate_id=command.assessment_id,
            aggregate_revision=command.assessment_revision,
            content_hash=command.source_context_sha256,
        ):
            raise CommandExecutionError("STALE_ASSESSMENT_REFERENCE")
        decision = session.scalar(
            sa.select(DecisionRecord)
            .where(
                DecisionRecord.tenant_id == tenant,
                DecisionRecord.case_id == case.id,
                DecisionRecord.id == command.decision_id,
            )
            .with_for_update()
        )
        if decision is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if (
            decision.aggregate_revision != command.expected_decision_revision
            or decision.validity != "CURRENT"
            or decision.lifecycle != "FINALIZED"
            or decision.outcome != "CONDITIONAL_GO"
            or decision.context_status != "FROZEN"
        ):
            raise CommandExecutionError("STALE_DECISION_OR_CONDITION")
        condition = session.scalar(
            sa.select(DecisionConditionRecord)
            .where(
                DecisionConditionRecord.tenant_id == tenant,
                DecisionConditionRecord.decision_id == decision.id,
                DecisionConditionRecord.id == command.condition_id,
            )
            .with_for_update()
        )
        if condition is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        reference = session.scalar(
            sa.select(DecisionContextReferenceRecord.id).where(
                DecisionContextReferenceRecord.tenant_id == tenant,
                DecisionContextReferenceRecord.decision_context_id
                == decision.selected_final_context_id,
                DecisionContextReferenceRecord.aggregate_type == "ANALYSIS_ASSESSMENT",
                DecisionContextReferenceRecord.aggregate_id == command.assessment_id,
                DecisionContextReferenceRecord.aggregate_revision == command.assessment_revision,
                DecisionContextReferenceRecord.content_hash == command.source_context_sha256,
            )
        )
        if condition.status != "OPEN" or reference is None:
            raise CommandExecutionError("STALE_DECISION_OR_CONDITION")
        existing = session.scalar(
            sa.select(Link.id).where(
                Link.tenant_id == tenant,
                Link.condition_id == condition.id,
                Link.assessment_id == command.assessment_id,
                Link.assessment_revision == command.assessment_revision,
            )
        )
        if existing is not None:
            raise CommandExecutionError("ASSESSMENT_LINK_CONFLICT")
        revision = SqlAlchemyDecisionRepository(session).update_root(
            tenant_id=tenant,
            aggregate_id=decision.id,
            expected_revision=command.expected_decision_revision,
            changes={"context_status": decision.context_status},
        )
        session.add(
            Link(
                id=command.link_id,
                tenant_id=tenant,
                case_id=case.id,
                decision_id=decision.id,
                context_id=decision.selected_final_context_id,
                condition_id=condition.id,
                assessment_id=command.assessment_id,
                assessment_revision=command.assessment_revision,
                source_context_sha256=command.source_context_sha256,
                justification=command.justification,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
            )
        )
        session.flush()
        return HandlerOutcome(
            result_code="DECISION_CONDITION_ASSESSMENT_LINKED",
            events=(),
            aggregate_refs=(
                {
                    "aggregate_type": "Decision",
                    "aggregate_id": str(decision.id),
                    "aggregate_revision": revision,
                },
            ),
        )
