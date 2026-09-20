"""Nominative tenant invitation issuance and neutral public validation."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.platform.persistence.models import TenantRecord
from app.platform.security.authentication import (
    Argon2idPasswordVerifier,
    Clock,
    OpaqueTokenGenerator,
    PasswordVerifier,
    SecureOpaqueTokenGenerator,
    UtcClock,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.bootstrap import (
    Argon2idPasswordCredentialHasher,
    PasswordCredentialHasher,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, DataClassification
from app.platform.security.models import (
    IdentityRecord,
    PasswordCredentialRecord,
    TenantInvitationRecord,
    TenantMembershipRecord,
)

_INVITATION_TTL = timedelta(days=7)


class InvitationConflictError(RuntimeError):
    """The named person already has a membership or current invitation."""


class InvitationUnavailableError(RuntimeError):
    """The invitation is unknown, expired, accepted or outside the actor tenant."""


@dataclass(frozen=True, slots=True)
class InvitationAcceptanceResult:
    """Server-side references after a successful one-time acceptance."""

    invitation_id: UUID
    tenant_id: UUID
    membership_id: UUID
    identity_id: UUID
    accepted_at: datetime


@dataclass(frozen=True, slots=True)
class InvitationIssueResult:
    invitation_id: UUID
    token: str
    expires_at: datetime


class InvitationService:
    """Keep only the current invitation token hash for one named membership."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
        token_generator: OpaqueTokenGenerator | None = None,
        clock: Clock | None = None,
        password_hasher: PasswordCredentialHasher | None = None,
        password_verifier: PasswordVerifier | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._policy = policy
        self._token_generator = token_generator or SecureOpaqueTokenGenerator()
        self._clock = clock or UtcClock()
        self._password_hasher = password_hasher or Argon2idPasswordCredentialHasher()
        self._password_verifier = password_verifier or Argon2idPasswordVerifier()

    def issue(self, *, actor: ActorContext, email: str) -> InvitationIssueResult:
        self._authorize(actor=actor, resource_id=actor.tenant_id)
        normalized_email = _normalize_email(email)
        now = self._clock.now()
        invitation_id = uuid4()
        membership_id = uuid4()
        try:
            with self._session_factory.begin() as session:
                identity = session.scalar(
                    sa.select(IdentityRecord)
                    .where(IdentityRecord.email_normalized == normalized_email)
                    .with_for_update()
                )
                if identity is None:
                    identity = IdentityRecord(
                        id=uuid4(),
                        email_normalized=normalized_email,
                        lifecycle="PENDING_VERIFICATION",
                        email_verified_at=None,
                    )
                    session.add(identity)
                    session.flush()

                membership = session.scalar(
                    sa.select(TenantMembershipRecord)
                    .where(
                        TenantMembershipRecord.tenant_id == actor.tenant_id,
                        TenantMembershipRecord.identity_id == identity.id,
                    )
                    .with_for_update()
                )
                if membership is not None:
                    raise InvitationConflictError("MEMBERSHIP_OR_INVITATION_EXISTS")

                token = self._token_generator.generate()
                membership = TenantMembershipRecord(
                    id=membership_id,
                    tenant_id=actor.tenant_id,
                    identity_id=identity.id,
                    role="COLLABORATEUR",
                    state="INVITED",
                    activated_at=None,
                    revoked_at=None,
                )
                session.add(membership)
                session.flush()
                session.add(
                    TenantInvitationRecord(
                        id=invitation_id,
                        tenant_id=actor.tenant_id,
                        membership_id=membership_id,
                        token_hash=_hash_token(token),
                        issued_at=now,
                        expires_at=now + _INVITATION_TTL,
                        reissued_at=None,
                        accepted_at=None,
                    )
                )
        except InvitationConflictError:
            raise
        except IntegrityError as error:
            raise InvitationConflictError("MEMBERSHIP_OR_INVITATION_EXISTS") from error
        return InvitationIssueResult(
            invitation_id=invitation_id,
            token=token,
            expires_at=now + _INVITATION_TTL,
        )

    def reissue(
        self,
        *,
        actor: ActorContext,
        invitation_id: UUID,
    ) -> InvitationIssueResult:
        self._authorize(actor=actor, resource_id=invitation_id)
        now = self._clock.now()
        with self._session_factory.begin() as session:
            invitation = session.scalar(
                sa.select(TenantInvitationRecord)
                .join(
                    TenantMembershipRecord,
                    sa.and_(
                        TenantMembershipRecord.tenant_id == TenantInvitationRecord.tenant_id,
                        TenantMembershipRecord.id == TenantInvitationRecord.membership_id,
                    ),
                )
                .join(TenantRecord, TenantRecord.id == TenantInvitationRecord.tenant_id)
                .where(
                    TenantInvitationRecord.id == invitation_id,
                    TenantInvitationRecord.tenant_id == actor.tenant_id,
                    TenantInvitationRecord.accepted_at.is_(None),
                    TenantMembershipRecord.state == "INVITED",
                    TenantMembershipRecord.role == "COLLABORATEUR",
                    TenantRecord.lifecycle == "ACTIVE",
                )
                .with_for_update()
            )
            if invitation is None:
                raise InvitationUnavailableError("INVITATION_UNAVAILABLE")
            token = self._token_generator.generate()
            invitation.token_hash = _hash_token(token)
            invitation.issued_at = now
            invitation.expires_at = now + _INVITATION_TTL
            invitation.reissued_at = now
        return InvitationIssueResult(
            invitation_id=invitation_id,
            token=token,
            expires_at=now + _INVITATION_TTL,
        )

    def verify(self, *, token: str) -> None:
        now = self._clock.now()
        with self._session_factory() as session:
            invitation_id = session.scalar(
                sa.select(TenantInvitationRecord.id)
                .join(
                    TenantMembershipRecord,
                    sa.and_(
                        TenantMembershipRecord.tenant_id == TenantInvitationRecord.tenant_id,
                        TenantMembershipRecord.id == TenantInvitationRecord.membership_id,
                    ),
                )
                .join(TenantRecord, TenantRecord.id == TenantInvitationRecord.tenant_id)
                .where(
                    TenantInvitationRecord.token_hash == _hash_token(token),
                    TenantInvitationRecord.accepted_at.is_(None),
                    TenantInvitationRecord.expires_at > now,
                    TenantMembershipRecord.state == "INVITED",
                    TenantMembershipRecord.role == "COLLABORATEUR",
                    TenantRecord.lifecycle == "ACTIVE",
                )
            )
        if invitation_id is None:
            raise InvitationUnavailableError("INVITATION_UNAVAILABLE")

    def accept(self, *, token: str, password: str) -> InvitationAcceptanceResult:
        """Consume an invitation and activate its identity without opening business access."""
        now = self._clock.now()
        token_hash = _hash_token(token)
        with self._session_factory.begin() as session:
            invitation = session.scalar(
                sa.select(TenantInvitationRecord)
                .join(
                    TenantMembershipRecord,
                    sa.and_(
                        TenantMembershipRecord.tenant_id == TenantInvitationRecord.tenant_id,
                        TenantMembershipRecord.id == TenantInvitationRecord.membership_id,
                    ),
                )
                .join(TenantRecord, TenantRecord.id == TenantInvitationRecord.tenant_id)
                .where(
                    TenantInvitationRecord.token_hash == token_hash,
                    TenantInvitationRecord.accepted_at.is_(None),
                    TenantInvitationRecord.expires_at > now,
                    TenantMembershipRecord.state == "INVITED",
                    TenantMembershipRecord.role == "COLLABORATEUR",
                    TenantRecord.lifecycle == "ACTIVE",
                )
                .with_for_update()
            )
            if invitation is None:
                raise InvitationUnavailableError("INVITATION_UNAVAILABLE")

            membership = session.scalar(
                sa.select(TenantMembershipRecord)
                .where(
                    TenantMembershipRecord.tenant_id == invitation.tenant_id,
                    TenantMembershipRecord.id == invitation.membership_id,
                    TenantMembershipRecord.state == "INVITED",
                    TenantMembershipRecord.role == "COLLABORATEUR",
                )
                .with_for_update()
            )
            if membership is None:
                raise InvitationUnavailableError("INVITATION_UNAVAILABLE")

            identity = session.scalar(
                sa.select(IdentityRecord)
                .where(IdentityRecord.id == membership.identity_id)
                .with_for_update()
            )
            if identity is None or identity.lifecycle not in {"PENDING_VERIFICATION", "ACTIVE"}:
                raise InvitationUnavailableError("INVITATION_UNAVAILABLE")

            credential = session.scalar(
                sa.select(PasswordCredentialRecord)
                .where(PasswordCredentialRecord.identity_id == identity.id)
                .with_for_update()
            )
            if identity.lifecycle == "PENDING_VERIFICATION":
                if credential is not None:
                    raise InvitationUnavailableError("INVITATION_UNAVAILABLE")
                credential_hash = self._new_password_hash(password)
                session.add(
                    PasswordCredentialRecord(
                        id=uuid4(),
                        identity_id=identity.id,
                        password_hash=credential_hash,
                        algorithm="ARGON2ID",
                        parameters_version=1,
                        changed_at=now,
                        must_change=False,
                    )
                )
                identity.lifecycle = "ACTIVE"
            elif credential is None:
                credential_hash = self._new_password_hash(password)
                session.add(
                    PasswordCredentialRecord(
                        id=uuid4(),
                        identity_id=identity.id,
                        password_hash=credential_hash,
                        algorithm="ARGON2ID",
                        parameters_version=1,
                        changed_at=now,
                        must_change=False,
                    )
                )
            elif credential.algorithm != "ARGON2ID" or not self._password_verifier.verify(
                password_hash=credential.password_hash,
                password=password,
            ):
                raise InvitationUnavailableError("INVITATION_UNAVAILABLE")

            identity.email_verified_at = identity.email_verified_at or now
            membership.state = "ACTIVE"
            membership.activated_at = now
            invitation.accepted_at = now
            return InvitationAcceptanceResult(
                invitation_id=invitation.id,
                tenant_id=invitation.tenant_id,
                membership_id=membership.id,
                identity_id=identity.id,
                accepted_at=now,
            )

    def _new_password_hash(self, password: str) -> str:
        if len(password) < 14 or len(password) > 1024:
            raise ValueError("INVALID_PASSWORD")
        password_hash = self._password_hasher.hash(password)
        if not password_hash.startswith("$argon2id$"):
            raise ValueError("INVALID_PASSWORD")
        return password_hash

    def _authorize(self, *, actor: ActorContext, resource_id: UUID) -> None:
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.MEMBERSHIP_MANAGE,
                resource=AuthorizationResource(
                    resource_type="TENANT_INVITATION",
                    resource_id=resource_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                ),
                mfa_required=True,
                evaluated_at=self._clock.now(),
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)


def _normalize_email(email: str) -> str:
    normalized = email.strip().lower()
    if (
        not normalized
        or len(normalized) > 320
        or normalized.count("@") != 1
        or any(character.isspace() for character in normalized)
    ):
        raise ValueError("INVALID_EMAIL")
    local_part, domain = normalized.split("@")
    if not local_part or not domain:
        raise ValueError("INVALID_EMAIL")
    return normalized


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
