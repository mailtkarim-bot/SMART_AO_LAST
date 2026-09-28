# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_payment_cycle_write import build_patron_payment_cycle_write_router
from app.modules.pricing.public.payment_cycle_contracts import RecordPaymentCycleRequest
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def execute(self, *, actor, command, now):
        return SimpleNamespace(command_id=str(command.command_id), idempotency_key=str(command.idempotency_key), result_code="PAYMENT_CYCLE_RECORDED", replayed=True)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_patron_payment_cycle_write_preserves_replay() -> None:
    router = build_patron_payment_cycle_write_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), RecordPaymentCycleRequest(command_id=uuid4(), idempotency_key=uuid4(), cycle_id=uuid4(), source_refs=("ccap://p12",), trigger_event="RECEPTION", status="REVIEW_REQUIRED"), authorization="Bearer token")
    assert response.status_code == 200
