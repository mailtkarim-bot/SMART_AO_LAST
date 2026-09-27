from uuid import uuid4
import pytest
from app.modules.pricing.domain.payment_post_reception_cycle import PaymentCycleStatus, PaymentPostReceptionCycle

def test_payment_cycle_requires_source_trigger_and_keeps_cash_prudent() -> None:
    cycle = PaymentPostReceptionCycle(uuid4(), ("ccap://p12",), "RECEPTION", PaymentCycleStatus.REVIEW_REQUIRED, "Hypothèse à confirmer", "Coût à qualifier")
    cycle.validate()

@pytest.mark.parametrize("source_refs, trigger, error", [((), "RECEPTION", "PAYMENT_SOURCE_REQUIRED"), (("source",), "", "PAYMENT_TRIGGER_REQUIRED")])
def test_payment_cycle_rejects_incomplete_contract(source_refs, trigger, error) -> None:
    with pytest.raises(ValueError, match=error):
        PaymentPostReceptionCycle(uuid4(), source_refs, trigger, PaymentCycleStatus.UNKNOWN, None, None).validate()
