from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.routes.patron_actions import build_patron_action_router
from app.modules.patron_action.public.contracts import RecordCaseTeachingApplicabilityRequest
from app.platform.events.dispatcher import CommandInProgressError, IdempotencyKeyReusedError
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException
from pydantic import ValidationError


class Resolver:
    def resolve(self, *, access_token: str):
        return _actor()


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


class Service:
    def __init__(self, *, denied: bool = False, error: Exception | None = None):
        self.denied = denied
        self.error = error
        self.command = None

    def record_applicability(self, *, actor, command, now):
        if self.denied:
            raise PermissionError("FORBIDDEN")
        if self.error is not None:
            raise self.error
        self.command = command
        return SimpleNamespace(
            result_code="CASE_TEACHING_APPLICABILITY_RECORDED",
            aggregate_refs=[{"aggregate_id": str(command.applicability_id)}],
            event_ids=[str(uuid4())],
            replayed=False,
        )

    def list_sources(self, *, actor, target_case_id, now):
        return (
            SimpleNamespace(
                source_case_id=uuid4(),
                source_case_label="Affaire source",
                source_interview_id=uuid4(),
                source_rex_id=uuid4(),
                held_on=date(2026, 9, 29),
                source_locator="entretien://source/1",
                interview_rationale="Revue source",
                expires_on=date(2027, 3, 30),
                source_validity="USABLE",
                snapshot={"scope": "ENTERPRISE_PATTERN", "validation": "APPROVED"},
                can_assess=True,
                block_reason=None,
            ),
        )

    def list_for_case(self, *, actor, target_case_id, now):
        record = SimpleNamespace(
            id=uuid4(),
            target_case_id=target_case_id,
            source_interview_id=uuid4(),
            source_rex_id=uuid4(),
            decision="APPLICABLE",
            rationale="Comparaison humaine",
            target_source_locator="dce://target/1",
            source_expires_on=date(2027, 3, 30),
            source_validity_at_recording="USABLE",
            source_snapshot_json={"rex_id": str(uuid4())},
            actor_id=uuid4(),
            created_at=now,
        )
        return (
            SimpleNamespace(
                record=record,
                source_case_id=uuid4(),
                source_case_label="Affaire source",
                source_validity="USABLE",
            ),
        )


def _router(service):
    return build_patron_action_router(
        service=object(),
        transition_service=object(),
        security_runtime=SimpleNamespace(context_resolver=Resolver()),
        teaching_applicability_service=service,
    )


def _request(target_case_id):
    return RecordCaseTeachingApplicabilityRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        applicability_id=uuid4(),
        target_case_id=target_case_id,
        source_case_id=uuid4(),
        source_interview_id=uuid4(),
        source_rex_id=uuid4(),
        decision="REVIEW_REQUIRED",
        rationale="Applicabilité à vérifier avec le CCTP du lot cible.",
        target_source_locator="dce://target/cctp/lot-01",
    )


def test_patron_can_record_explicit_case_teaching_applicability() -> None:
    service = Service()
    router = _router(service)
    route = next(
        r
        for r in router.routes
        if getattr(r, "path", "").endswith("/teaching-applicabilities") and "POST" in r.methods
    )
    target_case_id = uuid4()

    response = route.endpoint(
        target_case_id, _request(target_case_id), authorization="Bearer token"
    )

    assert response.status_code == 201
    assert response.body is not None
    assert b"CASE_TEACHING_APPLICABILITY_RECORDED" in response.body
    assert service.command.target_case_id == target_case_id


def test_teaching_applicability_path_mismatch_and_role_refusal_are_closed() -> None:
    route = next(
        r
        for r in _router(Service()).routes
        if getattr(r, "path", "").endswith("/teaching-applicabilities") and "POST" in r.methods
    )
    with pytest.raises(HTTPException) as mismatch:
        route.endpoint(uuid4(), _request(uuid4()), authorization="Bearer token")
    assert mismatch.value.status_code == 422

    denied_route = next(
        r
        for r in _router(Service(denied=True)).routes
        if getattr(r, "path", "").endswith("/teaching-applicabilities") and "POST" in r.methods
    )
    target_case_id = uuid4()
    with pytest.raises(HTTPException) as denied:
        denied_route.endpoint(
            target_case_id, _request(target_case_id), authorization="Bearer token"
        )
    assert denied.value.status_code == 403


def test_client_cannot_supply_the_frozen_source_snapshot() -> None:
    payload = _request(uuid4()).model_dump()
    payload["source_snapshot"] = {"validation": "APPROVED"}
    with pytest.raises(ValidationError):
        RecordCaseTeachingApplicabilityRequest.model_validate(payload)


def test_patron_reads_target_scoped_source_and_applicability_projection() -> None:
    router = _router(Service())
    source_route = next(
        r
        for r in router.routes
        if getattr(r, "path", "").endswith("/teaching-sources") and "GET" in r.methods
    )
    history_route = next(
        r
        for r in router.routes
        if getattr(r, "path", "").endswith("/teaching-applicabilities") and "GET" in r.methods
    )
    target_case_id = uuid4()

    sources = source_route.endpoint(target_case_id, authorization="Bearer token")
    history = history_route.endpoint(target_case_id, authorization="Bearer token")

    assert sources["case_id"] == str(target_case_id)
    assert sources["sources"][0]["can_assess"] is True
    assert history["applicabilities"][0]["source_validity_current"] == "USABLE"


@pytest.mark.parametrize(
    ("error", "detail"),
    [
        (IdempotencyKeyReusedError("reused"), "IDEMPOTENCY_KEY_REUSED"),
        (CommandInProgressError("in progress"), "COMMAND_IN_PROGRESS"),
    ],
)
def test_idempotency_conflicts_are_409_and_keep_the_same_command_available(error, detail) -> None:
    route = next(
        r for r in _router(Service(error=error)).routes
        if getattr(r, "path", "").endswith("/teaching-applicabilities") and "POST" in r.methods
    )
    target_case_id = uuid4()

    with pytest.raises(HTTPException) as conflict:
        route.endpoint(target_case_id, _request(target_case_id), authorization="Bearer token")

    assert conflict.value.status_code == 409
    assert conflict.value.detail == detail
