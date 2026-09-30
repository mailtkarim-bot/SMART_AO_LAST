# ruff: noqa: E501
from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

from app.interfaces.http.routes.patron_actions import build_patron_action_router
from app.modules.patron_action.application.case_interview_handler import CaseInterviewService
from app.modules.patron_action.public.contracts import RecordCaseInterviewRequest
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def resolve(self, *, access_token: str): return _actor()

class Dispatcher:
    def dispatch(self, *, command, context): return SimpleNamespace(command_id=str(command.command_id), idempotency_key=str(command.idempotency_key), result_code="CASE_INTERVIEW_RECORDED", aggregate_refs=[], event_ids=[], replayed=False)

class Policy:
    def authorize(self, *, context, request): return SimpleNamespace(allowed=True)

class Service(CaseInterviewService):
    def __init__(self): pass
    def record_interview(self, *, actor, command, now): return Dispatcher().dispatch(command=command, context=None)
    def list_interviews(self, *, actor, case_id, now): return ()

def _actor() -> ActorContext:
    actor_id = uuid4(); now = datetime.now(tz=UTC)
    return ActorContext(actor_id=actor_id, identity_id=actor_id, tenant_id=uuid4(), membership_id=uuid4(), actor_kind=ActorKind.PATRON_ADMIN, membership_state=MembershipState.ACTIVE, capabilities=frozenset(), assigned_case_ids=frozenset(), session_id=uuid4(), authenticated_at=now, mfa_verified_at=now, correlation_id=uuid4())

def test_patron_can_declare_a_case_interview() -> None:
    router = build_patron_action_router(
        service=object(), transition_service=object(), outcome_service=object(), order_service=object(),
        interview_service=Service(), security_runtime=SimpleNamespace(context_resolver=Resolver()),
    )
    route = next(r for r in router.routes if getattr(r, "path", "").endswith("/interviews") and "POST" in r.methods)
    case_id = uuid4()
    response = route.endpoint(case_id, RecordCaseInterviewRequest(command_id=uuid4(), idempotency_key=uuid4(), interview_id=uuid4(), case_id=case_id, held_on=date(2026, 9, 30), source_locator="entretien://comite/1", rationale="Revue des enseignements", expires_on=date(2027, 3, 30)), authorization="Bearer token")
    assert response.status_code == 201
