from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.routes.patron_regulatory_profiles import (
    build_patron_regulatory_profile_router,
)
from app.modules.case.public.regulatory_profile_contracts import RecordRegulatoryProfileRequest
from app.platform.events.dispatcher import CommandExecutionError
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException


class Resolver:
    def __init__(self, actor: ActorContext) -> None:
        self.actor = actor

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "session-token"
        return self.actor


class FakeService:
    def __init__(self, *, error: Exception | None = None) -> None:
        self.error = error
        self.command = None

    def execute(self, *, actor, command, now):
        if self.error is not None:
            raise self.error
        self.command = command
        return SimpleNamespace(
            command_id=str(command.command_id),
            idempotency_key=str(command.idempotency_key),
            result_code="REGULATORY_PROFILE_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_id": str(command.profile_id),
                    "aggregate_revision": command.profile_version,
                },
            ),
            event_ids=(str(uuid4()),),
            replayed=False,
        )


def _actor() -> ActorContext:
    actor_id = uuid4()
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
        authenticated_at=datetime.now(tz=UTC),
        mfa_verified_at=datetime.now(tz=UTC),
        correlation_id=uuid4(),
    )


def _endpoint(service: FakeService):
    router = build_patron_regulatory_profile_router(
        service=service,
        security_runtime=SimpleNamespace(context_resolver=Resolver(_actor())),
    )
    return router.routes[0].endpoint


def test_patron_can_record_profile_with_closed_response_contract() -> None:
    service = FakeService()
    profile_id = uuid4()
    response = _endpoint(service)(
        case_id=uuid4(),
        request=RecordRegulatoryProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            profile_id=profile_id,
            profile_version=1,
            status="UNKNOWN_APPLICABILITY",
            facts={"market_kind": "PUBLIC"},
            source_refs=("dce:rc:p4",),
        ),
        authorization="Bearer session-token",
    )

    assert response.status_code == 201
    assert response.body is not None and str(profile_id).encode() in response.body
    assert service.command is not None
    assert service.command.status == "UNKNOWN_APPLICABILITY"


def test_profile_route_keeps_foreign_case_refusal_neutral() -> None:
    service = FakeService(error=CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN"))
    with pytest.raises(HTTPException) as raised:
        _endpoint(service)(
            case_id=uuid4(),
            request=RecordRegulatoryProfileRequest(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                profile_id=uuid4(),
                profile_version=1,
                status="REVIEW_REQUIRED",
                facts={"market_kind": "PUBLIC"},
                source_refs=("manual:review",),
            ),
            authorization="Bearer session-token",
        )

    assert raised.value.status_code == 404
    assert raised.value.detail == "CASE_NOT_FOUND_OR_FORBIDDEN"
