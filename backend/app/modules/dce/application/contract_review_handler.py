# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.application.contract_review_commands import RecordContractProofReviewCommand
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.dce.infrastructure.models.contract_review import ContractProofReviewRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordContractProofReviewHandler(CommandHandler):
    def execute(self, *, session: Session, command: RecordContractProofReviewCommand, context: CommandContext) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        proof = session.scalar(sa.select(ContractBaselineDeviationImpactRecord).where(ContractBaselineDeviationImpactRecord.tenant_id == tenant_id, ContractBaselineDeviationImpactRecord.id == command.proof_id, ContractBaselineDeviationImpactRecord.proof_revision == command.reviewed_revision))
        if proof is None:
            raise CommandExecutionError("CONTRACT_PROOF_NOT_FOUND_OR_FORBIDDEN")
        if session.scalar(sa.select(ContractProofReviewRecord.id).where(ContractProofReviewRecord.tenant_id == tenant_id, ContractProofReviewRecord.id == command.review_id)) is not None:
            raise CommandExecutionError("CONTRACT_REVIEW_ID_REUSED")
        session.add(ContractProofReviewRecord(id=command.review_id, tenant_id=tenant_id, proof_id=command.proof_id, reviewer_id=UUID(str(context.actor_id)), reviewed_revision=command.reviewed_revision, decision=command.decision, rationale=command.rationale))
        return HandlerOutcome(result_code="CONTRACT_PROOF_REVIEW_RECORDED", aggregate_refs=({"aggregate_type": "CONTRACT_PROOF_REVIEW", "aggregate_id": str(command.review_id), "aggregate_revision": command.reviewed_revision},), events=(PendingDomainEvent(aggregate_type="CONTRACT_PROOF_REVIEW", aggregate_id=command.review_id, aggregate_revision=command.reviewed_revision, event_type="CONTRACT_PROOF_REVIEW_RECORDED", payload={"proof_id": str(command.proof_id), "decision": command.decision}),))

def contract_review_handlers() -> dict[str, RecordContractProofReviewHandler]:
    return {RecordContractProofReviewCommand.command_type: RecordContractProofReviewHandler()}


class ContractProofReviewReadService:
    def __init__(self, *, session_factory, policy) -> None:
        self._session_factory, self._policy = session_factory, policy

    def list_for_case(self, *, actor, case_id, now):
        from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
        from app.platform.security.capabilities import Capability
        from app.platform.security.context import ActorKind, DataClassification
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(context=actor, request=AuthorizationRequest(action=Capability.CASE_DCE_READ, resource=AuthorizationResource(resource_type="CONTRACT_PROOF_REVIEW", resource_id=case_id, tenant_id=actor.tenant_id, classification=DataClassification.INTERNAL_OPERATIONAL, case_id=case_id), evaluated_at=now))
        if not decision.allowed:
            raise PermissionError(decision.code)
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(ContractProofReviewRecord).join(ContractBaselineDeviationImpactRecord, sa.and_(ContractBaselineDeviationImpactRecord.id == ContractProofReviewRecord.proof_id, ContractBaselineDeviationImpactRecord.tenant_id == ContractProofReviewRecord.tenant_id)).where(ContractProofReviewRecord.tenant_id == actor.tenant_id, ContractBaselineDeviationImpactRecord.case_id == case_id).order_by(ContractProofReviewRecord.created_at.desc())).all())
