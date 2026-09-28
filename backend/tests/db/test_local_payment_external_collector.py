# ruff: noqa: E501, E702, I001
from datetime import UTC, datetime
from uuid import uuid4
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case
from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
from app.modules.pricing.infrastructure.local_payment_external_collector import LocalPaymentExternalCollector
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.persistence.models import TenantRecord

def test_local_external_collector_runs_real_dispatcher(database_engine, session_factory):
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"collector-{tenant_id.hex[:10]}", lifecycle="ACTIVE")); session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="e")); session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime.now(tz=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    collector = LocalPaymentExternalCollector(dispatcher=CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers()), payload_source=lambda: {"source_ref": "fixture://payment/1", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"})
    result = collector.collect(case_id=case_id, context=context, command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4())
    assert result.result_code == "PAYMENT_CYCLE_RECORDED"

def test_local_external_collector_enforces_fixture_budget(database_engine, session_factory):
    collector = LocalPaymentExternalCollector(dispatcher=CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers()), payload_source=lambda: {"source_ref": "fixture://payment/2", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"})
    with pytest.raises(ValueError, match="PAYMENT_EXTERNAL_COLLECTION_BUDGET_EXCEEDED"):
        collector.collect_many(case_id=uuid4(), context=None, identities=tuple((uuid4(), uuid4(), uuid4()) for _ in range(2)), max_payloads=1)

def test_local_external_collector_dispatches_multiple_fixtures(database_engine, session_factory):
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"multi-{tenant_id.hex[:10]}", lifecycle="ACTIVE")); session.flush(); session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="e")); session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime.now(tz=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    payloads = iter(({"source_ref": "fixture://payment/a", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}, {"source_ref": "fixture://payment/b", "trigger_event": "EXTERNAL_PAYMENT_SIGNAL"}))
    collector = LocalPaymentExternalCollector(dispatcher=CommandDispatcher(session_factory=session_factory, handlers=payment_cycle_handlers()), payload_source=lambda: next(payloads))
    identities = tuple((uuid4(), uuid4(), uuid4()) for _ in range(2))
    results = collector.collect_many(case_id=case_id, context=context, identities=identities)
    assert len(results) == 2
    with Session(database_engine) as session:
        assert session.scalar(sa.text("select count(*) from payment_post_reception_cycles where case_id = :case_id"), {"case_id": case_id}) == 2
