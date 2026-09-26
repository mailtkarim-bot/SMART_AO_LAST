from uuid import uuid4
import pytest
from app.modules.dce.application.human_resumption_commands import RecordHumanResumptionCommand

def test_resumption_command_keeps_export_identity_and_state() -> None:
    command = RecordHumanResumptionCommand(command_id=uuid4(), idempotency_key=uuid4(), act_id=uuid4(), export_id=uuid4(), state="FOLLOW_UP_REQUIRED", rationale="Action humaine requise")
    assert command.export_id is not None
    assert command.state == "FOLLOW_UP_REQUIRED"

def test_resumption_command_requires_rationale() -> None:
    with pytest.raises(ValueError):
        RecordHumanResumptionCommand(command_id=uuid4(), idempotency_key=uuid4(), act_id=uuid4(), export_id=uuid4(), state="BLOCKED", rationale="")
