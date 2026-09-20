"""Patronal reading and human qualification of persisted BOAMP observations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.opportunity.infrastructure.boamp_qualification_repository import (
    BoampObservationState,
    BoampQualificationRepository,
    QualificationPersistenceResult,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampOpportunityObservationRecord,
    BoampOpportunityQualificationRecord,
)
from app.platform.events.dispatcher import CommandContext
from app.platform.security.context import ActorKind
from app.platform.security.models import TenantMembershipRecord


class QualificationDecision(StrEnum):
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    SNOOZED = "SNOOZED"


class QualificationReason(StrEnum):
    RELEVANT_PUBLIC_SIGNAL = "RELEVANT_PUBLIC_SIGNAL"
    NOT_RELEVANT = "NOT_RELEVANT"
    INSUFFICIENT_PUBLIC_DATA = "INSUFFICIENT_PUBLIC_DATA"
    EXPIRED = "EXPIRED"


class BoampP0State(StrEnum):
    UNREVIEWED = "UNREVIEWED"
    TARGETED = "TARGETED"
    SNOOZED = "SNOOZED"
    DISCARDED = "DISCARDED"


class BoampP1State(StrEnum):
    NOT_OPEN = "NOT_OPEN"
    OPEN_WITH_UNKNOWNS = "OPEN_WITH_UNKNOWNS"


class BoampLotScopeState(StrEnum):
    UNKNOWN = "UNKNOWN"
    IDENTIFIED = "IDENTIFIED"
    CONFLICTING = "CONFLICTING"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class BoampDeadlineState(StrEnum):
    KNOWN = "KNOWN"
    MISSING = "MISSING"
    EXPIRED = "EXPIRED"
    CONFLICTING = "CONFLICTING"


class BoampUnknownCode(StrEnum):
    LOT_SCOPE = "LOT_SCOPE"
    DCE_NOT_RECEIVED = "DCE_NOT_RECEIVED"
    DEADLINE_MISSING = "DEADLINE_MISSING"
    DEADLINE_CONFLICT = "DEADLINE_CONFLICT"


@dataclass(frozen=True, slots=True)
class BoampQualificationCommand:
    observation_id: UUID
    decision: QualificationDecision
    reason_code: QualificationReason
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None

    def validate(self) -> None:
        allowed = {
            QualificationDecision.QUALIFIED: {QualificationReason.RELEVANT_PUBLIC_SIGNAL},
            QualificationDecision.REJECTED: {
                QualificationReason.NOT_RELEVANT,
                QualificationReason.EXPIRED,
            },
            QualificationDecision.SNOOZED: {QualificationReason.INSUFFICIENT_PUBLIC_DATA},
        }
        if self.reason_code not in allowed[self.decision]:
            raise ValueError("qualification decision and reason are incompatible")


@dataclass(frozen=True, slots=True)
class PatronBoampObservationProjection:
    observation_id: UUID
    source_notice_id: str
    title: str | None
    observed_at: str
    publication_date: str | None
    response_deadline: str | None
    department_codes: tuple[str, ...]
    market_types: tuple[str, ...]
    source_status: str | None
    score_version: str
    score: int
    score_explanation: dict[str, object]
    fingerprint_sha256: str
    p0_state: BoampP0State
    p0_decision: QualificationDecision | None
    p0_reason_code: QualificationReason | None
    p0_qualification_id: UUID | None
    p0_decided_at: str | None
    p1_state: BoampP1State
    p1_case_id: UUID | None
    p1_opened_at: str | None
    lot_scope_state: BoampLotScopeState
    lot_references: tuple[str, ...]
    lot_scope_source: str | None
    deadline_state: BoampDeadlineState
    deadline_source: str | None
    deadline_source_timezone: str | None
    deadline_normalized_timezone: str | None
    unknowns: tuple[dict[str, object], ...]


class PatronBoampObservationService:
    def __init__(self, *, repository: BoampQualificationRepository) -> None:
        self._repository = repository

    def read(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        actor_id: UUID,
        actor_kind: str,
        limit: int = 50,
        min_score: int = 0,
        now: datetime | None = None,
    ) -> tuple[PatronBoampObservationProjection, ...]:
        if not 1 <= limit <= 200:
            raise ValueError("limit must be between 1 and 200")
        if not 0 <= min_score <= 100:
            raise ValueError("min_score must be between 0 and 100")
        self._require_patron_membership(
            session=session, tenant_id=tenant_id, actor_id=actor_id, actor_kind=actor_kind
        )
        records = self._repository.list_observations(
            session=session, tenant_id=tenant_id, limit=limit, min_score=min_score
        )
        states = self._repository.states_for_observations(
            session=session,
            tenant_id=tenant_id,
            observation_ids=tuple(record.id for record in records),
        )
        current = now or datetime.now().astimezone()
        return tuple(
            _projection(record, states.get(record.id, BoampObservationState()), now=current)
            for record in records
        )

    def qualify(
        self,
        *,
        session: Session,
        context: CommandContext,
        command: BoampQualificationCommand,
        now: datetime,
    ) -> QualificationPersistenceResult:
        if context.actor_kind != ActorKind.PATRON_ADMIN.value:
            raise PermissionError("BOAMP_QUALIFICATION_PATRON_REQUIRED")
        tenant_id = UUID(str(context.tenant_id))
        actor_id = UUID(str(context.actor_id))
        command.validate()
        self._require_patron_membership(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_kind=context.actor_kind,
        )
        observation = session.scalar(
            sa.select(BoampOpportunityObservationRecord).where(
                BoampOpportunityObservationRecord.tenant_id == tenant_id,
                BoampOpportunityObservationRecord.id == command.observation_id,
            )
        )
        if observation is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        return self._repository.persist_qualification(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            observation=observation,
            command=command,
            now=now,
        )

    @staticmethod
    def _require_patron_membership(
        *, session: Session, tenant_id: UUID, actor_id: UUID, actor_kind: str
    ) -> None:
        if actor_kind != ActorKind.PATRON_ADMIN.value:
            raise PermissionError("BOAMP_QUALIFICATION_PATRON_REQUIRED")
        member = session.scalar(
            sa.select(TenantMembershipRecord.id).where(
                TenantMembershipRecord.tenant_id == tenant_id,
                TenantMembershipRecord.identity_id == actor_id,
                TenantMembershipRecord.role == ActorKind.PATRON_ADMIN.value,
                TenantMembershipRecord.state == "ACTIVE",
            )
        )
        if member is None:
            raise PermissionError("BOAMP_QUALIFICATION_PATRON_REQUIRED")


def _projection(
    record: BoampOpportunityObservationRecord,
    state: BoampObservationState,
    *,
    now: datetime,
) -> PatronBoampObservationProjection:
    qualification = state.latest_qualification
    p0_state = _p0_state(qualification)
    p1_state = (
        BoampP1State.OPEN_WITH_UNKNOWNS
        if state.case_id is not None
        else BoampP1State.NOT_OPEN
    )
    deadline_state = _deadline_state(
        record.response_deadline,
        now=now,
    )
    return PatronBoampObservationProjection(
        observation_id=record.id,
        source_notice_id=record.source_notice_id,
        title=record.title,
        observed_at=record.observed_at.isoformat(),
        publication_date=record.publication_date.isoformat()
        if record.publication_date is not None
        else None,
        response_deadline=record.response_deadline.isoformat()
        if record.response_deadline is not None
        else None,
        department_codes=tuple(record.department_codes),
        market_types=tuple(record.market_types),
        source_status=record.source_status,
        score_version=record.score_version,
        score=record.score,
        score_explanation=dict(record.score_explanation_json),
        fingerprint_sha256=record.fingerprint_sha256,
        p0_state=p0_state,
        p0_decision=(
            QualificationDecision(qualification.decision) if qualification is not None else None
        ),
        p0_reason_code=(
            QualificationReason(qualification.reason_code) if qualification is not None else None
        ),
        p0_qualification_id=qualification.id if qualification is not None else None,
        p0_decided_at=qualification.created_at.isoformat() if qualification is not None else None,
        p1_state=p1_state,
        p1_case_id=state.case_id,
        p1_opened_at=state.case_created_at.isoformat() if state.case_created_at else None,
        lot_scope_state=BoampLotScopeState.UNKNOWN,
        lot_references=(),
        lot_scope_source="BOAMP",
        deadline_state=deadline_state,
        deadline_source="BOAMP" if record.response_deadline is not None else None,
        deadline_source_timezone=None,
        deadline_normalized_timezone="UTC" if record.response_deadline is not None else None,
        unknowns=_unknowns(
            record,
            deadline_state=deadline_state,
            opened=state.case_id is not None,
        ),
    )


def _p0_state(
    qualification: BoampOpportunityQualificationRecord | None,
) -> BoampP0State:
    if qualification is None:
        return BoampP0State.UNREVIEWED
    if qualification.decision == QualificationDecision.QUALIFIED.value:
        return BoampP0State.TARGETED
    if qualification.decision == QualificationDecision.SNOOZED.value:
        return BoampP0State.SNOOZED
    return BoampP0State.DISCARDED


def _deadline_state(
    response_deadline: datetime | None,
    *,
    now: datetime,
) -> BoampDeadlineState:
    if response_deadline is None:
        return BoampDeadlineState.MISSING
    current = now if now.tzinfo is not None else now.astimezone()
    deadline = (
        response_deadline
        if response_deadline.tzinfo is not None
        else response_deadline.astimezone()
    )
    return BoampDeadlineState.EXPIRED if deadline < current else BoampDeadlineState.KNOWN


def _unknowns(
    record: BoampOpportunityObservationRecord,
    *,
    deadline_state: BoampDeadlineState,
    opened: bool,
) -> tuple[dict[str, object], ...]:
    if not opened:
        return ()
    source_ref = f"BOAMP:{record.source_notice_id}"
    unknowns: list[dict[str, object]] = [
        {
            "code": BoampUnknownCode.LOT_SCOPE.value,
            "missing": "Référence(s) de lot",
            "why_it_matters": "P1 exige un périmètre de lot connu ou signalé manquant.",
            "possible_impact": "Périmètre d’étude et de prix non démontré.",
            "responsible": None,
            "next_action": "Obtenir le RC/DCE ou saisir une référence de lot sourcée.",
            "due_at": None,
            "state": "OPEN",
            "source_ref": source_ref,
        },
        {
            "code": BoampUnknownCode.DCE_NOT_RECEIVED.value,
            "missing": "DCE ou dossier de candidature",
            "why_it_matters": (
                "L’ouverture P1 doit reposer sur un dossier reçu ou une phase documentée."
            ),
            "possible_impact": "Éligibilité et exigences non vérifiables.",
            "responsible": None,
            "next_action": "Obtenir et contrôler le dossier avant toute porte P2.",
            "due_at": None,
            "state": "OPEN",
            "source_ref": source_ref,
        },
    ]
    if deadline_state == BoampDeadlineState.MISSING:
        unknowns.append(
            {
                "code": BoampUnknownCode.DEADLINE_MISSING.value,
                "missing": "Date limite de réponse",
                "why_it_matters": (
                    "Une échéance absente ne permet pas de sécuriser l’effort d’étude."
                ),
                "possible_impact": "Risque de remise hors délai.",
                "responsible": None,
                "next_action": "Confirmer la date auprès de la source ou du dossier reçu.",
                "due_at": None,
                "state": "OPEN",
                "source_ref": source_ref,
            }
        )
    return tuple(unknowns)
