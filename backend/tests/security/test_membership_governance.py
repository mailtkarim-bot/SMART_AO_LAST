from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.platform.persistence.models import TenantRecord
from app.platform.security.authenticated_context import AuthenticationContextResolver
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from app.platform.security.continuity import (
    ContinuityGovernanceService,
    HandoverAcceptCommand,
    HandoverRequestCommand,
    RecoveryCommand,
)
from app.platform.security.membership_governance import (
    ChangeOwnerCommand,
    GrantDelegationCommand,
    MembershipGovernanceService,
    SuspendMembershipCommand,
)
from app.platform.security.models import (
    AuthSessionRecord,
    IdentityRecord,
    MembershipSuspensionRecord,
    TenantDelegationEventRecord,
    TenantDelegationRecord,
    TenantHandoverEventRecord,
    TenantHandoverRecord,
    TenantMembershipRecord,
    TenantOwnerChangeRecord,
    TenantOwnerRecord,
    TenantRecoveryRecord,
)
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 9, 20, 12, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolate_governance_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _actor(*, tenant_id: UUID, membership_id: UUID) -> ActorContext:
    return ActorContext(
        actor_id=membership_id,
        identity_id=uuid4(),
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )


def _seed(database_engine: sa.Engine) -> tuple[UUID, UUID, UUID, UUID]:
    tenant_id, owner_id, patron_id, member_id = (uuid4() for _ in range(4))
    owner_identity, patron_identity, member_identity = (uuid4() for _ in range(3))
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"tenant-{tenant_id.hex[:12]}", lifecycle="ACTIVE")
        )
        for identity_id in (owner_identity, patron_identity, member_identity):
            session.add(
                IdentityRecord(
                    id=identity_id,
                    email_normalized=f"{identity_id.hex}@example.test",
                    lifecycle="ACTIVE",
                    email_verified_at=NOW,
                )
            )
        session.flush()
        for membership_id, identity_id, role in (
            (owner_id, owner_identity, "PATRON_ADMIN"),
            (patron_id, patron_identity, "PATRON_ADMIN"),
            (member_id, member_identity, "COLLABORATEUR"),
        ):
            session.add(
                TenantMembershipRecord(
                    id=membership_id,
                    tenant_id=tenant_id,
                    identity_id=identity_id,
                    role=role,
                    state="ACTIVE",
                    activated_at=NOW,
                    revoked_at=None,
                )
            )
        session.flush()
        session.add(
            TenantOwnerRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                membership_id=owner_id,
                designated_by_membership_id=owner_id,
            )
        )
        session.add(
            AuthSessionRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                membership_id=member_id,
                identity_id=member_identity,
                state="ACTIVE",
                auth_strength="MFA",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=24),
                mfa_verified_at=NOW,
                revoked_at=None,
                revoke_reason=None,
            )
        )
        session.commit()
    return tenant_id, owner_id, patron_id, member_id


def _command(
    *, membership_id: UUID, idempotency_key: UUID | None = None
) -> SuspendMembershipCommand:
    return SuspendMembershipCommand(
        suspension_id=uuid4(),
        membership_id=membership_id,
        command_id=uuid4(),
        idempotency_key=idempotency_key or uuid4(),
        reason_code="COMPROMISE_SUSPECTED",
        rationale="Suspension de précaution validée par le propriétaire.",
    )


def _owner_command(*, membership_id: UUID, transfer: bool = False) -> ChangeOwnerCommand:
    return ChangeOwnerCommand(
        change_id=uuid4(),
        new_owner_membership_id=membership_id,
        command_id=uuid4(),
        idempotency_key=uuid4(),
        rationale="Désignation organisationnelle approuvée.",
        transfer=transfer,
    )


def _add_delegate(database_engine: sa.Engine, *, tenant_id: UUID) -> UUID:
    identity_id = uuid4()
    membership_id = uuid4()
    with Session(database_engine) as session:
        session.add(
            IdentityRecord(
                id=identity_id,
                email_normalized=f"{identity_id.hex}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.add(
            TenantMembershipRecord(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=identity_id,
                role="PATRON_DELEGATE",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        session.commit()
    return membership_id


def _add_support(database_engine: sa.Engine, *, tenant_id: UUID) -> UUID:
    identity_id = uuid4()
    membership_id = uuid4()
    with Session(database_engine) as session:
        session.add(
            IdentityRecord(
                id=identity_id,
                email_normalized=f"{identity_id.hex}@support.example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.add(
            TenantMembershipRecord(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=identity_id,
                role="SUPPORT_BREAK_GLASS",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        session.commit()
    return membership_id


def _support_actor(*, tenant_id: UUID, membership_id: UUID) -> ActorContext:
    return ActorContext(
        actor_id=membership_id,
        identity_id=uuid4(),
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.SUPPORT_BREAK_GLASS,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )


@pytest.mark.db
@pytest.mark.security
def test_owner_suspends_member_append_only_revokes_sessions_and_replays_idempotently(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, _, member_id = _seed(database_engine)
    service = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )
    command = _command(membership_id=member_id)

    result = service.suspend(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id), command=command, now=NOW
    )
    replay = service.suspend(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id), command=command, now=NOW
    )

    assert result.replayed is False
    assert result.revoked_session_count == 1
    assert replay == type(replay)(
        suspension_id=result.suspension_id, revoked_session_count=0, replayed=True
    )
    with Session(database_engine) as session:
        membership = session.get(TenantMembershipRecord, member_id)
        suspension = session.scalar(sa.select(MembershipSuspensionRecord))
        auth_session = session.scalar(sa.select(AuthSessionRecord))
        assert membership is not None and membership.state == "SUSPENDED"
        assert suspension is not None and suspension.membership_id == member_id
        assert auth_session is not None and auth_session.state == "REVOKED"
        assert auth_session.revoke_reason == "MEMBERSHIP_SUSPENDED"
        assert auth_session.token_version == 2


@pytest.mark.db
@pytest.mark.security
def test_patron_role_without_organization_ownership_cannot_suspend_member(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, _, patron_id, member_id = _seed(database_engine)
    service = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )

    with pytest.raises(PermissionError, match="ORGANIZATION_OWNER_REQUIRED"):
        service.suspend(
            actor=_actor(tenant_id=tenant_id, membership_id=patron_id),
            command=_command(membership_id=member_id),
            now=NOW,
        )

    with Session(database_engine) as session:
        assert session.get(TenantMembershipRecord, member_id).state == "ACTIVE"
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(MembershipSuspensionRecord)) == 0
        )


@pytest.mark.db
@pytest.mark.security
def test_owner_designation_is_append_only_and_does_not_elevate_business_role(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, patron_id, _ = _seed(database_engine)
    service = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )
    command = _owner_command(membership_id=patron_id)

    result = service.change_owner(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id), command=command, now=NOW
    )
    replay = service.change_owner(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id), command=command, now=NOW
    )

    assert result.action == "DESIGNATED"
    assert replay.replayed is True
    with Session(database_engine) as session:
        target = session.get(TenantMembershipRecord, patron_id)
        ownership = session.scalar(
            sa.select(TenantOwnerRecord).where(
                TenantOwnerRecord.membership_id == patron_id,
                TenantOwnerRecord.ended_at.is_(None),
            )
        )
        change = session.get(TenantOwnerChangeRecord, command.change_id)
        assert target is not None and target.role == "PATRON_ADMIN"
        assert ownership is not None
        assert change is not None and change.action == "DESIGNATED"


@pytest.mark.db
@pytest.mark.security
def test_owner_transfer_ends_previous_projection_without_changing_target_role(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, _, member_id = _seed(database_engine)
    service = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )
    command = _owner_command(membership_id=member_id, transfer=True)

    result = service.change_owner(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id),
        command=command,
        now=NOW,
    )

    assert result.action == "TRANSFERRED"
    with Session(database_engine) as session:
        previous = session.scalar(
            sa.select(TenantOwnerRecord).where(TenantOwnerRecord.membership_id == owner_id)
        )
        target = session.scalar(
            sa.select(TenantOwnerRecord).where(
                TenantOwnerRecord.membership_id == member_id,
                TenantOwnerRecord.ended_at.is_(None),
            )
        )
        target_membership = session.get(TenantMembershipRecord, member_id)
        assert previous is not None and previous.ended_at == NOW
        assert target is not None
        assert target_membership is not None and target_membership.role == "COLLABORATEUR"


@pytest.mark.db
@pytest.mark.security
def test_bounded_delegation_resolves_and_is_invalidated_by_member_suspension(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, _, _ = _seed(database_engine)
    delegate_id = _add_delegate(database_engine, tenant_id=tenant_id)
    service = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )
    grant = GrantDelegationCommand(
        delegation_id=uuid4(),
        delegatee_membership_id=delegate_id,
        capabilities=("consultation.read", "dce.prepare"),
        doors=("P0", "P1"),
        case_ids=(uuid4(),),
        starts_at=NOW,
        expires_at=NOW + timedelta(hours=2),
        command_id=uuid4(),
        idempotency_key=uuid4(),
        rationale="Relève temporaire validée par le Propriétaire.",
    )
    owner_actor = _actor(tenant_id=tenant_id, membership_id=owner_id)

    result = service.grant_delegation(actor=owner_actor, command=grant, now=NOW)
    with Session(database_engine) as session:
        capabilities, case_ids = AuthenticationContextResolver._active_delegation_scope(
            session=session,
            tenant_id=tenant_id,
            membership_id=delegate_id,
            actor_kind=ActorKind.PATRON_DELEGATE,
            now=NOW,
        )
    assert result.replayed is False
    assert capabilities == frozenset({"consultation.read", "dce.prepare"})
    assert case_ids == frozenset(grant.case_ids)

    service.suspend(
        actor=owner_actor,
        command=_command(membership_id=delegate_id),
        now=NOW,
    )
    with Session(database_engine) as session:
        delegation = session.get(TenantDelegationRecord, grant.delegation_id)
        events = session.scalars(
            sa.select(TenantDelegationEventRecord).where(
                TenantDelegationEventRecord.delegation_id == grant.delegation_id
            )
        ).all()
        assert delegation is not None and delegation.state == "REVOKED"
        assert len(events) == 2


@pytest.mark.db
@pytest.mark.security
def test_handover_is_nominative_and_requires_successor_acceptance(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, _, successor_id = _seed(database_engine)
    service = ContinuityGovernanceService(session_factory=session_factory)
    handover = HandoverRequestCommand(
        handover_id=uuid4(),
        successor_membership_id=successor_id,
        assignment_ids=(uuid4(),),
        command_id=uuid4(),
        idempotency_key=uuid4(),
        rationale="Relève nominative avant absence du responsable.",
    )

    requested = service.request_handover(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id), command=handover, now=NOW
    )
    accepted = service.accept_handover(
        actor=_actor(tenant_id=tenant_id, membership_id=successor_id),
        command=HandoverAcceptCommand(
            handover_id=handover.handover_id,
            command_id=uuid4(),
            reason="Je prends la relève des éléments listés.",
        ),
        now=NOW,
    )
    accepted_replay = service.accept_handover(
        actor=_actor(tenant_id=tenant_id, membership_id=successor_id),
        command=HandoverAcceptCommand(
            handover_id=handover.handover_id,
            command_id=uuid4(),
            reason="Relecture idempotente de la prise en charge.",
        ),
        now=NOW,
    )

    assert requested.state == "REQUESTED"
    assert accepted.state == "ACCEPTED"
    assert accepted_replay.replayed is True
    with Session(database_engine) as session:
        record = session.get(TenantHandoverRecord, handover.handover_id)
        successor = session.get(TenantMembershipRecord, successor_id)
        events = session.scalars(
            sa.select(TenantHandoverEventRecord).where(
                TenantHandoverEventRecord.handover_id == handover.handover_id
            )
        ).all()
        assert record is not None and record.state == "ACCEPTED"
        assert successor is not None and successor.role == "COLLABORATEUR"
        assert {event.event_type for event in events} == {"REQUESTED", "ACCEPTED"}


@pytest.mark.db
@pytest.mark.security
def test_last_owner_status_blocks_then_r03_requires_two_support_actors(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    tenant_id, owner_id, patron_id, _ = _seed(database_engine)
    first_support_id = _add_support(database_engine, tenant_id=tenant_id)
    second_support_id = _add_support(database_engine, tenant_id=tenant_id)
    service = ContinuityGovernanceService(session_factory=session_factory)
    governance = MembershipGovernanceService(
        session_factory=session_factory, policy=AuthorizationPolicy()
    )
    assert service.authority_status(tenant_id=tenant_id) == "ACTIVE_OWNER"
    governance.suspend(
        actor=_actor(tenant_id=tenant_id, membership_id=owner_id),
        command=_command(membership_id=owner_id),
        now=NOW,
    )
    assert service.authority_status(tenant_id=tenant_id) == "NO_ACTIVE_OWNER"

    recovery_command = RecoveryCommand(
        recovery_id=uuid4(),
        target_membership_id=patron_id,
        authority_evidence_ref="client-registry://proof-001",
        approval_ref="approval://dual-control-001",
        command_id=uuid4(),
        idempotency_key=uuid4(),
    )
    result = service.recover_last_owner(
        first_support=_support_actor(tenant_id=tenant_id, membership_id=first_support_id),
        second_support=_support_actor(tenant_id=tenant_id, membership_id=second_support_id),
        command=recovery_command,
        now=NOW,
    )

    assert result.state == "COMPLETED"
    replay = service.recover_last_owner(
        first_support=_support_actor(tenant_id=tenant_id, membership_id=first_support_id),
        second_support=_support_actor(tenant_id=tenant_id, membership_id=second_support_id),
        command=recovery_command,
        now=NOW,
    )
    assert replay.replayed is True
    assert service.authority_status(tenant_id=tenant_id) == "ACTIVE_OWNER"
    with Session(database_engine) as session:
        target = session.get(TenantMembershipRecord, patron_id)
        recovery = session.get(TenantRecoveryRecord, result.record_id)
        assert target is not None and target.role == "PATRON_ADMIN"
        assert recovery is not None and recovery.status == "COMPLETED"
