from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.interfaces.http.routes.patron_contract_baseline_impacts import (
    build_patron_contract_baseline_impact_router,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def resolve(self, *, access_token: str):
        return _actor()


class Reader:
    def __init__(self, rows=()):
        self.rows = rows

    def list_for_case(self, *, actor, case_id, now):
        return self.rows


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


def test_patron_contract_baseline_impact_projection_is_closed_and_read_only() -> None:
    case_id, proof_id, observation_id = uuid4(), uuid4(), uuid4()
    row = SimpleNamespace(
        id=proof_id,
        case_id=case_id,
        baseline_observation_id=observation_id,
        proof_revision=1,
        baseline_source_refs_json=["dce://ccap/page-4"],
        baseline_statement="Clause baseline",
        deviation_statement="Déroge",
        impact_statement="Revue requise",
        status="HUMAN_REVIEW_REQUIRED",
    )
    router = build_patron_contract_baseline_impact_router(
        service=Reader((row,)),
        security_runtime=SimpleNamespace(context_resolver=Resolver()),
    )
    response = router.routes[0].endpoint(case_id, "Bearer session-token")
    assert response.items[0].status == "HUMAN_REVIEW_REQUIRED"
    assert response.items[0].baseline_source_refs == ["dce://ccap/page-4"]
