from uuid import uuid4
import pytest
from app.modules.dce.application.contract_query_export_transition_commands import TransitionContractQueryExportCommand


def test_ready_transition_keeps_local_proof_reference_explicit() -> None:
    command = TransitionContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), transition_id=uuid4(), export_id=uuid4(), from_status="REQUESTED", to_status="READY", local_proof_ref="local://export/sha256")
    assert command.to_status == "READY"
    assert command.local_proof_ref is not None


@pytest.mark.parametrize("status", ["REQUESTED", "READY", "UNKNOWN", "REFUSED"])
def test_transition_statuses_are_closed(status: str) -> None:
    command = TransitionContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), transition_id=uuid4(), export_id=uuid4(), from_status="REQUESTED", to_status=status)
    assert command.to_status == status
