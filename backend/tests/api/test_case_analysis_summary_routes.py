from dataclasses import replace
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.platform.security.context import ActorKind
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.api.test_case_dce_reading_routes import _Decision, _Policy, _Resolver


def client(role=ActorKind.PATRON_ADMIN, allowed=True):
    from app.interfaces.http.routes.case_analysis_summary import build_case_analysis_summary_router
    from app.modules.case.application.analysis_summary import build_analysis_summary

    actor = replace(_Resolver().resolve(access_token="test-token"), actor_kind=role)
    case = uuid4()
    policy = _Policy(_Decision(allowed))
    calls = []

    def read(**kw):
        calls.append(kw)
        return build_analysis_summary(
            case_id=case,
            dce_version_id=uuid4(),
            case_scope_kind="SINGLE_LOT",
            requirements=(),
            risks=(),
            coverage=None,
            truncated=False,
        )

    runtime = SimpleNamespace(
        get_case_tenant_id=lambda **kw: actor.tenant_id, get_case_analysis_summary=read
    )
    security = ConsultationSecurityRuntime(
        context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kw: actor)), policy=policy
    )
    app = FastAPI()
    app.include_router(
        build_case_analysis_summary_router(runtime=runtime, security_runtime=security)
    )
    return TestClient(app), case, policy, calls


def test_patron_summary_requires_all_existing_analysis_and_financial_capabilities():
    c, case, policy, calls = client()
    result = c.get(
        f"/api/v1/cases/{case}/analysis-summary", headers={"Authorization": "Bearer test-token"}
    )
    assert result.status_code == 200 and len(result.json()["axes"]) == 12
    assert len(policy.calls) == 6 and len(calls) == 1
    assert all(set(call) == {"context", "request"} for call in policy.calls)
    assert {x["request"].action.value for x in policy.calls} == {
        "case.dce.read",
        "decision.risk.read",
        "patron.action.read",
        "decision.finalize",
        "pricing.read",
        "financial.report.read",
    }
    assert not result.json()["analysis_complete"]


@pytest.mark.parametrize("role", [ActorKind.COLLABORATEUR, ActorKind.SYSTEM])
def test_non_patron_never_reads_or_observes_risk_counts(role):
    c, case, policy, calls = client(role=role)
    result = c.get(
        f"/api/v1/cases/{case}/analysis-summary", headers={"Authorization": "Bearer test-token"}
    )
    assert result.status_code == 403 and not calls and not policy.calls
    assert result.json() == {"detail": "FORBIDDEN"}


def test_denied_capability_and_missing_auth_do_not_read():
    c, case, policy, calls = client(allowed=False)
    assert c.get(f"/api/v1/cases/{case}/analysis-summary").status_code == 401
    assert (
        c.get(
            f"/api/v1/cases/{case}/analysis-summary", headers={"Authorization": "Bearer test-token"}
        ).status_code
        == 403
    )
    assert not calls
