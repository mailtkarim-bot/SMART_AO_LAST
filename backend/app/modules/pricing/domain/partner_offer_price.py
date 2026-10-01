import re
from dataclasses import dataclass
from uuid import UUID

_DECLARED_AMOUNT = re.compile(r"^[0-9]+(?:[,.][0-9]{1,6})?$")
_CURRENCY_CODE = re.compile(r"^[A-Z]{3}$")


@dataclass(frozen=True, slots=True)
class PartnerOfferPriceDeclaration:
    receipt_event_id: UUID
    amount_as_declared: str
    currency_code: str


def build_partner_offer_price(
    *, receipt_event_id: UUID, amount_as_declared: str, currency_code: str
) -> PartnerOfferPriceDeclaration:
    amount = amount_as_declared.strip()
    currency = currency_code.strip()
    if not amount:
        raise ValueError("PARTNER_OFFER_AMOUNT_REQUIRED")
    if not _DECLARED_AMOUNT.fullmatch(amount):
        raise ValueError("PARTNER_OFFER_AMOUNT_FORMAT_INVALID")
    if not _CURRENCY_CODE.fullmatch(currency):
        raise ValueError("PARTNER_OFFER_CURRENCY_INVALID")
    return PartnerOfferPriceDeclaration(
        receipt_event_id=receipt_event_id,
        amount_as_declared=amount,
        currency_code=currency,
    )
