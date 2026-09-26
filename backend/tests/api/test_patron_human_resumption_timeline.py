# ruff: noqa: E501
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_human_resumption_timeline import build_patron_human_resumption_timeline_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id):
        now = datetime.now(tz=UTC)
        return tuple({"event_type": kind, "event_id": uuid4(), "status": status, "created_at": now + timedelta(seconds=index)} for index, (kind, status) in enumerate((("TRANSITION", "UNKNOWN"), ("HUMAN_RESUMPTION", "FOLLOW_UP_REQUIRED"))))

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_resumption_timeline_keeps_technical_and_human_events_separate() -> None:
    router = build_patron_human_resumption_timeline_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert [item.event_type for item in response.items] == ["TRANSITION", "HUMAN_RESUMPTION"]
