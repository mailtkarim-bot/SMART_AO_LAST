# ruff: noqa: E501, I001
from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException

from app.interfaces.http.routes.patron_post_reception_obligations import build_patron_post_reception_obligations_router
from app.modules.pricing.public.post_reception_obligation_contracts import RecordPostReceptionObligationRequest, TransitionPostReceptionObligationRequest
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def __init__(self, actor_kind): self.actor_kind = actor_kind
    def resolve(self, *, access_token: str):
        actor_id = uuid4()
        now = datetime.now(tz=UTC)
        return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=self.actor_kind, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())


class Dispatcher:
    def __init__(self): self.command = None
    def dispatch(self, *, command, context):
        self.command = command
        return SimpleNamespace(command_id=str(command.command_id), idempotency_key=str(command.idempotency_key), result_code="POST_RECEPTION_OBLIGATION_RECORDED", replayed=False, aggregate_refs=({"aggregate_revision": getattr(command, "expected_revision", 0) + 1},))


class ReadService:
    def list_for_case(self, *, actor, case_id):
        if actor.actor_kind is not ActorKind.PATRON_ADMIN:
            raise PermissionError("PATRON_REQUIRED")
        return (SimpleNamespace(id=uuid4(), case_id=case_id, obligation_type="DOE_DIUO", summary="Remettre le DOE", source_refs_json=["ccap://clause/12"], due_date=None, resource_note=None, cost_estimate_note=None, fulfillment_proof_refs_json=[], sanction_ref=None, status="REVIEW_REQUIRED", actor_id=actor.actor_id, created_at=datetime.now(tz=UTC)),)


def test_patron_can_record_and_read_sourced_obligation():
    case_id, obligation_id = uuid4(), uuid4()
    dispatcher = Dispatcher()
    router = build_patron_post_reception_obligations_router(dispatcher=dispatcher, service=ReadService(), security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)))
    request = RecordPostReceptionObligationRequest(command_id=uuid4(), idempotency_key=uuid4(), obligation_id=obligation_id, obligation_type="DOE_DIUO", summary="Remettre le DOE", source_refs=("ccap://clause/12",), due_date=date(2027, 3, 31))
    receipt = router.routes[0].endpoint(case_id, request, authorization="Bearer token")
    listed = router.routes[1].endpoint(case_id, authorization="Bearer token")
    assert receipt.status_code == 201
    assert dispatcher.command.obligation_type == "DOE_DIUO"
    assert not hasattr(dispatcher.command, "status")
    assert listed[0].status == "REVIEW_REQUIRED"
    assert listed[0].source_refs == ["ccap://clause/12"]

def test_patron_can_record_proof_backed_obligation_transition():
    case_id, obligation_id = uuid4(), uuid4()
    dispatcher = Dispatcher()
    router = build_patron_post_reception_obligations_router(dispatcher=dispatcher, service=ReadService(), security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)))
    request = TransitionPostReceptionObligationRequest(command_id=uuid4(), idempotency_key=uuid4(), transition_id=uuid4(), expected_revision=1, resulting_status="COMPLETED", rationale="PV de levée contrôlé", evidence_refs=("document://pv-levee",))
    response = router.routes[2].endpoint(case_id, obligation_id, request, authorization="Bearer token")
    assert response.status_code == 201
    assert dispatcher.command.expected_revision == 1
    assert dispatcher.command.evidence_refs == ("document://pv-levee",)


def test_collaborator_cannot_create_post_reception_obligation():
    dispatcher = Dispatcher()
    router = build_patron_post_reception_obligations_router(dispatcher=dispatcher, service=ReadService(), security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.COLLABORATEUR)))
    request = RecordPostReceptionObligationRequest(command_id=uuid4(), idempotency_key=uuid4(), obligation_id=uuid4(), obligation_type="DOE_DIUO", summary="Remettre le DOE", source_refs=("ccap://clause/12",))
    try:
        router.routes[0].endpoint(uuid4(), request, authorization="Bearer token")
    except HTTPException as error:
        assert error.status_code == 403
    else:
        raise AssertionError("Collaborateur must be denied")
    assert dispatcher.command is None
