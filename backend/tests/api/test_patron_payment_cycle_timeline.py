# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_payment_cycle_timeline import build_patron_payment_cycle_timeline_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def list_for_case(self, *, actor, case_id):
        return (SimpleNamespace(id=uuid4(), case_id=case_id, source_refs_json=["ccap://p12"], trigger_event="RECEPTION", status="UNKNOWN", cash_assumption="À confirmer", post_reception_cost_note="À qualifier"),)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_payment_timeline_preserves_unknown_and_cash_hypothesis() -> None:
    router = build_patron_payment_cycle_timeline_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response[0].status == "UNKNOWN"
    assert response[0].cash_assumption == "À confirmer"
