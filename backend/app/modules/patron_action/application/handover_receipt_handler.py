"""Record an assigned Responsable's receipt of one exact operational view."""

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.handover_receipt import (
    CaseHandoverReceiptRecord,
)
from app.modules.patron_action.infrastructure.operational_handover import current_handover_view
from app.platform.events.dispatcher import CommandExecutionError, HandlerOutcome, PendingDomainEvent


class AcknowledgeHandoverHandler:
    def __init__(self, storage=None):
        self._storage = storage

    def execute(self, *, session, command, context):
        if context.actor_kind != "COLLABORATEUR" or context.membership_id is None:
            raise CommandExecutionError("RESPONSABLE_REQUIRED")
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == context.tenant_id, CaseRecord.id == command.case_id)
            .with_for_update(nowait=True)
        )
        snapshot = session.scalar(
            sa.select(CaseHandoverSnapshotRecord)
            .where(
                CaseHandoverSnapshotRecord.tenant_id == context.tenant_id,
                CaseHandoverSnapshotRecord.case_id == command.case_id,
                CaseHandoverSnapshotRecord.id == command.snapshot_id,
            )
            .with_for_update(nowait=True)
        )
        if case is None or snapshot is None or case.lifecycle != "ACTIVE":
            raise CommandExecutionError("HANDOVER_SOURCE_NOT_FOUND_OR_FORBIDDEN")
        from app.modules.patron_action.infrastructure.operational_handover import (
            lock_handover_sources,
        )

        lock_handover_sources(session, snapshot)
        public, state, reasons, fingerprint = current_handover_view(
            session, snapshot, storage=self._storage
        )
        if (
            state == "HISTORICAL"
            or snapshot.revision != command.expected_snapshot_revision
            or fingerprint != command.expected_view_sha256
        ):
            raise CommandExecutionError("HANDOVER_VIEW_CONFLICT")
        if command.receipt_kind == "RECEIVED" and (
            state != "CURRENT" or public["operational_review"]["missing"]
        ):
            raise CommandExecutionError("HANDOVER_GAPS_REQUIRE_EXPLICIT_RECEIPT")
        session.add(
            CaseHandoverReceiptRecord(
                id=command.receipt_id,
                tenant_id=context.tenant_id,
                case_id=case.id,
                snapshot_id=snapshot.id,
                snapshot_revision=snapshot.revision,
                view_sha256=fingerprint,
                receipt_kind=command.receipt_kind,
                note=command.note,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=command.correlation_id,
            )
        )
        payload = {
            "receipt_id": str(command.receipt_id),
            "snapshot_id": str(snapshot.id),
            "snapshot_revision": snapshot.revision,
            "view_sha256": fingerprint,
            "receipt_kind": command.receipt_kind,
            "p7_is_order_service": False,
        }
        return HandlerOutcome(
            result_code="CASE_HANDOVER_RECEIPT_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CaseHandoverReceipt",
                    "aggregate_id": str(command.receipt_id),
                    "aggregate_revision": 1,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CaseHandoverReceipt",
                    aggregate_id=command.receipt_id,
                    aggregate_revision=1,
                    event_type="CaseHandoverReceiptRecorded",
                    payload=payload,
                ),
            ),
        )
