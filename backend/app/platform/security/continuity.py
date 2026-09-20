"""C14 continuity: nominative handover and bounded last-owner recovery."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.platform.security.context import ActorContext, ActorKind
from app.platform.security.models import (
    TenantHandoverEventRecord,
    TenantHandoverRecord,
    TenantMembershipRecord,
    TenantOwnerChangeRecord,
    TenantOwnerRecord,
    TenantRecoveryRecord,
)


@dataclass(frozen=True, slots=True)
class HandoverRequestCommand:
    handover_id: UUID
    successor_membership_id: UUID
    assignment_ids: tuple[UUID, ...]
    command_id: UUID
    idempotency_key: UUID
    rationale: str
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class HandoverAcceptCommand:
    handover_id: UUID
    command_id: UUID
    reason: str
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RecoveryCommand:
    recovery_id: UUID
    target_membership_id: UUID
    authority_evidence_ref: str
    approval_ref: str
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ContinuityResult:
    record_id: UUID
    state: str
    replayed: bool = False


class ContinuityGovernanceService:
    """Keep handover and recovery explicit without granting support business rights."""

    def __init__(self, *, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def authority_status(self, *, tenant_id: UUID) -> str:
        with self._session_factory() as session:
            active_owner = session.scalar(
                sa.select(TenantOwnerRecord.id)
                .join(
                    TenantMembershipRecord,
                    sa.and_(
                        TenantMembershipRecord.tenant_id == TenantOwnerRecord.tenant_id,
                        TenantMembershipRecord.id == TenantOwnerRecord.membership_id,
                    ),
                )
                .where(
                    TenantOwnerRecord.tenant_id == tenant_id,
                    TenantOwnerRecord.ended_at.is_(None),
                    TenantMembershipRecord.state == "ACTIVE",
                )
            )
        return "ACTIVE_OWNER" if active_owner is not None else "NO_ACTIVE_OWNER"

    def request_handover(
        self, *, actor: ActorContext, command: HandoverRequestCommand, now: datetime
    ) -> ContinuityResult:
        self._require_owner(actor=actor)
        if not command.assignment_ids or not command.rationale.strip():
            raise ValueError("HANDOVER_SCOPE_REQUIRED")
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(TenantHandoverRecord).where(
                    TenantHandoverRecord.tenant_id == actor.tenant_id,
                    TenantHandoverRecord.requested_by_membership_id == actor.membership_id,
                    TenantHandoverRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return ContinuityResult(replay.id, replay.state, replayed=True)
            successor = session.scalar(
                sa.select(TenantMembershipRecord).where(
                    TenantMembershipRecord.tenant_id == actor.tenant_id,
                    TenantMembershipRecord.id == command.successor_membership_id,
                )
            )
            if successor is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            if successor.state != "ACTIVE" or successor.id == actor.membership_id:
                raise ValueError("SUCCESSOR_NOT_ELIGIBLE")
            handover = TenantHandoverRecord(
                id=command.handover_id,
                tenant_id=actor.tenant_id,
                requested_by_membership_id=actor.membership_id,
                successor_membership_id=successor.id,
                assignment_ids_json=[str(value) for value in command.assignment_ids],
                state="REQUESTED",
                rationale=command.rationale.strip(),
                requested_at=now,
                accepted_at=None,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
            session.add(handover)
            session.flush()
            session.add(
                TenantHandoverEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    handover_id=handover.id,
                    event_type="REQUESTED",
                    actor_membership_id=actor.membership_id,
                    occurred_at=now,
                    command_id=command.command_id,
                    reason=command.rationale.strip(),
                )
            )
        return ContinuityResult(command.handover_id, "REQUESTED")

    def accept_handover(
        self, *, actor: ActorContext, command: HandoverAcceptCommand, now: datetime
    ) -> ContinuityResult:
        if not command.reason.strip():
            raise ValueError("REASON_REQUIRED")
        with self._session_factory.begin() as session:
            handover = session.scalar(
                sa.select(TenantHandoverRecord)
                .where(
                    TenantHandoverRecord.tenant_id == actor.tenant_id,
                    TenantHandoverRecord.id == command.handover_id,
                )
                .with_for_update()
            )
            if handover is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            if handover.successor_membership_id != actor.membership_id:
                raise PermissionError("HANDOVER_SUCCESSOR_REQUIRED")
            if handover.state == "ACCEPTED":
                return ContinuityResult(handover.id, handover.state, replayed=True)
            if handover.state != "REQUESTED":
                raise ValueError("HANDOVER_NOT_ACCEPTABLE")
            if actor.membership_state.value != "ACTIVE":
                raise PermissionError("MEMBERSHIP_NOT_ACTIVE")
            handover.state = "ACCEPTED"
            handover.accepted_at = now
            session.add(
                TenantHandoverEventRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    handover_id=handover.id,
                    event_type="ACCEPTED",
                    actor_membership_id=actor.membership_id,
                    occurred_at=now,
                    command_id=command.command_id,
                    reason=command.reason.strip(),
                )
            )
        return ContinuityResult(command.handover_id, "ACCEPTED")

    def recover_last_owner(
        self,
        *,
        first_support: ActorContext,
        second_support: ActorContext,
        command: RecoveryCommand,
        now: datetime,
    ) -> ContinuityResult:
        if first_support.actor_kind is not ActorKind.SUPPORT_BREAK_GLASS:
            raise PermissionError("SUPPORT_BREAK_GLASS_REQUIRED")
        if second_support.actor_kind is not ActorKind.SUPPORT_BREAK_GLASS:
            raise PermissionError("SUPPORT_BREAK_GLASS_REQUIRED")
        if first_support.tenant_id != second_support.tenant_id:
            raise PermissionError("TENANT_MISMATCH")
        if first_support.membership_id == second_support.membership_id:
            raise PermissionError("TWO_SUPPORT_ACTORS_REQUIRED")
        if not command.authority_evidence_ref.strip() or not command.approval_ref.strip():
            raise ValueError("RECOVERY_PROOF_REQUIRED")
        with self._session_factory.begin() as session:
            replay = session.scalar(
                sa.select(TenantRecoveryRecord).where(
                    TenantRecoveryRecord.tenant_id == first_support.tenant_id,
                    TenantRecoveryRecord.first_support_membership_id == first_support.membership_id,
                    TenantRecoveryRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                return ContinuityResult(replay.id, replay.status, replayed=True)
            active_owner = session.scalar(
                sa.select(TenantOwnerRecord.id)
                .join(
                    TenantMembershipRecord,
                    sa.and_(
                        TenantMembershipRecord.tenant_id == TenantOwnerRecord.tenant_id,
                        TenantMembershipRecord.id == TenantOwnerRecord.membership_id,
                    ),
                )
                .where(
                    TenantOwnerRecord.tenant_id == first_support.tenant_id,
                    TenantOwnerRecord.ended_at.is_(None),
                    TenantMembershipRecord.state == "ACTIVE",
                )
            )
            if active_owner is not None:
                raise ValueError("ACTIVE_OWNER_PRESENT")
            target = session.scalar(
                sa.select(TenantMembershipRecord).where(
                    TenantMembershipRecord.tenant_id == first_support.tenant_id,
                    TenantMembershipRecord.id == command.target_membership_id,
                    TenantMembershipRecord.state == "ACTIVE",
                )
            )
            if target is None:
                raise ValueError("RECOVERY_TARGET_NOT_ACTIVE")
            recovery = TenantRecoveryRecord(
                id=command.recovery_id,
                tenant_id=first_support.tenant_id,
                target_membership_id=target.id,
                first_support_membership_id=first_support.membership_id,
                second_support_membership_id=second_support.membership_id,
                authority_evidence_ref=command.authority_evidence_ref.strip(),
                approval_ref=command.approval_ref.strip(),
                status="COMPLETED",
                completed_at=now,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
            session.add(recovery)
            session.add(
                TenantOwnerRecord(
                    id=uuid4(),
                    tenant_id=first_support.tenant_id,
                    membership_id=target.id,
                    designated_by_membership_id=first_support.membership_id,
                    ended_at=None,
                )
            )
            session.add(
                TenantOwnerChangeRecord(
                    id=uuid4(),
                    tenant_id=first_support.tenant_id,
                    action="DESIGNATED",
                    previous_owner_membership_id=None,
                    new_owner_membership_id=target.id,
                    changed_by_membership_id=first_support.membership_id,
                    rationale=f"R03 recovery {command.approval_ref.strip()}",
                    changed_at=now,
                    command_id=command.command_id,
                    idempotency_key=command.idempotency_key,
                    correlation_id=command.correlation_id,
                )
            )
        return ContinuityResult(command.recovery_id, "COMPLETED")

    def _require_owner(self, *, actor: ActorContext) -> None:
        if not actor.membership_is_active:
            raise PermissionError("MEMBERSHIP_NOT_ACTIVE")
        with self._session_factory() as session:
            owner = session.scalar(
                sa.select(TenantOwnerRecord.id).where(
                    TenantOwnerRecord.tenant_id == actor.tenant_id,
                    TenantOwnerRecord.membership_id == actor.membership_id,
                    TenantOwnerRecord.ended_at.is_(None),
                )
            )
        if owner is None:
            raise PermissionError("ORGANIZATION_OWNER_REQUIRED")
