from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from app.modules.pricing.application.transition_commands import TransitionPricingScenarioCommand
from app.modules.pricing.application.transition_service import PricingScenarioTransitionService
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.context import ActorContext, ActorKind, MembershipState

NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


class _Reader:
    def __init__(self, scenario_id=None):
        self.scenario_id = scenario_id

    def list_for_case(self, *, tenant_id, case_id):
        return (SimpleNamespace(scenario_id=self.scenario_id, case_id=case_id),)


class _Dispatcher:
    def __init__(self):
        self.calls = []

    def dispatch(self, *, command, context):
        self.calls.append((command, context))
        return SimpleNamespace(replayed=False)


class _Policy:
    def authorize(self, *, context, request):
        return SimpleNamespace(allowed=True, code="ALLOWED")


def _actor() -> ActorContext:
    return ActorContext(
        tenant_id=uuid4(),
        actor_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        identity_id=uuid4(),
        membership_id=uuid4(),
        session_id=uuid4(),
        correlation_id=uuid4(),
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
    )


def test_transition_facade_dispatches_without_session_factory() -> None:
    dispatcher = _Dispatcher()
    reader = _Reader()
    service = PricingScenarioTransitionService(
        reader=reader,
        dispatcher=cast(CommandDispatcher, dispatcher),
        policy=_Policy(),
    )
    command = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        transition_id=uuid4(),
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )

    reader.scenario_id = command.scenario_id
    case_id = uuid4()
    result = service.execute(actor=_actor(), case_id=case_id, command=command, now=NOW)

    assert result.replayed is False
    assert dispatcher.calls[0][0] is command
    assert dispatcher.calls[0][1].case_id == case_id


def test_transition_facade_rejects_non_patron_before_dispatch() -> None:
    service = PricingScenarioTransitionService(
        reader=_Reader(),
        dispatcher=cast(CommandDispatcher, _Dispatcher()),
        policy=_Policy(),
    )
    command = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        scenario_id=uuid4(),
        transition_id=uuid4(),
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )

    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        service.execute(
            case_id=uuid4(),
            actor=ActorContext(
                tenant_id=uuid4(),
                actor_id=uuid4(),
                actor_kind=ActorKind.COLLABORATEUR,
                identity_id=uuid4(),
                membership_id=uuid4(),
                session_id=uuid4(),
                correlation_id=uuid4(),
                membership_state=MembershipState.ACTIVE,
                capabilities=frozenset(),
                assigned_case_ids=frozenset(),
                authenticated_at=NOW,
                mfa_verified_at=NOW,
            ),
            command=command,
            now=NOW,
        )


def test_transition_facade_refuses_before_dispatch_or_receipt_replay() -> None:
    dispatcher = _Dispatcher()
    service = PricingScenarioTransitionService(
        reader=_Reader(),
        dispatcher=cast(CommandDispatcher, dispatcher),
        policy=_Policy(),
    )
    command = TransitionPricingScenarioCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        scenario_id=uuid4(),
        transition_id=uuid4(),
        expected_version=1,
        target_state="SELECTED",
        reason_code="PATRON_SELECTED",
    )
    with pytest.raises(CommandExecutionError, match="^NOT_FOUND_OR_FORBIDDEN$"):
        service.execute(actor=_actor(), case_id=uuid4(), command=command, now=NOW)
    assert dispatcher.calls == []
