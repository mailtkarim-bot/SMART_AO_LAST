from uuid import uuid4
import pytest
from app.modules.pricing.application.payment_cycle_commands import RecordPaymentPostReceptionCycleCommand

def test_payment_cycle_command_keeps_business_facts_explicit() -> None:
    command = RecordPaymentPostReceptionCycleCommand(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4(), case_id=uuid4(), source_refs=("ccap://p12",), trigger_event="RECEPTION", status="REVIEW_REQUIRED", cash_assumption="À confirmer", post_reception_cost_note="À qualifier")
    assert command.status == "REVIEW_REQUIRED"
    assert command.cash_assumption == "À confirmer"

def test_payment_cycle_command_requires_source_and_trigger() -> None:
    with pytest.raises(ValueError):
        RecordPaymentPostReceptionCycleCommand(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4(), case_id=uuid4(), source_refs=(), trigger_event="", status="UNKNOWN")
