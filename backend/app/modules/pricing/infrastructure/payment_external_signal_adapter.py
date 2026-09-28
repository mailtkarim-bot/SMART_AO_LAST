# ruff: noqa: E501, I001
from uuid import UUID
from app.modules.pricing.domain.payment_post_reception_cycle import PaymentPostReceptionCycle, build_external_payment_signal

def adapt_external_payment_signal(*, case_id: UUID, payload: dict[str, object]) -> PaymentPostReceptionCycle:
    source_ref = payload.get("source_ref")
    trigger_event = payload.get("trigger_event")
    if not isinstance(source_ref, str) or not source_ref.strip():
        raise ValueError("PAYMENT_EXTERNAL_SOURCE_REQUIRED")
    if not isinstance(trigger_event, str) or not trigger_event.strip():
        raise ValueError("PAYMENT_EXTERNAL_TRIGGER_REQUIRED")
    cost_note = payload.get("post_reception_cost_note")
    if cost_note is not None and not isinstance(cost_note, str):
        raise ValueError("PAYMENT_EXTERNAL_COST_NOTE_INVALID")
    return build_external_payment_signal(case_id=case_id, source_refs=(source_ref,), trigger_event=trigger_event, post_reception_cost_note=cost_note)
