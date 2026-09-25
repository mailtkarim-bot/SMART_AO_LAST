from uuid import uuid4
import pytest
from app.modules.dce.application.contract_query_receipt_commands import RecordContractQueryReceiptCommand


@pytest.mark.parametrize("limit", [0, 101])
def test_query_receipt_limit_is_closed(limit: int) -> None:
    with pytest.raises(ValueError):
        RecordContractQueryReceiptCommand(command_id=uuid4(), idempotency_key=uuid4(), receipt_id=uuid4(), case_id=uuid4(), limit_value=limit, offset_value=0)
