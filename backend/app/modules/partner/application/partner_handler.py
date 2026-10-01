from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.partner.application.commands import (
    DeclareCasePartnerEngagementCommand,
    RecordCasePartnerReceiptCommand,
    RecordCasePartnerRequestCommand,
)
from app.modules.partner.domain.events import (
    PartnerReceipt,
    build_partner_receipt,
    build_partner_request,
    validate_partner_engagement,
)
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    DispatchResult,
    HandlerOutcome,
    PendingDomainEvent,
)
from app.platform.security.authorization import (
    AuthorizationPolicyPort,
    AuthorizationRequest,
    AuthorizationResource,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, DataClassification


def _lock_case(session: Session, *, tenant_id: UUID, case_id: UUID) -> None:
    exists = session.scalar(
        sa.select(CaseRecord.id)
        .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
        .with_for_update()
    )
    if exists is None:
        raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")


def _latest_event(session: Session, *, tenant_id: UUID, case_id: UUID, partner_id: UUID):
    return session.scalar(
        sa.select(CasePartnerEventRecord)
        .where(
            CasePartnerEventRecord.tenant_id == tenant_id,
            CasePartnerEventRecord.case_id == case_id,
            CasePartnerEventRecord.partner_id == partner_id,
        )
        .order_by(CasePartnerEventRecord.revision.desc())
        .limit(1)
        .with_for_update()
    )


def _assert_event_id_available(session: Session, *, tenant_id: UUID, event_id: UUID) -> None:
    if (
        session.scalar(
            sa.select(CasePartnerEventRecord.event_id).where(
                CasePartnerEventRecord.event_id == event_id,
            )
        )
        is not None
    ):
        raise CommandExecutionError("PARTNER_EVENT_ID_REUSED")


def _next_revision(expected_revision: int, current: CasePartnerEventRecord | None) -> int:
    revision = current.revision if current is not None else 0
    if expected_revision != revision:
        raise CommandExecutionError("PARTNER_VERSION_CONFLICT")
    return revision + 1


def _assert_identity(current, *, partner_kind: str, partner_label: str) -> None:
    if current is not None and (
        current.partner_kind != partner_kind or current.partner_label != partner_label
    ):
        raise CommandExecutionError("PARTNER_IDENTITY_CONFLICT")


def _validity(valid_until: date | None, *, on_date: date) -> str:
    if valid_until is None:
        return "UNKNOWN"
    return "VALID" if valid_until >= on_date else "EXPIRED"


def _outcome(*, event_id: UUID, partner_id: UUID, revision: int, kind: str, case_id: UUID):
    return HandlerOutcome(
        result_code=f"CASE_PARTNER_{kind}_RECORDED",
        aggregate_refs=(
            {
                "aggregate_type": "CASE_PARTNER",
                "aggregate_id": str(partner_id),
                "aggregate_revision": revision,
            },
        ),
        events=(
            PendingDomainEvent(
                aggregate_type="CASE_PARTNER",
                aggregate_id=partner_id,
                aggregate_revision=revision,
                event_type=f"CASE_PARTNER_{kind}_RECORDED",
                payload={
                    "event_id": str(event_id),
                    "partner_id": str(partner_id),
                    "case_id": str(case_id),
                },
            ),
        ),
    )


class RecordCasePartnerRequestHandler(CommandHandler):
    def execute(
        self, *, session: Session, command: RecordCasePartnerRequestCommand, context: CommandContext
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        _lock_case(session, tenant_id=tenant_id, case_id=command.case_id)
        _assert_event_id_available(session, tenant_id=tenant_id, event_id=command.event_id)
        current = _latest_event(
            session, tenant_id=tenant_id, case_id=command.case_id, partner_id=command.partner_id
        )
        revision = _next_revision(command.expected_revision, current)
        _assert_identity(
            current, partner_kind=command.partner_kind, partner_label=command.partner_label.strip()
        )
        try:
            request = build_partner_request(
                partner_kind=command.partner_kind,
                partner_label=command.partner_label,
                source_locator=command.source_locator,
                rationale=command.rationale,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        session.add(
            CasePartnerEventRecord(
                event_id=command.event_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                partner_id=command.partner_id,
                revision=revision,
                event_type="REQUESTED",
                partner_kind=request.partner_kind,
                partner_label=request.partner_label,
                related_event_id=None,
                source_locator=request.source_locator,
                rationale=request.rationale,
                valid_until=None,
                validity_at_recording="UNKNOWN",
                exclusions_state="UNKNOWN",
                exclusions_json=[],
                mandate_state="UNKNOWN",
                mandate_source_locator=None,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return _outcome(
            event_id=command.event_id,
            partner_id=command.partner_id,
            revision=revision,
            kind="REQUESTED",
            case_id=command.case_id,
        )


class RecordCasePartnerReceiptHandler(CommandHandler):
    def execute(
        self, *, session: Session, command: RecordCasePartnerReceiptCommand, context: CommandContext
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        _lock_case(session, tenant_id=tenant_id, case_id=command.case_id)
        _assert_event_id_available(session, tenant_id=tenant_id, event_id=command.event_id)
        current = _latest_event(
            session, tenant_id=tenant_id, case_id=command.case_id, partner_id=command.partner_id
        )
        revision = _next_revision(command.expected_revision, current)
        _assert_identity(
            current, partner_kind=command.partner_kind, partner_label=command.partner_label.strip()
        )
        if command.request_event_id is not None:
            request = session.scalar(
                sa.select(CasePartnerEventRecord).where(
                    CasePartnerEventRecord.tenant_id == tenant_id,
                    CasePartnerEventRecord.case_id == command.case_id,
                    CasePartnerEventRecord.partner_id == command.partner_id,
                    CasePartnerEventRecord.event_id == command.request_event_id,
                    CasePartnerEventRecord.event_type == "REQUESTED",
                )
            )
            if request is None:
                raise CommandExecutionError("PARTNER_REQUEST_NOT_FOUND_OR_FORBIDDEN")
            receipt_exists = session.scalar(
                sa.select(CasePartnerEventRecord.event_id).where(
                    CasePartnerEventRecord.tenant_id == tenant_id,
                    CasePartnerEventRecord.event_type == "RECEIVED",
                    CasePartnerEventRecord.related_event_id == command.request_event_id,
                )
            )
            if receipt_exists is not None:
                raise CommandExecutionError("PARTNER_REQUEST_ALREADY_RECEIVED")
        try:
            receipt = build_partner_receipt(
                receipt_id=command.event_id,
                partner_kind=command.partner_kind,
                partner_label=command.partner_label,
                source_locator=command.source_locator,
                rationale=command.rationale,
                valid_until=command.valid_until,
                exclusions_state=command.exclusions_state,
                exclusions=command.exclusions,
                mandate_state=command.mandate_state,
                mandate_source_locator=command.mandate_source_locator,
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        validity = receipt.validity(context.received_at.date())
        session.add(
            CasePartnerEventRecord(
                event_id=command.event_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                partner_id=command.partner_id,
                revision=revision,
                event_type="RECEIVED",
                partner_kind=receipt.partner_kind,
                partner_label=receipt.partner_label,
                related_event_id=command.request_event_id,
                source_locator=receipt.source_locator,
                rationale=receipt.rationale,
                valid_until=receipt.valid_until,
                validity_at_recording=validity,
                exclusions_state=receipt.exclusions_state,
                exclusions_json=list(receipt.exclusions),
                mandate_state=receipt.mandate_state,
                mandate_source_locator=receipt.mandate_source_locator,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return _outcome(
            event_id=command.event_id,
            partner_id=command.partner_id,
            revision=revision,
            kind="RECEIVED",
            case_id=command.case_id,
        )


class DeclareCasePartnerEngagementHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command: DeclareCasePartnerEngagementCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        tenant_id = UUID(str(context.tenant_id))
        _lock_case(session, tenant_id=tenant_id, case_id=command.case_id)
        _assert_event_id_available(session, tenant_id=tenant_id, event_id=command.event_id)
        current = _latest_event(
            session, tenant_id=tenant_id, case_id=command.case_id, partner_id=command.partner_id
        )
        revision = _next_revision(command.expected_revision, current)
        receipt_row = session.scalar(
            sa.select(CasePartnerEventRecord)
            .where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.partner_id == command.partner_id,
                CasePartnerEventRecord.event_id == command.receipt_event_id,
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
            .with_for_update()
        )
        if receipt_row is None:
            raise CommandExecutionError("PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN")
        latest_receipt_id = session.scalar(
            sa.select(CasePartnerEventRecord.event_id)
            .where(
                CasePartnerEventRecord.tenant_id == tenant_id,
                CasePartnerEventRecord.case_id == command.case_id,
                CasePartnerEventRecord.partner_id == command.partner_id,
                CasePartnerEventRecord.event_type == "RECEIVED",
            )
            .order_by(CasePartnerEventRecord.revision.desc())
            .limit(1)
        )
        if latest_receipt_id != receipt_row.event_id:
            raise CommandExecutionError("PARTNER_RECEIPT_VERSION_CONFLICT")
        if (
            session.scalar(
                sa.select(CasePartnerEventRecord.event_id).where(
                    CasePartnerEventRecord.tenant_id == tenant_id,
                    CasePartnerEventRecord.event_type == "ENGAGEMENT_DECLARED",
                    CasePartnerEventRecord.related_event_id == receipt_row.event_id,
                )
            )
            is not None
        ):
            raise CommandExecutionError("PARTNER_RECEIPT_ALREADY_ENGAGED")
        receipt = PartnerReceipt(
            receipt_id=receipt_row.event_id,
            event_type="RECEIVED",
            partner_kind=receipt_row.partner_kind,
            partner_label=receipt_row.partner_label,
            source_locator=receipt_row.source_locator,
            rationale=receipt_row.rationale,
            valid_until=receipt_row.valid_until,
            exclusions_state=receipt_row.exclusions_state,
            exclusions=tuple(receipt_row.exclusions_json),
            mandate_state=receipt_row.mandate_state,
            mandate_source_locator=receipt_row.mandate_source_locator,
        )
        try:
            engagement = validate_partner_engagement(
                receipt=receipt, source_locator=command.source_locator, rationale=command.rationale
            )
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        validity = receipt.validity(context.received_at.date())
        session.add(
            CasePartnerEventRecord(
                event_id=command.event_id,
                tenant_id=tenant_id,
                case_id=command.case_id,
                partner_id=command.partner_id,
                revision=revision,
                event_type="ENGAGEMENT_DECLARED",
                partner_kind=receipt_row.partner_kind,
                partner_label=receipt_row.partner_label,
                related_event_id=receipt_row.event_id,
                source_locator=engagement.source_locator,
                rationale=engagement.rationale,
                valid_until=receipt_row.valid_until,
                validity_at_recording=validity,
                exclusions_state=receipt_row.exclusions_state,
                exclusions_json=list(receipt_row.exclusions_json),
                mandate_state=receipt_row.mandate_state,
                mandate_source_locator=receipt_row.mandate_source_locator,
                actor_id=UUID(str(context.actor_id)),
                membership_id=UUID(str(context.membership_id)),
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        return _outcome(
            event_id=command.event_id,
            partner_id=command.partner_id,
            revision=revision,
            kind="ENGAGEMENT_DECLARED",
            case_id=command.case_id,
        )


def partner_event_handlers() -> dict[str, CommandHandler]:
    return {
        RecordCasePartnerRequestCommand.command_type: RecordCasePartnerRequestHandler(),
        RecordCasePartnerReceiptCommand.command_type: RecordCasePartnerReceiptHandler(),
        DeclareCasePartnerEngagementCommand.command_type: DeclareCasePartnerEngagementHandler(),
    }


@dataclass(frozen=True, slots=True)
class PartnerEventProjection:
    record: CasePartnerEventRecord
    validity_current: str


@dataclass(frozen=True, slots=True)
class CasePartnerListProjection:
    case_id: UUID
    events: tuple[PartnerEventProjection, ...]
    can_request: bool
    can_receive: bool
    can_declare_engagement: bool


class CasePartnerService:
    def __init__(
        self, *, dispatcher, session_factory: sessionmaker[Session], policy: AuthorizationPolicyPort
    ) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def record_request(
        self, *, actor: ActorContext, command: RecordCasePartnerRequestCommand, now: datetime
    ) -> DispatchResult:
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.CASE_PARTNER_WRITE, now=now
        )
        return self._dispatch(actor=actor, command=command, now=now, case_id=command.case_id)

    def record_receipt(
        self, *, actor: ActorContext, command: RecordCasePartnerReceiptCommand, now: datetime
    ) -> DispatchResult:
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.CASE_PARTNER_WRITE, now=now
        )
        return self._dispatch(actor=actor, command=command, now=now, case_id=command.case_id)

    def declare_engagement(
        self, *, actor: ActorContext, command: DeclareCasePartnerEngagementCommand, now: datetime
    ) -> DispatchResult:
        self._authorize(
            actor=actor, case_id=command.case_id, action=Capability.CASE_PARTNER_ENGAGE, now=now
        )
        return self._dispatch(actor=actor, command=command, now=now, case_id=command.case_id)

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> CasePartnerListProjection:
        self._authorize(actor=actor, case_id=case_id, action=Capability.CASE_PARTNER_READ, now=now)
        with self._session_factory() as session:
            exists = session.scalar(
                sa.select(CaseRecord.id).where(
                    CaseRecord.tenant_id == actor.tenant_id, CaseRecord.id == case_id
                )
            )
            if exists is None:
                return CasePartnerListProjection(case_id, (), False, False, False)
            rows = session.scalars(
                sa.select(CasePartnerEventRecord)
                .where(
                    CasePartnerEventRecord.tenant_id == actor.tenant_id,
                    CasePartnerEventRecord.case_id == case_id,
                )
                .order_by(
                    CasePartnerEventRecord.created_at.asc(), CasePartnerEventRecord.event_id.asc()
                )
            ).all()
            today = now.date()
            events = tuple(
                PartnerEventProjection(
                    record=row,
                    validity_current="UNKNOWN"
                    if row.valid_until is None
                    else "VALID"
                    if row.valid_until >= today
                    else "EXPIRED",
                )
                for row in rows
            )
            return CasePartnerListProjection(
                case_id=case_id,
                events=events,
                can_request=self._allowed(
                    actor=actor, case_id=case_id, action=Capability.CASE_PARTNER_WRITE, now=now
                ),
                can_receive=self._allowed(
                    actor=actor, case_id=case_id, action=Capability.CASE_PARTNER_WRITE, now=now
                ),
                can_declare_engagement=self._allowed(
                    actor=actor, case_id=case_id, action=Capability.CASE_PARTNER_ENGAGE, now=now
                ),
            )

    def _dispatch(
        self, *, actor: ActorContext, command, now: datetime, case_id: UUID
    ) -> DispatchResult:
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
                case_id=case_id,
                correlation_id=actor.correlation_id,
            ),
        )

    def _allowed(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime) -> bool:
        return self._decision(actor=actor, case_id=case_id, action=action, now=now).allowed

    def _authorize(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime) -> None:
        decision = self._decision(actor=actor, case_id=case_id, action=action, now=now)
        if not decision.allowed:
            raise PermissionError(decision.code)

    def _decision(self, *, actor: ActorContext, case_id: UUID, action: str, now: datetime):
        return self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=action,
                resource=AuthorizationResource(
                    resource_type="CASE_PARTNER",
                    resource_id=case_id,
                    tenant_id=actor.tenant_id,
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                    case_id=case_id,
                ),
                evaluated_at=now,
            ),
        )
