from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.modules.pricing.application.service import PricingScenarioService
from app.modules.pricing.application.transition_service import PricingScenarioTransitionService
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    DataClassification,
    MembershipState,
)

NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def test_pricing_scenario_facade_uses_reader_and_dispatcher_without_session_factory() -> None:
    tenant_id = uuid4()
    case_id = uuid4()
    scenario_id = uuid4()
    actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_id=uuid4(),
        tenant_id=tenant_id,
        actor_id=uuid4(),
        identity_id=uuid4(),
        session_id=uuid4(),
        correlation_id=uuid4(),
    )
    command = SimpleNamespace(scenario_id=scenario_id, case_id=case_id)
    reader = Mock()
    reader.list_for_case.return_value = ()
    policy = Mock()
    policy.authorize.return_value = SimpleNamespace(allowed=True)
    dispatcher = Mock()
    dispatcher.dispatch.return_value = SimpleNamespace(result_code="PRICING_SCENARIO_CREATED")
    service = PricingScenarioService(reader=reader, dispatcher=dispatcher, policy=policy)

    result = service.execute(actor=cast(ActorContext, actor), command=command, now=NOW)
    scenarios = service.list_for_case(actor=cast(ActorContext, actor), case_id=case_id, now=NOW)

    assert result.result_code == "PRICING_SCENARIO_CREATED"
    assert scenarios == ()
    reader.list_for_case.assert_called_once_with(tenant_id=tenant_id, case_id=case_id)
    dispatcher.dispatch.assert_called_once()
    requests = [call.kwargs["request"] for call in policy.authorize.call_args_list]
    assert [request.action for request in requests] == [
        Capability.PRICING_WRITE,
        Capability.PRICING_READ,
    ]
    assert requests[1].resource.classification is DataClassification.FINANCIAL_PRIVATE
    assert requests[1].resource.tenant_id == tenant_id
    assert requests[1].resource.case_id == case_id
    assert requests[1].evaluated_at == NOW


@pytest.mark.parametrize("service_type", [PricingScenarioService, PricingScenarioTransitionService])
@pytest.mark.parametrize("code", ["AUTHORIZATION_DENIED", "STEP_UP_REQUIRED"])
def test_pricing_read_denied_before_reader(code: str, service_type) -> None:
    actor = cast(
        ActorContext,
        SimpleNamespace(
            actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=uuid4()
        ),
    )
    reader = Mock()
    policy = Mock()
    policy.authorize.return_value = SimpleNamespace(allowed=False, code=code)
    service = service_type(reader=reader, dispatcher=Mock(), policy=policy)
    with pytest.raises(PermissionError, match=code):
        service.list_for_case(actor=actor, case_id=uuid4(), now=NOW)
    reader.list_for_case.assert_not_called()


@pytest.mark.parametrize("change", ["missing_capability", "suspended", "delegate", "collaborator"])
def test_pricing_read_real_policy_refuses_before_query(change: str) -> None:
    actor = ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset({Capability.PRICING_READ}),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )
    if change == "missing_capability":
        actor = replace(actor, capabilities=frozenset())
    elif change == "suspended":
        actor = replace(actor, membership_state=MembershipState.SUSPENDED)
    else:
        actor = replace(
            actor,
            actor_kind=ActorKind.PATRON_DELEGATE
            if change == "delegate"
            else ActorKind.COLLABORATEUR,
        )
    reader = Mock()
    service = PricingScenarioService(reader=reader, dispatcher=Mock(), policy=AuthorizationPolicy())
    with pytest.raises(PermissionError):
        service.list_for_case(actor=actor, case_id=uuid4(), now=NOW)
    reader.list_for_case.assert_not_called()
