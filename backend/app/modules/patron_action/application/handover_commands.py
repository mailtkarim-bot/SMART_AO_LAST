from uuid import UUID

from pydantic import model_serializer

from app.modules.patron_action.public.handover_contracts import (
    HandoverOperationalReview,
    HandoverReceiptFields,
)
from app.platform.events.command_contracts import ApplicationCommand


class RecordCaseHandoverSnapshotCommand(ApplicationCommand):
    command_type = "RecordCaseHandoverSnapshot"

    snapshot_id: UUID
    case_id: UUID
    outcome_id: UUID
    submission_package_id: UUID

    operational_review: HandoverOperationalReview | None = None

    @model_serializer(mode="wrap")
    def legacy_payload(self, handler):
        payload = handler(self)
        if self.operational_review is None:
            payload.pop("operational_review", None)
        return payload


class AcknowledgeHandoverCommand(ApplicationCommand, HandoverReceiptFields):
    command_type = "AcknowledgeHandover"
    case_id: UUID
    snapshot_id: UUID
