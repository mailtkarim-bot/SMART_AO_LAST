# ruff: noqa: E501, I001
from uuid import uuid4
from app.modules.pricing.application.payment_external_signal_handler import build_external_payment_signal_command

def test_external_signal_service_builds_dispatchable_prudent_command():
    command_id, idem, cycle_id, case_id = uuid4(), uuid4(), uuid4(), uuid4()
    command = build_external_payment_signal_command(case_id=case_id, payload={"source_ref": "external://payment/3", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}, command_id=command_id, idempotency_key=idem, cycle_id=cycle_id)
    assert command.command_id == command_id
    assert command.idempotency_key == idem
    assert command.cycle_id == cycle_id
    assert command.status == "SOURCE_SIGNAL_ONLY"
