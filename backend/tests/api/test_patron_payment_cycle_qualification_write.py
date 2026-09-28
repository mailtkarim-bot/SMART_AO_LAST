# ruff: noqa: E501, E702
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.interfaces.http.routes.patron_payment_cycle_qualification_write import (
    build_patron_payment_cycle_qualification_write_router,
)
from app.modules.pricing.public.payment_cycle_contracts import QualifyPaymentCycleRequest
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def execute(self, *, actor, command, now):
        return SimpleNamespace(command_id=str(command.command_id), idempotency_key=str(command.idempotency_key), result_code="PAYMENT_CYCLE_QUALIFIED", replayed=False)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_patron_payment_cycle_qualification_records_prudent_hypothesis() -> None:
    router = build_patron_payment_cycle_qualification_write_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    cycle_id = uuid4()
    response = router.routes[0].endpoint(uuid4(), cycle_id, QualifyPaymentCycleRequest(command_id=uuid4(), idempotency_key=uuid4(), cash_assumption="Délai prudent 75 jours", post_reception_cost_note="Levée de réserves à chiffrer"), authorization="Bearer token")
    assert response.status_code == 201
