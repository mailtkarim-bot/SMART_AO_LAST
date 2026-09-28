# ruff: noqa: E501, E702, I001
from datetime import UTC, datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case
from app.modules.pricing.application.payment_external_signal_handler import build_external_payment_signal_command
from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
from app.modules.pricing.application.payment_cycle_review_commands import RecordPaymentCycleReviewCommand
from app.modules.pricing.application.payment_cycle_review_handler import payment_cycle_review_handlers
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.persistence.models import TenantRecord

def test_payment_signal_review_projection_replay_is_single_chain(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"pay-e2e-{tenant_id.hex[:10]}", lifecycle="ACTIVE"))
        session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="e")); session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime(2026, 9, 28, tzinfo=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    cycle_id = uuid4()
    signal = build_external_payment_signal_command(case_id=case_id, payload={"source_ref": "external://payment-signal/1", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}, command_id=uuid4(), idempotency_key=uuid4(), cycle_id=cycle_id)
    cycle_dispatcher = CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers())
    first = cycle_dispatcher.dispatch(command=signal, context=context)
    replay = cycle_dispatcher.dispatch(command=signal, context=context)
    review = RecordPaymentCycleReviewCommand(command_id=uuid4(), idempotency_key=uuid4(), review_id=uuid4(), cycle_id=cycle_id, decision="REVIEW_REQUIRED", rationale="Signal externe à confirmer")
    review_dispatcher = CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_review_handlers())
    review_result = review_dispatcher.dispatch(command=review, context=context)
    assert first.result_code == "PAYMENT_CYCLE_RECORDED"
    assert replay.replayed is True
    assert review_result.result_code == "PAYMENT_CYCLE_REVIEW_RECORDED"
    with Session(database_engine) as session:
        assert session.scalar(sa.text("select count(*) from payment_post_reception_cycles where id = :id"), {"id": cycle_id}) == 1
        assert session.scalar(sa.text("select status from payment_post_reception_cycles where id = :id"), {"id": cycle_id}) == "SOURCE_SIGNAL_ONLY"
        assert session.scalar(sa.text("select count(*) from payment_cycle_reviews where cycle_id = :id"), {"id": cycle_id}) == 1
