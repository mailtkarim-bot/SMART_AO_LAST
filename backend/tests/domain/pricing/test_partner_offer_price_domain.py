from uuid import uuid4

import pytest
from app.modules.pricing.domain.partner_offer_price import build_partner_offer_price


def test_partner_offer_price_keeps_the_exact_declared_total_and_source_receipt():
    receipt_event_id = uuid4()

    price = build_partner_offer_price(
        receipt_event_id=receipt_event_id,
        amount_as_declared="1234,50",
        currency_code="MAD",
    )

    assert price.receipt_event_id == receipt_event_id
    assert price.amount_as_declared == "1234,50"
    assert price.currency_code == "MAD"


def test_explicit_zero_is_distinct_from_an_unknown_offer_price():
    price = build_partner_offer_price(
        receipt_event_id=uuid4(),
        amount_as_declared="0",
        currency_code="EUR",
    )
    assert price.amount_as_declared == "0"


@pytest.mark.parametrize(
    ("amount", "currency", "error"),
    [
        ("", "EUR", "PARTNER_OFFER_AMOUNT_REQUIRED"),
        ("1 234,50", "EUR", "PARTNER_OFFER_AMOUNT_FORMAT_INVALID"),
        ("-10,00", "EUR", "PARTNER_OFFER_AMOUNT_FORMAT_INVALID"),
        ("123,4567890", "EUR", "PARTNER_OFFER_AMOUNT_FORMAT_INVALID"),
        ("123,00", "eu", "PARTNER_OFFER_CURRENCY_INVALID"),
    ],
)
def test_partner_offer_price_rejects_ambiguous_amount_or_currency(amount, currency, error):
    with pytest.raises(ValueError, match=error):
        build_partner_offer_price(
            receipt_event_id=uuid4(),
            amount_as_declared=amount,
            currency_code=currency,
        )
