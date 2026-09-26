# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_export_operational_handoff import build_patron_export_operational_handoff_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id):
        transition = SimpleNamespace(created_at=datetime.now(tz=UTC))
        return SimpleNamespace(id=export_id, status="UNKNOWN", filters_json={"status": "SUPERSEDED"}), (transition,)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_operational_handoff_preserves_unknown_and_is_read_only() -> None:
    router = build_patron_export_operational_handoff_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response.current_status == "UNKNOWN"
    assert response.transition_count == 1
    assert response.read_only is True
