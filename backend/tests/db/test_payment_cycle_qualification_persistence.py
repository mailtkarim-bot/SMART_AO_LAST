# ruff: noqa: E501, E702, I001
from datetime import UTC, datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case
from app.modules.pricing.application.payment_cycle_commands import QualifyPaymentPostReceptionCycleCommand
from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
from app.modules.pricing.application.payment_external_signal_handler import build_external_payment_signal_command
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.persistence.models import TenantRecord

def test_qualification_updates_cost_note_and_cash_hypothesis_without_status_change(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"pay-qual-{tenant_id.hex[:10]}", lifecycle="ACTIVE"))
        session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="q")); session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime(2026, 9, 28, tzinfo=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    cycle_id = uuid4()
    signal = build_external_payment_signal_command(case_id=case_id, payload={"source_ref": "external://payment-signal/1", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}, command_id=uuid4(), idempotency_key=uuid4(), cycle_id=cycle_id)
    dispatcher = CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers())
    dispatcher.dispatch(command=signal, context=context)
    qualify = QualifyPaymentPostReceptionCycleCommand(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=cycle_id, case_id=case_id, cash_assumption="Délai prudent 75 jours", post_reception_cost_note="Levée de réserves à chiffrer")
    result = dispatcher.dispatch(command=qualify, context=context)
    replay = dispatcher.dispatch(command=qualify, context=context)
    assert result.result_code == "PAYMENT_CYCLE_QUALIFIED"
    assert replay.replayed is True
    with Session(database_engine) as session:
        row = session.execute(sa.text("select status, cash_assumption, post_reception_cost_note from payment_post_reception_cycles where id = :id"), {"id": cycle_id}).one()
        assert row.status == "SOURCE_SIGNAL_ONLY"
        assert row.cash_assumption == "Délai prudent 75 jours"
        assert row.post_reception_cost_note == "Levée de réserves à chiffrer"

def test_qualification_is_refused_for_unknown_cycle(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"pay-qualx-{tenant_id.hex[:10]}", lifecycle="ACTIVE"))
        session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="x")); session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime(2026, 9, 28, tzinfo=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    dispatcher = CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers())
    import pytest
    with pytest.raises(Exception, match="PAYMENT_CYCLE_NOT_FOUND"):
        dispatcher.dispatch(command=QualifyPaymentPostReceptionCycleCommand(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4(), case_id=case_id, cash_assumption="Délai prudent", post_reception_cost_note=None), context=context)
