"""Persistence adapter for patron qualifications of BOAMP observations."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4, uuid5

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord

if TYPE_CHECKING:
    from app.modules.opportunity.application.boamp_qualification import (
        BoampQualificationCommand,
    )

from app.modules.opportunity.application.boamp_qualification_errors import (
    BoampQualificationIdempotencyConflict,
)
from app.modules.opportunity.infrastructure.observation_models import (
    BoampIngestionObservationLinkRecord,
    BoampIngestionRunRecord,
    BoampOpportunityObservationRecord,
    BoampOpportunityQualificationRecord,
)
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord


@dataclass(frozen=True, slots=True)
class QualificationPersistenceResult:
    qualification_id: UUID
    event_id: UUID
    replayed: bool


@dataclass(frozen=True, slots=True)
class BoampObservationState:
    latest_qualification: BoampOpportunityQualificationRecord | None = None
    case_id: UUID | None = None
    case_created_at: datetime | None = None
    source_captures: tuple[BoampSourceCaptureRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class BoampSourceCaptureRecord:
    ingestion_run_id: UUID
    source_mode: str
    run_recorded_at: datetime
    source_contract_version: str | None
    source_response_sha256: str | None


class BoampQualificationRepository:
    def list_observations(
        self, *, session: Session, tenant_id: UUID, limit: int, min_score: int
    ) -> tuple[BoampOpportunityObservationRecord, ...]:
        return tuple(
            session.scalars(
                sa.select(BoampOpportunityObservationRecord)
                .where(
                    BoampOpportunityObservationRecord.tenant_id == tenant_id,
                    BoampOpportunityObservationRecord.score >= min_score,
                )
                .order_by(
                    BoampOpportunityObservationRecord.score.desc(),
                    BoampOpportunityObservationRecord.response_deadline.asc().nullslast(),
                    BoampOpportunityObservationRecord.id,
                )
                .limit(limit)
            )
        )

    def last_successful_ingestion_at(self, *, session: Session, tenant_id: UUID) -> datetime | None:
        """Return the latest completed, recorded BOAMP ingestion for one tenant."""
        return session.scalar(
            sa.select(BoampIngestionRunRecord.completed_at)
            .where(
                BoampIngestionRunRecord.tenant_id == tenant_id,
                BoampIngestionRunRecord.status == "RECORDED",
                BoampIngestionRunRecord.source_mode == "LIVE",
            )
            .order_by(
                BoampIngestionRunRecord.completed_at.desc(),
                BoampIngestionRunRecord.id.desc(),
            )
            .limit(1)
        )

    def states_for_observations(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        observation_ids: tuple[UUID, ...],
    ) -> dict[UUID, BoampObservationState]:
        if not observation_ids:
            return {}
        states = {observation_id: BoampObservationState() for observation_id in observation_ids}
        for qualification in session.scalars(
            sa.select(BoampOpportunityQualificationRecord)
            .where(
                BoampOpportunityQualificationRecord.tenant_id == tenant_id,
                BoampOpportunityQualificationRecord.observation_id.in_(observation_ids),
            )
            .order_by(
                BoampOpportunityQualificationRecord.created_at.desc(),
                BoampOpportunityQualificationRecord.id.desc(),
            )
        ):
            current = states[qualification.observation_id]
            if current.latest_qualification is None:
                states[qualification.observation_id] = BoampObservationState(
                    latest_qualification=qualification,
                    case_id=current.case_id,
                    case_created_at=current.case_created_at,
                )
        for case in session.scalars(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.business_origin == "OPPORTUNITY",
                CaseRecord.origin_reference_id.in_(observation_ids),
                CaseRecord.lifecycle != "ARCHIVED",
            )
        ):
            current = states[case.origin_reference_id]
            if current.case_id is None:
                states[case.origin_reference_id] = BoampObservationState(
                    latest_qualification=current.latest_qualification,
                    case_id=case.id,
                    case_created_at=case.created_at,
                    source_captures=current.source_captures,
                )

        captures_by_observation: dict[UUID, list[BoampSourceCaptureRecord]] = {
            observation_id: [] for observation_id in observation_ids
        }
        captures = session.execute(
            sa.select(BoampIngestionObservationLinkRecord, BoampIngestionRunRecord)
            .join(
                BoampIngestionRunRecord,
                sa.and_(
                    BoampIngestionRunRecord.tenant_id
                    == BoampIngestionObservationLinkRecord.tenant_id,
                    BoampIngestionRunRecord.id
                    == BoampIngestionObservationLinkRecord.ingestion_run_id,
                ),
            )
            .where(
                BoampIngestionObservationLinkRecord.tenant_id == tenant_id,
                BoampIngestionObservationLinkRecord.observation_id.in_(observation_ids),
                BoampIngestionRunRecord.status == "RECORDED",
            )
            .order_by(
                BoampIngestionObservationLinkRecord.observation_id,
                BoampIngestionRunRecord.completed_at,
                BoampIngestionRunRecord.id,
            )
        )
        for link, run in captures:
            captures_by_observation[link.observation_id].append(
                BoampSourceCaptureRecord(
                    ingestion_run_id=run.id,
                    source_mode=run.source_mode,
                    run_recorded_at=run.completed_at,
                    source_contract_version=link.source_contract_version,
                    source_response_sha256=link.source_response_sha256,
                )
            )
        for observation_id, source_captures in captures_by_observation.items():
            if source_captures:
                states[observation_id] = replace(
                    states[observation_id], source_captures=tuple(source_captures)
                )
        return states

    def persist_qualification(
        self,
        *,
        session: Session,
        tenant_id: UUID,
        actor_id: UUID,
        observation: BoampOpportunityObservationRecord,
        command: BoampQualificationCommand,
        now: datetime,
    ) -> QualificationPersistenceResult:
        qualification_id = uuid5(
            UUID("00000000-0000-0000-0000-000000000004"),
            f"boamp-qualification:{tenant_id}:{command.idempotency_key}",
        )
        candidates = session.scalars(
            sa.select(BoampOpportunityQualificationRecord).where(
                BoampOpportunityQualificationRecord.tenant_id == tenant_id,
                sa.or_(
                    BoampOpportunityQualificationRecord.id == qualification_id,
                    BoampOpportunityQualificationRecord.command_id == command.command_id,
                    BoampOpportunityQualificationRecord.idempotency_key == command.idempotency_key,
                ),
            )
        ).all()
        if len({record.id for record in candidates}) > 1:
            raise BoampQualificationIdempotencyConflict(
                "ambiguous qualification identity collision"
            )
        if candidates:
            record = candidates[0]
            if (
                record.id != qualification_id
                or record.observation_id != observation.id
                or record.decision != command.decision.value
                or record.reason_code != command.reason_code.value
            ):
                raise BoampQualificationIdempotencyConflict("qualification idempotency conflict")
            event = session.scalar(
                sa.select(DomainEventRecord).where(
                    DomainEventRecord.tenant_id == tenant_id,
                    DomainEventRecord.aggregate_id == record.id,
                    DomainEventRecord.event_type == "BoampOpportunityQualified",
                )
            )
            if event is None:
                raise BoampQualificationIdempotencyConflict(
                    "qualification replay has no audit event"
                )
            return QualificationPersistenceResult(
                qualification_id=record.id,
                event_id=event.id,
                replayed=True,
            )

        record = BoampOpportunityQualificationRecord(
            id=qualification_id,
            tenant_id=tenant_id,
            observation_id=observation.id,
            actor_id=actor_id,
            decision=command.decision.value,
            reason_code=command.reason_code.value,
            score_snapshot=observation.score,
            score_version=observation.score_version,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        event_id = uuid4()
        session.add(
            DomainEventRecord(
                id=event_id,
                tenant_id=tenant_id,
                aggregate_type="BoampOpportunityQualification",
                aggregate_id=qualification_id,
                aggregate_revision=0,
                event_type="BoampOpportunityQualified",
                payload_version=1,
                payload_json={
                    "qualification_id": str(qualification_id),
                    "observation_id": str(observation.id),
                    "decision": command.decision.value,
                    "reason_code": command.reason_code.value,
                    "score_snapshot": observation.score,
                },
                actor_id=actor_id,
                command_id=command.command_id,
                correlation_id=command.correlation_id,
                causation_id=None,
                occurred_at=now,
            )
        )
        session.flush()
        session.add(
            OutboxMessageRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                event_id=event_id,
                topic="opportunity.boamp.qualification.recorded",
                payload_version=1,
                payload_json={
                    "qualification_id": str(qualification_id),
                    "observation_id": str(observation.id),
                    "decision": command.decision.value,
                    "reason_code": command.reason_code.value,
                },
                status="PENDING",
                attempt_count=0,
                next_attempt_at=None,
                published_at=None,
                last_error_code=None,
                dedupe_key=f"boamp-qualification:{tenant_id}:{qualification_id}",
            )
        )
        return QualificationPersistenceResult(
            qualification_id=qualification_id,
            event_id=event_id,
            replayed=False,
        )
