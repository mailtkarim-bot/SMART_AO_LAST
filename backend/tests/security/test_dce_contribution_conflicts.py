from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.application.contribution_conflicts import (
    DceContributionConflictService,
    RecordContributionCommand,
)
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_contributions import (
    DceRequirementConflictRecord,
    DceRequirementConflictResolutionRecord,
    DceRequirementContributionRecord,
)
from app.modules.dce.infrastructure.models.dce_rc_analysis import (
    DceRcAnalysisRunRecord,
    DceRcRequirementObservationRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord,
    DceRequirementRecord,
)
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.platform.persistence.models import TenantRecord
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 9, 20, 14, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolate_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _seed(
    session_factory: sessionmaker[Session],
) -> tuple[UUID, UUID, ActorContext]:
    tenant_id, actor_id, requirement_id = uuid4(), uuid4(), uuid4()
    consultation_id, version_id, analysis_id, observation_id, run_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with session_factory.begin() as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"contrib-{tenant_id.hex[:12]}", lifecycle="ACTIVE")
        )
        session.flush()
        session.add(
            ConsultationRecord(
                id=consultation_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="a" * 64,
                buyer_legal_name="Ville test",
                buyer_normalized_id="VILLE-TEST",
                external_reference="AO-CONTRIB",
                object_label="Objet test",
                location_label="Lille",
                source_channel="MANUAL_UPLOAD",
                source_reference="fixture",
                source_received_at=NOW,
                lifecycle="OPEN",
                freshness="CURRENT",
                metadata_history_json=[],
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
        session.add(
            DceVersionRecord(
                id=version_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                consultation_id=consultation_id,
                corpus_hash="b" * 64,
                predecessor_dce_version_id=None,
                provenance_channel="MANUAL_UPLOAD",
                provenance_reference=None,
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
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
        session.flush()
        session.add(
            DceRcAnalysisRunRecord(
                id=analysis_id,
                tenant_id=tenant_id,
                dce_version_id=version_id,
                input_manifest_sha256="c" * 64,
                analyzer_id="test",
                analyzer_version="1",
                status="COMPLETED",
                source_fragment_count=1,
                source_char_count=1,
                failure_code=None,
            )
        )
        session.add(
            DceRcRequirementObservationRecord(
                id=observation_id,
                tenant_id=tenant_id,
                analysis_id=analysis_id,
                dce_version_id=version_id,
                requirement_kind="RC_DOCUMENT_CANDIDATURE",
                directive="REQUIRED_SIGNAL",
                rule_id="RULE",
                rule_version="1",
                fragment_id=uuid4(),
                start_byte_offset=0,
                end_byte_offset=1,
                excerpt="document",
            )
        )
        session.add(
            DceRequirementMaterializationRunRecord(
                id=run_id,
                tenant_id=tenant_id,
                dce_version_id=version_id,
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
                dce_version_id=version_id,
                source_observation_id=observation_id,
                requirement_type="CANDIDATURE_DOCUMENT",
                directive_signal="REQUIRED_SIGNAL",
                confirmation_status="PENDING_HUMAN_CONFIRMATION",
                uncertainty_status="SOURCE_SIGNAL_ONLY",
            )
        )
    actor = ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )
    return tenant_id, requirement_id, actor


def _command(requirement_id: UUID, *, proposal: str, contribution_id: UUID | None = None):
    return RecordContributionCommand(
        contribution_id=contribution_id or uuid4(),
        requirement_id=requirement_id,
        expected_confirmation_revision=0,
        source_locator=f"CCAP/p.{proposal}",
        basis_fingerprint=("a" if proposal == "one" else "b") * 64,
        proposed_outcome="CONFIRMED" if proposal == "one" else "REVIEW_REQUIRED",
        proposed_reason_code="SOURCE_REVIEWED" if proposal == "one" else "CONTRADICTORY_DCE",
        command_id=uuid4(),
        idempotency_key=uuid4(),
    )


@pytest.mark.db
@pytest.mark.security
def test_concurrent_proposals_are_retained_blocked_and_resolvable(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, requirement_id, actor = _seed(session_factory)
    service = DceContributionConflictService(session_factory=session_factory)
    first = service.record(actor=actor, command=_command(requirement_id, proposal="one"), now=NOW)
    second = service.record(actor=actor, command=_command(requirement_id, proposal="two"), now=NOW)

    assert first.conflict_id is None
    assert second.conflict_id is not None
    with pytest.raises(ValueError, match="DCE_REQUIREMENT_CONFLICT_OPEN"):
        service.require_no_open_conflict(tenant_id=tenant_id, requirement_id=requirement_id)
    resolution_id = service.resolve(
        actor=actor,
        conflict_id=second.conflict_id,
        selected_contribution_id=first.contribution_id,
        resolution_id=uuid4(),
        command_id=uuid4(),
        idempotency_key=uuid4(),
        reason="Le premier extrait est celui retenu.",
        now=NOW,
    )
    assert resolution_id
    service.require_no_open_conflict(tenant_id=tenant_id, requirement_id=requirement_id)
    with Session(database_engine) as session:
        contributions = session.scalars(sa.select(DceRequirementContributionRecord)).all()
        conflicts = session.scalars(sa.select(DceRequirementConflictRecord)).all()
        resolutions = session.scalars(sa.select(DceRequirementConflictResolutionRecord)).all()
        assert len(contributions) == 2 and len(conflicts) == 1 and len(resolutions) == 1


@pytest.mark.db
@pytest.mark.security
def test_contribution_replay_does_not_reveal_or_create_another_proposal(
    session_factory: sessionmaker[Session],
) -> None:
    _, requirement_id, actor = _seed(session_factory)
    service = DceContributionConflictService(session_factory=session_factory)
    command = _command(requirement_id, proposal="one")
    first = service.record(actor=actor, command=command, now=NOW)
    replay = service.record(actor=actor, command=command, now=NOW)
    assert replay.replayed is True and replay.contribution_id == first.contribution_id
