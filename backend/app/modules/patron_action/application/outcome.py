from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.application.transmission_commands import TransmitWonOutcomeCommand
from app.modules.patron_action.infrastructure.models.outcome import CaseOutcomeRecord
from app.modules.patron_action.infrastructure.models.transmission import (
    CaseOutcomeTransmissionRecord,
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


class CaseOutcomeService:
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

    def execute(self, *, actor: ActorContext, command: RecordCaseOutcomeCommand, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=command.case_id, now=now)
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

    def list_for_case(
        self, *, actor: ActorContext, case_id: UUID, now: datetime
    ) -> tuple[CaseOutcomeRecord, ...]:
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=case_id, now=now)
        with self._session_factory() as session:
            return tuple(
                session.scalars(
                    sa.select(CaseOutcomeRecord)
                    .where(
                        CaseOutcomeRecord.tenant_id == actor.tenant_id,
                        CaseOutcomeRecord.case_id == case_id,
                    )
                    .order_by(CaseOutcomeRecord.created_at, CaseOutcomeRecord.id)
                ).all()
            )

    def transmit(self, *, actor: ActorContext, command: TransmitWonOutcomeCommand, now: datetime):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        self._authorize(actor=actor, case_id=command.case_id, now=now)
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
        decision = self._policy.authorize(
            context=actor,
            request=AuthorizationRequest(
                action=Capability.PATRON_ACTION_WRITE,
                resource=AuthorizationResource(
                    resource_type="CASE_OUTCOME",
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


class CaseOutcomeHandler:
    def execute(
        self, *, session: Session, command: RecordCaseOutcomeCommand, context: CommandContext
    ) -> HandlerOutcome:
        if isinstance(command, TransmitWonOutcomeCommand):
            outcome = session.scalar(
                sa.select(CaseOutcomeRecord).where(
                    CaseOutcomeRecord.tenant_id == context.tenant_id,
                    CaseOutcomeRecord.id == command.outcome_id,
                    CaseOutcomeRecord.case_id == command.case_id,
                )
            )
            if outcome is None:
                raise CommandExecutionError("OUTCOME_NOT_FOUND_OR_FORBIDDEN")
            if outcome.outcome != "WON":
                raise CommandExecutionError("ONLY_WON_OUTCOMES_TRANSMITTABLE")
            existing = session.scalar(
                sa.select(CaseOutcomeTransmissionRecord).where(
                    CaseOutcomeTransmissionRecord.tenant_id == context.tenant_id,
                    CaseOutcomeTransmissionRecord.outcome_id == outcome.id,
                )
            )
            if existing is not None:
                return HandlerOutcome(
                    result_code="CASE_OUTCOME_TRANSMITTED",
                    aggregate_refs=(
                        {
                            "aggregate_type": "CaseOutcomeTransmission",
                            "aggregate_id": str(existing.id),
                            "aggregate_revision": 1,
                        },
                    ),
                )
            transmission = CaseOutcomeTransmissionRecord(
                id=command.transmission_id,
                tenant_id=context.tenant_id,
                outcome_id=outcome.id,
                case_id=outcome.case_id,
                lot_reference=outcome.lot_reference,
                recipient=command.recipient,
                reservations_json=outcome.reservations_json,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
            session.add(transmission)
            return HandlerOutcome(
                result_code="CASE_OUTCOME_TRANSMITTED",
                aggregate_refs=(
                    {
                        "aggregate_type": "CaseOutcomeTransmission",
                        "aggregate_id": str(transmission.id),
                        "aggregate_revision": 1,
                    },
                ),
                events=(
                    PendingDomainEvent(
                        aggregate_type="CaseOutcomeTransmission",
                        aggregate_id=transmission.id,
                        aggregate_revision=1,
                        event_type="CaseOutcomeTransmitted",
                        payload={
                            "outcome_id": str(outcome.id),
                            "lot_reference": outcome.lot_reference,
                            "recipient": command.recipient,
                        },
                    ),
                ),
            )
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == context.tenant_id, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        lots = {str(x).strip() for x in case.scope_json.get("lot_numbers", []) if str(x).strip()}
        if command.lot_reference not in lots:
            raise CommandExecutionError("LOT_NOT_IN_CASE_SCOPE")
        if command.outcome == "WON" and not command.source_locator:
            raise CommandExecutionError("WON_SOURCE_REQUIRED")
        if command.outcome == "UNKNOWN" and not command.unknown_reason:
            raise CommandExecutionError("UNKNOWN_REASON_REQUIRED")
        record = CaseOutcomeRecord(
            id=command.outcome_id,
            tenant_id=context.tenant_id,
            case_id=case.id,
            lot_reference=command.lot_reference,
            outcome=command.outcome,
            source_locator=command.source_locator,
            reservations_json=command.reservations,
            unknown_reason=command.unknown_reason,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return HandlerOutcome(
            result_code="CASE_OUTCOME_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseOutcome",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseOutcome",
                    aggregate_id=record.id,
                    aggregate_revision=1,
                    event_type="CaseOutcomeRecorded",
                    payload={
                        "case_id": str(case.id),
                        "lot_reference": record.lot_reference,
                        "outcome": record.outcome,
                    },
                ),
            ),
        )


def case_outcome_handlers():
    handler = CaseOutcomeHandler()
    return {
        RecordCaseOutcomeCommand.command_type: handler,
        TransmitWonOutcomeCommand.command_type: handler,
    }
