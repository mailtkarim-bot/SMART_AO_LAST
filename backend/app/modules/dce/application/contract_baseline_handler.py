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
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
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
        exact_baseline_observation_id = command.baseline_observation_id
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
        if command.dce_requirement_id is not None:
            requirement_source_observation = session.scalar(
                sa.select(DceRequirementRecord.source_observation_id)
                .join(
                    DceRequirementConfirmationCurrentRecord,
                    sa.and_(
                        DceRequirementConfirmationCurrentRecord.tenant_id
                        == DceRequirementRecord.tenant_id,
                        DceRequirementConfirmationCurrentRecord.requirement_id
                        == DceRequirementRecord.id,
                    ),
                )
                .join(
                    CaseRecord,
                    sa.and_(
                        CaseRecord.tenant_id == DceRequirementRecord.tenant_id,
                        CaseRecord.applicable_dce_version_id == DceRequirementRecord.dce_version_id,
                    ),
                )
                .where(
                    DceRequirementRecord.tenant_id == tenant_id,
                    DceRequirementRecord.id == command.dce_requirement_id,
                    CaseRecord.id == command.case_id,
                    CaseRecord.lifecycle == "ACTIVE",
                    DceRequirementConfirmationCurrentRecord.revision
                    == command.dce_requirement_revision,
                    DceRequirementConfirmationCurrentRecord.outcome == "CONFIRMED",
                )
            )
            if requirement_source_observation is None:
                raise CommandExecutionError("DCE_REQUIREMENT_NOT_CURRENTLY_CONFIRMED")
            if (
                exact_baseline_observation_id is not None
                and requirement_source_observation != exact_baseline_observation_id
            ):
                raise CommandExecutionError("BASELINE_OBSERVATION_NOT_EXACT_REQUIREMENT_SOURCE")
            exact_baseline_observation_id = requirement_source_observation
            exact_requirement_reference = (
                f"DCE_REQUIREMENT:{command.dce_requirement_id}@{command.dce_requirement_revision}"
            )
            if exact_requirement_reference not in command.baseline_source_refs:
                raise CommandExecutionError("EXACT_DCE_REQUIREMENT_SOURCE_REFERENCE_REQUIRED")
        if exact_baseline_observation_id is None:
            raise CommandExecutionError("BASELINE_OBSERVATION_REQUIRED")
        if command.proof_revision > 1:
            previous = session.scalar(
                sa.select(ContractBaselineDeviationImpactRecord.id).where(
                    ContractBaselineDeviationImpactRecord.tenant_id == tenant_id,
                    ContractBaselineDeviationImpactRecord.case_id == command.case_id,
                    ContractBaselineDeviationImpactRecord.baseline_observation_id
                    == exact_baseline_observation_id,
                    ContractBaselineDeviationImpactRecord.proof_revision
                    == command.proof_revision - 1,
                )
            )
            if previous is None:
                raise CommandExecutionError("PREVIOUS_CONTRACT_PROOF_REVISION_REQUIRED")
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
                baseline_observation_id=exact_baseline_observation_id,
                dce_requirement_id=command.dce_requirement_id,
                dce_requirement_revision=command.dce_requirement_revision,
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
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PRICING_READ,
                resource=AuthorizationResource(
                    resource_type="CONTRACT_BASELINE_IMPACT",
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
        with self._session_factory() as session:
            return tuple(
                session.scalars(
                    sa.select(ContractBaselineDeviationImpactRecord)
                    .where(
                        ContractBaselineDeviationImpactRecord.tenant_id == actor.tenant_id,
                        ContractBaselineDeviationImpactRecord.case_id == case_id,
                    )
                    .order_by(ContractBaselineDeviationImpactRecord.proof_revision.desc())
                ).all()
            )


class ContractBaselineImpactWriteService:
    def __init__(self, *, dispatcher, policy) -> None:
        self._dispatcher = dispatcher
        self._policy = policy

    def execute(self, *, actor, command, now):
        from app.platform.events.dispatcher import CommandContext
        from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
        from app.platform.security.capabilities import Capability
        from app.platform.security.context import ActorKind, DataClassification

        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PRICING_WRITE,
                resource=AuthorizationResource(
                    resource_type="CONTRACT_BASELINE_IMPACT",
                    resource_id=command.proof_id,
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
