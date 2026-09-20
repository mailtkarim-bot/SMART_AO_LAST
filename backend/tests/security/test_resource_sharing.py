from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.platform.persistence.models import TenantRecord
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from app.platform.security.models import (
    IdentityRecord,
    TenantMembershipRecord,
    TenantResourceShareEventRecord,
    TenantResourceShareRecord,
)
from app.platform.security.resource_sharing import (
    CreateResourceShareCommand,
    ResourceSharingService,
)
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 9, 20, 14, 0, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolate_share_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _seed(database_engine: sa.Engine) -> tuple[UUID, ActorContext]:
    tenant_id, membership_id, identity_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"share-{tenant_id.hex[:12]}", lifecycle="ACTIVE")
        )
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
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        session.commit()
    actor = ActorContext(
        actor_id=identity_id,
        identity_id=identity_id,
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
    return tenant_id, actor


def _command(*, share_id: UUID, idempotency_key: UUID | None = None, expires_at=None):
    return CreateResourceShareCommand(
        share_id=share_id,
        resource_type="SUBMISSION_PACKAGE",
        resource_id=uuid4(),
        resource_fingerprint="a" * 64,
        recipient_ref="client@example.test",
        purpose="Relecture du paquet candidat.",
        classification="INTERNAL_OPERATIONAL",
        starts_at=NOW,
        expires_at=expires_at or NOW + timedelta(hours=1),
        command_id=uuid4(),
        idempotency_key=idempotency_key or uuid4(),
    )


@pytest.mark.db
@pytest.mark.security
def test_version_pinned_share_is_idempotent_readable_and_revocable(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    _, actor = _seed(database_engine)
    service = ResourceSharingService(session_factory=session_factory)
    command = _command(share_id=uuid4())

    created = service.create(actor=actor, command=command, now=NOW)
    replay = service.create(actor=actor, command=command, now=NOW)
    shared = service.read(
        recipient_ref="CLIENT@EXAMPLE.TEST", access_token=created.access_token or "", now=NOW
    )
    revoked = service.revoke(
        actor=actor, share_id=created.share_id, reason="Relecture terminée.", now=NOW
    )

    assert created.state == "ACTIVE"
    assert created.access_token
    assert replay.replayed is True and replay.access_token is None
    assert shared.resource_fingerprint == "a" * 64
    assert revoked.state == "REVOKED"
    with pytest.raises(PermissionError, match="SHARE_NOT_AVAILABLE"):
        service.read(
            recipient_ref="client@example.test", access_token=created.access_token, now=NOW
        )
    with Session(database_engine) as session:
        record = session.get(TenantResourceShareRecord, created.share_id)
        events = session.scalars(
            sa.select(TenantResourceShareEventRecord).where(
                TenantResourceShareEventRecord.share_id == created.share_id
            )
        ).all()
        assert record is not None and record.state == "REVOKED"
        assert {event.event_type for event in events} == {"CREATED", "ACCESSED", "REVOKED"}


@pytest.mark.db
@pytest.mark.security
def test_share_requires_recent_mfa_and_expires_without_success_presumption(
    database_engine: sa.Engine, session_factory: sessionmaker[Session]
) -> None:
    _, actor = _seed(database_engine)
    service = ResourceSharingService(session_factory=session_factory)
    password_actor = replace(actor, mfa_verified_at=None)
    with pytest.raises(PermissionError, match="STEP_UP_REQUIRED"):
        service.create(actor=password_actor, command=_command(share_id=uuid4()), now=NOW)

    command = _command(share_id=uuid4(), expires_at=NOW + timedelta(seconds=1))
    created = service.create(actor=actor, command=command, now=NOW)
    with pytest.raises(PermissionError, match="SHARE_NOT_AVAILABLE"):
        service.read(
            recipient_ref="client@example.test",
            access_token=created.access_token or "",
            now=NOW + timedelta(seconds=2),
        )
    with Session(database_engine) as session:
        record = session.get(TenantResourceShareRecord, created.share_id)
        assert record is not None and record.state == "EXPIRED"
