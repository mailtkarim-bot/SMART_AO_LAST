# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.contract_baseline_commands import (
    RecordContractBaselineImpactCommand,
)
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class RecordContractBaselineImpactHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordContractBaselineImpactCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        if (
            session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == tenant_id, CaseRecord.id == command.case_id
                )
            )
            is None
        ):
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if command.status == "CONFIRMED" and (
            command.deviation_statement is None or command.impact_statement is None
        ):
            raise CommandExecutionError("CONFIRMED_CHAIN_INCOMPLETE")
        existing = session.scalar(
            sa.select(ContractBaselineDeviationImpactRecord).where(
                ContractBaselineDeviationImpactRecord.tenant_id == tenant_id,
                ContractBaselineDeviationImpactRecord.id == command.proof_id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("CONTRACT_PROOF_ID_REUSED")
        session.add(
            ContractBaselineDeviationImpactRecord(
                id=command.proof_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                baseline_observation_id=command.baseline_observation_id,
                proof_revision=command.proof_revision,
                baseline_source_refs_json=list(command.baseline_source_refs),
                baseline_statement=command.baseline_statement,
                deviation_statement=command.deviation_statement,
                impact_statement=command.impact_statement,
                status=command.status,
                created_by_actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="CONTRACT_BASELINE_IMPACT_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CONTRACT_BASELINE_IMPACT",
                    "aggregate_id": str(command.proof_id),
                    "aggregate_revision": command.proof_revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CONTRACT_BASELINE_IMPACT",
                    aggregate_id=command.proof_id,
                    aggregate_revision=command.proof_revision,
                    event_type="CONTRACT_BASELINE_IMPACT_RECORDED",
                    payload={"case_id": str(command.case_id), "status": command.status},
                ),
            ),
        )


def contract_baseline_handlers() -> dict[str, RecordContractBaselineImpactHandler]:
    return {RecordContractBaselineImpactCommand.command_type: RecordContractBaselineImpactHandler()}


class ContractBaselineImpactReadService:
    def __init__(self, *, session_factory, policy) -> None:
        self._session_factory = session_factory
        self._policy = policy

    def list_for_case(self, *, actor, case_id, now):
        from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
        from app.platform.security.capabilities import Capability
        from app.platform.security.context import ActorKind, DataClassification
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(context=actor, request=AuthorizationRequest(
            action=Capability.CASE_DCE_READ,
            resource=AuthorizationResource(resource_type="CONTRACT_BASELINE_IMPACT", resource_id=case_id, tenant_id=actor.tenant_id, classification=DataClassification.INTERNAL_OPERATIONAL, case_id=case_id),
            evaluated_at=now,
        ))
        if not decision.allowed:
            raise PermissionError(decision.code)
        with self._session_factory() as session:
            return tuple(session.scalars(sa.select(ContractBaselineDeviationImpactRecord).where(ContractBaselineDeviationImpactRecord.tenant_id == actor.tenant_id, ContractBaselineDeviationImpactRecord.case_id == case_id).order_by(ContractBaselineDeviationImpactRecord.proof_revision.desc())).all())
