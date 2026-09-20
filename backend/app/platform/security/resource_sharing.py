"""Bounded, version-pinned resource sharing without permanent public links."""

import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind
from app.platform.security.models import (
    TenantResourceShareEventRecord,
    TenantResourceShareRecord,
)

_FINGERPRINT = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True, slots=True)
class CreateResourceShareCommand:
    share_id: UUID
    resource_type: str
    resource_id: UUID
    resource_fingerprint: str
    recipient_ref: str
    purpose: str
    classification: str
    starts_at: datetime
    expires_at: datetime
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ResourceShareResult:
    share_id: UUID
    state: str
    access_token: str | None = None
    replayed: bool = False


@dataclass(frozen=True, slots=True)
class SharedResource:
    share_id: UUID
    resource_type: str
    resource_id: UUID
    resource_fingerprint: str
    purpose: str
    classification: str
    recipient_ref: str
    starts_at: datetime
    expires_at: datetime


class ResourceSharingService:
    """Issue opaque, expiring links and keep their lifecycle auditable."""

    def __init__(self, *, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(
        self, *, actor: ActorContext, command: CreateResourceShareCommand, now: datetime
    ) -> ResourceShareResult:
        self._require_sensitive_actor(actor=actor, now=now)
        fingerprint = command.resource_fingerprint.strip().lower()
        recipient = command.recipient_ref.strip().lower()
        purpose = command.purpose.strip()
        if not _FINGERPRINT.fullmatch(fingerprint):
            raise ValueError("RESOURCE_FINGERPRINT_REQUIRED")
        if not recipient or not purpose:
            raise ValueError("SHARE_RECIPIENT_AND_PURPOSE_REQUIRED")
        if command.expires_at <= command.starts_at or command.expires_at <= now:
            raise ValueError("SHARE_EXPIRY_INVALID")
        raw_token = secrets.token_urlsafe(32)
        token_hash = _hash_token(raw_token)
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(TenantResourceShareRecord).where(
                    TenantResourceShareRecord.tenant_id == actor.tenant_id,
                    TenantResourceShareRecord.created_by_membership_id == actor.membership_id,
                    TenantResourceShareRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return ResourceShareResult(replay.id, replay.state, replayed=True)
            share = TenantResourceShareRecord(
                id=command.share_id,
                tenant_id=actor.tenant_id,
                resource_type=command.resource_type.strip(),
                resource_id=command.resource_id,
                resource_fingerprint=fingerprint,
                recipient_ref=recipient,
                purpose=purpose,
                classification=command.classification.strip(),
                access_token_hash=token_hash,
                starts_at=command.starts_at,
                expires_at=command.expires_at,
                state="ACTIVE",
                created_by_membership_id=actor.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
            session.add(share)
            session.flush()
            session.add(
                TenantResourceShareEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    share_id=share.id,
                    event_type="CREATED",
                    actor_membership_id=actor.membership_id,
                    recipient_ref=recipient,
                    occurred_at=now,
                    command_id=command.command_id,
                    reason=purpose,
                )
            )
        return ResourceShareResult(command.share_id, "ACTIVE", raw_token)

    def read(self, *, recipient_ref: str, access_token: str, now: datetime) -> SharedResource:
        recipient = recipient_ref.strip().lower()
        token_hash = _hash_token(access_token)
        expired = False
        shared: SharedResource | None = None
        with self._session_factory.begin() as session:
            share = session.scalar(
                sa.select(TenantResourceShareRecord)
                .where(
                    TenantResourceShareRecord.recipient_ref == recipient,
                    TenantResourceShareRecord.access_token_hash == token_hash,
                )
                .with_for_update()
            )
            if share is None:
                raise PermissionError("SHARE_NOT_AVAILABLE")
            if share.state != "ACTIVE":
                raise PermissionError("SHARE_NOT_AVAILABLE")
            if now < share.starts_at or now >= share.expires_at:
                share.state = "EXPIRED"
                session.add(
                    TenantResourceShareEventRecord(
                        id=uuid4(),
                        tenant_id=share.tenant_id,
                        share_id=share.id,
                        event_type="EXPIRED",
                        actor_membership_id=None,
                        recipient_ref=recipient,
                        occurred_at=now,
                        command_id=uuid4(),
                        reason="SHARE_EXPIRED",
                    )
                )
                expired = True
            else:
                session.add(
                    TenantResourceShareEventRecord(
                        id=uuid4(),
                        tenant_id=share.tenant_id,
                        share_id=share.id,
                        event_type="ACCESSED",
                        actor_membership_id=None,
                        recipient_ref=recipient,
                        occurred_at=now,
                        command_id=uuid4(),
                        reason="SHARE_ACCESSED",
                    )
                )
                shared = SharedResource(
                    share_id=share.id,
                    resource_type=share.resource_type,
                    resource_id=share.resource_id,
                    resource_fingerprint=share.resource_fingerprint,
                    purpose=share.purpose,
                    classification=share.classification,
                    recipient_ref=share.recipient_ref,
                    starts_at=share.starts_at,
                    expires_at=share.expires_at,
                )
        if expired:
            raise PermissionError("SHARE_NOT_AVAILABLE")
        assert shared is not None
        return shared

    def revoke(
        self, *, actor: ActorContext, share_id: UUID, reason: str, now: datetime
    ) -> ResourceShareResult:
        self._require_sensitive_actor(actor=actor, now=now)
        if not reason.strip():
            raise ValueError("SHARE_REVOCATION_REASON_REQUIRED")
        with self._session_factory.begin() as session:
            share = session.scalar(
                sa.select(TenantResourceShareRecord)
                .where(
                    TenantResourceShareRecord.tenant_id == actor.tenant_id,
                    TenantResourceShareRecord.id == share_id,
                )
                .with_for_update()
            )
            if share is None:
                raise PermissionError("SHARE_NOT_AVAILABLE")
            if share.state == "REVOKED":
                return ResourceShareResult(share.id, share.state, replayed=True)
            if share.state == "EXPIRED":
                return ResourceShareResult(share.id, share.state, replayed=True)
            share.state = "REVOKED"
            share.revoked_at = now
            share.revoke_reason = reason.strip()
            session.add(
                TenantResourceShareEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    share_id=share.id,
                    event_type="REVOKED",
                    actor_membership_id=actor.membership_id,
                    recipient_ref=share.recipient_ref,
                    occurred_at=now,
                    command_id=uuid4(),
                    reason=reason.strip(),
                )
            )
        return ResourceShareResult(share_id, "REVOKED")

    @staticmethod
    def _require_sensitive_actor(*, actor: ActorContext, now: datetime) -> None:
        if actor.actor_kind not in {ActorKind.PATRON_ADMIN, ActorKind.PATRON_DELEGATE}:
            raise PermissionError("SHARE_PATRON_REQUIRED")
        if not actor.membership_is_active:
            raise PermissionError("MEMBERSHIP_NOT_ACTIVE")
        if Capability.SENSITIVE_EXPORT not in actor.capabilities:
            raise PermissionError("SHARE_CAPABILITY_REQUIRED")
        if not actor.has_recent_mfa(evaluated_at=now):
            raise PermissionError("STEP_UP_REQUIRED")


def _hash_token(raw_token: str) -> str:
    if not raw_token.strip():
        raise ValueError("SHARE_TOKEN_REQUIRED")
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
