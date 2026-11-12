from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, cast
from uuid import NAMESPACE_URL, uuid4, uuid5

import pytest
from app.interfaces.http.routes.collaborator_capabilities import (
    build_collaborator_capability_router,
)
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.membership.public.collab_capability_contracts import (
    ProposeCapabilityForCaseRequest,
    ReportCapabilityGapRequest,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)
from app.platform.security.authenticated_context import (
    UnauthenticatedError,
)
from app.platform.security.authorization import AuthorizationPolicyPort
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import FastAPI
from fastapi.testclient import TestClient


@dataclass
class _Resolver:
    error: Exception | None = None

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "test-token"
        if self.error is not None:
            raise self.error
        return _actor()


def _actor() -> ActorContext:
    from datetime import UTC, datetime

    return ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=ActorKind.COLLABORATEUR,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=datetime.now(tz=UTC),
        mfa_verified_at=datetime.now(tz=UTC),
        correlation_id=uuid4(),
    )


def _runtime(*, resolver_error: Exception | None = None) -> ConsultationSecurityRuntime:
    return ConsultationSecurityRuntime(
        context_resolver=cast(Any, _Resolver(error=resolver_error)),
        policy=cast(AuthorizationPolicyPort, SimpleNamespace()),
    )


def _client(*, service=None, resolver_error=None, raise_server_exceptions=False) -> TestClient:
    app = FastAPI()
    app.include_router(
        build_collaborator_capability_router(
            service=service or cast(Any, _CapabilityService()),
            security_runtime=_runtime(resolver_error=resolver_error),
        )
    )
    return TestClient(app, raise_server_exceptions=raise_server_exceptions)


def _result(*, replayed: bool = False, result_code: str) -> SimpleNamespace:
    return SimpleNamespace(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        result_code=result_code,
        aggregate_refs=[{"aggregate_id": str(uuid4()), "aggregate_revision": 1}],
        event_ids=[str(uuid4())],
        replayed=replayed,
    )


def _proposal_payload() -> dict[str, object]:
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "assignment_id": str(uuid4()),
        "capability_id": str(uuid4()),
        "capability_version_id": str(uuid4()),
        "requirement_id": str(uuid4()),
        "task_id": str(uuid4()),
        "justification": "Référence travaux similaire validée.",
        "source_locator": "qualification:reference:42",
    }


def _gap_payload() -> dict[str, object]:
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "assignment_id": str(uuid4()),
        "capability_id": str(uuid4()),
        "requirement_id": str(uuid4()),
        "task_id": str(uuid4()),
        "gap_kind": "MISSING",
        "severity": "BLOCKING",
        "reason": "La qualification obligatoire n’est pas disponible.",
        "source_locator": "requirement:qualification:7",
        "recommended_action": "Demander une preuve de qualification valide.",
    }


class _CapabilityService:
    def __init__(self, *, propose_error=None, gap_error=None, read_error=None):
        self.propose_error = propose_error
        self.gap_error = gap_error
        self.read_error = read_error
        self.candidate_calls = 0
        self.candidate_kwargs = None
        self.propose_calls = 0
        self.gap_calls = 0

    def propose_capability(self, **kwargs):
        self.propose_calls += 1
        if self.propose_error is not None:
            raise self.propose_error
        return _result(
            replayed=self.propose_calls > 1,
            result_code="CAPABILITY_PROPOSAL_CREATED",
        )

    def report_gap(self, **kwargs):
        self.gap_calls += 1
        if self.gap_error is not None:
            raise self.gap_error
        return _result(
            replayed=self.gap_calls > 1,
            result_code="CAPABILITY_GAP_REPORTED",
        )

    def read_candidates(self, **kwargs):
        from datetime import UTC, datetime

        self.candidate_calls += 1
        self.candidate_kwargs = kwargs
        return (
            SimpleNamespace(
                capability_id=uuid4(),
                capability_kind="EQUIPMENT",
                name="Fixture means",
                version_id=uuid4(),
                version_number=1,
                title="Fixture version",
                valid_from=datetime(2026, 8, 1, tzinfo=UTC),
                valid_until=None,
                validity_state="CURRENT",
                source_evidence_state="UNKNOWN",
                evaluated_at=datetime(2026, 10, 8, 9, tzinfo=UTC),
            ),
        )

    def read_assessments(self, **kwargs):
        if self.read_error is not None:
            raise self.read_error
        case_id = kwargs["case_id"]
        assignment_id = kwargs["assignment_id"]
        proposal = SimpleNamespace(
            proposal_id=uuid4(),
            case_id=case_id,
            assignment_id=assignment_id,
            capability_id=uuid4(),
            capability_version_id=uuid4(),
            requirement_id=uuid4(),
            task_id=uuid4(),
            state="PROPOSED",
            validity_state="CURRENT",
            justification="Référence pertinente.",
            source_locator="reference:42",
        )
        gap = SimpleNamespace(
            gap_id=uuid4(),
            case_id=case_id,
            assignment_id=assignment_id,
            capability_id=None,
            requirement_id=uuid4(),
            task_id=None,
            gap_kind="MISSING",
            severity="BLOCKING",
            reason="Preuve absente.",
            source_locator="requirement:7",
            recommended_action="Collecter la preuve.",
        )
        return SimpleNamespace(proposals=[proposal], gaps=[gap])


def _headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.mark.parametrize("authorization", [None, "Basic test-token", "Bearer"])
def test_collaborator_capability_routes_reject_missing_or_malformed_bearer(authorization):
    client = _client()
    headers = {} if authorization is None else {"Authorization": authorization}

    response = client.post(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-proposals",
        json=_proposal_payload(),
        headers=headers,
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "UNAUTHENTICATED"}


def test_collaborator_capability_routes_map_invalid_context_to_401():
    client = _client(resolver_error=UnauthenticatedError())

    response = client.get(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-assessments",
        params={"assignment_id": str(uuid4())},
        headers=_headers(),
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "UNAUTHENTICATED"}


def test_propose_capability_returns_201_then_200_on_replay():
    service = cast(Any, _CapabilityService())
    client = _client(service=service)
    case_id = uuid4()
    payload = _proposal_payload()

    first = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-proposals",
        json=payload,
        headers=_headers(),
    )
    replay = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-proposals",
        json=payload,
        headers=_headers(),
    )

    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["result_code"] == "CAPABILITY_PROPOSAL_CREATED"
    assert replay.json()["replayed"] is True


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    [
        (PermissionError("ASSIGNMENT_REQUIRED"), 403, "FORBIDDEN"),
        (IdempotencyKeyReusedError("reused"), 409, "IDEMPOTENCY_CONFLICT"),
        (CommandInProgressError("running"), 409, "IDEMPOTENCY_CONFLICT"),
        (CommandExecutionError("NOT_FOUND_OR_FORBIDDEN"), 404, "NOT_FOUND_OR_FORBIDDEN"),
        (CommandExecutionError("SCOPE_DENIED"), 403, "FORBIDDEN"),
        (CommandExecutionError("ASSIGNMENT_REQUIRED"), 403, "FORBIDDEN"),
        (
            CommandExecutionError("CAPABILITY_PROPOSAL_ALREADY_EXISTS"),
            409,
            "CAPABILITY_PROPOSAL_ALREADY_EXISTS",
        ),
        (CommandExecutionError("INVALID_CAPABILITY"), 422, "COMMAND_REJECTED"),
    ],
)
def test_propose_capability_maps_service_errors(error, status_code, detail):
    client = _client(service=_CapabilityService(propose_error=error))

    response = client.post(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-proposals",
        json=_proposal_payload(),
        headers=_headers(),
    )

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def test_report_gap_returns_201_then_200_on_replay():
    service = cast(Any, _CapabilityService())
    client = _client(service=service)
    case_id = uuid4()
    payload = _gap_payload()

    first = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-gaps",
        json=payload,
        headers=_headers(),
    )
    replay = client.post(
        f"/api/v1/collaborator/cases/{case_id}/capability-gaps",
        json=payload,
        headers=_headers(),
    )

    assert first.status_code == 201
    assert replay.status_code == 200
    assert first.json()["result_code"] == "CAPABILITY_GAP_REPORTED"
    assert replay.json()["replayed"] is True


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    [
        (PermissionError("PATRON_REQUIRED"), 403, "FORBIDDEN"),
        (IdempotencyKeyReusedError("reused"), 409, "IDEMPOTENCY_CONFLICT"),
        (CommandInProgressError("running"), 409, "IDEMPOTENCY_CONFLICT"),
        (CommandExecutionError("NOT_FOUND_OR_FORBIDDEN"), 404, "NOT_FOUND_OR_FORBIDDEN"),
        (CommandExecutionError("SCOPE_DENIED"), 403, "FORBIDDEN"),
        (CommandExecutionError("ASSIGNMENT_REQUIRED"), 403, "FORBIDDEN"),
        (
            CommandExecutionError("CAPABILITY_GAP_ALREADY_REPORTED"),
            409,
            "CAPABILITY_GAP_ALREADY_REPORTED",
        ),
        (CommandExecutionError("INVALID_GAP"), 422, "COMMAND_REJECTED"),
    ],
)
def test_report_gap_maps_service_errors(error, status_code, detail):
    client = _client(service=_CapabilityService(gap_error=error))

    response = client.post(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-gaps",
        json=_gap_payload(),
        headers=_headers(),
    )

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def test_read_assessments_returns_proposals_and_gaps_without_financial_fields():
    case_id = uuid4()
    response = _client().get(
        f"/api/v1/collaborator/cases/{case_id}/capability-assessments",
        params={"assignment_id": str(uuid4())},
        headers=_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["proposals"][0]["state"] == "PROPOSED"
    assert body["gaps"][0]["severity"] == "BLOCKING"
    assert "sales_total_minor" not in body
    assert "gross_margin_minor" not in body
    assert "total_cost_minor" not in body


@pytest.mark.parametrize(
    ("error", "status_code", "detail"),
    [
        (PermissionError("ASSIGNMENT_REQUIRED"), 403, "FORBIDDEN"),
        (CommandExecutionError("NOT_FOUND_OR_FORBIDDEN"), 404, "NOT_FOUND_OR_FORBIDDEN"),
        (CommandExecutionError("SCOPE_DENIED"), 403, "FORBIDDEN"),
    ],
)
def test_read_assessments_maps_service_errors(error, status_code, detail):
    client = _client(service=_CapabilityService(read_error=error))

    response = client.get(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-assessments",
        params={"assignment_id": str(uuid4())},
        headers=_headers(),
    )

    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


def test_collaborator_payload_rejects_financial_fields():
    response = _client().post(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-gaps",
        json={**_gap_payload(), "gross_margin_minor": 100},
        headers=_headers(),
    )

    assert response.status_code == 422


def test_legacy_assessment_stays_unknown_and_no_store():
    response = _client().get(
        f"/api/v1/collaborator/cases/{uuid4()}/capability-assessments",
        params={"assignment_id": str(uuid4())},
        headers=_headers(),
    )
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store"
    assert response.json()["proposals"][0]["source_evidence_state"] == "UNKNOWN"
    assert response.json()["proposals"][0]["source_evidence_evaluated_at"] is None


def test_case_only_read_accepts_omitted_assignment_without_cache() -> None:
    from unittest.mock import Mock

    service = Mock()
    service.read_assessments.return_value = SimpleNamespace(proposals=[], gaps=[])
    case_id = uuid4()
    response = _client(service=service).get(
        f"/api/v1/collaborator/cases/{case_id}/capability-assessments", headers=_headers()
    )
    assert response.status_code == 200
    assert response.json() == {"proposals": [], "gaps": []}
    assert response.headers["Cache-Control"] == "no-store"
    assert service.read_assessments.call_args.kwargs["assignment_id"] is None


def test_capability_act_ids_are_stable_within_but_distinct_between_tenants() -> None:
    tenant_a, tenant_b, case_id = uuid4(), uuid4(), uuid4()
    command_id = uuid4()
    proposal = ProposeCapabilityForCaseRequest(
        command_id=command_id,
        idempotency_key=uuid4(),
        assignment_id=uuid4(),
        capability_id=uuid4(),
        capability_version_id=uuid4(),
        requirement_id=uuid4(),
        justification="Human synthetic proposal",
    )
    proposal_a = proposal.to_command(case_id=case_id, tenant_id=tenant_a)
    proposal_retry = proposal.to_command(case_id=case_id, tenant_id=tenant_a)
    proposal_b = proposal.to_command(case_id=case_id, tenant_id=tenant_b)
    assert proposal_a.proposal_id == proposal_retry.proposal_id
    assert proposal_a.proposal_id != proposal_b.proposal_id
    assert proposal_a.proposal_id == uuid5(
        NAMESPACE_URL, f"case-capability-proposal:{tenant_a}:{command_id}"
    )

    gap = ReportCapabilityGapRequest(
        command_id=command_id,
        idempotency_key=uuid4(),
        assignment_id=uuid4(),
        requirement_id=uuid4(),
        gap_kind="MISSING",
        severity="IMPORTANT",
        reason="Synthetic reason",
        recommended_action="Review source",
    )
    gap_a = gap.to_command(case_id=case_id, tenant_id=tenant_a)
    gap_retry = gap.to_command(case_id=case_id, tenant_id=tenant_a)
    gap_b = gap.to_command(case_id=case_id, tenant_id=tenant_b)
    assert gap_a.gap_id == gap_retry.gap_id
    assert gap_a.gap_id != gap_b.gap_id
    assert gap_a.gap_id == uuid5(NAMESPACE_URL, f"case-capability-gap:{tenant_a}:{command_id}")


def test_capability_candidates_resolves_case_assignment_and_uses_closed_projection() -> None:
    service = _CapabilityService()
    case_id = uuid4()
    client = _client(service=service, raise_server_exceptions=True)

    response = client.get(
        f"/api/v1/collaborator/cases/{case_id}/capability-candidates",
        headers=_headers(),
    )

    assert response.status_code == 200, response.text
    assert response.headers["Cache-Control"] == "no-store"
    assert set(response.json()[0]) == {
        "capability_id",
        "capability_kind",
        "name",
        "version_id",
        "version_number",
        "title",
        "valid_from",
        "valid_until",
        "validity_state",
        "source_evidence_state",
        "evaluated_at",
    }
    assert "assignment_id" not in response.json()[0]
    assert service.candidate_calls == 1
    assert service.candidate_kwargs is not None
    assert service.candidate_kwargs["case_id"] == case_id
