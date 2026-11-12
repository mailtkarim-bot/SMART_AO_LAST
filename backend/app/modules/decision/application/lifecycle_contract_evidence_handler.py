from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa

from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.decision.application.lifecycle_commands import (
    LinkDecisionConditionContractEvidenceCommand,
)
from app.modules.decision.application.ports import DecisionLifecycleRepository
from app.modules.decision.infrastructure.models.decision import (
    DecisionConditionContractEvidenceLinkRecord,
    DecisionConditionRecord,
    DecisionContextRecord,
    DecisionContextReferenceRecord,
    DecisionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class LinkConditionEvidenceHandler(CommandHandler):
    def __init__(self, *, lifecycle_repository: DecisionLifecycleRepository) -> None:
        self._lifecycle_repository = lifecycle_repository

    def execute(
        self,
        *,
        session,
        command: LinkDecisionConditionContractEvidenceCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        decision = session.scalar(
            sa.select(DecisionRecord)
            .where(
                DecisionRecord.tenant_id == tenant_id,
                DecisionRecord.id == command.decision_id,
                DecisionRecord.case_id == command.case_id,
            )
            .with_for_update()
        )
        if decision is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if decision.aggregate_revision != command.expected_decision_revision:
            raise CommandExecutionError("STALE_DECISION_REVISION")
        if (
            decision.lifecycle != "FINALIZED"
            or decision.outcome != "CONDITIONAL_GO"
            or decision.validity != "CURRENT"
        ):
            raise CommandExecutionError("DECISION_NOT_CONDITIONAL_GO")
        condition = session.scalar(
            sa.select(DecisionConditionRecord)
            .where(
                DecisionConditionRecord.tenant_id == tenant_id,
                DecisionConditionRecord.decision_id == decision.id,
                DecisionConditionRecord.id == command.condition_id,
            )
            .with_for_update()
        )
        if condition is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        if condition.status != "OPEN":
            raise CommandExecutionError("DECISION_CONDITION_NOT_OPEN")
        if decision.selected_final_context_id is None:
            raise CommandExecutionError("DECISION_FINAL_CONTEXT_REQUIRED")
        proof = session.scalar(
            sa.select(ContractBaselineDeviationImpactRecord).where(
                ContractBaselineDeviationImpactRecord.tenant_id == tenant_id,
                ContractBaselineDeviationImpactRecord.case_id == command.case_id,
                ContractBaselineDeviationImpactRecord.id == command.contract_impact_id,
                ContractBaselineDeviationImpactRecord.proof_revision == command.proof_revision,
                ContractBaselineDeviationImpactRecord.dce_requirement_id.is_not(None),
            )
        )
        if proof is None or proof.dce_requirement_revision is None:
            raise CommandExecutionError("EXACT_CONTRACT_PROOF_NOT_FOUND")
        if proof.status != "HUMAN_REVIEW_REQUIRED":
            raise CommandExecutionError("CONTRACT_PROOF_REQUIRES_HUMAN_REVIEW_STATE")
        context_record = session.scalar(
            sa.select(DecisionContextRecord).where(
                DecisionContextRecord.tenant_id == tenant_id,
                DecisionContextRecord.decision_id == decision.id,
                DecisionContextRecord.id == decision.selected_final_context_id,
                DecisionContextRecord.context_state == "FROZEN",
            )
        )
        if context_record is None:
            raise CommandExecutionError("DECISION_FINAL_CONTEXT_REQUIRED")
        references = tuple(
            session.scalars(
                sa.select(DecisionContextReferenceRecord).where(
                    DecisionContextReferenceRecord.tenant_id == tenant_id,
                    DecisionContextReferenceRecord.decision_context_id == context_record.id,
                )
            ).all()
        )
        expected = {
            ("DCE_REQUIREMENT", proof.dce_requirement_id, proof.dce_requirement_revision, None),
            ("CONTRACT_BASELINE_IMPACT", proof.id, proof.proof_revision, None),
        }
        actual = {
            (item.aggregate_type, item.aggregate_id, item.aggregate_revision, item.content_hash)
            for item in references
        }
        if not expected.issubset(actual):
            raise CommandExecutionError("A1_EVIDENCE_NOT_IN_FROZEN_CONTEXT")
        profiles = [item for item in references if item.aggregate_type == "BUSINESS_METHOD_PROFILE"]
        if len(profiles) != 1 or profiles[0].content_hash is None:
            raise CommandExecutionError("ADOPTED_BUSINESS_METHOD_PROFILE_REFERENCE_REQUIRED")
        for reference in references:
            if reference.aggregate_type not in {
                "DCE_REQUIREMENT",
                "CONTRACT_BASELINE_IMPACT",
                "BUSINESS_METHOD_PROFILE",
            }:
                continue
            if not self._lifecycle_repository.context_reference_is_valid(
                session=session,
                tenant_id=tenant_id,
                case_id=command.case_id,
                aggregate_type=reference.aggregate_type,
                aggregate_id=reference.aggregate_id,
                aggregate_revision=reference.aggregate_revision,
                content_hash=reference.content_hash,
            ):
                raise CommandExecutionError("A1_EVIDENCE_REFERENCE_STALE_OR_FORBIDDEN")
        profile = profiles[0]
        session.add(
            DecisionConditionContractEvidenceLinkRecord(
                id=command.link_id,
                tenant_id=tenant_id,
                decision_id=decision.id,
                condition_id=condition.id,
                context_id=context_record.id,
                dce_requirement_id=proof.dce_requirement_id,
                dce_requirement_revision=proof.dce_requirement_revision,
                contract_impact_id=proof.id,
                proof_revision=proof.proof_revision,
                profile_version_id=profile.aggregate_id,
                profile_version=profile.aggregate_revision,
                profile_content_sha256=profile.content_hash.lower(),
                created_by_actor_id=UUID(str(context.actor_id)),
                command_id=UUID(str(command.command_id)),
                idempotency_key=UUID(str(command.idempotency_key)),
                correlation_id=(
                    UUID(str(command.correlation_id)) if command.correlation_id else None
                ),
            )
        )
        return HandlerOutcome(
            result_code="DECISION_CONDITION_CONTRACT_EVIDENCE_LINKED",
            aggregate_refs=(
                {
                    "aggregate_type": "DECISION_CONDITION_CONTRACT_EVIDENCE_LINK",
                    "aggregate_id": str(command.link_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="DECISION_CONDITION_CONTRACT_EVIDENCE_LINK",
                    aggregate_id=command.link_id,
                    aggregate_revision=1,
                    event_type="DECISION_CONDITION_CONTRACT_EVIDENCE_LINKED",
                    payload={
                        "decision_id": str(decision.id),
                        "condition_id": str(condition.id),
                        "proof_id": str(proof.id),
                        "status": "LINKED",
                    },
                ),
            ),
        )
