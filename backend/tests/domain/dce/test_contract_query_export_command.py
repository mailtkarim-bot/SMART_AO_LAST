from uuid import uuid4
import pytest
from app.modules.dce.application.contract_query_export_commands import RequestContractQueryExportCommand


def test_query_export_command_starts_requested_by_handler_contract() -> None:
    command = RequestContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), export_id=uuid4(), case_id=uuid4())
    assert command.filters == {}


def test_query_export_command_requires_identity() -> None:
    with pytest.raises(ValueError):
        RequestContractQueryExportCommand(command_id=uuid4(), idempotency_key=uuid4(), export_id=None, case_id=uuid4())
