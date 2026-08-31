from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from app.modules.decision.application.ports import DecisionRiskPage
from app.modules.decision.application.risk_read import PatronDecisionRiskReadService
from app.platform.security.authorization import AuthorizationDecision
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    MembershipState,
)

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


def _actor(*, kind: ActorKind = ActorKind.PATRON_ADMIN) -> ActorContext:
    return ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=uuid4(),
        membership_id=uuid4(),
        actor_kind=kind,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset(),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=None,
        correlation_id=uuid4(),
    )


def _snapshot(**overrides: object) -> SimpleNamespace:
    return SimpleNamespace(
        id=overrides.get("id", uuid4()),
        tenant_id=overrides.get("tenant_id", uuid4()),
        case_id=overrides.get("case_id", uuid4()),
        dce_version_id=overrides.get("dce_version_id", uuid4()),
        source_fragment_id=overrides.get("source_fragment_id", uuid4()),
        risk_code=overrides.get("risk_code", "CCAP-DELAI-001"),
        category=overrides.get("category", "CCAP"),
        title=overrides.get("title", "Délai contractuel critique"),
        severity=overrides.get("severity", "HIGH"),
        likelihood=overrides.get("likelihood", "LIKELY"),
        treatment=overrides.get("treatment", "OPEN"),
        revision=overrides.get("revision", 1),
        due_at=overrides.get("due_at"),
        created_at=overrides.get("created_at", NOW),
        latest_treatment_evidence=overrides.get("latest_treatment_evidence"),
    )


class _FakeReader:
    def __init__(self, page: DecisionRiskPage | None = None) -> None:
        self.calls: list[dict[str, object]] = []
        self.page = page or DecisionRiskPage(items=(), next_cursor=None)

    def list_for_case(
        self,
        *,
        session: object,
        tenant_id: UUID,
        case_id: UUID,
        limit: int,
        after_created_at: datetime | None,
        after_id: UUID | None,
    ) -> DecisionRiskPage:
        self.calls.append(
            {
                "session": session,
                "tenant_id": tenant_id,
                "case_id": case_id,
                "limit": limit,
                "after_created_at": after_created_at,
                "after_id": after_id,
            }
        )
        return self.page


class _AllowPolicy:
    def authorize(self, **kwargs: object) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=True,
            code="ALLOWED",
            http_status_code=200,
            reason=None,
        )


class _DenyPolicy:
    def __init__(self, code: str = "AUTHORIZATION_DENIED") -> None:
        self._code = code

    def authorize(self, **kwargs: object) -> AuthorizationDecision:
        return AuthorizationDecision(
            allowed=False,
            code=self._code,
            http_status_code=403,
            reason=None,
        )


def _service(*, reader: Any = None, policy: Any = None) -> PatronDecisionRiskReadService:
    return PatronDecisionRiskReadService(
        session_factory=MagicMock(),
        reader=cast(Any, reader or _FakeReader()),
        policy=policy or _AllowPolicy(),
    )


def test_list_for_case_authorizes_and_delegates_to_reader() -> None:
    actor = _actor()
    case_id = uuid4()
    snapshot = _snapshot(case_id=case_id)
    reader = _FakeReader(page=DecisionRiskPage(items=cast(Any, (snapshot,)), next_cursor=None))
    service = _service(reader=reader)

    page = service.list_for_case(
        actor=actor,
        case_id=case_id,
        limit=25,
        cursor=None,
        now=NOW,
    )

    assert len(page.items) == 1
    assert page.items[0] is snapshot
    assert page.next_cursor is None
    assert reader.calls[0]["tenant_id"] == actor.tenant_id
    assert reader.calls[0]["case_id"] == case_id
    assert reader.calls[0]["limit"] == 25
    assert reader.calls[0]["after_created_at"] is None
    assert reader.calls[0]["after_id"] is None


def test_list_for_case_decodes_cursor_and_forwards_pagination() -> None:
    import base64

    actor = _actor()
    case_id = uuid4()
    risk_id = uuid4()
    created_at = datetime(2026, 8, 19, 10, 0, tzinfo=UTC)
    cursor = (
        base64.urlsafe_b64encode(f"{created_at.isoformat()}|{risk_id}".encode())
        .decode("ascii")
        .rstrip("=")
    )
    reader = _FakeReader()
    service = _service(reader=reader)

    service.list_for_case(
        actor=actor,
        case_id=case_id,
        limit=10,
        cursor=cursor,
        now=NOW,
    )

    assert reader.calls[0]["limit"] == 10
    assert reader.calls[0]["after_created_at"] == created_at
    assert reader.calls[0]["after_id"] == risk_id


def test_list_for_case_rejects_out_of_range_limit() -> None:
    service = _service()

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        service.list_for_case(
            actor=_actor(),
            case_id=uuid4(),
            limit=0,
            cursor=None,
            now=NOW,
        )

    with pytest.raises(ValueError, match="limit must be between 1 and 100"):
        service.list_for_case(
            actor=_actor(),
            case_id=uuid4(),
            limit=101,
            cursor=None,
            now=NOW,
        )


def test_list_for_case_rejects_non_patron() -> None:
    service = _service()

    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        service.list_for_case(
            actor=_actor(kind=ActorKind.COLLABORATEUR),
            case_id=uuid4(),
            limit=25,
            cursor=None,
            now=NOW,
        )


def test_list_for_case_rejects_policy_denial() -> None:
    service = _service(policy=_DenyPolicy(code="FORBIDDEN"))

    with pytest.raises(PermissionError, match="FORBIDDEN"):
        service.list_for_case(
            actor=_actor(),
            case_id=uuid4(),
            limit=25,
            cursor=None,
            now=NOW,
        )
