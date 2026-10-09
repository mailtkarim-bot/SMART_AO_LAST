from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseConsultationLinkRecord, CaseRecord
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_rc_analysis import (
    DceRcAnalysisRunRecord,
    DceRcRequirementObservationRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord,
    DceRequirementRecord,
)
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.enterprise.infrastructure.models import EnterpriseCompanyRecord
from app.modules.membership.application.collab_capability import (
    CollaboratorCapabilityAssessmentService,
    collaborator_capability_handlers,
)
from app.modules.membership.application.collab_capability_commands import (
    ProposeCapabilityForCaseCommand,
    ReportCapabilityGapCommand,
)
from app.modules.membership.infrastructure.collab_capability_reader import (
    SqlAlchemyCollaboratorCapabilityReader,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord, TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    AssignmentScope,
    DataClassification,
    MembershipState,
)
from app.platform.security.models import (
    CaseAssignmentRecord,
    CaseCapabilityGapRecord,
    CaseCapabilityProposalRecord,
    CollaboratorTaskRecord,
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
    IdentityRecord,
    TenantMembershipRecord,
)
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolate_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _seed(session_factory: sessionmaker[Session], *, include_scope: bool = True):
    tenant_id, identity_id, membership_id = uuid4(), uuid4(), uuid4()
    consultation_id, dce_version_id = uuid4(), uuid4()
    analysis_id, observation_id, run_id, requirement_id = uuid4(), uuid4(), uuid4(), uuid4()
    case_id, assignment_id = uuid4(), uuid4()
    company_id, capability_id, version_id = uuid4(), uuid4(), uuid4()
    actions = (
        [
            Capability.PREPARATION_CAPABILITY_PROPOSE.value,
            Capability.PREPARATION_CAPABILITY_GAP_REPORT.value,
        ]
        if include_scope
        else [Capability.WORK_TASK_READ.value]
    )
    with session_factory.begin() as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"tenant-{tenant_id.hex[:12]}", lifecycle="ACTIVE"),
                IdentityRecord(
                    id=identity_id,
                    email_normalized=f"collab-{identity_id.hex[:12]}@example.test",
                    lifecycle="ACTIVE",
                    email_verified_at=NOW,
                ),
                TenantMembershipRecord(
                    id=membership_id,
                    tenant_id=tenant_id,
                    identity_id=identity_id,
                    role="COLLABORATEUR",
                    state="ACTIVE",
                    activated_at=NOW,
                    revoked_at=None,
                ),
            ]
        )
        session.flush()
        session.add(
            ConsultationRecord(
                id=consultation_id,
                tenant_id=tenant_id,
                aggregate_revision=0,
                functional_identity_hash="a" * 64,
                buyer_legal_name="Acheteur test",
                buyer_normalized_id=None,
                external_reference=None,
                object_label="Objet test",
                location_label=None,
                source_channel="MANUAL",
                source_reference=None,
                source_received_at=NOW,
                lifecycle="OPEN",
                freshness="CURRENT",
                metadata_history_json=[],
                created_by_actor_id=identity_id,
                updated_by_actor_id=identity_id,
            )
        )
        session.add(
            DceVersionRecord(
                id=dce_version_id,
                tenant_id=tenant_id,
                aggregate_revision=0,
                consultation_id=consultation_id,
                corpus_hash="b" * 64,
                predecessor_dce_version_id=None,
                provenance_channel="TEST",
                provenance_reference="test",
                provenance_url=None,
                source_received_at=NOW,
                lifecycle="ADMITTED",
                integrity="VERIFIED",
                classification_readiness="CLASSIFIED",
                analysis_readiness="READY_FOR_ANALYSIS",
                withdrawal_source=None,
                withdrawal_reason=None,
                superseded_at=None,
                withdrawn_at=None,
                created_by_actor_id=identity_id,
                updated_by_actor_id=identity_id,
            )
        )
        session.flush()
        session.add_all(
            [
                DceRcAnalysisRunRecord(
                    id=analysis_id,
                    tenant_id=tenant_id,
                    dce_version_id=dce_version_id,
                    input_manifest_sha256="c" * 64,
                    analyzer_id="test",
                    analyzer_version="1",
                    status="COMPLETED",
                    source_fragment_count=1,
                    source_char_count=1,
                    failure_code=None,
                ),
                DceRcRequirementObservationRecord(
                    id=observation_id,
                    tenant_id=tenant_id,
                    analysis_id=analysis_id,
                    dce_version_id=dce_version_id,
                    requirement_kind="RC_DOCUMENT_CANDIDATURE",
                    directive="REQUIRED_SIGNAL",
                    rule_id="TEST_RULE",
                    rule_version="1",
                    fragment_id=uuid4(),
                    start_byte_offset=0,
                    end_byte_offset=1,
                    excerpt="X",
                ),
            ]
        )
        session.flush()
        session.add(
            DceRequirementMaterializationRunRecord(
                id=run_id,
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                dce_rc_analysis_id=analysis_id,
                input_manifest_sha256="d" * 64,
                materializer_id="test",
                materializer_version="1",
                status="COMPLETED",
                source_observation_count=1,
                failure_code=None,
            )
        )
        session.flush()
        session.add(
            DceRequirementRecord(
                id=requirement_id,
                tenant_id=tenant_id,
                requirements_run_id=run_id,
                dce_version_id=dce_version_id,
                source_observation_id=observation_id,
                requirement_type="CANDIDATURE_DOCUMENT",
                directive_signal="REQUIRED_SIGNAL",
                confirmation_status="PENDING_HUMAN_CONFIRMATION",
                uncertainty_status="SOURCE_SIGNAL_ONLY",
            )
        )
        session.add(
            CaseRecord(
                id=case_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="e" * 64,
                title="Affaire capacité",
                object_description=None,
                business_origin="OPPORTUNITY",
                origin_reference_id=None,
                origin_rationale=None,
                consultation_id=consultation_id,
                scope_kind="CUSTOM",
                scope_json={},
                scope_fingerprint="f" * 64,
                applicable_dce_version_id=dce_version_id,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="ASSIGNED",
                stopped_reason=None,
                stopped_at=None,
                archived_reason=None,
                archived_at=None,
                created_by_actor_id=identity_id,
                updated_by_actor_id=identity_id,
            )
        )
        session.add(
            CaseAssignmentRecord(
                id=assignment_id,
                tenant_id=tenant_id,
                membership_id=membership_id,
                case_id=case_id,
                aggregate_revision=0,
                state="ACTIVE",
                scope_actions_json=actions,
                scope_classifications_json=[DataClassification.INTERNAL_OPERATIONAL.value],
                granted_by_membership_id=membership_id,
                granted_at=NOW,
                starts_at=NOW,
                ends_at=None,
                ended_at=None,
            )
        )
        session.add(
            EnterpriseCompanyRecord(
                id=company_id,
                tenant_id=tenant_id,
                aggregate_revision=0,
                legal_name="Entreprise test",
                trade_name=None,
                siren="123456789",
                siret="12345678900011",
                vat_number="FR12123456789",
                address_line1="1 rue test",
                postal_code="75001",
                city="Paris",
                country_code="FR",
            )
        )
        session.flush()
        session.add(
            EnterpriseCapabilityRecord(
                id=capability_id,
                tenant_id=tenant_id,
                company_id=company_id,
                aggregate_revision=1,
                capability_kind="QUALIFICATION",
                name="Qualification test",
                summary="Capacité de test",
                state="ACTIVE",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        session.add(
            EnterpriseCapabilityVersionRecord(
                id=version_id,
                tenant_id=tenant_id,
                capability_id=capability_id,
                version_number=1,
                title="Version actuelle",
                description="Preuve de qualification test",
                valid_from=NOW - timedelta(days=1),
                valid_until=NOW + timedelta(days=365),
                usage_scope="Réponse technique attribuée",
                created_by_membership_id=membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
    actor = ActorContext(
        actor_id=identity_id,
        identity_id=identity_id,
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.COLLABORATEUR,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        assigned_case_ids=frozenset({case_id}),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
        assignment_scopes=(
            AssignmentScope(
                case_id=case_id,
                allowed_actions=frozenset(actions),
                allowed_classifications=frozenset({DataClassification.INTERNAL_OPERATIONAL}),
            ),
        ),
    )
    return actor, assignment_id, case_id, requirement_id, capability_id, version_id


def _service(factory: sessionmaker[Session]) -> CollaboratorCapabilityAssessmentService:
    return CollaboratorCapabilityAssessmentService(
        reader=SqlAlchemyCollaboratorCapabilityReader(factory),
        dispatcher=CommandDispatcher(
            session_factory=factory,
            handlers=collaborator_capability_handlers(),
        ),
        policy=AuthorizationPolicy(),
    )


def _proposal(
    *,
    assignment_id: UUID,
    case_id: UUID,
    requirement_id: UUID,
    capability_id: UUID,
    version_id: UUID,
):
    return ProposeCapabilityForCaseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        proposal_id=uuid4(),
        case_id=case_id,
        assignment_id=assignment_id,
        capability_id=capability_id,
        capability_version_id=version_id,
        requirement_id=requirement_id,
        justification="Cette qualification correspond au périmètre demandé.",
        source_locator="RC p. 8",
    )


def _gap(*, assignment_id: UUID, case_id: UUID, requirement_id: UUID, capability_id: UUID):
    return ReportCapabilityGapCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        gap_id=uuid4(),
        case_id=case_id,
        assignment_id=assignment_id,
        capability_id=capability_id,
        requirement_id=requirement_id,
        gap_kind="EXPIRED",
        severity="IMPORTANT",
        reason="La preuve actuellement connue doit être renouvelée.",
        source_locator="RC p. 9",
        recommended_action="Demander une preuve actuelle au patron.",
    )


@pytest.mark.db
@pytest.mark.security
def test_proposal_and_gap_are_rebac_scoped_idempotent_and_projected(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    service = _service(session_factory)
    proposal = _proposal(
        assignment_id=assignment_id,
        case_id=case_id,
        requirement_id=requirement_id,
        capability_id=capability_id,
        version_id=version_id,
    )
    gap = _gap(
        assignment_id=assignment_id,
        case_id=case_id,
        requirement_id=requirement_id,
        capability_id=capability_id,
    )

    proposed = service.propose_capability(actor=actor, command=proposal, now=NOW)
    replay = service.propose_capability(actor=actor, command=proposal, now=NOW)
    reported = service.report_gap(actor=actor, command=gap, now=NOW)
    projection = service.read_assessments(
        actor=actor, case_id=case_id, assignment_id=assignment_id, now=NOW
    )

    assert service.read_assessments(actor=actor, case_id=case_id, now=NOW) == projection
    assert proposed.result_code == "CAPABILITY_PROPOSED_FOR_CASE"
    assert replay.replayed is True
    assert reported.result_code == "CAPABILITY_GAP_REPORTED"
    assert projection.proposals[0].validity_state == "CURRENT"
    assert projection.gaps[0].gap_kind == "EXPIRED"
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseCapabilityProposalRecord))
            == 1
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(CaseCapabilityGapRecord)) == 1
        events = list(session.scalars(sa.select(DomainEventRecord)))
        outbox = list(session.scalars(sa.select(OutboxMessageRecord)))
    assert len(events) == 2
    assert len(outbox) == 2
    assert all("justification" not in event.payload_json["data"] for event in events)
    assert all("reason" not in message.payload_json["data"] for message in outbox)


@pytest.mark.db
@pytest.mark.security
def test_proposal_and_gap_refuse_missing_scope_foreign_capability_and_financial_text(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory, include_scope=False
    )
    service = _service(session_factory)
    with pytest.raises(PermissionError, match="AUTHORIZATION_DENIED"):
        service.propose_capability(
            actor=actor,
            command=_proposal(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=requirement_id,
                capability_id=capability_id,
                version_id=version_id,
            ),
            now=NOW,
        )

    actor, assignment_id, case_id, requirement_id, _, _ = _seed(session_factory)
    with pytest.raises(CommandExecutionError, match="NOT_FOUND_OR_FORBIDDEN"):
        service.report_gap(
            actor=actor,
            command=_gap(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=requirement_id,
                capability_id=uuid4(),
            ),
            now=NOW,
        )

    with pytest.raises(ValueError, match="FINANCIAL_DATA_FORBIDDEN"):
        ProposeCapabilityForCaseCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            proposal_id=uuid4(),
            case_id=case_id,
            assignment_id=assignment_id,
            capability_id=capability_id,
            capability_version_id=version_id,
            requirement_id=requirement_id,
            justification="Inclure le prix et la marge.",
        )


@pytest.mark.db
@pytest.mark.security
def test_append_only_and_tenant_neutrality(session_factory: sessionmaker[Session]) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    service = _service(session_factory)
    service.propose_capability(
        actor=actor,
        command=_proposal(
            assignment_id=assignment_id,
            case_id=case_id,
            requirement_id=requirement_id,
            capability_id=capability_id,
            version_id=version_id,
        ),
        now=NOW,
    )
    with session_factory() as session, pytest.raises(sa.exc.ProgrammingError), session.begin():
        session.execute(
            sa.delete(CaseCapabilityProposalRecord).where(
                CaseCapabilityProposalRecord.case_id == case_id
            )
        )

    _, other_assignment, other_case, _, _, _ = _seed(session_factory)
    with pytest.raises(PermissionError, match="AUTHORIZATION_DENIED"):
        service.read_assessments(
            actor=actor,
            case_id=other_case,
            assignment_id=other_assignment,
            now=NOW,
        )


@pytest.mark.parametrize(
    "change", ["suspended", "future", "ended", "scope", "tenant", "member", "case"]
)
def test_case_only_assignment_resolution_preserves_boundaries(session_factory, change):
    actor, assignment_id, case_id, *_ = _seed(session_factory)
    reader = SqlAlchemyCollaboratorCapabilityReader(session_factory)
    params = dict(
        tenant_id=actor.tenant_id,
        membership_id=actor.membership_id,
        case_id=case_id,
        assignment_id=None,
        required_action=Capability.PREPARATION_CAPABILITY_PROPOSE.value,
        received_at=NOW,
    )
    if change in {"tenant", "member", "case"}:
        params[{"tenant": "tenant_id", "member": "membership_id", "case": "case_id"}[change]] = (
            uuid4()
        )
    else:
        with session_factory.begin() as session:
            assignment = session.get(CaseAssignmentRecord, assignment_id)
            if change == "suspended":
                assignment.state = "SUSPENDED"
            if change == "future":
                assignment.starts_at = NOW + timedelta(seconds=1)
            if change == "ended":
                assignment.starts_at = NOW - timedelta(seconds=1)
                assignment.ends_at = NOW
            if change == "scope":
                assignment.scope_actions_json = [Capability.WORK_TASK_READ.value]
    with pytest.raises(
        CommandExecutionError,
        match="SCOPE_DENIED" if change == "scope" else "NOT_FOUND_OR_FORBIDDEN",
    ):
        reader.require_active_assignment(**params)


def _clone_requirement_for_another_consultation(
    session_factory: sessionmaker[Session], requirement_id: UUID
) -> UUID:
    with session_factory.begin() as session:
        source_requirement = session.get(DceRequirementRecord, requirement_id)
        source_run = session.get(
            DceRequirementMaterializationRunRecord, source_requirement.requirements_run_id
        )
        source_observation = session.get(
            DceRcRequirementObservationRecord, source_requirement.source_observation_id
        )
        source_analysis = session.get(DceRcAnalysisRunRecord, source_observation.analysis_id)
        source_version = session.get(DceVersionRecord, source_requirement.dce_version_id)
        source_consultation = session.get(ConsultationRecord, source_version.consultation_id)

        consultation_id, version_id, analysis_id = uuid4(), uuid4(), uuid4()
        observation_id, run_id, foreign_requirement_id = uuid4(), uuid4(), uuid4()
        consultation_values = {
            column.name: getattr(source_consultation, column.name)
            for column in ConsultationRecord.__table__.columns
        }
        consultation_values.update(
            id=consultation_id,
            functional_identity_hash=uuid4().hex + uuid4().hex,
        )
        consultation = ConsultationRecord(**consultation_values)
        version_values = {
            column.name: getattr(source_version, column.name)
            for column in DceVersionRecord.__table__.columns
        }
        version_values.update(
            id=version_id,
            consultation_id=consultation_id,
            predecessor_dce_version_id=None,
            corpus_hash=uuid4().hex + uuid4().hex,
        )
        version = DceVersionRecord(**version_values)
        analysis_values = {
            column.name: getattr(source_analysis, column.name)
            for column in DceRcAnalysisRunRecord.__table__.columns
        }
        analysis_values.update(id=analysis_id, dce_version_id=version_id)
        analysis = DceRcAnalysisRunRecord(**analysis_values)
        observation_values = {
            column.name: getattr(source_observation, column.name)
            for column in DceRcRequirementObservationRecord.__table__.columns
        }
        observation_values.update(
            id=observation_id,
            analysis_id=analysis_id,
            dce_version_id=version_id,
            fragment_id=uuid4(),
        )
        observation = DceRcRequirementObservationRecord(**observation_values)
        run_values = {
            column.name: getattr(source_run, column.name)
            for column in DceRequirementMaterializationRunRecord.__table__.columns
        }
        run_values.update(id=run_id, dce_version_id=version_id, dce_rc_analysis_id=analysis_id)
        run = DceRequirementMaterializationRunRecord(**run_values)
        foreign_requirement = DceRequirementRecord(
            **{
                column.name: getattr(source_requirement, column.name)
                for column in DceRequirementRecord.__table__.columns
                if column.name
                not in {"id", "dce_version_id", "requirements_run_id", "source_observation_id"}
            },
            id=foreign_requirement_id,
            dce_version_id=version_id,
            requirements_run_id=run_id,
            source_observation_id=observation_id,
        )
        for source_row in (consultation, version, analysis, observation, run, foreign_requirement):
            session.add(source_row)
            session.flush()
        return foreign_requirement_id


def test_capability_commands_reject_requirement_from_another_case_consultation(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    foreign_requirement_id = _clone_requirement_for_another_consultation(
        session_factory, requirement_id
    )
    service = _service(session_factory)

    for command, execute in (
        (
            _proposal(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=foreign_requirement_id,
                capability_id=capability_id,
                version_id=version_id,
            ),
            service.propose_capability,
        ),
        (
            _gap(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=foreign_requirement_id,
                capability_id=capability_id,
            ),
            service.report_gap,
        ),
    ):
        with pytest.raises(CommandExecutionError, match="NOT_FOUND_OR_FORBIDDEN"):
            execute(actor=actor, command=command, now=NOW)

    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseCapabilityProposalRecord))
            == 0
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(CaseCapabilityGapRecord)) == 0
        assert session.scalar(sa.select(sa.func.count()).select_from(DomainEventRecord)) == 0
        assert session.scalar(sa.select(sa.func.count()).select_from(OutboxMessageRecord)) == 0


def _clone_requirement_on_same_dce(
    session_factory: sessionmaker[Session], requirement_id: UUID
) -> UUID:
    with session_factory.begin() as session:
        source = session.get(DceRequirementRecord, requirement_id)
        observation = session.get(DceRcRequirementObservationRecord, source.source_observation_id)
        new_observation_id, new_requirement_id = uuid4(), uuid4()
        observation_values = {
            column.name: getattr(observation, column.name)
            for column in DceRcRequirementObservationRecord.__table__.columns
        }
        observation_values.update(id=new_observation_id, fragment_id=uuid4())
        session.add(DceRcRequirementObservationRecord(**observation_values))
        session.flush()
        requirement_values = {
            column.name: getattr(source, column.name)
            for column in DceRequirementRecord.__table__.columns
        }
        requirement_values.update(id=new_requirement_id, source_observation_id=new_observation_id)
        session.add(DceRequirementRecord(**requirement_values))
        return new_requirement_id


@pytest.mark.db
@pytest.mark.security
def test_capability_commands_refuse_requirement_different_from_task_source(
    session_factory: sessionmaker[Session],
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    other_requirement_id = _clone_requirement_on_same_dce(session_factory, requirement_id)
    task_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            CollaboratorTaskRecord(
                id=task_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                assignment_id=assignment_id,
                requirement_id=requirement_id,
                task_kind="SYNTHETIC_REQUIREMENT",
                title="Fixture task",
                objective="Source consistency test",
                priority="NORMAL",
                state="READY",
                functional_key=str(uuid4()),
                aggregate_revision=0,
            )
        )
    service = _service(session_factory)
    commands = (
        (
            _proposal(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=other_requirement_id,
                capability_id=capability_id,
                version_id=version_id,
            ).model_copy(update={"task_id": task_id}),
            service.propose_capability,
        ),
        (
            _gap(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=other_requirement_id,
                capability_id=capability_id,
            ).model_copy(update={"task_id": task_id}),
            service.report_gap,
        ),
    )
    for command, execute in commands:
        with pytest.raises(CommandExecutionError, match="NOT_FOUND_OR_FORBIDDEN"):
            execute(actor=actor, command=command, now=NOW)


@pytest.mark.parametrize("case_change", ["no_dce", "review_required", "consultation_unlinked"])
@pytest.mark.db
@pytest.mark.security
def test_capability_commands_reject_missing_or_obsolete_case_dce(
    session_factory: sessionmaker[Session], case_change: str
) -> None:
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    with session_factory.begin() as session:
        case = session.get(CaseRecord, case_id)
        if case_change == "no_dce":
            case.applicable_dce_version_id = None
            case.dce_freshness = "NO_DCE"
        elif case_change == "review_required":
            case.dce_freshness = "REVIEW_REQUIRED"
        else:
            session.add(
                CaseConsultationLinkRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    case_id=case_id,
                    consultation_id=case.consultation_id,
                    scope_snapshot_json={},
                    rationale="Synthetic historical link only",
                    is_current=False,
                    created_by_actor_id=actor.identity_id,
                )
            )
    service = _service(session_factory)
    commands = (
        (
            _proposal(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=requirement_id,
                capability_id=capability_id,
                version_id=version_id,
            ),
            service.propose_capability,
        ),
        (
            _gap(
                assignment_id=assignment_id,
                case_id=case_id,
                requirement_id=requirement_id,
                capability_id=capability_id,
            ),
            service.report_gap,
        ),
    )
    for command, execute in commands:
        with pytest.raises(CommandExecutionError, match="NOT_FOUND_OR_FORBIDDEN"):
            execute(actor=actor, command=command, now=NOW)
