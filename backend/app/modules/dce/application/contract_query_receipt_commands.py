from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordContractQueryReceiptCommand(ApplicationCommand):
    command_type = "RecordContractQueryReceipt"
    receipt_id: UUID
    case_id: UUID
    filters: dict[str, object] = Field(default_factory=dict)
    order_key: Literal["revision_created_at"] = "revision_created_at"
    limit_value: int = Field(ge=1, le=100)
    offset_value: int = Field(ge=0)
