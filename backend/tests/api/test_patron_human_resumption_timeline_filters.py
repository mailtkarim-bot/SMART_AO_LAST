# ruff: noqa: E501
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_human_resumption_timeline import build_patron_human_resumption_timeline_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id, state, limit, offset):
        rows = tuple({"event_type": "HUMAN_RESUMPTION", "event_id": uuid4(), "status": value, "created_at": datetime.now(tz=UTC) + timedelta(seconds=index)} for index, value in enumerate(("ACKNOWLEDGED", "FOLLOW_UP_REQUIRED", "BLOCKED")))
        if state: rows = tuple(row for row in rows if row["status"] == state)
        return rows[offset:offset + limit]

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_resumption_timeline_filter_and_pagination_are_server_bounded() -> None:
    router = build_patron_human_resumption_timeline_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), state="FOLLOW_UP_REQUIRED", limit=1, offset=0, authorization="Bearer token")
    assert len(response.items) == 1
    assert response.items[0].status == "FOLLOW_UP_REQUIRED"
