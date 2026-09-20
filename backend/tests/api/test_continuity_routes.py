from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.routes.continuity import (
    AcceptHandoverRequest,
    RequestHandoverRequest,
    build_continuity_router,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from app.platform.security.continuity import ContinuityResult
from fastapi import HTTPException


class FakeContextResolver:
    def __init__(self, context: ActorContext) -> None:
        self.context = context

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "session-token"
        return self.context


class FakeContinuityService:
    def __init__(self) -> None:
        self.requested = None
        self.accepted = None

    def request_handover(self, **kwargs):
        self.requested = kwargs
        return ContinuityResult(kwargs["command"].handover_id, "REQUESTED")

    def accept_handover(self, **kwargs):
        self.accepted = kwargs
        return ContinuityResult(kwargs["command"].handover_id, "ACCEPTED")


def _context() -> ActorContext:
    member = uuid4()
    return ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=uuid4(),
        membership_id=member,
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=datetime.now(tz=UTC),
        mfa_verified_at=datetime.now(tz=UTC),
        correlation_id=uuid4(),
    )


def test_request_handover_keeps_actor_server_side_and_returns_created_response() -> None:
    service = FakeContinuityService()
    context = _context()
    runtime = SimpleNamespace(context_resolver=FakeContextResolver(context))
    endpoint = build_continuity_router(
        service=service, security_runtime=runtime
    ).routes[0].endpoint
    handover_id = uuid4()
    response = endpoint(
        RequestHandoverRequest(
            handover_id=handover_id,
            successor_membership_id=uuid4(),
            assignment_ids=[uuid4()],
            command_id=uuid4(),
            idempotency_key=uuid4(),
            rationale="Relève nominative.",
        ),
        authorization="Bearer session-token",
    )
    assert response.status_code == 201
    assert service.requested["actor"].membership_id == context.membership_id
    assert response.body is not None and b'"state":"REQUESTED"' in response.body


def test_acceptance_replay_is_returned_as_successful_http_response() -> None:
    service = FakeContinuityService()
    runtime = SimpleNamespace(context_resolver=FakeContextResolver(_context()))
    endpoint = build_continuity_router(
        service=service, security_runtime=runtime
    ).routes[1].endpoint
    response = endpoint(
        uuid4(),
        AcceptHandoverRequest(command_id=uuid4(), reason="Je prends la relève."),
        authorization="Bearer session-token",
    )
    assert response.status_code == 201
    assert service.accepted["command"].reason == "Je prends la relève."


def test_neutral_not_found_and_validation_are_preserved() -> None:
    service = FakeContinuityService()
    service.request_handover = lambda **_: (_ for _ in ()).throw(
        PermissionError("NOT_FOUND_OR_FORBIDDEN")
    )
    runtime = SimpleNamespace(context_resolver=FakeContextResolver(_context()))
    endpoint = build_continuity_router(
        service=service, security_runtime=runtime
    ).routes[0].endpoint
    request = RequestHandoverRequest(
        handover_id=uuid4(),
        successor_membership_id=uuid4(),
        assignment_ids=[uuid4()],
        command_id=uuid4(),
        idempotency_key=uuid4(),
        rationale="Relève.",
    )
    with pytest.raises(HTTPException) as error:
        endpoint(request, authorization="Bearer session-token")
    assert error.value.status_code == 404
    assert error.value.detail == "NOT_FOUND_OR_FORBIDDEN"
