from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from app.interfaces.http.routes.case_partners import build_case_partner_router
from app.modules.partner.public.contracts import (
    CasePartnerEventResponse,
    DeclareCasePartnerEngagementRequest,
    RecordCasePartnerReceiptRequest,
    RecordCasePartnerRequestRequest,
)
from app.platform.events.dispatcher import CommandExecutionError
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException
from pydantic import ValidationError


class Resolver:
    def resolve(self, *, access_token: str):
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


class PartnerService:
    def __init__(self, *, error: Exception | None = None):
        self.error = error
        self.commands: list[Any] = []

    def _write(self, command, result_code):
        if self.error is not None:
            raise self.error
        self.commands.append(command)
        return SimpleNamespace(
            replayed=False,
            result_code=result_code,
            aggregate_refs=[],
            event_ids=[str(command.event_id)],
        )

    def record_request(self, *, actor, command, now):
        return self._write(command, "CASE_PARTNER_REQUESTED_RECORDED")

    def record_receipt(self, *, actor, command, now):
        return self._write(command, "CASE_PARTNER_RECEIVED_RECORDED")

    def declare_engagement(self, *, actor, command, now):
        return self._write(command, "CASE_PARTNER_ENGAGEMENT_DECLARED_RECORDED")

    def list_for_case(self, *, actor, case_id, now):
        return SimpleNamespace(
            case_id=case_id,
            events=(),
            can_request=True,
            can_receive=True,
            can_declare_engagement=False,
        )


def _router(service):
    return build_case_partner_router(
        service=service,
        security_runtime=SimpleNamespace(context_resolver=Resolver()),
    )


def _request(case_id):
    return RecordCasePartnerRequestRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=uuid4(),
        case_id=case_id,
        expected_revision=0,
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="communication://demande/1",
        rationale="Demande déclarée, sans envoi SmartAO.",
    )


def test_case_partner_request_path_is_scoped_and_request_does_not_send_externally() -> None:
    service = PartnerService()
    route = next(
        route
        for route in _router(service).routes
        if route.path.endswith("/partners/requests") and "POST" in route.methods
    )
    case_id = uuid4()

    response = route.endpoint(case_id, _request(case_id), authorization="Bearer test")

    assert response.status_code == 201
    assert b"CASE_PARTNER_REQUESTED_RECORDED" in response.body
    assert service.commands[0].expected_revision == 0
    with pytest.raises(HTTPException) as mismatch:
        route.endpoint(uuid4(), _request(case_id), authorization="Bearer test")
    assert mismatch.value.status_code == 422


def test_partner_receipt_preserves_unknown_exclusions_and_mandate_states() -> None:
    case_id = uuid4()
    request = RecordCasePartnerReceiptRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=uuid4(),
        case_id=case_id,
        expected_revision=0,
        request_event_id=None,
        partner_kind="CO_CONTRACTOR",
        partner_label="Groupement déclaré",
        source_locator="offer://received/1",
        rationale="Offre reçue.",
        valid_until=None,
        exclusions_state="UNKNOWN",
        exclusions=[],
        mandate_state="RECEIVED",
        mandate_source_locator="mandate://received/1",
    )
    service = PartnerService()
    route = next(
        route
        for route in _router(service).routes
        if route.path.endswith("/partners/receipts") and "POST" in route.methods
    )

    response = route.endpoint(case_id, request, authorization="Bearer test")

    assert response.status_code == 201
    assert service.commands[0].exclusions_state == "UNKNOWN"
    assert service.commands[0].mandate_state == "RECEIVED"
    assert b"ENGAGEMENT_DECLARED" not in response.body


def test_partner_engagement_is_a_separate_human_act_and_conflicts_are_not_success() -> None:
    case_id = uuid4()
    request = DeclareCasePartnerEngagementRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=uuid4(),
        case_id=case_id,
        expected_revision=2,
        receipt_event_id=uuid4(),
        source_locator="agreement://signed/1",
        rationale="Le Patron déclare cet engagement documenté.",
    )
    route = next(
        route
        for route in _router(PartnerService()).routes
        if route.path.endswith("/partners/engagements") and "POST" in route.methods
    )

    response = route.endpoint(case_id, request, authorization="Bearer test")

    assert response.status_code == 201
    assert b"CASE_PARTNER_ENGAGEMENT_DECLARED_RECORDED" in response.body
    conflict_route = next(
        route
        for route in _router(
            PartnerService(error=CommandExecutionError("PARTNER_VERSION_CONFLICT"))
        ).routes
        if route.path.endswith("/partners/engagements") and "POST" in route.methods
    )
    with pytest.raises(HTTPException) as conflict:
        conflict_route.endpoint(case_id, request, authorization="Bearer test")
    assert conflict.value.status_code == 409


def test_partner_events_read_returns_server_granted_actions_and_rejects_extra_source_snapshot():
    router = _router(PartnerService())
    route = next(
        route
        for route in router.routes
        if route.path.endswith("/{case_id}/partners") and "GET" in route.methods
    )
    result = route.endpoint(uuid4(), authorization="Bearer test")
    assert result.can_request is True
    assert result.can_receive is True
    assert result.can_declare_engagement is False

    payload = _request(uuid4()).model_dump()
    payload["source_snapshot"] = {"received": True}
    with pytest.raises(ValidationError):
        RecordCasePartnerRequestRequest.model_validate(payload)


def test_c09_contract_contains_no_financial_amount_fields():
    assert "amount_as_declared" not in CasePartnerEventResponse.model_fields
    assert "currency_code" not in CasePartnerEventResponse.model_fields
