# ruff: noqa: E501, E702, I001
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_payment_unknown_audit_owner_act_read import build_patron_payment_unknown_audit_owner_act_read_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState
class Resolver:
    def resolve(self, *, access_token: str):
        actor_id = uuid4(); now = datetime.now(tz=UTC)
        return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())
class Service:
    def get_for_case(self, *, actor, case_id): return SimpleNamespace(id=uuid4(), case_id=case_id, owner_id=actor.actor_id, approved=True, rationale="Revue locale", created_at=datetime.now(tz=UTC))
def test_owner_act_read_is_patron_scoped():
    router = build_patron_payment_unknown_audit_owner_act_read_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), authorization="Bearer token")
    assert response.approved is True
    assert response.rationale == "Revue locale"
