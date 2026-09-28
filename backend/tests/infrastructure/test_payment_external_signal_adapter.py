# ruff: noqa: E501, I001
from uuid import uuid4
import pytest
from app.modules.pricing.infrastructure.payment_external_signal_adapter import adapt_external_payment_signal
from app.modules.pricing.domain.payment_post_reception_cycle import PaymentCycleStatus

def test_adapter_forces_prudent_external_signal():
    cycle = adapt_external_payment_signal(case_id=uuid4(), payload={"source_ref": "external://payment/2", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"})
    assert cycle.status is PaymentCycleStatus.SOURCE_SIGNAL_ONLY
    assert cycle.cash_assumption is None

def test_adapter_rejects_missing_source():
    with pytest.raises(ValueError, match="PAYMENT_EXTERNAL_SOURCE_REQUIRED"):
        adapt_external_payment_signal(case_id=uuid4(), payload={"trigger_event": "EXTERNAL_PAYMENT_SIGNAL"})
