from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class DeclarePartnerOfferPriceCommand(ApplicationCommand):
    command_type = "DeclarePartnerOfferPrice"

    declaration_id: UUID
    case_id: UUID
    receipt_event_id: UUID
    expected_revision: int = Field(ge=0)
    amount_as_declared: str = Field(min_length=1, max_length=80)
    currency_code: str = Field(min_length=3, max_length=3)
