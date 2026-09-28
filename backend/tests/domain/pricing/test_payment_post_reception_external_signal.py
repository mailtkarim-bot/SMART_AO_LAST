# ruff: noqa: E501, I001
from uuid import uuid4
from app.modules.pricing.domain.payment_post_reception_cycle import PaymentCycleStatus, build_external_payment_signal

def test_external_signal_is_always_source_signal_only():
    cycle = build_external_payment_signal(case_id=uuid4(), source_refs=("external://payment/1",), trigger_event="EXTERNAL_PAYMENT_SIGNAL")
    assert cycle.status is PaymentCycleStatus.SOURCE_SIGNAL_ONLY
    assert cycle.cash_assumption is None
