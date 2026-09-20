"""Small append-only contribution registry for concurrent DCE confirmations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.dce.infrastructure.models.dce_contributions import (
    DceRequirementConflictRecord,
    DceRequirementConflictResolutionRecord,
    DceRequirementContributionRecord,
)
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.platform.security.context import ActorContext, ActorKind, MembershipState


@dataclass(frozen=True, slots=True)
class RecordContributionCommand:
    contribution_id: UUID
    requirement_id: UUID
    expected_confirmation_revision: int
    source_locator: str
    basis_fingerprint: str
    proposed_outcome: str
    proposed_reason_code: str
    command_id: UUID
    idempotency_key: UUID


@dataclass(frozen=True, slots=True)
class ContributionResult:
    contribution_id: UUID
    conflict_id: UUID | None
    replayed: bool = False


class DceContributionConflictService:
    """Retain competing human proposals; never let the last write win."""

    def __init__(self, *, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def record(
        self, *, actor: ActorContext, command: RecordContributionCommand, now: datetime
    ) -> ContributionResult:
        if (
            actor.actor_kind is ActorKind.SYSTEM
            or actor.membership_state is not MembershipState.ACTIVE
        ):
            raise PermissionError("DCE_CONTRIBUTION_HUMAN_ACTIVE_ACTOR_REQUIRED")
        if command.expected_confirmation_revision < 0:
            raise ValueError("DCE_CONTRIBUTION_REVISION_INVALID")
        if len(command.basis_fingerprint) != 64 or any(
            char not in "0123456789abcdef" for char in command.basis_fingerprint.lower()
        ):
            raise ValueError("DCE_CONTRIBUTION_FINGERPRINT_REQUIRED")
        if not command.source_locator.strip():
            raise ValueError("DCE_CONTRIBUTION_SOURCE_REQUIRED")
        with self._session_factory.begin() as session:
            requirement = session.scalar(
                sa.select(DceRequirementRecord)
                .where(
                    DceRequirementRecord.tenant_id == actor.tenant_id,
                    DceRequirementRecord.id == command.requirement_id,
                )
                .with_for_update()
            )
            if requirement is None:
                raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
            replay = session.scalar(
                sa.select(DceRequirementContributionRecord).where(
                    DceRequirementContributionRecord.tenant_id == actor.tenant_id,
                    DceRequirementContributionRecord.author_actor_id == actor.actor_id,
                    DceRequirementContributionRecord.idempotency_key == command.idempotency_key,
                )
            )
            if replay is not None:
                conflict = session.scalar(
                    sa.select(DceRequirementConflictRecord).where(
                        DceRequirementConflictRecord.tenant_id == actor.tenant_id,
                        DceRequirementConflictRecord.requirement_id == command.requirement_id,
                        DceRequirementConflictRecord.observed_revision == replay.observed_revision,
                    )
                )
                return ContributionResult(replay.id, conflict.id if conflict else None, True)
            current_revision = (
                session.scalar(
                    sa.select(DceRequirementConfirmationCurrentRecord.revision).where(
                        DceRequirementConfirmationCurrentRecord.tenant_id == actor.tenant_id,
                        DceRequirementConfirmationCurrentRecord.requirement_id
                        == command.requirement_id,
                    )
                )
                or 0
            )
            contribution = DceRequirementContributionRecord(
                id=command.contribution_id,
                tenant_id=actor.tenant_id,
                requirement_id=command.requirement_id,
                observed_revision=command.expected_confirmation_revision,
                current_revision_at_submission=current_revision,
                author_actor_id=actor.actor_id,
                source_locator=command.source_locator.strip(),
                basis_fingerprint=command.basis_fingerprint.lower(),
                proposed_outcome=command.proposed_outcome,
                proposed_reason_code=command.proposed_reason_code,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                contributed_at=now,
            )
            session.add(contribution)
            session.flush()
            peer = session.scalar(
                sa.select(DceRequirementContributionRecord)
                .where(
                    DceRequirementContributionRecord.tenant_id == actor.tenant_id,
                    DceRequirementContributionRecord.requirement_id == command.requirement_id,
                    DceRequirementContributionRecord.observed_revision
                    == command.expected_confirmation_revision,
                    DceRequirementContributionRecord.id != contribution.id,
                )
                .order_by(DceRequirementContributionRecord.contributed_at)
            )
            if peer is None or _same_proposal(peer, contribution):
                return ContributionResult(contribution.id, None)
            first, second = sorted((peer.id, contribution.id), key=str)
            conflict = session.scalar(
                sa.select(DceRequirementConflictRecord).where(
                    DceRequirementConflictRecord.tenant_id == actor.tenant_id,
                    DceRequirementConflictRecord.requirement_id == command.requirement_id,
                    DceRequirementConflictRecord.observed_revision
                    == command.expected_confirmation_revision,
                )
            )
            if conflict is None:
                conflict = DceRequirementConflictRecord(
                    id=uuid4(),
                    tenant_id=actor.tenant_id,
                    requirement_id=command.requirement_id,
                    observed_revision=command.expected_confirmation_revision,
                    first_contribution_id=first,
                    second_contribution_id=second,
                    opened_at=now,
                )
                session.add(conflict)
            return ContributionResult(contribution.id, conflict.id)

    def resolve(
        self,
        *,
        actor: ActorContext,
        conflict_id: UUID,
        selected_contribution_id: UUID,
        resolution_id: UUID,
        command_id: UUID,
        idempotency_key: UUID,
        reason: str,
        now: datetime,
    ) -> UUID:
        if (
            actor.actor_kind is ActorKind.SYSTEM
            or actor.membership_state is not MembershipState.ACTIVE
        ):
            raise PermissionError("DCE_CONTRIBUTION_HUMAN_ACTIVE_ACTOR_REQUIRED")
        if not reason.strip():
            raise ValueError("DCE_CONTRIBUTION_RESOLUTION_REASON_REQUIRED")
        with self._session_factory.begin() as session:
            conflict = session.scalar(
                sa.select(DceRequirementConflictRecord)
                .where(
                    DceRequirementConflictRecord.tenant_id == actor.tenant_id,
                    DceRequirementConflictRecord.id == conflict_id,
                )
                .with_for_update()
            )
            if conflict is None:
                raise PermissionError("DCE_CONTRIBUTION_CONFLICT_NOT_FOUND")
            if selected_contribution_id not in {
                conflict.first_contribution_id,
                conflict.second_contribution_id,
            }:
                raise ValueError("DCE_CONTRIBUTION_SELECTION_INVALID")
            replay = session.scalar(
                sa.select(DceRequirementConflictResolutionRecord).where(
                    DceRequirementConflictResolutionRecord.tenant_id == actor.tenant_id,
                    DceRequirementConflictResolutionRecord.conflict_id == conflict_id,
                )
            )
            if replay is not None:
                return replay.id
            session.add(
                DceRequirementConflictResolutionRecord(
                    id=resolution_id,
                    tenant_id=actor.tenant_id,
                    conflict_id=conflict.id,
                    selected_contribution_id=selected_contribution_id,
                    resolved_by_actor_id=actor.actor_id,
                    reason=reason.strip(),
                    command_id=command_id,
                    idempotency_key=idempotency_key,
                    resolved_at=now,
                )
            )
            return resolution_id

    def require_no_open_conflict(self, *, tenant_id: UUID, requirement_id: UUID) -> None:
        with self._session_factory() as session:
            conflict = session.scalar(
                sa.select(DceRequirementConflictRecord.id)
                .outerjoin(
                    DceRequirementConflictResolutionRecord,
                    sa.and_(
                        DceRequirementConflictResolutionRecord.tenant_id
                        == DceRequirementConflictRecord.tenant_id,
                        DceRequirementConflictResolutionRecord.conflict_id
                        == DceRequirementConflictRecord.id,
                    ),
                )
                .where(
                    DceRequirementConflictRecord.tenant_id == tenant_id,
                    DceRequirementConflictRecord.requirement_id == requirement_id,
                    DceRequirementConflictResolutionRecord.id.is_(None),
                )
            )
        if conflict is not None:
            raise ValueError("DCE_REQUIREMENT_CONFLICT_OPEN")


def _same_proposal(
    left: DceRequirementContributionRecord, right: DceRequirementContributionRecord
) -> bool:
    return (
        left.source_locator == right.source_locator
        and left.basis_fingerprint == right.basis_fingerprint
        and left.proposed_outcome == right.proposed_outcome
        and left.proposed_reason_code == right.proposed_reason_code
    )
