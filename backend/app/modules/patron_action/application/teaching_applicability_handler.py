from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.application.teaching_applicability_commands import (
    RecordCaseTeachingApplicabilityCommand,
)
from app.modules.patron_action.domain.teaching_applicability import (
    build_case_teaching_applicability,
)
from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord
from app.modules.patron_action.infrastructure.models.teaching_applicability import (
    CaseTeachingApplicabilityRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, DataClassification


class RecordCaseTeachingApplicabilityHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: RecordCaseTeachingApplicabilityCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        target_case_exists = session.scalar(
            sa.select(CaseRecord.id).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == command.target_case_id,
            )
        )
        source = session.scalar(
            sa.select(CaseInterviewRecord).where(
                CaseInterviewRecord.tenant_id == tenant_id,
                CaseInterviewRecord.case_id == command.source_case_id,
                CaseInterviewRecord.id == command.source_interview_id,
            )
        )
        if target_case_exists is None or source is None:
            raise CommandExecutionError("SOURCE_OR_TARGET_CASE_NOT_FOUND_OR_FORBIDDEN")
        if (
            session.scalar(
                sa.select(CaseTeachingApplicabilityRecord.id).where(
                    CaseTeachingApplicabilityRecord.tenant_id == tenant_id,
                    CaseTeachingApplicabilityRecord.id == command.applicability_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("TEACHING_APPLICABILITY_ID_REUSED")

        snapshot_rows = source.snapshot_json.get("rex")
        if not isinstance(snapshot_rows, list):
            raise CommandExecutionError("SOURCE_SNAPSHOT_UNAVAILABLE")
        selected_snapshot = next(
            (
                item
                for item in snapshot_rows
                if isinstance(item, dict) and item.get("rex_id") == str(command.source_rex_id)
            ),
            None,
        )
        if selected_snapshot is None:
            raise CommandExecutionError("SOURCE_TEACHING_NOT_FOUND_OR_FORBIDDEN")

        source_rex = session.scalar(
            sa.select(CaseRexRecord).where(
                CaseRexRecord.tenant_id == tenant_id,
                CaseRexRecord.case_id == command.source_case_id,
                CaseRexRecord.id == command.source_rex_id,
            )
        )
        if source_rex is None or not _snapshot_matches_record(selected_snapshot, source_rex):
            raise CommandExecutionError("SOURCE_SNAPSHOT_MISMATCH")

        try:
            applicability = build_case_teaching_applicability(
                source_case_id=source.case_id,
                target_case_id=command.target_case_id,
                source_interview_id=source.id,
                source_rex_id=command.source_rex_id,
                decision=command.decision,
                rationale=command.rationale,
                target_source_locator=command.target_source_locator,
                source_expires_on=source.expires_on,
                source_snapshot=selected_snapshot,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error

        recorded_at = context.received_at
        source_validity = applicability.source_validity(recorded_at.date())
        session.add(
            CaseTeachingApplicabilityRecord(
                id=command.applicability_id,
                tenant_id=tenant_id,
                target_case_id=applicability.target_case_id,
                source_interview_id=applicability.source_interview_id,
                source_rex_id=applicability.source_rex_id,
                decision=applicability.decision,
                rationale=applicability.rationale,
                target_source_locator=applicability.target_source_locator,
                source_expires_on=applicability.source_expires_on,
                source_validity_at_recording=source_validity,
                source_snapshot_json=applicability.source_snapshot,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return HandlerOutcome(
            result_code="CASE_TEACHING_APPLICABILITY_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CASE_TEACHING_APPLICABILITY",
                    "aggregate_id": str(command.applicability_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CASE_TEACHING_APPLICABILITY",
                    aggregate_id=command.applicability_id,
                    aggregate_revision=1,
                    event_type="CASE_TEACHING_APPLICABILITY_RECORDED",
                    payload={
                        "target_case_id": str(command.target_case_id),
                        "source_interview_id": str(source.id),
                        "source_rex_id": str(command.source_rex_id),
                        "decision": applicability.decision,
                        "source_validity": source_validity,
                    },
                ),
            ),
        )


def _snapshot_matches_record(snapshot: dict[str, object], record: CaseRexRecord) -> bool:
    return all(
        snapshot.get(key) == value
        for key, value in {
            "rex_id": str(record.id),
            "lot_reference": record.lot_reference,
            "motif": record.motif,
            "scope": record.scope,
            "validation": record.validation,
            "observation": record.observation,
            "consequence": record.consequence,
            "follow_up": record.follow_up,
            "source_locator": record.source_locator,
        }.items()
    )


def case_teaching_applicability_handlers() -> dict[str, CommandHandler]:
    command_type = RecordCaseTeachingApplicabilityCommand.command_type
    return {command_type: RecordCaseTeachingApplicabilityHandler()}


@dataclass(frozen=True, slots=True)
class CaseTeachingSourceProjection:
    source_case_id: UUID
    source_case_label: str
    source_interview_id: UUID
    source_rex_id: UUID
    held_on: date
    source_locator: str
    interview_rationale: str
    expires_on: date
    source_validity: str
    snapshot: dict[str, object]
    can_assess: bool
    block_reason: str | None


@dataclass(frozen=True, slots=True)
class CaseTeachingApplicabilityProjection:
    record: CaseTeachingApplicabilityRecord
    source_case_id: UUID
    source_case_label: str
    source_validity: str


class CaseTeachingApplicabilityService:
    def __init__(self, *, dispatcher, session_factory, policy: AuthorizationPolicyPort) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def _authorize(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="CASE_TEACHING_APPLICABILITY",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=case_id,
                ),
                evaluated_at=now,
            ),
        )
        if not decision.allowed:
            raise PermissionError(decision.code)

    def record_applicability(
        self,
        *,
        actor: ActorContext,
        command: RecordCaseTeachingApplicabilityCommand,
        now: datetime,
    ):
        self._authorize(
            actor=actor,
            case_id=command.target_case_id,
            action=Capability.PATRON_ACTION_WRITE,
            now=now,
        )
        self._authorize(
            actor=actor,
            case_id=command.source_case_id,
            action=Capability.PATRON_ACTION_READ,
            now=now,
        )
        return self._dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=actor.tenant_id,
                actor_id=actor.actor_id,
                actor_kind=actor.actor_kind.value,
                received_at=now,
                identity_id=actor.identity_id,
                membership_id=actor.membership_id,
                session_id=actor.session_id,
                case_id=command.target_case_id,
                correlation_id=actor.correlation_id,
            ),
        )

    def list_sources(
        self, *, actor: ActorContext, target_case_id: UUID, now: datetime
    ) -> tuple[CaseTeachingSourceProjection, ...]:
        self._authorize(
            actor=actor,
            case_id=target_case_id,
            action=Capability.PATRON_ACTION_READ,
            now=now,
        )
        with self._session_factory() as session:
            target_exists = session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == actor.tenant_id,
                    CaseRecord.id == target_case_id,
                )
            )
            if target_exists is None:
                return ()
            rows = session.execute(
                sa.select(CaseInterviewRecord, CaseRecord.title)
                .join(
                    CaseRecord,
                    sa.and_(
                        CaseRecord.tenant_id == CaseInterviewRecord.tenant_id,
                        CaseRecord.id == CaseInterviewRecord.case_id,
                    ),
                )
                .where(CaseInterviewRecord.tenant_id == actor.tenant_id)
                .order_by(CaseInterviewRecord.created_at.desc(), CaseInterviewRecord.id.desc())
            ).all()
            projections: list[CaseTeachingSourceProjection] = []
            today = now.date()
            for interview, source_label in rows:
                try:
                    self._authorize(
                        actor=actor,
                        case_id=interview.case_id,
                        action=Capability.PATRON_ACTION_READ,
                        now=now,
                    )
                except PermissionError:
                    continue
                teachings = interview.snapshot_json.get("rex")
                if not isinstance(teachings, list):
                    continue
                for teaching in teachings:
                    if not isinstance(teaching, dict) or not isinstance(
                        teaching.get("rex_id"), str
                    ):
                        continue
                    scope = teaching.get("scope")
                    validation = teaching.get("validation")
                    snapshot_complete = all(
                        field in teaching
                        for field in ("observation", "consequence", "follow_up", "source_locator")
                    )
                    can_assess = (
                        snapshot_complete
                        and validation == "APPROVED"
                        and (
                            scope in {"LOT_PATTERN", "ENTERPRISE_PATTERN"}
                            or (scope == "CASE_ONLY" and interview.case_id == target_case_id)
                        )
                    )
                    block_reason = None
                    if not snapshot_complete:
                        block_reason = "SOURCE_SNAPSHOT_INCOMPLETE"
                    elif validation != "APPROVED":
                        block_reason = "REX_REVIEW_REQUIRED"
                    elif scope == "CASE_ONLY" and interview.case_id != target_case_id:
                        block_reason = "CASE_ONLY_TEACHING_CANNOT_CROSS_CASES"
                    elif scope not in {"CASE_ONLY", "LOT_PATTERN", "ENTERPRISE_PATTERN"}:
                        block_reason = "SOURCE_SCOPE_UNKNOWN"
                    projections.append(
                        CaseTeachingSourceProjection(
                            source_case_id=interview.case_id,
                            source_case_label=source_label,
                            source_interview_id=interview.id,
                            source_rex_id=UUID(teaching["rex_id"]),
                            held_on=interview.held_on,
                            source_locator=interview.source_locator,
                            interview_rationale=interview.rationale,
                            expires_on=interview.expires_on,
                            source_validity="USABLE"
                            if interview.expires_on >= today
                            else "EXPIRED",
                            snapshot=dict(teaching),
                            can_assess=can_assess,
                            block_reason=block_reason,
                        )
                    )
            return tuple(projections)

    def list_for_case(
        self, *, actor: ActorContext, target_case_id: UUID, now: datetime
    ) -> tuple[CaseTeachingApplicabilityProjection, ...]:
        self._authorize(
            actor=actor,
            case_id=target_case_id,
            action=Capability.PATRON_ACTION_READ,
            now=now,
        )
        with self._session_factory() as session:
            rows = session.execute(
                sa.select(
                    CaseTeachingApplicabilityRecord, CaseInterviewRecord.case_id, CaseRecord.title
                )
                .join(
                    CaseInterviewRecord,
                    sa.and_(
                        CaseInterviewRecord.tenant_id == CaseTeachingApplicabilityRecord.tenant_id,
                        CaseInterviewRecord.id
                        == CaseTeachingApplicabilityRecord.source_interview_id,
                    ),
                )
                .join(
                    CaseRecord,
                    sa.and_(
                        CaseRecord.tenant_id == CaseInterviewRecord.tenant_id,
                        CaseRecord.id == CaseInterviewRecord.case_id,
                    ),
                )
                .where(
                    CaseTeachingApplicabilityRecord.tenant_id == actor.tenant_id,
                    CaseTeachingApplicabilityRecord.target_case_id == target_case_id,
                )
                .order_by(
                    CaseTeachingApplicabilityRecord.created_at.asc(),
                    CaseTeachingApplicabilityRecord.id.asc(),
                )
            ).all()
            today = now.date()
            projections: list[CaseTeachingApplicabilityProjection] = []
            for record, source_case_id, source_case_label in rows:
                try:
                    self._authorize(
                        actor=actor,
                        case_id=source_case_id,
                        action=Capability.PATRON_ACTION_READ,
                        now=now,
                    )
                except PermissionError:
                    continue
                projections.append(
                    CaseTeachingApplicabilityProjection(
                        record=record,
                        source_case_id=source_case_id,
                        source_case_label=source_case_label,
                        source_validity="USABLE"
                        if record.source_expires_on >= today
                        else "EXPIRED",
                    )
                )
            return tuple(projections)
