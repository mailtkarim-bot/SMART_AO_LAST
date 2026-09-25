# ruff: noqa: E501
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.interfaces.http.routes.patron_contract_query_receipts import (
    build_patron_contract_query_receipt_router,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def resolve(self, *, access_token: str):
        return _actor()


class Service:
    def list_for_case(self, *, actor, case_id, limit, offset):
        assert limit == 1
        assert offset == 1
        return (SimpleNamespace(id=uuid4(), case_id=case_id, filters_json={"status": "SUPERSEDED"}, order_key="revision_created_at", limit_value=1, offset_value=1, actor_id=actor.actor_id, created_at=datetime.now(tz=UTC)),)


def _actor() -> ActorContext:
    actor_id = uuid4()
    now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())


def test_patron_receipt_read_preserves_filters_and_pagination() -> None:
    router = build_patron_contract_query_receipt_router(service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()))
    response = router.routes[0].endpoint(uuid4(), limit=1, offset=1, authorization="Bearer token")
    assert response.items[0].filters == {"status": "SUPERSEDED"}
    assert response.items[0].limit_value == 1
    assert response.items[0].offset_value == 1
