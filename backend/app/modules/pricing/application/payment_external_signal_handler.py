# ruff: noqa: E501, I001
from uuid import UUID, uuid4
from app.modules.pricing.infrastructure.payment_external_signal_adapter import adapt_external_payment_signal
from app.modules.pricing.application.payment_cycle_commands import RecordPaymentPostReceptionCycleCommand

def build_external_payment_signal_command(*, case_id: UUID, payload: dict[str, object], command_id: UUID | None = None, idempotency_key: UUID | None = None, cycle_id: UUID | None = None) -> RecordPaymentPostReceptionCycleCommand:
    cycle = adapt_external_payment_signal(case_id=case_id, payload=payload)
    return RecordPaymentPostReceptionCycleCommand(command_id=command_id or uuid4(), idempotency_key=idempotency_key or uuid4(), cycle_id=cycle_id or uuid4(), case_id=cycle.case_id, source_refs=cycle.source_refs, trigger_event=cycle.trigger_event, status=cycle.status.value, cash_assumption=cycle.cash_assumption, post_reception_cost_note=cycle.post_reception_cost_note)
