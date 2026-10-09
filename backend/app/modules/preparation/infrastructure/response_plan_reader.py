from __future__ import annotations

from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.enterprise.infrastructure.models import (
    CaseCapabilityProposalRecord,
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
)
from app.modules.membership.application.collab_capability_ports import CollaboratorCapabilityReader
from app.modules.preparation.application.ports import (
    PreparationResponsePlanFact,
    PreparationResponsePlanSources,
    PreparationSourceState,
)


class SqlAlchemyPreparationResponsePlanSourceReader:
    """Resolve preparation sources from the existing DCE and Enterprise contexts."""

    def __init__(self, *, capability_reader: CollaboratorCapabilityReader) -> None:
        self._capability_reader = capability_reader

    def read(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        case_id: UUID,
        assignment_id: UUID,
        dce_version_id: UUID,
        requirement_ids: set[UUID],
        proposal_ids: set[UUID],
        evaluated_at: datetime,
    ) -> PreparationResponsePlanSources:
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
            )
        )
        if case is None:
            return PreparationResponsePlanSources(
                dce_current=False,
                requirement_states={},
                facts={},
            )
        dce = session.scalar(
            sa.select(DceVersionRecord).where(
                DceVersionRecord.tenant_id == tenant_id,
                DceVersionRecord.id == dce_version_id,
                DceVersionRecord.consultation_id == case.consultation_id,
                DceVersionRecord.lifecycle == "ADMITTED",
                DceVersionRecord.integrity == "VERIFIED",
            )
        )
        if case.applicable_dce_version_id != dce_version_id or dce is None:
            return PreparationResponsePlanSources(
                dce_current=False,
                requirement_states={},
                facts={},
            )

        requirements = list(
            session.scalars(
                sa.select(DceRequirementRecord).where(
                    DceRequirementRecord.tenant_id == tenant_id,
                    DceRequirementRecord.dce_version_id == dce_version_id,
                    DceRequirementRecord.id.in_(requirement_ids),
                )
            ).all()
        )
        confirmations = {
            row.requirement_id: row.outcome
            for row in session.scalars(
                sa.select(DceRequirementConfirmationCurrentRecord).where(
                    DceRequirementConfirmationCurrentRecord.tenant_id == tenant_id,
                    DceRequirementConfirmationCurrentRecord.requirement_id.in_(requirement_ids),
                )
            ).all()
        }
        requirement_states = {
            requirement.id: confirmations.get(requirement.id, "UNKNOWN")
            for requirement in requirements
        }
        proposals = list(
            session.scalars(
                sa.select(CaseCapabilityProposalRecord).where(
                    CaseCapabilityProposalRecord.tenant_id == tenant_id,
                    CaseCapabilityProposalRecord.case_id == case_id,
                    CaseCapabilityProposalRecord.assignment_id == assignment_id,
                    CaseCapabilityProposalRecord.id.in_(proposal_ids),
                )
            ).all()
        )
        evidence = self._capability_reader.read_proposal_source_evidence(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            assignment_id=assignment_id,
            proposal_ids=proposal_ids,
            evaluated_at=evaluated_at,
        )
        facts: dict[UUID, PreparationResponsePlanFact] = {}
        for proposal in proposals:
            capability = session.scalar(
                sa.select(EnterpriseCapabilityRecord).where(
                    EnterpriseCapabilityRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityRecord.id == proposal.capability_id,
                )
            )
            version = session.scalar(
                sa.select(EnterpriseCapabilityVersionRecord).where(
                    EnterpriseCapabilityVersionRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityVersionRecord.id == proposal.capability_version_id,
                    EnterpriseCapabilityVersionRecord.capability_id == proposal.capability_id,
                )
            )
            validity_state: PreparationSourceState
            if capability is None or version is None:
                validity_state = "UNKNOWN"
            elif (
                proposal.validity_state == "EXPIRED"
                or capability.state != "ACTIVE"
                or version.valid_from > evaluated_at
                or (version.valid_until is not None and version.valid_until <= evaluated_at)
            ):
                validity_state = "EXPIRED"
            elif proposal.validity_state == "CURRENT":
                validity_state = "CURRENT"
            else:
                validity_state = "UNKNOWN"
            evidence_projection = evidence.get(proposal.id)
            facts[proposal.id] = PreparationResponsePlanFact(
                proposal_id=proposal.id,
                requirement_id=proposal.requirement_id,
                task_id=proposal.task_id,
                capability_version_id=proposal.capability_version_id,
                validity_state=validity_state,
                evidence_state=(
                    evidence_projection.state if evidence_projection is not None else "UNKNOWN"
                ),
                proof_refs=(
                    evidence_projection.proof_refs if evidence_projection is not None else ()
                ),
            )
        return PreparationResponsePlanSources(
            dce_current=True,
            requirement_states=requirement_states,
            facts=facts,
        )
