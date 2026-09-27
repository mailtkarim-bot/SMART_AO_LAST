# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_unknown_audit_provenance import build_patron_unknown_audit_provenance_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id):
        return (SimpleNamespace(id=uuid4(), export_id=export_id, source_type="HUMAN_RESUMPTION", source_event_id=uuid4(), actor_id=actor.actor_id, status="BLOCKED", occurred_at=datetime.now(tz=UTC), rationale="Action requise"),)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_unknown_provenance_read_projection_preserves_source_and_rationale() -> None:
    router = build_patron_unknown_audit_provenance_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response[0].source_type == "HUMAN_RESUMPTION"
    assert response[0].status == "BLOCKED"
    assert response[0].rationale == "Action requise"
