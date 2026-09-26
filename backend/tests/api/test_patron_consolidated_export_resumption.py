# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_consolidated_export_resumption import build_patron_consolidated_export_resumption_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id, export_status, resumption_state, limit, offset):
        assert (export_status, resumption_state, limit, offset) == ("UNKNOWN", "FOLLOW_UP_REQUIRED", 1, 0)
        return ({"event_type": "HUMAN_RESUMPTION", "event_id": uuid4(), "status": "FOLLOW_UP_REQUIRED", "created_at": datetime.now(tz=UTC)},)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_consolidated_query_applies_combined_filters_and_keeps_event_type() -> None:
    router = build_patron_consolidated_export_resumption_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), export_status="UNKNOWN", resumption_state="FOLLOW_UP_REQUIRED", limit=1, offset=0, authorization="Bearer token")
    assert response.items[0].event_type == "HUMAN_RESUMPTION"
    assert response.items[0].status == "FOLLOW_UP_REQUIRED"
