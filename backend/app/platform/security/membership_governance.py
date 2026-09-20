"""Minimal C14 ownership and membership-suspension application service."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import ActorContext, ActorKind, DataClassification
from app.platform.security.models import (
    AuthSessionRecord,
    MembershipSuspensionRecord,
    TenantDelegationEventRecord,
    TenantDelegationRecord,
    TenantMembershipRecord,
    TenantOwnerChangeRecord,
    TenantOwnerRecord,
)


@dataclass(frozen=True, slots=True)
class SuspendMembershipCommand:
    suspension_id: UUID
    membership_id: UUID
    command_id: UUID
    idempotency_key: UUID
    reason_code: str
    rationale: str
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class MembershipSuspensionResult:
    suspension_id: UUID
    revoked_session_count: int
    replayed: bool


@dataclass(frozen=True, slots=True)
class ChangeOwnerCommand:
    change_id: UUID
    new_owner_membership_id: UUID
    command_id: UUID
    idempotency_key: UUID
    rationale: str
    transfer: bool = False
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class OwnerChangeResult:
    change_id: UUID
    action: str
    replayed: bool


@dataclass(frozen=True, slots=True)
class GrantDelegationCommand:
    delegation_id: UUID
    delegatee_membership_id: UUID
    capabilities: tuple[str, ...]
    doors: tuple[str, ...]
    case_ids: tuple[UUID, ...]
    starts_at: datetime
    expires_at: datetime
    command_id: UUID
    idempotency_key: UUID
    rationale: str
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RevokeDelegationCommand:
    delegation_id: UUID
    command_id: UUID
    idempotency_key: UUID
    reason: str
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class DelegationResult:
    delegation_id: UUID
    replayed: bool


class MembershipGovernanceService:
    """Suspend a member without conflating organization ownership with Patron role."""

    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._session_factory = session_factory
        self._policy = policy

    def suspend(
        self, *, actor: ActorContext, command: SuspendMembershipCommand, now: datetime
    ) -> MembershipSuspensionResult:
        self._authorize(actor=actor, now=now)
        reason_code = command.reason_code.strip()
        if (
            not reason_code
            or not reason_code.replace("_", "").isalnum()
            or reason_code != reason_code.upper()
        ):
            raise ValueError("INVALID_REASON_CODE")
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(MembershipSuspensionRecord).where(
                    MembershipSuspensionRecord.tenant_id == actor.tenant_id,
                    MembershipSuspensionRecord.suspended_by_membership_id == actor.membership_id,
                    MembershipSuspensionRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return MembershipSuspensionResult(
                    suspension_id=replay.id,
                    revoked_session_count=0,
                    replayed=True,
                )
            owner = session.scalar(
                sa.select(TenantOwnerRecord.id).where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == actor.membership_id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
            )
            if owner is None:
                raise PermissionError("ORGANIZATION_OWNER_REQUIRED")
            membership = session.scalar(
                sa.select(TenantMembershipRecord)
                .where(
                    TenantMembershipRecord.tenant_id == actor.tenant_id,
                    TenantMembershipRecord.id == command.membership_id,
                )
                .with_for_update()
            )
            if membership is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            if membership.state != "ACTIVE":
                raise ValueError("MEMBERSHIP_NOT_ACTIVE")
            session.add(
                MembershipSuspensionRecord(
                    id=command.suspension_id,
                    tenant_id=actor.tenant_id,
                    membership_id=membership.id,
                    suspended_by_membership_id=actor.membership_id,
                    reason_code=reason_code,
                    rationale=command.rationale.strip(),
                    suspended_at=now,
                    command_id=command.command_id,
                    idempotency_key=command.idempotency_key,
                    correlation_id=command.correlation_id,
                )
            )
            membership.state = "SUSPENDED"
            revoked = session.execute(
                sa.update(AuthSessionRecord)
                .where(
                    AuthSessionRecord.tenant_id == actor.tenant_id,
                    AuthSessionRecord.membership_id == membership.id,
                    AuthSessionRecord.state == "ACTIVE",
                )
                .values(
                    state="REVOKED",
                    revoked_at=now,
                    revoke_reason="MEMBERSHIP_SUSPENDED",
                    token_version=AuthSessionRecord.token_version + 1,
                )
            )
            active_delegations = session.scalars(
                sa.select(TenantDelegationRecord)
                .where(
                    TenantDelegationRecord.tenant_id == actor.tenant_id,
                    TenantDelegationRecord.state == "ACTIVE",
                    sa.or_(
                        TenantDelegationRecord.delegatee_membership_id == membership.id,
                        TenantDelegationRecord.delegator_membership_id == membership.id,
                    ),
                )
                .with_for_update()
            ).all()
            for delegation in active_delegations:
                delegation.state = "REVOKED"
                delegation.revoked_at = now
                delegation.revoke_reason = "MEMBERSHIP_SUSPENDED"
                session.add(
                    TenantDelegationEventRecord(
                        id=uuid4(),
                        tenant_id=actor.tenant_id,
                        delegation_id=delegation.id,
                        event_type="REVOKED",
                        actor_membership_id=actor.membership_id,
                        occurred_at=now,
                        command_id=command.command_id,
                        reason="MEMBERSHIP_SUSPENDED",
                    )
                )
        return MembershipSuspensionResult(
            suspension_id=command.suspension_id,
            revoked_session_count=revoked.rowcount or 0,
            replayed=False,
        )

    def grant_delegation(
        self, *, actor: ActorContext, command: GrantDelegationCommand, now: datetime
    ) -> DelegationResult:
        self._authorize(actor=actor, now=now)
        allowed = capabilities_for(
            ActorKind.PATRON_DELEGATE, delegated_capabilities=command.capabilities
        )
        if not allowed or set(command.capabilities) != set(allowed):
            raise ValueError("CAPABILITY_NOT_DELEGABLE")
        if not command.doors or not command.case_ids:
            raise ValueError("DELEGATION_SCOPE_REQUIRED")
        if command.starts_at < now or command.expires_at <= command.starts_at:
            raise ValueError("INVALID_DELEGATION_WINDOW")
        if not command.rationale.strip():
            raise ValueError("RATIONALE_REQUIRED")
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(TenantDelegationRecord).where(
                    TenantDelegationRecord.tenant_id == actor.tenant_id,
                    TenantDelegationRecord.delegator_membership_id == actor.membership_id,
                    TenantDelegationRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return DelegationResult(delegation_id=replay.id, replayed=True)
            owner = session.scalar(
                sa.select(TenantOwnerRecord.id).where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == actor.membership_id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
            )
            if owner is None:
                raise PermissionError("ORGANIZATION_OWNER_REQUIRED")
            target = session.scalar(
                sa.select(TenantMembershipRecord).where(
                    TenantMembershipRecord.tenant_id == actor.tenant_id,
                    TenantMembershipRecord.id == command.delegatee_membership_id,
                )
            )
            if target is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            if target.state != "ACTIVE" or target.role != "PATRON_DELEGATE":
                raise ValueError("DELEGATEE_NOT_ELIGIBLE")
            delegation = TenantDelegationRecord(
                id=command.delegation_id,
                tenant_id=actor.tenant_id,
                delegator_membership_id=actor.membership_id,
                delegatee_membership_id=target.id,
                capabilities_json=sorted(allowed),
                doors_json=list(command.doors),
                case_ids_json=[str(case_id) for case_id in command.case_ids],
                starts_at=command.starts_at,
                expires_at=command.expires_at,
                state="ACTIVE",
                rationale=command.rationale.strip(),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
                revoked_at=None,
                revoke_reason=None,
            )
            session.add(delegation)
            session.flush()
            session.add(
                TenantDelegationEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    delegation_id=delegation.id,
                    event_type="GRANTED",
                    actor_membership_id=actor.membership_id,
                    occurred_at=now,
                    command_id=command.command_id,
                    reason=command.rationale.strip(),
                )
            )
        return DelegationResult(delegation_id=command.delegation_id, replayed=False)

    def revoke_delegation(
        self, *, actor: ActorContext, command: RevokeDelegationCommand, now: datetime
    ) -> DelegationResult:
        self._authorize(actor=actor, now=now)
        if not command.reason.strip():
            raise ValueError("REASON_REQUIRED")
        with self._session_factory.begin() as session:
            delegation = session.scalar(
                sa.select(TenantDelegationRecord)
                .where(
                    TenantDelegationRecord.tenant_id == actor.tenant_id,
                    TenantDelegationRecord.id == command.delegation_id,
                )
                .with_for_update()
            )
            if delegation is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            owner = session.scalar(
                sa.select(TenantOwnerRecord.id).where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == actor.membership_id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
            )
            if owner is None:
                raise PermissionError("ORGANIZATION_OWNER_REQUIRED")
            if delegation.state == "REVOKED":
                return DelegationResult(delegation_id=delegation.id, replayed=True)
            delegation.state = "REVOKED"
            delegation.revoked_at = now
            delegation.revoke_reason = command.reason.strip()
            session.add(
                TenantDelegationEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    delegation_id=delegation.id,
                    event_type="REVOKED",
                    actor_membership_id=actor.membership_id,
                    occurred_at=now,
                    command_id=command.command_id,
                    reason=command.reason.strip(),
                )
            )
        return DelegationResult(delegation_id=command.delegation_id, replayed=False)

    def change_owner(
        self, *, actor: ActorContext, command: ChangeOwnerCommand, now: datetime
    ) -> OwnerChangeResult:
        self._authorize(actor=actor, now=now)
        if not command.rationale.strip():
            raise ValueError("RATIONALE_REQUIRED")
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(TenantOwnerChangeRecord).where(
                    TenantOwnerChangeRecord.tenant_id == actor.tenant_id,
                    TenantOwnerChangeRecord.changed_by_membership_id == actor.membership_id,
                    TenantOwnerChangeRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return OwnerChangeResult(change_id=replay.id, action=replay.action, replayed=True)
            actor_owner = session.scalar(
                sa.select(TenantOwnerRecord)
                .where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == actor.membership_id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
                .with_for_update()
            )
            if actor_owner is None:
                raise PermissionError("ORGANIZATION_OWNER_REQUIRED")
            target = session.scalar(
                sa.select(TenantMembershipRecord)
                .where(
                    TenantMembershipRecord.tenant_id == actor.tenant_id,
                    TenantMembershipRecord.id == command.new_owner_membership_id,
                )
                .with_for_update()
            )
            if target is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            if target.state != "ACTIVE":
                raise ValueError("OWNER_MEMBERSHIP_NOT_ACTIVE")
            existing_target = session.scalar(
                sa.select(TenantOwnerRecord.id).where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == target.id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
            )
            if existing_target is not None:
                raise ValueError("MEMBERSHIP_ALREADY_OWNER")
            action = "TRANSFERRED" if command.transfer else "DESIGNATED"
            if command.transfer:
                actor_owner.ended_at = now
            session.add(
                TenantOwnerRecord(
                    id=command.change_id,
                    tenant_id=actor.tenant_id,
                    membership_id=target.id,
                    designated_by_membership_id=actor.membership_id,
                    ended_at=None,
                )
            )
            session.add(
                TenantOwnerChangeRecord(
                    id=command.change_id,
                    tenant_id=actor.tenant_id,
                    action=action,
                    previous_owner_membership_id=(
                        actor.membership_id if command.transfer else None
                    ),
                    new_owner_membership_id=target.id,
                    changed_by_membership_id=actor.membership_id,
                    rationale=command.rationale.strip(),
                    changed_at=now,
                    command_id=command.command_id,
                    idempotency_key=command.idempotency_key,
                    correlation_id=command.correlation_id,
                )
            )
        return OwnerChangeResult(change_id=command.change_id, action=action, replayed=False)

    def _authorize(self, *, actor: ActorContext, now: datetime) -> None:
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.MEMBERSHIP_MANAGE,
                resource=AuthorizationResource(
                    resource_type="TENANT_MEMBERSHIP",
                    resource_id=actor.tenant_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.PERSONAL_OR_ADMINISTRATIVE,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)
