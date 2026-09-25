# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4
from app.interfaces.http.routes.patron_contract_query_export_audit import build_patron_contract_query_export_audit_router
from app.platform.security.context import ActorContext, ActorKind, MembershipState

class Resolver:
    def resolve(self, *, access_token: str):
        return _actor()

class Service:
    def get_for_case(self, *, actor, case_id, export_id):
        now = datetime.now(tz=UTC)
        export = SimpleNamespace(id=export_id, case_id=case_id, filters_json={"status": "SUPERSEDED"}, status="UNKNOWN", actor_id=actor.actor_id, created_at=now)
        transition = SimpleNamespace(id=uuid4(), from_status="REQUESTED", to_status="UNKNOWN", local_proof_ref=None, created_at=now)
        return export, (transition,)

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_export_audit_keeps_request_and_transition_separate() -> None:
    router = build_patron_contract_query_export_audit_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), uuid4(), authorization="Bearer token")
    assert response.export.status == "UNKNOWN"
    assert len(response.transitions) == 1
    assert response.transitions[0].from_status == "REQUESTED"
