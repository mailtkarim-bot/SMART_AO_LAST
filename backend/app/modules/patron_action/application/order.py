from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.application.order_commands import (
    RecordCaseDispositionCommand,
    RecordCaseOrderCommand,
    RecordCaseP6ControlCommand,
    RecordCaseP7ResultCommand,
    RecordCaseRetentionCommand,
    RecordCaseRexCommand,
    RequestCaseExportCommand,
)
from app.modules.patron_action.infrastructure.models import (
    CaseDispositionRecord,
    CaseExportRequestRecord,
    CaseOrderRecord,
    CaseOutcomeRecord,
    CaseP6ControlRecord,
    CaseP7ResultRecord,
    CaseRetentionRecord,
    CaseRexRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
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


class CaseOrderService:
    def __init__(
        self,
        *,
        dispatcher,
        session_factory: sessionmaker[Session],
        policy: AuthorizationPolicyPort,
    ) -> None:
        self._dispatcher = dispatcher
        self._session_factory = session_factory
        self._policy = policy

    def record_order(self, *, actor: ActorContext, command: RecordCaseOrderCommand, now: datetime):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def record_p6(self, *, actor: ActorContext, command: RecordCaseP6ControlCommand, now: datetime):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def record_p7(self, *, actor: ActorContext, command: RecordCaseP7ResultCommand, now: datetime):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def record_rex(self, *, actor: ActorContext, command: RecordCaseRexCommand, now: datetime):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def record_disposition(
        self, *, actor: ActorContext, command: RecordCaseDispositionCommand, now: datetime
    ):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def request_export(
        self, *, actor: ActorContext, command: RequestCaseExportCommand, now: datetime
    ):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def record_retention(
        self, *, actor: ActorContext, command: RecordCaseRetentionCommand, now: datetime
    ):
        self._authorize(actor=actor, case_id=command.case_id, now=now)
        return self._dispatch(actor=actor, command=command, now=now)

    def list_rex(self, *, actor: ActorContext, case_id: UUID, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=case_id, now=now)
        with self._session_factory() as session:
            return tuple(
                session.scalars(
                    sa.select(CaseRexRecord)
                    .where(
                        CaseRexRecord.tenant_id == actor.tenant_id,
                        CaseRexRecord.case_id == case_id,
                    )
                    .order_by(CaseRexRecord.created_at, CaseRexRecord.id)
                ).all()
            )

    def _dispatch(self, *, actor: ActorContext, command, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
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
                case_id=command.case_id,
                correlation_id=command.correlation_id,
            ),
        )

    def _authorize(self, *, actor: ActorContext, case_id: UUID, now: datetime) -> None:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PATRON_ACTION_WRITE,
                resource=AuthorizationResource(
                    resource_type="CASE_ORDER",
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


class CaseOrderHandler:
    def execute(
        self,
        *,
        session: Session,
        command: RecordCaseOrderCommand
        | RecordCaseP6ControlCommand
        | RecordCaseP7ResultCommand
        | RecordCaseRexCommand
        | RecordCaseDispositionCommand
        | RequestCaseExportCommand
        | RecordCaseRetentionCommand,
        context: CommandContext,
    ) -> HandlerOutcome:
        if isinstance(command, RecordCaseP6ControlCommand):
            return self._record_p6(session=session, command=command, context=context)
        if isinstance(command, RecordCaseP7ResultCommand):
            return self._record_p7(session=session, command=command, context=context)
        if isinstance(command, RecordCaseRexCommand):
            return self._record_rex(session=session, command=command, context=context)
        if isinstance(command, RecordCaseDispositionCommand):
            return self._record_disposition(session=session, command=command, context=context)
        if isinstance(command, RequestCaseExportCommand):
            return self._request_export(session=session, command=command, context=context)
        if isinstance(command, RecordCaseRetentionCommand):
            return self._record_retention(session=session, command=command, context=context)
        return self._record_order(session=session, command=command, context=context)

    @staticmethod
    def _case_lot(session: Session, *, tenant_id, case_id: UUID, lot_reference: str) -> CaseRecord:
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
            )
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        lots = {
            str(value).strip()
            for value in case.scope_json.get("lot_numbers", [])
            if str(value).strip()
        }
        if lot_reference not in lots:
            raise CommandExecutionError("LOT_NOT_IN_CASE_SCOPE")
        return case

    def _record_order(
        self, *, session: Session, command: RecordCaseOrderCommand, context: CommandContext
    ):
        outcome = session.scalar(
            sa.select(CaseOutcomeRecord)
            .where(
                CaseOutcomeRecord.tenant_id == context.tenant_id,
                CaseOutcomeRecord.id == command.outcome_id,
                CaseOutcomeRecord.case_id == command.case_id,
            )
            .with_for_update()
        )
        if outcome is None:
            raise CommandExecutionError("OUTCOME_NOT_FOUND_OR_FORBIDDEN")
        if outcome.outcome != "WON":
            raise CommandExecutionError("ONLY_WON_OUTCOMES_ORDERABLE")
        self._case_lot(
            session,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            lot_reference=outcome.lot_reference,
        )
        existing = session.scalar(
            sa.select(CaseOrderRecord).where(
                CaseOrderRecord.tenant_id == context.tenant_id,
                CaseOrderRecord.outcome_id == outcome.id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("CASE_ORDER_ALREADY_RECORDED")
        record = CaseOrderRecord(
            id=command.order_id,
            tenant_id=context.tenant_id,
            outcome_id=outcome.id,
            case_id=outcome.case_id,
            lot_reference=outcome.lot_reference,
            decision=command.decision,
            source_locator=outcome.source_locator,
            reservations_json=list(outcome.reservations_json),
            rationale=command.rationale.strip(),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_ORDER_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseOrder",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseOrder",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseOrderRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "outcome_id": str(record.outcome_id),
                        "lot_reference": record.lot_reference,
                        "decision": record.decision,
                    },
                ),
            ),
        )

    def _record_p6(
        self, *, session: Session, command: RecordCaseP6ControlCommand, context: CommandContext
    ):
        order = session.scalar(
            sa.select(CaseOrderRecord)
            .where(
                CaseOrderRecord.tenant_id == context.tenant_id,
                CaseOrderRecord.id == command.order_id,
                CaseOrderRecord.case_id == command.case_id,
            )
            .with_for_update()
        )
        if order is None:
            raise CommandExecutionError("ORDER_NOT_FOUND_OR_FORBIDDEN")
        if order.decision != "ACCEPTED":
            raise CommandExecutionError("ORDER_NOT_ACCEPTED")
        existing = session.scalar(
            sa.select(CaseP6ControlRecord).where(
                CaseP6ControlRecord.tenant_id == context.tenant_id,
                CaseP6ControlRecord.order_id == order.id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("P6_ALREADY_RECORDED")
        record = CaseP6ControlRecord(
            id=command.p6_control_id,
            tenant_id=context.tenant_id,
            order_id=order.id,
            case_id=order.case_id,
            lot_reference=order.lot_reference,
            decision=command.decision,
            reservations_json=list(command.reservations),
            rationale=command.rationale.strip(),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_P6_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseP6Control",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseP6Control",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseP6ControlRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "order_id": str(record.order_id),
                        "lot_reference": record.lot_reference,
                        "decision": record.decision,
                        "reservation_count": len(record.reservations_json),
                    },
                ),
            ),
        )

    def _record_p7(
        self, *, session: Session, command: RecordCaseP7ResultCommand, context: CommandContext
    ):
        p6 = session.scalar(
            sa.select(CaseP6ControlRecord)
            .where(
                CaseP6ControlRecord.tenant_id == context.tenant_id,
                CaseP6ControlRecord.id == command.p6_control_id,
                CaseP6ControlRecord.case_id == command.case_id,
            )
            .with_for_update()
        )
        if p6 is None:
            raise CommandExecutionError("P6_NOT_FOUND_OR_FORBIDDEN")
        if p6.decision != "APPROVED":
            raise CommandExecutionError("P6_NOT_APPROVED")
        if command.result == "COMPLETED" and not command.source_locator:
            raise CommandExecutionError("P7_SOURCE_REQUIRED")
        if command.result in {"UNKNOWN", "INTERRUPTED"} and not command.reason:
            raise CommandExecutionError("P7_REASON_REQUIRED")
        existing = session.scalar(
            sa.select(CaseP7ResultRecord).where(
                CaseP7ResultRecord.tenant_id == context.tenant_id,
                CaseP7ResultRecord.p6_control_id == p6.id,
            )
        )
        if existing is not None:
            raise CommandExecutionError("P7_ALREADY_RECORDED")
        record = CaseP7ResultRecord(
            id=command.p7_result_id,
            tenant_id=context.tenant_id,
            p6_control_id=p6.id,
            case_id=p6.case_id,
            lot_reference=p6.lot_reference,
            result=command.result,
            source_locator=command.source_locator,
            reason=command.reason,
            reservations_json=list(command.reservations),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_P7_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseP7Result",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseP7Result",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseP7ResultRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "p6_control_id": str(record.p6_control_id),
                        "lot_reference": record.lot_reference,
                        "result": record.result,
                    },
                ),
            ),
        )

    def _record_rex(
        self, *, session: Session, command: RecordCaseRexCommand, context: CommandContext
    ):
        p7 = session.scalar(
            sa.select(CaseP7ResultRecord)
            .where(
                CaseP7ResultRecord.tenant_id == context.tenant_id,
                CaseP7ResultRecord.id == command.p7_result_id,
                CaseP7ResultRecord.case_id == command.case_id,
            )
            .with_for_update()
        )
        if p7 is None:
            raise CommandExecutionError("P7_NOT_FOUND_OR_FORBIDDEN")
        if command.scope == "ENTERPRISE_PATTERN" and (
            p7.result != "COMPLETED"
            or command.validation != "APPROVED"
            or not command.source_locator
        ):
            raise CommandExecutionError("ENTERPRISE_REX_REQUIRES_SOURCE_AND_APPROVAL")
        record = CaseRexRecord(
            id=command.rex_id,
            tenant_id=context.tenant_id,
            p7_result_id=p7.id,
            case_id=p7.case_id,
            lot_reference=p7.lot_reference,
            motif=command.motif,
            scope=command.scope,
            validation=command.validation,
            observation=command.observation.strip(),
            consequence=command.consequence.strip(),
            follow_up=command.follow_up.strip(),
            source_locator=command.source_locator,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_REX_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseRex",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseRex",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseRexRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "p7_result_id": str(record.p7_result_id),
                        "lot_reference": record.lot_reference,
                        "motif": record.motif,
                        "scope": record.scope,
                        "validation": record.validation,
                    },
                ),
            ),
        )

    def _record_disposition(
        self, *, session: Session, command: RecordCaseDispositionCommand, context: CommandContext
    ):
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == context.tenant_id, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        latest = session.scalar(
            sa.select(CaseDispositionRecord)
            .where(
                CaseDispositionRecord.tenant_id == context.tenant_id,
                CaseDispositionRecord.case_id == command.case_id,
            )
            .order_by(CaseDispositionRecord.created_at.desc(), CaseDispositionRecord.id.desc())
            .limit(1)
        )
        if command.state == "RESUMED" and (latest is None or latest.state != "SUSPENDED"):
            raise CommandExecutionError("CASE_NOT_SUSPENDED")
        if command.state == "CLOSED":
            if latest is not None and latest.state == "SUSPENDED":
                code = (
                    "CASE_LITIGATION_OPEN"
                    if latest.reason_code == "OPEN_LITIGATION"
                    else "CASE_SUSPENDED"
                )
                raise CommandExecutionError(code)
            if command.p7_result_id is None:
                raise CommandExecutionError("P7_RESULT_REQUIRED_FOR_CLOSURE")
            p7 = session.scalar(
                sa.select(CaseP7ResultRecord).where(
                    CaseP7ResultRecord.tenant_id == context.tenant_id,
                    CaseP7ResultRecord.id == command.p7_result_id,
                    CaseP7ResultRecord.case_id == command.case_id,
                )
            )
            if p7 is None:
                raise CommandExecutionError("P7_NOT_FOUND_OR_FORBIDDEN")
            if p7.result != "COMPLETED":
                raise CommandExecutionError("P7_NOT_COMPLETED")
            unresolved = session.scalar(
                sa.select(CaseP7ResultRecord.id).where(
                    CaseP7ResultRecord.tenant_id == context.tenant_id,
                    CaseP7ResultRecord.case_id == command.case_id,
                    CaseP7ResultRecord.result.in_(("UNKNOWN", "INTERRUPTED")),
                )
            )
            if unresolved is not None:
                raise CommandExecutionError("CASE_P7_UNRESOLVED")
        record = CaseDispositionRecord(
            id=command.disposition_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            p7_result_id=command.p7_result_id,
            state=command.state,
            reason_code=command.reason_code,
            rationale=command.rationale.strip(),
            source_locator=command.source_locator,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_DISPOSITION_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseDisposition",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseDisposition",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseDispositionRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "p7_result_id": str(record.p7_result_id) if record.p7_result_id else None,
                        "state": record.state,
                        "reason_code": record.reason_code,
                    },
                ),
            ),
        )

    @staticmethod
    def _case_exists(session: Session, *, tenant_id, case_id: UUID) -> None:
        case = session.scalar(
            sa.select(CaseRecord.id).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
            )
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")

    def _request_export(
        self, *, session: Session, command: RequestCaseExportCommand, context: CommandContext
    ):
        self._case_exists(session, tenant_id=context.tenant_id, case_id=command.case_id)
        record = CaseExportRequestRecord(
            id=command.export_request_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            artifact_kind=command.artifact_kind,
            recipient_label=command.recipient_label,
            purpose=command.purpose.strip(),
            source_locator=command.source_locator,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_EXPORT_REQUESTED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseExportRequest",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseExportRequest",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseExportRequested",
                    payload={
                        "case_id": str(record.case_id),
                        "artifact_kind": record.artifact_kind,
                        "external_receipt": "NOT_PERFORMED",
                    },
                ),
            ),
        )

    def _record_retention(
        self, *, session: Session, command: RecordCaseRetentionCommand, context: CommandContext
    ):
        self._case_exists(session, tenant_id=context.tenant_id, case_id=command.case_id)
        record = CaseRetentionRecord(
            id=command.retention_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            evidence_locator=command.evidence_locator.strip(),
            retention_basis=command.retention_basis,
            retain_until=command.retain_until,
            rationale=command.rationale.strip(),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_RETENTION_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseRetention",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseRetention",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseRetentionRecorded",
                    payload={
                        "case_id": str(record.case_id),
                        "retention_basis": record.retention_basis,
                        "retain_until": record.retain_until.isoformat(),
                    },
                ),
            ),
        )


def case_order_handlers():
    handler = CaseOrderHandler()
    return {
        RecordCaseOrderCommand.command_type: handler,
        RecordCaseP6ControlCommand.command_type: handler,
        RecordCaseP7ResultCommand.command_type: handler,
        RecordCaseRexCommand.command_type: handler,
        RecordCaseDispositionCommand.command_type: handler,
        RequestCaseExportCommand.command_type: handler,
        RecordCaseRetentionCommand.command_type: handler,
    }
