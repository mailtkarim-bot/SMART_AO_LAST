# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_payment_cycle_review_write import build_patron_payment_cycle_review_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Dispatcher:
    def dispatch(self, *, command, context):
        return SimpleNamespace(command_id=str(command.command_id), idempotency_key=str(command.idempotency_key), result_code="PAYMENT_CYCLE_REVIEW_RECORDED", replayed=True)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_payment_review_write_preserves_idempotent_replay() -> None:
    router = build_patron_payment_cycle_review_router(dispatcher=Dispatcher(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    from app.modules.pricing.public.payment_cycle_review_contracts import RecordPaymentCycleReviewRequest
    response = router.routes[0].endpoint(uuid4(), RecordPaymentCycleReviewRequest(command_id=uuid4(), idempotency_key=uuid4(), review_id=uuid4(), decision="ACCEPTED_FOR_PLANNING", rationale="Planification"), authorization="Bearer token")
    assert response.status_code == 200
