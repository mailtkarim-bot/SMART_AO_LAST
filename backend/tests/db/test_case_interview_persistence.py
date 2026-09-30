# ruff: noqa: E501, E702, I001
from datetime import UTC, datetime, date
from uuid import uuid4
import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case
from app.modules.patron_action.application.case_interview_commands import RecordCaseInterviewCommand
from app.modules.patron_action.application.case_interview_handler import case_interview_handlers, CaseInterviewReadService
from app.modules.patron_action.application.order_commands import RecordCaseOrderCommand, RecordCaseP6ControlCommand, RecordCaseP7ResultCommand, RecordCaseRexCommand
from app.modules.patron_action.application.order import case_order_handlers
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.application.outcome import case_outcome_handlers
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.persistence.models import TenantRecord
from app.platform.security.context import ActorKind

def _seed(database_engine):
    tenant_id, case_id, actor_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(TenantRecord(id=tenant_id, slug=f"ivw-{tenant_id.hex[:10]}", lifecycle="ACTIVE"))
        session.flush()
        case = _case(tenant_id=tenant_id, case_id=case_id, marker="i")
        case.scope_kind = "MULTI_LOT"
        case.scope_json = {"lot_numbers": ["01"]}
        session.add(case)
        session.commit()
    context = CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=datetime(2026, 9, 30, tzinfo=UTC), identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=case_id, correlation_id=uuid4())
    return tenant_id, case_id, actor_id, context

def _full_chain_dispatcher(session_factory):
    return CommandDispatcher(session_factory=session_factory, handlers={**case_order_handlers(), **case_outcome_handlers(), **case_interview_handlers()})

def test_interview_captures_server_side_snapshot_and_replays_idempotently(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id, context = _seed(database_engine)
    dispatcher = _full_chain_dispatcher(session_factory)
    outcome_id, order_id, p6_id, p7_id = uuid4(), uuid4(), uuid4(), uuid4()
    dispatcher.dispatch(command=RecordCaseOutcomeCommand(command_id=uuid4(), idempotency_key=uuid4(), outcome_id=outcome_id, case_id=case_id, lot_reference="01", outcome="WON", source_locator="notification://r/1", reservations=[], unknown_reason=None), context=context)
    dispatcher.dispatch(command=RecordCaseOrderCommand(command_id=uuid4(), idempotency_key=uuid4(), order_id=order_id, outcome_id=outcome_id, case_id=case_id, decision="ACCEPTED", rationale="Commande rapprochée"), context=context)
    dispatcher.dispatch(command=RecordCaseP6ControlCommand(command_id=uuid4(), idempotency_key=uuid4(), p6_control_id=p6_id, order_id=order_id, case_id=case_id, decision="APPROVED", reservations=[], rationale="Revue P6"), context=context)
    dispatcher.dispatch(command=RecordCaseP7ResultCommand(command_id=uuid4(), idempotency_key=uuid4(), p7_result_id=p7_id, p6_control_id=p6_id, case_id=case_id, result="UNKNOWN", source_locator=None, reason="Retour en attente", reservations=[]), context=context)
    dispatcher.dispatch(command=RecordCaseRexCommand(command_id=uuid4(), idempotency_key=uuid4(), rex_id=uuid4(), p7_result_id=p7_id, case_id=case_id, motif="UNKNOWN", scope="CASE_ONLY", validation="PENDING", observation="DOE tardif", consequence="Marge érodée", follow_up="Revue délai"), context=context)
    interview_id = uuid4()
    command = RecordCaseInterviewCommand(command_id=uuid4(), idempotency_key=uuid4(), interview_id=interview_id, case_id=case_id, held_on=date(2026, 9, 30), source_locator="entretien://comite/2026-09-30", rationale="Revue des enseignements du lot 01", expires_on=date(2027, 3, 30))
    result = dispatcher.dispatch(command=command, context=context)
    replay = dispatcher.dispatch(command=command, context=context)
    assert result.result_code == "CASE_INTERVIEW_RECORDED"
    assert replay.replayed is True
    with Session(database_engine) as session:
        row = session.execute(sa.text("select snapshot_json, held_on, expires_on, source_locator from case_interviews where id = :id"), {"id": interview_id}).one()
        assert row.source_locator == "entretien://comite/2026-09-30"
        assert row.expires_on.isoformat() == "2027-03-30"
        entries = row.snapshot_json if isinstance(row.snapshot_json, list) else row.snapshot_json["rex"]
        assert len(entries) == 1
        assert entries[0]["validation"] == "PENDING"
        assert entries[0]["lot_reference"] == "01"
        assert session.scalar(sa.text("select count(*) from case_interviews where id = :id"), {"id": interview_id}) == 1
    reader = CaseInterviewReadService(session_factory=session_factory)
    from types import SimpleNamespace
    rows = reader.list_for_case(actor=SimpleNamespace(actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id), case_id=case_id, now=datetime(2026, 10, 1, tzinfo=UTC))
    assert len(rows) == 1
    assert rows[0].status == "USABLE"
    expired = reader.list_for_case(actor=SimpleNamespace(actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id), case_id=case_id, now=datetime(2027, 4, 1, tzinfo=UTC))
    assert expired[0].status == "EXPIRED"

def test_interview_is_refused_for_unknown_case(database_engine, session_factory) -> None:
    tenant_id, case_id, actor_id, context = _seed(database_engine)
    dispatcher = _full_chain_dispatcher(session_factory)
    with pytest.raises(Exception, match="CASE_NOT_FOUND_OR_FORBIDDEN"):
        dispatcher.dispatch(command=RecordCaseInterviewCommand(command_id=uuid4(), idempotency_key=uuid4(), interview_id=uuid4(), case_id=uuid4(), held_on=date(2026, 9, 30), source_locator="entretien://comite/1", rationale="Revue", expires_on=date(2027, 3, 30)), context=context)
