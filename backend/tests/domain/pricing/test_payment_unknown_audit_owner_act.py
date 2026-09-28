# ruff: noqa: E501, I001
from uuid import uuid4
from app.modules.pricing.application.payment_unknown_audit_owner_act_commands import RecordPaymentUnknownAuditOwnerActCommand
from app.modules.pricing.application.payment_unknown_audit_owner_act_handler import RecordPaymentUnknownAuditOwnerActHandler
from app.platform.events.dispatcher import CommandContext, CommandExecutionError

class Session:
    def __init__(self, values): self.values = iter(values); self.added = []
    def scalar(self, statement): return next(self.values)
    def add(self, value): self.added.append(value)

def _context(tenant_id, actor_id):
    return CommandContext(tenant_id=tenant_id, actor_id=actor_id, actor_kind="PATRON_ADMIN", received_at=None, identity_id=actor_id, membership_id=uuid4(), session_id=uuid4(), case_id=None, correlation_id=uuid4())

def test_owner_act_is_idempotence_guarded_by_owner_act_id():
    tenant_id, actor_id, case_id, act_id = uuid4(), uuid4(), uuid4(), uuid4()
    command = RecordPaymentUnknownAuditOwnerActCommand(command_id=uuid4(), idempotency_key=uuid4(), owner_act_id=act_id, case_id=case_id, approved=True, rationale="Revue locale")
    session = Session([case_id, None])
    result = RecordPaymentUnknownAuditOwnerActHandler().execute(session=session, command=command, context=_context(tenant_id, actor_id))
    assert result.result_code == "PAYMENT_UNKNOWN_AUDIT_OWNER_ACT_RECORDED"
    duplicate = Session([case_id, act_id])
    try:
        RecordPaymentUnknownAuditOwnerActHandler().execute(session=duplicate, command=command, context=_context(tenant_id, actor_id))
    except CommandExecutionError as error:
        assert str(error) == "PAYMENT_UNKNOWN_AUDIT_OWNER_ACT_ID_REUSED"
    else:
        raise AssertionError("duplicate owner act must be rejected")
