# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_final_unknown_audit import build_patron_final_unknown_audit_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Service:
    def get_for_export(self, *, actor, export_id):
        return {"UNKNOWN": 1, "BLOCKED": 1}, (SimpleNamespace(id=uuid4(), export_id=export_id, source_type="VERIFICATION", source_event_id=uuid4(), actor_id=actor.actor_id, status="UNKNOWN", occurred_at=datetime.now(tz=UTC), rationale="Inconnu"),)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_final_unknown_audit_read_preserves_provenance() -> None:
    router = build_patron_final_unknown_audit_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response[0].status == "UNKNOWN"
    assert response[0].source_type == "VERIFICATION"
