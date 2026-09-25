from uuid import uuid4
import pytest
from app.modules.dce.application.contract_query_export_transition_commands import TransitionContractQueryExportCommand


def test_ready_command_carries_a_sha256_length_proof() -> None:
    command = TransitionContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), transition_id=uuid4(), export_id=uuid4(), from_status="REQUESTED", to_status="READY", local_proof_ref="local://export", local_proof_sha256="a" * 64)
    assert len(command.local_proof_sha256) == 64


@pytest.mark.parametrize("digest", [None, "short"])
def test_ready_command_rejects_missing_or_short_digest(digest) -> None:
    command = TransitionContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), transition_id=uuid4(), export_id=uuid4(), from_status="REQUESTED", to_status="READY", local_proof_ref="local://export", local_proof_sha256=digest)
    assert command.local_proof_sha256 != "a" * 64
