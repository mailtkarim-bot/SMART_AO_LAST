from typing import Literal
from uuid import UUID

from app.platform.events.command_contracts import ApplicationCommand


class TransitionContractQueryExportCommand(ApplicationCommand):
    command_type = "TransitionContractQueryExport"
    transition_id: UUID
    export_id: UUID
    from_status: Literal["REQUESTED", "READY", "UNKNOWN", "REFUSED"]
    to_status: Literal["REQUESTED", "READY", "UNKNOWN", "REFUSED"]
    local_proof_ref: str | None = None
    local_proof_sha256: str | None = None
