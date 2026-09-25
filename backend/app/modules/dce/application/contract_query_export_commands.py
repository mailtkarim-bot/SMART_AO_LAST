from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RequestContractQueryExportCommand(ApplicationCommand):
    command_type = "RequestContractQueryExport"
    export_id: UUID
    case_id: UUID
    filters: dict[str, object] = Field(default_factory=dict)
