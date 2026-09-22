from __future__ import annotations

import hashlib
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import app.interfaces.http.routes.invitations as route_module
import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.invitations import build_invitation_router
from app.platform.persistence.models import TenantRecord
from app.platform.security.authentication import AuthenticationService
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from app.platform.security.invitations import InvitationService
from app.platform.security.models import (
    AuthSessionRecord,
    IdentityRecord,
    PasswordCredentialRecord,
    TenantInvitationRecord,
    TenantMembershipRecord,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker


@dataclass
class MutableClock:
    current: datetime

    def now(self) -> datetime:
        return self.current


class SequenceTokens:
    def __init__(self) -> None:
        self._tokens = iter(("first-" + "a" * 48, "second-" + "b" * 48))

    def generate(self) -> str:
        return next(self._tokens)


class FixedPasswordHasher:
    def hash(self, password: str) -> str:
        del password
        return "$argon2id$accept-fixed"


class FixedPasswordVerifier:
    def verify(self, *, password_hash: str, password: str) -> bool:
        return password_hash == "$argon2id$accept-fixed" and password == (
            "Invitee#Password123"  # pragma: allowlist secret
        )


@pytest.fixture(autouse=True)
def isolate_invitation_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _actor(*, tenant_id, now: datetime) -> ActorContext:
    actor_id = uuid4()
    return ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=now,
        mfa_verified_at=now,
        correlation_id=uuid4(),
    )


def _client(
    *,
    service: InvitationService,
    actor_ref: list[ActorContext],
    monkeypatch,
) -> TestClient:
    monkeypatch.setattr(route_module, "_resolve_context", lambda **_kwargs: actor_ref[0])
    runtime = cast(
        ConsultationSecurityRuntime,
        SimpleNamespace(context_resolver=object(), policy=AuthorizationPolicy()),
    )
    app = FastAPI()
    app.include_router(build_invitation_router(service=service, security_runtime=runtime))
    return TestClient(app)


def test_invitation_is_nominative_reissued_expiring_and_non_disclosing(
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    clock = MutableClock(now)
    tenant_id = uuid4()
    with session_factory.begin() as session:
        session.add(TenantRecord(id=tenant_id, slug="invitation-proof", lifecycle="ACTIVE"))

    actor_ref = [_actor(tenant_id=tenant_id, now=now)]
    service = InvitationService(
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
        token_generator=SequenceTokens(),
        clock=clock,
    )
    client = _client(service=service, actor_ref=actor_ref, monkeypatch=monkeypatch)

    issued = client.post(
        "/api/v1/patron/invitations",
        json={"email": "  Collaborateur@Example.Test "},
    )
    assert issued.status_code == 201
    first = issued.json()
    assert set(first) == {"invitation_id", "token", "expires_at"}

    with session_factory() as session:
        identity = session.scalar(sa.select(IdentityRecord))
        membership = session.scalar(sa.select(TenantMembershipRecord))
        invitation = session.scalar(sa.select(TenantInvitationRecord))
        assert identity is not None and identity.email_normalized == "collaborateur@example.test"
        assert membership is not None and membership.identity_id == identity.id
        assert membership.state == "INVITED" and membership.role == "COLLABORATEUR"
        assert invitation is not None and invitation.membership_id == membership.id
        assert invitation.token_hash == hashlib.sha256(first["token"].encode()).hexdigest()
        assert first["token"] not in invitation.token_hash
        invitation_columns = {
            column["name"]
            for column in sa.inspect(session.get_bind()).get_columns("tenant_invitations")
        }
        assert "token_hash" in invitation_columns
        assert not {"token", "secret", "raw_token"} & invitation_columns

    valid = client.post("/api/v1/invitations/verify", json={"token": first["token"]})
    assert valid.status_code == 204 and valid.content == b""

    clock.current += timedelta(minutes=1)
    reissued = client.post(f"/api/v1/patron/invitations/{first['invitation_id']}/reissue")
    assert reissued.status_code == 200
    second = reissued.json()
    assert second["invitation_id"] == first["invitation_id"]
    assert second["token"] != first["token"]
    assert set(second) == {"invitation_id", "token", "expires_at"}
    with session_factory() as session:
        invitation = session.get(TenantInvitationRecord, first["invitation_id"])
        assert invitation is not None
        assert invitation.token_hash == hashlib.sha256(second["token"].encode()).hexdigest()
        assert invitation.reissued_at == clock.current

    old = client.post("/api/v1/invitations/verify", json={"token": first["token"]})
    assert old.status_code == 404

    duplicate = client.post(
        "/api/v1/patron/invitations",
        json={"email": "collaborateur@example.test"},
    )
    assert duplicate.status_code == 409
    with session_factory() as session:
        assert session.scalar(sa.select(sa.func.count()).select_from(IdentityRecord)) == 1
        assert session.scalar(sa.select(sa.func.count()).select_from(TenantMembershipRecord)) == 1

    clock.current += timedelta(days=7)
    expired = client.post("/api/v1/invitations/verify", json={"token": second["token"]})
    unknown = client.post("/api/v1/invitations/verify", json={"token": "unknown-" + "x" * 48})
    assert expired.status_code == unknown.status_code == 404
    assert expired.json() == unknown.json() == {"detail": "INVITATION_UNAVAILABLE"}


def test_invitation_requires_membership_management_and_valid_email(
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    tenant_id = uuid4()
    with session_factory.begin() as session:
        session.add(TenantRecord(id=tenant_id, slug="invitation-authz", lifecycle="ACTIVE"))
    patron = _actor(tenant_id=tenant_id, now=now)
    actor_ref = [
        replace(
            patron,
            actor_kind=ActorKind.COLLABORATEUR,
            capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        )
    ]
    service = InvitationService(
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
        clock=MutableClock(now),
    )
    client = _client(service=service, actor_ref=actor_ref, monkeypatch=monkeypatch)

    forbidden = client.post(
        "/api/v1/patron/invitations",
        json={"email": "person@example.test"},
    )
    assert forbidden.status_code == 403

    actor_ref[0] = patron
    invalid = client.post("/api/v1/patron/invitations", json={"email": "not-an-email"})
    assert invalid.status_code == 422


def test_invitation_acceptance_is_one_time_activates_identity_and_stays_before_mfa(
    session_factory: sessionmaker[Session],
    monkeypatch,
) -> None:
    now = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    clock = MutableClock(now)
    tenant_id = uuid4()
    with session_factory.begin() as session:
        session.add(TenantRecord(id=tenant_id, slug="invitation-acceptance", lifecycle="ACTIVE"))

    actor_ref = [_actor(tenant_id=tenant_id, now=now)]
    service = InvitationService(
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
        token_generator=SequenceTokens(),
        clock=clock,
        password_hasher=FixedPasswordHasher(),
        password_verifier=FixedPasswordVerifier(),
    )
    client = _client(service=service, actor_ref=actor_ref, monkeypatch=monkeypatch)
    issued = client.post(
        "/api/v1/patron/invitations",
        json={"email": "invitee@example.test"},
    )
    token = issued.json()["token"]

    accepted = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": "Invitee#Password123"},  # pragma: allowlist secret
    )
    assert accepted.status_code == 204 and accepted.content == b""

    with session_factory() as session:
        identity = session.scalar(
            sa.select(IdentityRecord).where(
                IdentityRecord.email_normalized == "invitee@example.test"
            )
        )
        membership = session.scalar(
            sa.select(TenantMembershipRecord).where(TenantMembershipRecord.tenant_id == tenant_id)
        )
        invitation = session.scalar(sa.select(TenantInvitationRecord))
        credential = session.scalar(sa.select(PasswordCredentialRecord))
        assert identity is not None and identity.lifecycle == "ACTIVE"
        assert identity.email_verified_at == now
        assert membership is not None and membership.state == "ACTIVE"
        assert membership.activated_at == now
        assert invitation is not None and invitation.accepted_at == now
        assert credential is not None and credential.password_hash == "$argon2id$accept-fixed"
        assert "Invitee#Password123" not in credential.password_hash

    second_issued = client.post(
        "/api/v1/patron/invitations",
        json={"email": "expired@example.test"},
    )
    second_token = second_issued.json()["token"]
    clock.current += timedelta(days=7)
    expired = client.post(
        "/api/v1/invitations/accept",
        json={"token": second_token, "password": "Invitee#Password123"},  # pragma: allowlist secret
    )
    assert expired.status_code == 404
    with session_factory() as session:
        expired_identity = session.scalar(
            sa.select(IdentityRecord).where(
                IdentityRecord.email_normalized == "expired@example.test"
            )
        )
        assert expired_identity is not None and expired_identity.lifecycle == "PENDING_VERIFICATION"

    login = AuthenticationService(
        session_factory=session_factory,
        password_verifier=FixedPasswordVerifier(),
        token_generator=SequenceTokens(),
        clock=clock,
    ).login(
        email="invitee@example.test",
        password="Invitee#Password123",  # pragma: allowlist secret
        tenant_id=tenant_id,
    )
    with session_factory() as session:
        auth_session = session.get(AuthSessionRecord, login.session_id)
        assert auth_session is not None and auth_session.auth_strength == "PASSWORD"
        assert auth_session.mfa_verified_at is None

    reused = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": "Invitee#Password123"},  # pragma: allowlist secret
    )
    assert reused.status_code == 404
    assert reused.json() == {"detail": "INVITATION_UNAVAILABLE"}
    assert client.post("/api/v1/invitations/verify", json={"token": token}).status_code == 404

    invalid_password = client.post(
        "/api/v1/invitations/accept",
        json={"token": "unknown-token", "password": "short"},  # pragma: allowlist secret
    )
    assert invalid_password.status_code == 404
