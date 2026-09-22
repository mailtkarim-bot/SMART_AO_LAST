from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException


def test_business_bearer_requires_mfa() -> None:
    identifier = uuid4()
    actor = ActorContext(
        actor_id=identifier,
        identity_id=identifier,
        tenant_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=datetime.now(tz=UTC),
        mfa_verified_at=None,
        correlation_id=uuid4(),
    )

    with pytest.raises(HTTPException) as raised:
        resolve_bearer_context(
            authorization="Bearer password-only",
            context_resolver=SimpleNamespace(resolve=lambda **_kwargs: actor),  # type: ignore[arg-type]
        )

    assert raised.value.status_code == 403
    assert raised.value.detail == "STEP_UP_REQUIRED"
