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
    def timeline_for_case(self, *, actor, case_id, now, revision=None, status=None, limit=50, offset=0):
        rows = (
            {
                "event_type": "REVIEW",
                "event_id": uuid4(),
                "proof_id": uuid4(),
                "revision": 1,
                "status": "SUPERSEDED",
                "rationale": "Rectificatif reçu",
                "created_at": now,
            },
            {
                "event_type": "REVIEW",
                "event_id": uuid4(),
                "proof_id": uuid4(),
                "revision": 2,
                "status": "NEEDS_CLARIFICATION",
                "rationale": "Nouvelle revue",
                "created_at": now,
            },
        )
        if revision is not None:
            rows = tuple(row for row in rows if row["revision"] == revision)
        if status is not None:
            rows = tuple(row for row in rows if row["status"] == status)
        return rows[offset : offset + limit]


def _actor() -> ActorContext:
    actor_id = uuid4()
    now = datetime.now(tz=UTC)
    return ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=now,
        mfa_verified_at=now,
        correlation_id=uuid4(),
    )


def test_timeline_projection_keeps_superseded_and_new_review_visible() -> None:
    router = build_patron_contract_proof_review_router(
        service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver())
    )
    response = router.routes[2].endpoint(uuid4(), revision=None, review_status=None, limit=50, offset=0, authorization="Bearer token")
    assert [item.status for item in response.items] == ["SUPERSEDED", "NEEDS_CLARIFICATION"]


def test_timeline_endpoint_accepts_bounded_filters() -> None:
    router = build_patron_contract_proof_review_router(
        service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver())
    )
    response = router.routes[2].endpoint(
        uuid4(),
        revision=2,
        review_status="NEEDS_CLARIFICATION",
        limit=1,
        offset=0,
        authorization="Bearer token",
    )
    assert len(response.items) == 1
