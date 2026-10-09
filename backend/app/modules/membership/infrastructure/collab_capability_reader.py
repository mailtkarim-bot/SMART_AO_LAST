from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.enterprise.infrastructure.models import (
    CaseCapabilityGapRecord,
    CaseCapabilityProposalRecord,
    EnterpriseCapabilityProofLinkRecord,
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
    EnterpriseCompanyRecord,
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.modules.membership.application.collab_capability_ports import (
    AssignmentProjection,
    CapabilityCandidateProjection,
    CapabilityGapProjection,
    CapabilityProposalProjection,
    CapabilityProposalSourceEvidence,
    CollaboratorCapabilityAssessmentProjection,
    CollaboratorCapabilityReader,
)
from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.platform.events.dispatcher import CommandExecutionError


class SqlAlchemyCollaboratorCapabilityReader(CollaboratorCapabilityReader):
    """SQLAlchemy adapter for collaborator capability authorization and reads."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def require_active_assignment(
        self,
        *,
        tenant_id: UUID,
        membership_id: UUID,
        case_id: UUID,
        assignment_id: UUID | None,
        required_action: str,
        received_at: datetime,
    ) -> AssignmentProjection:
        with self._session_factory() as session:
            assignment = session.scalar(
                sa.select(CaseAssignmentRecord).where(
                    CaseAssignmentRecord.tenant_id == tenant_id,
                    sa.true()
                    if assignment_id is None
                    else CaseAssignmentRecord.id == assignment_id,
                    CaseAssignmentRecord.case_id == case_id,
                    CaseAssignmentRecord.membership_id == membership_id,
                    CaseAssignmentRecord.state == "ACTIVE",
                    CaseAssignmentRecord.starts_at <= received_at,
                    sa.or_(
                        CaseAssignmentRecord.ends_at.is_(None),
                        CaseAssignmentRecord.ends_at > received_at,
                    ),
                )
            )
            if assignment is None:
                raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
            if required_action not in assignment.scope_actions_json:
                raise CommandExecutionError("SCOPE_DENIED")
            return AssignmentProjection(id=assignment.id, case_id=assignment.case_id)

    def read_candidates(
        self, *, tenant_id: UUID, evaluated_at: datetime
    ) -> tuple[CapabilityCandidateProjection, ...]:
        with self._session_factory() as session:
            company_id = session.scalar(
                sa.select(EnterpriseCompanyRecord.id).where(
                    EnterpriseCompanyRecord.tenant_id == tenant_id
                )
            )
            if company_id is None:
                return ()
            rows = session.execute(
                sa.select(
                    EnterpriseCapabilityRecord,
                    EnterpriseCapabilityVersionRecord,
                    EnterpriseCapabilityProofLinkRecord,
                    EnterpriseDocumentRecord,
                    EnterpriseDocumentUploadRecord,
                )
                .join(
                    EnterpriseCapabilityVersionRecord,
                    sa.and_(
                        EnterpriseCapabilityVersionRecord.tenant_id == tenant_id,
                        EnterpriseCapabilityVersionRecord.capability_id
                        == EnterpriseCapabilityRecord.id,
                    ),
                )
                .outerjoin(
                    EnterpriseCapabilityProofLinkRecord,
                    sa.and_(
                        EnterpriseCapabilityProofLinkRecord.tenant_id == tenant_id,
                        EnterpriseCapabilityProofLinkRecord.capability_version_id
                        == EnterpriseCapabilityVersionRecord.id,
                    ),
                )
                .outerjoin(
                    EnterpriseDocumentRecord,
                    sa.and_(
                        EnterpriseDocumentRecord.tenant_id == tenant_id,
                        EnterpriseDocumentRecord.id
                        == EnterpriseCapabilityProofLinkRecord.document_id,
                        EnterpriseDocumentRecord.company_id == company_id,
                    ),
                )
                .outerjoin(
                    EnterpriseDocumentUploadRecord,
                    sa.and_(
                        EnterpriseDocumentUploadRecord.tenant_id == tenant_id,
                        EnterpriseDocumentUploadRecord.id
                        == EnterpriseDocumentRecord.storage_object_id,
                        EnterpriseDocumentUploadRecord.document_id == EnterpriseDocumentRecord.id,
                        EnterpriseDocumentUploadRecord.company_id
                        == EnterpriseDocumentRecord.company_id,
                        EnterpriseDocumentUploadRecord.document_kind
                        == EnterpriseDocumentRecord.document_kind,
                        EnterpriseDocumentUploadRecord.sha256 == EnterpriseDocumentRecord.sha256,
                        EnterpriseDocumentUploadRecord.state == "CLEAN",
                    ),
                )
                .where(
                    EnterpriseCapabilityRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityRecord.company_id == company_id,
                )
                .order_by(
                    EnterpriseCapabilityRecord.capability_kind,
                    EnterpriseCapabilityRecord.name,
                    EnterpriseCapabilityVersionRecord.version_number,
                )
            ).all()
            states: dict[UUID, list[str]] = {}
            versions: dict[
                UUID, tuple[EnterpriseCapabilityRecord, EnterpriseCapabilityVersionRecord]
            ] = {}
            for capability, version, link, document, upload in rows:
                versions.setdefault(version.id, (capability, version))
                states.setdefault(version.id, []).append(
                    _source_evidence_state(
                        capability, version, link, document, upload, evaluated_at
                    )
                )
            candidates = []
            for capability, version in versions.values():
                validity: Literal["CURRENT", "EXPIRED"] = (
                    "CURRENT"
                    if capability.state == "ACTIVE"
                    and version.valid_from <= evaluated_at
                    and (version.valid_until is None or version.valid_until > evaluated_at)
                    else "EXPIRED"
                )
                evidence_states = states[version.id]
                evidence: Literal["CURRENT", "EXPIRED", "UNKNOWN"] = (
                    "UNKNOWN"
                    if "UNKNOWN" in evidence_states
                    else "EXPIRED"
                    if "EXPIRED" in evidence_states
                    else "CURRENT"
                )
                candidates.append(
                    CapabilityCandidateProjection(
                        capability_id=capability.id,
                        capability_kind=capability.capability_kind,
                        name=capability.name,
                        version_id=version.id,
                        version_number=version.version_number,
                        title=version.title,
                        valid_from=version.valid_from,
                        valid_until=version.valid_until,
                        validity_state=validity,
                        source_evidence_state=evidence,
                        evaluated_at=evaluated_at,
                    )
                )
            return tuple(candidates)

    def read_assessments(
        self, *, tenant_id: UUID, case_id: UUID, assignment_id: UUID, evaluated_at: datetime
    ) -> CollaboratorCapabilityAssessmentProjection:
        with self._session_factory() as session:
            records = session.scalars(
                sa.select(CaseCapabilityProposalRecord)
                .where(
                    CaseCapabilityProposalRecord.tenant_id == tenant_id,
                    CaseCapabilityProposalRecord.case_id == case_id,
                    CaseCapabilityProposalRecord.assignment_id == assignment_id,
                )
                .order_by(CaseCapabilityProposalRecord.created_at, CaseCapabilityProposalRecord.id)
            ).all()
            source_states: dict[UUID, list[str]] = {}
            source_capabilities: dict[UUID, UUID] = {}
            if records:
                sources = session.execute(
                    sa.select(
                        EnterpriseCapabilityVersionRecord,
                        EnterpriseCapabilityRecord,
                        EnterpriseCapabilityProofLinkRecord,
                        EnterpriseDocumentRecord,
                        EnterpriseDocumentUploadRecord,
                    )
                    .join(
                        EnterpriseCapabilityRecord,
                        sa.and_(
                            EnterpriseCapabilityRecord.tenant_id == tenant_id,
                            EnterpriseCapabilityRecord.id
                            == EnterpriseCapabilityVersionRecord.capability_id,
                        ),
                    )
                    .outerjoin(
                        EnterpriseCapabilityProofLinkRecord,
                        sa.and_(
                            EnterpriseCapabilityProofLinkRecord.tenant_id == tenant_id,
                            EnterpriseCapabilityProofLinkRecord.capability_version_id
                            == EnterpriseCapabilityVersionRecord.id,
                        ),
                    )
                    .outerjoin(
                        EnterpriseDocumentRecord,
                        sa.and_(
                            EnterpriseDocumentRecord.tenant_id == tenant_id,
                            EnterpriseDocumentRecord.id
                            == EnterpriseCapabilityProofLinkRecord.document_id,
                            EnterpriseDocumentRecord.company_id
                            == EnterpriseCapabilityRecord.company_id,
                        ),
                    )
                    .outerjoin(
                        EnterpriseDocumentUploadRecord,
                        sa.and_(
                            EnterpriseDocumentUploadRecord.tenant_id == tenant_id,
                            EnterpriseDocumentUploadRecord.id
                            == EnterpriseDocumentRecord.storage_object_id,
                            EnterpriseDocumentUploadRecord.document_id
                            == EnterpriseDocumentRecord.id,
                            EnterpriseDocumentUploadRecord.company_id
                            == EnterpriseDocumentRecord.company_id,
                            EnterpriseDocumentUploadRecord.document_kind
                            == EnterpriseDocumentRecord.document_kind,
                            EnterpriseDocumentUploadRecord.sha256
                            == EnterpriseDocumentRecord.sha256,
                            EnterpriseDocumentUploadRecord.state == "CLEAN",
                        ),
                    )
                    .where(
                        EnterpriseCapabilityVersionRecord.tenant_id == tenant_id,
                        EnterpriseCapabilityVersionRecord.id.in_(
                            {item.capability_version_id for item in records}
                        ),
                    )
                ).all()
                for version, capability, link, document, upload in sources:
                    source_capabilities[version.id] = capability.id
                    source_states.setdefault(version.id, []).append(
                        _source_evidence_state(
                            capability, version, link, document, upload, evaluated_at
                        )
                    )
            proposals = []
            for item in records:
                states = source_states.get(item.capability_version_id, [])
                state: Literal["CURRENT", "EXPIRED", "UNKNOWN"] = "UNKNOWN"
                if (
                    states
                    and "UNKNOWN" not in states
                    and source_capabilities[item.capability_version_id] == item.capability_id
                ):
                    state = "EXPIRED" if "EXPIRED" in states else "CURRENT"
                proposals.append(
                    CapabilityProposalProjection(
                        proposal_id=item.id,
                        case_id=item.case_id,
                        assignment_id=item.assignment_id,
                        capability_id=item.capability_id,
                        capability_version_id=item.capability_version_id,
                        requirement_id=item.requirement_id,
                        task_id=item.task_id,
                        state=item.state,
                        validity_state=item.validity_state,
                        justification=item.justification,
                        source_locator=item.source_locator,
                        source_evidence_state=state,
                        source_evidence_evaluated_at=evaluated_at,
                    )
                )
            gaps = tuple(
                CapabilityGapProjection(
                    gap_id=item.id,
                    case_id=item.case_id,
                    assignment_id=item.assignment_id,
                    capability_id=item.capability_id,
                    requirement_id=item.requirement_id,
                    task_id=item.task_id,
                    gap_kind=item.gap_kind,
                    severity=item.severity,
                    reason=item.reason,
                    source_locator=item.source_locator,
                    recommended_action=item.recommended_action,
                )
                for item in session.scalars(
                    sa.select(CaseCapabilityGapRecord)
                    .where(
                        CaseCapabilityGapRecord.tenant_id == tenant_id,
                        CaseCapabilityGapRecord.case_id == case_id,
                        CaseCapabilityGapRecord.assignment_id == assignment_id,
                    )
                    .order_by(CaseCapabilityGapRecord.created_at, CaseCapabilityGapRecord.id)
                ).all()
            )
        return CollaboratorCapabilityAssessmentProjection(proposals=tuple(proposals), gaps=gaps)

    def read_proposal_source_evidence(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        case_id: UUID,
        assignment_id: UUID,
        proposal_ids: set[UUID],
        evaluated_at: datetime,
    ) -> dict[UUID, CapabilityProposalSourceEvidence]:
        """Resolve exact proposal proof state and immutable proof identities."""
        if not proposal_ids:
            return {}
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
        capability_ids = {item.capability_version_id: item.capability_id for item in proposals}
        rows = session.execute(
            sa.select(
                EnterpriseCapabilityVersionRecord,
                EnterpriseCapabilityRecord,
                EnterpriseCapabilityProofLinkRecord,
                EnterpriseDocumentRecord,
                EnterpriseDocumentUploadRecord,
            )
            .join(
                EnterpriseCapabilityRecord,
                sa.and_(
                    EnterpriseCapabilityRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityRecord.id
                    == EnterpriseCapabilityVersionRecord.capability_id,
                ),
            )
            .outerjoin(
                EnterpriseCapabilityProofLinkRecord,
                sa.and_(
                    EnterpriseCapabilityProofLinkRecord.tenant_id == tenant_id,
                    EnterpriseCapabilityProofLinkRecord.capability_version_id
                    == EnterpriseCapabilityVersionRecord.id,
                ),
            )
            .outerjoin(
                EnterpriseDocumentRecord,
                sa.and_(
                    EnterpriseDocumentRecord.tenant_id == tenant_id,
                    EnterpriseDocumentRecord.id == EnterpriseCapabilityProofLinkRecord.document_id,
                    EnterpriseDocumentRecord.company_id == EnterpriseCapabilityRecord.company_id,
                ),
            )
            .outerjoin(
                EnterpriseDocumentUploadRecord,
                sa.and_(
                    EnterpriseDocumentUploadRecord.tenant_id == tenant_id,
                    EnterpriseDocumentUploadRecord.id == EnterpriseDocumentRecord.storage_object_id,
                    EnterpriseDocumentUploadRecord.document_id == EnterpriseDocumentRecord.id,
                    EnterpriseDocumentUploadRecord.company_id
                    == EnterpriseDocumentRecord.company_id,
                    EnterpriseDocumentUploadRecord.document_kind
                    == EnterpriseDocumentRecord.document_kind,
                    EnterpriseDocumentUploadRecord.sha256 == EnterpriseDocumentRecord.sha256,
                    EnterpriseDocumentUploadRecord.state == "CLEAN",
                ),
            )
            .where(
                EnterpriseCapabilityVersionRecord.tenant_id == tenant_id,
                EnterpriseCapabilityVersionRecord.id.in_(capability_ids),
            )
        ).all()
        states: dict[UUID, list[str]] = {}
        capabilities: dict[UUID, UUID] = {}
        proof_refs: dict[UUID, list[tuple[UUID, str]]] = {}
        for version, capability, link, document, upload in rows:
            capabilities[version.id] = capability.id
            state = _source_evidence_state(
                capability, version, link, document, upload, evaluated_at
            )
            states.setdefault(version.id, []).append(state)
            if state == "CURRENT" and document is not None:
                proof_refs.setdefault(version.id, []).append((document.id, document.sha256))
        result: dict[UUID, CapabilityProposalSourceEvidence] = {}
        for proposal in proposals:
            evidence_states = states.get(proposal.capability_version_id, [])
            evidence_state: Literal["CURRENT", "EXPIRED", "UNKNOWN"] = "UNKNOWN"
            if (
                evidence_states
                and "UNKNOWN" not in evidence_states
                and capabilities.get(proposal.capability_version_id) == proposal.capability_id
            ):
                evidence_state = "EXPIRED" if "EXPIRED" in evidence_states else "CURRENT"
            refs = (
                tuple(sorted(set(proof_refs.get(proposal.capability_version_id, []))))
                if evidence_state == "CURRENT"
                else ()
            )
            result[proposal.id] = CapabilityProposalSourceEvidence(
                state=evidence_state, proof_refs=refs
            )
        return result


def _source_evidence_state(
    capability: EnterpriseCapabilityRecord,
    version: EnterpriseCapabilityVersionRecord,
    link: EnterpriseCapabilityProofLinkRecord | None,
    document: EnterpriseDocumentRecord | None,
    upload: EnterpriseDocumentUploadRecord | None,
    evaluated_at: datetime,
) -> Literal["CURRENT", "EXPIRED", "UNKNOWN"]:
    """Metadata eligibility only; never retrieval, reservation or external confirmation."""
    if (
        capability.state != "ACTIVE"
        or version.valid_from > evaluated_at
        or link is None
        or link.relation_label != "SUPPORTS_CAPABILITY"
        or document is None
        or upload is None
        or upload.scan_verdict != "CLEAN"
        or document.issued_at > evaluated_at
        or document.verification_status not in {"VALIDATED", "EXPIRED"}
    ):
        return "UNKNOWN"
    if (
        document.verification_status == "EXPIRED"
        or (version.valid_until is not None and version.valid_until <= evaluated_at)
        or (document.expires_at is not None and document.expires_at <= evaluated_at)
    ):
        return "EXPIRED"
    return "CURRENT"
