"""Transactional handler for sourced post-award contract changes."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.pricing.application.case_contract_change_commands import (
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEventCommand,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEventRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


class CaseContractChangeHandler(CommandHandler):
    def execute(
        self,
        *,
        session: Session,
        command,
        context: CommandContext,
    ) -> HandlerOutcome:
        case_id = command.case_id
        tenant_id = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        if isinstance(command, RecordCaseContractChangeEventCommand):
            return self._record_event(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeApplicabilityCommand):
            return self._record_applicability(session=session, command=command, context=context)
        if isinstance(command, RecordCaseContractChangeActionCommand):
            return self._record_action(session=session, command=command, context=context)
        raise CommandExecutionError("UNSUPPORTED_CASE_CONTRACT_CHANGE_COMMAND")

    def _record_event(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        snapshot = session.scalar(
            sa.select(CaseHandoverSnapshotRecord).where(
                CaseHandoverSnapshotRecord.tenant_id == context.tenant_id,
                CaseHandoverSnapshotRecord.case_id == command.case_id,
                CaseHandoverSnapshotRecord.id == command.handover_snapshot_id,
            )
        )
        if snapshot is None:
            raise CommandExecutionError("HANDOVER_NOT_FOUND_OR_FORBIDDEN")
        if command.contract_instrument_version_id is not None:
            instrument = session.scalar(
                sa.select(ContractInstrumentVersionRecord.id).where(
                    ContractInstrumentVersionRecord.tenant_id == context.tenant_id,
                    ContractInstrumentVersionRecord.case_id == command.case_id,
                    ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
                )
            )
            if instrument is None:
                raise CommandExecutionError("CONTRACT_INSTRUMENT_NOT_FOUND_OR_FORBIDDEN")
        record = CaseContractChangeEventRecord(
            id=command.event_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            handover_snapshot_id=snapshot.id,
            contract_instrument_version_id=command.contract_instrument_version_id,
            change_kind=command.change_kind,
            issuer=command.issuer,
            summary=command.summary.strip(),
            scope_note=command.scope_note.strip(),
            source_refs_json=list(command.source_refs),
            evidence_refs_json=list(command.evidence_refs),
            declared_received_at=command.declared_received_at,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=1,
            event_type="CaseContractChangeEventRecorded",
            result_code="CASE_CONTRACT_CHANGE_EVENT_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "handover_snapshot_id": str(snapshot.id),
                "event_id": str(record.id),
                "change_kind": record.change_kind,
                "applicability": "UNKNOWN",
            },
        )

    def _record_applicability(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        if event is None or event.handover_snapshot_id != command.handover_snapshot_id:
            raise CommandExecutionError("CONTRACT_CHANGE_EVENT_NOT_FOUND_OR_FORBIDDEN")
        if (
            event.contract_instrument_version_id is not None
            and event.contract_instrument_version_id != command.contract_instrument_version_id
        ):
            raise CommandExecutionError("CONTRACT_VERSION_MISMATCH")
        instrument = session.scalar(
            sa.select(ContractInstrumentVersionRecord.id).where(
                ContractInstrumentVersionRecord.tenant_id == context.tenant_id,
                ContractInstrumentVersionRecord.case_id == command.case_id,
                ContractInstrumentVersionRecord.id == command.contract_instrument_version_id,
            )
        )
        if instrument is None:
            raise CommandExecutionError("CONTRACT_INSTRUMENT_NOT_FOUND_OR_FORBIDDEN")
        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeApplicabilityRecord.revision), 0)
            ).where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == event.id,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_APPLICABILITY_VERSION_CONFLICT")
        revision = current_revision + 1
        record = CaseContractChangeApplicabilityRecord(
            id=command.review_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            handover_snapshot_id=event.handover_snapshot_id,
            contract_instrument_version_id=command.contract_instrument_version_id,
            revision=revision,
            decision=command.decision,
            delta_state=command.delta_state,
            delta_note=command.delta_note.strip() if command.delta_note else None,
            rationale=command.rationale.strip(),
            evidence_refs_json=list(command.evidence_refs),
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=revision,
            event_type="CaseContractChangeApplicabilityRecorded",
            result_code="CASE_CONTRACT_CHANGE_APPLICABILITY_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "handover_snapshot_id": str(event.handover_snapshot_id),
                "contract_instrument_version_id": str(command.contract_instrument_version_id),
                "decision": command.decision,
            },
        )

    def _record_action(
        self, *, session: Session, command, context: CommandContext
    ) -> HandlerOutcome:
        event = session.scalar(
            sa.select(CaseContractChangeEventRecord).where(
                CaseContractChangeEventRecord.tenant_id == context.tenant_id,
                CaseContractChangeEventRecord.case_id == command.case_id,
                CaseContractChangeEventRecord.id == command.event_id,
            )
        )
        review = session.scalar(
            sa.select(CaseContractChangeApplicabilityRecord).where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == command.event_id,
                CaseContractChangeApplicabilityRecord.id == command.applicability_review_id,
            )
        )
        if event is None or review is None or review.decision != "APPLICABLE_TO_HANDOVER":
            raise CommandExecutionError("CONTRACT_CHANGE_NOT_APPLICABLE_TO_HANDOVER")
        latest_review = session.scalar(
            sa.select(CaseContractChangeApplicabilityRecord)
            .where(
                CaseContractChangeApplicabilityRecord.tenant_id == context.tenant_id,
                CaseContractChangeApplicabilityRecord.case_id == command.case_id,
                CaseContractChangeApplicabilityRecord.event_id == command.event_id,
            )
            .order_by(CaseContractChangeApplicabilityRecord.revision.desc())
            .limit(1)
        )
        if latest_review is None or latest_review.id != review.id:
            raise CommandExecutionError("CONTRACT_CHANGE_APPLICABILITY_STALE")
        latest_revision = session.scalar(
            sa.select(
                sa.func.coalesce(sa.func.max(CaseContractChangeActionRecord.revision), 0)
            ).where(
                CaseContractChangeActionRecord.tenant_id == context.tenant_id,
                CaseContractChangeActionRecord.case_id == command.case_id,
                CaseContractChangeActionRecord.event_id == command.event_id,
            )
        )
        current_revision = int(latest_revision or 0)
        if command.expected_revision != current_revision:
            raise CommandExecutionError("CONTRACT_CHANGE_ACTION_VERSION_CONFLICT")
        revision = current_revision + 1
        record = CaseContractChangeActionRecord(
            id=command.action_id,
            tenant_id=context.tenant_id,
            case_id=command.case_id,
            event_id=event.id,
            applicability_id=review.id,
            revision=revision,
            action_summary=command.action_summary.strip(),
            evidence_refs_json=list(command.evidence_refs),
            due_at=command.due_at,
            due_date_absence_reason=command.due_date_absence_reason,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
            correlation_id=command.correlation_id,
        )
        session.add(record)
        return self._outcome(
            record=record,
            revision=revision,
            event_type="CaseContractChangeActionRecorded",
            result_code="CASE_CONTRACT_CHANGE_ACTION_RECORDED",
            payload={
                "case_id": str(command.case_id),
                "event_id": str(event.id),
                "applicability_id": str(review.id),
                "action_id": str(record.id),
                "state": "RECORDED",
            },
        )

    @staticmethod
    def _outcome(*, record, revision: int, event_type: str, result_code: str, payload: dict):
        return HandlerOutcome(
            result_code=result_code,
            aggregate_refs=(
                {
                    "aggregate_type": event_type,
                    "aggregate_id": str(record.id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type=event_type,
                    aggregate_id=record.id,
                    aggregate_revision=revision,
                    event_type=event_type,
                    payload=payload,
                ),
            ),
        )
