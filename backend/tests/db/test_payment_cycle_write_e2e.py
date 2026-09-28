from datetime import UTC, datetime
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case
from app.modules.pricing.application.payment_cycle_commands import RecordPaymentPostReceptionCycleCommand
from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord

NOW = datetime(2026, 9, 27, 12, 0, tzinfo=UTC)

def test_payment_cycle_e2e_persists_and_rejects_id_reuse(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"pay-{tenant_id.hex[:12]}", lifecycle="ACTIVE"))
        session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="p")); session.commit()
    command = RecordPaymentPostReceptionCycleCommand(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4(), case_id=case_id, source_refs=("ccap://p12",), trigger_event="RECEPTION", status="REVIEW_REQUIRED", cash_assumption="À confirmer")
    dispatcher = CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers())
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=NOW, identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    result = dispatcher.dispatch(command=command, context=context)
    replay = dispatcher.dispatch(command=command, context=context)
    assert result.result_code == "PAYMENT_CYCLE_RECORDED"
    assert replay.replayed is True
    with Session(database_engine) as session:
        assert session.scalar(sa.text("select count(*) from payment_post_reception_cycles")) == 1
