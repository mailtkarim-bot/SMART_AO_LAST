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
