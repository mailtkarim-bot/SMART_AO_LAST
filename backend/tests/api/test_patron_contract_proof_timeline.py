# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.interfaces.http.routes.patron_contract_proof_reviews import (
    build_patron_contract_proof_review_router,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def resolve(self, *, access_token: str):
        return _actor()


class Service:
    def timeline_for_case(self, *, actor, case_id, now):
        return (
            {"event_type": "REVIEW", "event_id": uuid4(), "proof_id": uuid4(), "revision": 1, "status": "SUPERSEDED", "rationale": "Rectificatif reçu", "created_at": now},
            {"event_type": "REVIEW", "event_id": uuid4(), "proof_id": uuid4(), "revision": 2, "status": "NEEDS_CLARIFICATION", "rationale": "Nouvelle revue", "created_at": now},
        )


def _actor() -> ActorContext:
    actor_id = uuid4()
    now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())


def test_timeline_projection_keeps_superseded_and_new_review_visible() -> None:
    router = build_patron_contract_proof_review_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[2].endpoint(uuid4(), "Bearer token")
    assert [item.status for item in response.items] == ["SUPERSEDED", "NEEDS_CLARIFICATION"]
