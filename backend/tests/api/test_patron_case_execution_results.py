from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_actions import build_patron_action_router
from app.modules.patron_action.application.order import CaseOrderService
from app.platform.security.authenticated_context import AuthenticationContextResolver
from app.platform.security.authorization import AuthorizationPolicyPort
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException


@dataclass
class Resolver:
    actor_kind: ActorKind

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "test-token"
        now = datetime.now(tz=UTC)
        identifier = uuid4()
        return ActorContext(
            actor_id=identifier,
            identity_id=uuid4(),
            tenant_id=uuid4(),
            membership_id=uuid4(),
            actor_kind=self.actor_kind,
            membership_state=MembershipState.ACTIVE,
            capabilities=frozenset(),
            assigned_case_ids=frozenset(),
            session_id=uuid4(),
            authenticated_at=now,
            mfa_verified_at=now,
            correlation_id=uuid4(),
        )


class OrderReadService:
    def list_execution_results(self, *, actor, case_id, now):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise PermissionError("PATRON_REQUIRED")
        return SimpleNamespace(
            case_id=case_id,
            lot_references=("01",),
            results=(
                SimpleNamespace(
                    outcome=SimpleNamespace(
                        id=uuid4(),
                        lot_reference="01",
                        outcome="UNKNOWN",
                        source_locator=None,
                        reservations_json=["Notification non rapprochée"],
                        unknown_reason="Réponse inconnue",
                        created_at=now,
                        actor_id=uuid4(),
                    ),
                    transmission=None,
                    order=None,
                    p6=None,
                    p7=None,
                ),
            ),
        )


def router_for(actor_kind: ActorKind):
    return build_patron_action_router(
        service=SimpleNamespace(),
        transition_service=SimpleNamespace(),
        outcome_service=None,
        order_service=cast(CaseOrderService, OrderReadService()),
        security_runtime=ConsultationSecurityRuntime(
            context_resolver=cast(AuthenticationContextResolver, Resolver(actor_kind)),
            policy=cast(AuthorizationPolicyPort, SimpleNamespace()),
        ),
    )


def test_patron_reads_lot_outcome_projection_with_unknown_and_missing_steps_explicit() -> None:
    case_id = uuid4()
    router = router_for(ActorKind.PATRON_ADMIN)
    route = next(route for route in router.routes if route.path.endswith("/execution-results"))
    body = route.endpoint(case_id=case_id, authorization="Bearer test-token").model_dump(
        mode="json"
    )
    assert body["case_id"] == str(case_id)
    assert body["lot_references"] == ["01"]
    assert body["results"][0]["outcome"] == "UNKNOWN"
    assert body["results"][0]["unknown_reason"] == "Réponse inconnue"
    assert body["results"][0]["order"] is None
    assert body["results"][0]["p6"] is None
    assert body["results"][0]["p7"] is None


def test_collaborator_cannot_read_patron_execution_result_projection() -> None:
    router = router_for(ActorKind.COLLABORATEUR)
    route = next(route for route in router.routes if route.path.endswith("/execution-results"))
    try:
        route.endpoint(case_id=uuid4(), authorization="Bearer test-token")
    except HTTPException as error:
        assert error.status_code == 403
    else:
        raise AssertionError("collaborator request should be refused")
