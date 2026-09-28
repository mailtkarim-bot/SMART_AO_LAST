# ruff: noqa: E501, E701, E702, I001
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.interfaces.http.routes.patron_payment_unknown_audit import build_patron_payment_unknown_audit_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def __init__(self, actor_kind=ActorKind.PATRON_ADMIN): self.actor_kind = actor_kind
    def resolve(self, *, access_token: str): return _actor(self.actor_kind)

class Service:
    def audit_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN: raise PermissionError("PATRON_REQUIRED")
        return SimpleNamespace(status_counts={"UNKNOWN": 1}, entries=({"cycle_id": uuid4(), "status": "UNKNOWN", "source_refs": ("ccap://p20",), "trigger_event": "RECEPTION"},))

def _actor(actor_kind=ActorKind.PATRON_ADMIN) -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=actor_kind, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_payment_unknown_audit_keeps_prudent_status_and_source():
    router = build_patron_payment_unknown_audit_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response.status_counts == {"UNKNOWN": 1}
    assert response.entries[0].source_refs == ("ccap://p20",)

def test_payment_unknown_audit_refuses_collaborator():
    router = build_patron_payment_unknown_audit_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.COLLABORATEUR)))
    with pytest.raises(Exception, match="403"):
        router.routes[0].endpoint(uuid4(), authorization="Bearer token")
