from uuid import UUID

from app.platform.events.command_contracts import ApplicationCommand


class RecordCaseHandoverSnapshotCommand(ApplicationCommand):
    command_type = "RecordCaseHandoverSnapshot"

    snapshot_id: UUID
    case_id: UUID
    outcome_id: UUID
    submission_package_id: UUID
