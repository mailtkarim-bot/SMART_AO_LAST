from dataclasses import dataclass
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from app.interfaces.http.routes.case_dce_reading import build_case_dce_reading_router
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.queries import CaseDceReadingAvailability
from app.modules.dce.application.source_anchor_projection import (
    DceSourceAnchorLocatorState,
    DceSourceAnchorProjection,
    DceSourceLocator,
    DceSourceLocatorKind,
)
from app.platform.security.authenticated_context import (
    AuthenticationContextResolver,
    UnauthenticatedError,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import FastAPI
from fastapi.testclient import TestClient

NOW = datetime(2026, 8, 19, 12, 0, tzinfo=UTC)


@dataclass
class _Resolver:
    error: Exception | None = None

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "test-token"
        if self.error is not None:
            raise self.error
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
            authenticated_at=NOW,
            mfa_verified_at=NOW,
            correlation_id=uuid4(),
        )


@dataclass
class _Decision:
    allowed: bool
    http_status_code: int = 403


class _Policy:
    def __init__(self, decision: _Decision):
        self.decision = decision
        self.calls: list[Any] = []

    def authorize(self, **kwargs):
        self.calls.append(kwargs)
        return self.decision


@dataclass
class _Reading:
    dce_version_id: object
    lifecycle: str
    integrity: str
    classification_readiness: str
    analysis_readiness: str
    source_received_at: datetime
    counters: object
    requirements: list[object]


@dataclass
class _Lookup:
    availability: CaseDceReadingAvailability
    reading: object | None
    case_id: object
    work_label: str
    case_lifecycle: str
    commercial_stage: str
    dce_freshness: str


class _Runtime:
    def __init__(self, *, tenant_id=None, lookup=None):
        self.tenant_id = tenant_id or uuid4()
        self.lookup = lookup
        self.tenant_calls = []
        self.reading_calls = []

    def get_case_tenant_id(self, *, case_id):
        self.tenant_calls.append(case_id)
        return self.tenant_id

    def get_case_dce_reading(self, *, tenant_id, case_id):
        self.reading_calls.append((tenant_id, case_id))
        return self.lookup


def _security(*, policy=None, resolver_error=None):
    return ConsultationSecurityRuntime(
        context_resolver=cast(AuthenticationContextResolver, _Resolver(error=resolver_error)),
        policy=policy or _Policy(_Decision(True)),
    )


def _client(*, runtime=None, policy=None, resolver_error=None):
    app = FastAPI()
    app.include_router(
        build_case_dce_reading_router(
            runtime=runtime or _Runtime(),
            security_runtime=_security(policy=policy, resolver_error=resolver_error),
        )
    )
    return TestClient(app, raise_server_exceptions=False)


def _available_lookup(case_id):
    requirement = SimpleNamespace(
        requirement_id=uuid4(),
        confirmation_revision=2,
        requirement_type="ADMINISTRATIVE",
        directive_signal="REQUIRED",
        confirmation_outcome="CONFIRMED",
        uncertainty_status="NONE",
        document_family="K_BIS",
        source_locator_label="page 2",
        source_anchor=None,
    )
    reading = _Reading(
        dce_version_id=uuid4(),
        lifecycle="REGISTERED",
        integrity="VERIFIED",
        classification_readiness="READY",
        analysis_readiness="READY",
        source_received_at=NOW,
        counters=SimpleNamespace(
            total=3, pending_human_confirmation=0, confirmed=2, review_required=1, not_applicable=0
        ),
        requirements=[requirement],
    )
    return _Lookup(
        CaseDceReadingAvailability.AVAILABLE,
        reading,
        case_id,
        "Réhabilitation école",
        "ACTIVE",
        "SUBMISSION",
        "CURRENT",
    )


def _headers():
    return {"Authorization": "Bearer test-token"}


@pytest.mark.parametrize("authorization", [None, "Basic test-token", "Bearer"])
def test_case_dce_reading_rejects_missing_or_malformed_bearer(authorization):
    client = _client()
    headers = {} if authorization is None else {"Authorization": authorization}
    response = client.get(f"/api/v1/cases/{uuid4()}/dce-reading", headers=headers)
    assert response.status_code == 401
    assert response.json() == {"detail": "UNAUTHENTICATED"}


def test_case_dce_reading_maps_invalid_context_to_401():
    response = _client(resolver_error=UnauthenticatedError()).get(
        f"/api/v1/cases/{uuid4()}/dce-reading", headers=_headers()
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "UNAUTHENTICATED"}


def test_case_dce_reading_returns_closed_projection_and_uses_server_tenant():
    case_id = uuid4()
    runtime = _Runtime(lookup=_available_lookup(case_id))
    policy = _Policy(_Decision(True))
    response = _client(runtime=runtime, policy=policy).get(
        f"/api/v1/cases/{case_id}/dce-reading", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == str(case_id)
    assert body["availability"] == "AVAILABLE"
    assert body["dce"]["integrity"] == "VERIFIED"
    assert body["counters"]["confirmed"] == 2
    assert body["requirements"][0]["source_locator_label"] == "page 2"
    assert body["requirements"][0]["source_anchor"] is None
    assert body["requirements"][0]["confirmation_revision"] == 2
    assert runtime.reading_calls[0][1] == case_id
    assert policy.calls[0]["request"].resource.tenant_id == runtime.tenant_id
    assert "gross_margin_minor" not in body


def test_case_dce_reading_exposes_typed_source_anchor_without_source_text():
    case_id = uuid4()
    lookup = _available_lookup(case_id)
    lookup.reading.requirements[0].source_anchor = DceSourceAnchorProjection(
        source_anchor_id=uuid4(),
        dce_version_id=uuid4(),
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_ordinal=2,
        source_sha256="a" * 64,
        extractor_id="smart-ao-native",
        extractor_version="2",
        fragment_sha256="b" * 64,
        locator=DceSourceLocator(
            kind=DceSourceLocatorKind.PDF_PAGE,
            coordinates={"page": 2, "part": 1},
        ),
    )

    response = _client(runtime=_Runtime(lookup=lookup)).get(
        f"/api/v1/cases/{case_id}/dce-reading", headers=_headers()
    )

    assert response.status_code == 200
    anchor = response.json()["requirements"][0]["source_anchor"]
    expected_anchor_id = lookup.reading.requirements[0].source_anchor.source_anchor_id
    assert anchor["source_anchor_id"] == str(expected_anchor_id)
    assert anchor["locator_state"] == DceSourceAnchorLocatorState.RESOLVED.value
    assert anchor["locator"] == {"kind": "pdf_page", "coordinates": {"page": 2, "part": 1}}
    assert anchor["source_sha256"] == "a" * 64
    assert anchor["fragment_sha256"] == "b" * 64
    assert set(anchor) == {
        "source_anchor_id",
        "dce_version_id",
        "dce_document_id",
        "extraction_id",
        "fragment_ordinal",
        "source_sha256",
        "extractor_id",
        "extractor_version",
        "fragment_sha256",
        "locator_state",
        "locator",
    }
    assert "source_text" not in anchor


def test_case_dce_reading_preserves_unknown_source_anchor_locator():
    case_id = uuid4()
    lookup = _available_lookup(case_id)
    lookup.reading.requirements[0].source_anchor = DceSourceAnchorProjection(
        source_anchor_id=uuid4(),
        dce_version_id=uuid4(),
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_ordinal=1,
        source_sha256="a" * 64,
        extractor_id="legacy-parser",
        extractor_version="1",
        fragment_sha256="b" * 64,
        locator=None,
    )

    response = _client(runtime=_Runtime(lookup=lookup)).get(
        f"/api/v1/cases/{case_id}/dce-reading", headers=_headers()
    )

    assert response.status_code == 200
    anchor = response.json()["requirements"][0]["source_anchor"]
    assert anchor["locator_state"] == "UNKNOWN"
    assert anchor["locator"] is None


def test_case_dce_reading_exposes_confirmed_revision_for_a1_context():
    case_id = uuid4()
    runtime = _Runtime(lookup=_available_lookup(case_id))
    router = build_case_dce_reading_router(
        runtime=runtime,
        security_runtime=_security(),
    )
    response = router.routes[0].endpoint(case_id, "Bearer test-token")
    assert response.requirements[0].confirmation_revision == 2


def test_case_dce_reading_returns_neutral_404_for_unknown_case():
    runtime = _Runtime(tenant_id=None, lookup=None)
    runtime.tenant_id = None
    response = _client(runtime=runtime).get(
        f"/api/v1/cases/{uuid4()}/dce-reading", headers=_headers()
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    assert not runtime.reading_calls


@pytest.mark.parametrize(
    ("decision", "status_code", "detail"),
    [
        (_Decision(False, 403), 403, "FORBIDDEN"),
        (_Decision(False, 404), 404, "NOT_FOUND_OR_FORBIDDEN"),
    ],
)
def test_case_dce_reading_maps_authorization_decision(decision, status_code, detail):
    response = _client(policy=_Policy(decision)).get(
        f"/api/v1/cases/{uuid4()}/dce-reading", headers=_headers()
    )
    assert response.status_code == status_code
    assert response.json() == {"detail": detail}


@pytest.mark.parametrize(
    "lookup",
    [
        None,
        _Lookup(CaseDceReadingAvailability.NO_APPLICABLE_DCE, None, uuid4(), "", "", "", ""),
        _Lookup(CaseDceReadingAvailability.AVAILABLE, None, uuid4(), "", "", "", ""),
    ],
)
def test_case_dce_reading_maps_missing_or_unavailable_projection(lookup):
    response = _client(runtime=_Runtime(lookup=lookup)).get(
        f"/api/v1/cases/{uuid4()}/dce-reading", headers=_headers()
    )
    expected = 404 if lookup is None else 422
    assert response.status_code == expected
    assert response.json() == {
        "detail": "NOT_FOUND_OR_FORBIDDEN" if lookup is None else "COMMAND_REJECTED"
    }


def test_case_reading_exposes_closed_coverage_and_rejects_complete_claim():
    from dataclasses import asdict

    from app.modules.dce.application.queries import (
        CaseDceCoverageProjection,
        CaseDceDocumentCoverage,
    )
    from app.modules.dce.public.contracts import CaseDceCoverageResponse
    from pydantic import ValidationError

    case_id, document_id = uuid4(), uuid4()
    lookup = _available_lookup(case_id)
    lookup.reading.coverage = CaseDceCoverageProjection(
        case_scope_kind="SINGLE_LOT",
        total_documents=1,
        completed_extractions=0,
        unread_documents=1,
        documents=(
            CaseDceDocumentCoverage(
                document_id=document_id,
                extraction_id=None,
                document_family="RC",
                extraction_status="NOT_STARTED",
            ),
        ),
    )
    response = _client(runtime=_Runtime(lookup=lookup)).get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(),
    )
    assert response.status_code == 200
    coverage = response.json()["coverage"]
    assert coverage["documents"][0]["document_id"] == str(document_id)
    assert coverage["analysis_complete"] is False
    assert coverage["critical_unread_documents"] is None
    payload = asdict(lookup.reading.coverage)
    payload["analysis_complete"] = True
    with pytest.raises(ValidationError):
        CaseDceCoverageResponse.model_validate(payload)


def test_case_reading_exposes_structured_candidates_without_promoting_confirmation():
    from app.modules.dce.application.requirement_values import project_rc_requirement_values

    fragment_id = uuid4()
    case_id = uuid4()
    lookup = _available_lookup(case_id)
    item = lookup.reading.requirements[0]
    item.source_anchor = DceSourceAnchorProjection(
        source_anchor_id=fragment_id,
        dce_version_id=lookup.reading.dce_version_id,
        dce_document_id=uuid4(),
        extraction_id=uuid4(),
        fragment_ordinal=1,
        source_sha256="a" * 64,
        fragment_sha256="b" * 64,
        extractor_id="synthetic",
        extractor_version="1",
        locator=DceSourceLocator(
            kind=DceSourceLocatorKind.TEXT_LINE, coordinates={"line": 1, "part": 1}
        ),
    )
    item.confirmation_outcome = "PENDING_HUMAN_CONFIRMATION"
    item.structured_candidate = project_rc_requirement_values(
        excerpt="Date limite de remise : 21/11/2034 à 10h30 pour le lot 2.",
        requirement_type="SUBMISSION_DEADLINE_SIGNAL",
        directive_signal="UNSPECIFIED",
        start_byte_offset=0,
        source_fragment_id=fragment_id,
    )
    response = _client(runtime=_Runtime(lookup=lookup)).get(
        f"/api/v1/cases/{case_id}/dce-reading", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()["requirements"][0]
    values = body.get("structured_candidate")
    assert values is not None
    assert values["date_iso"] == "2034-11-21" and values["time_local"] == "10:30"
    assert values["lot_numbers"] == [2] and values["applicability"] == "UNKNOWN"
    assert values["timezone"] is None and values["timezone_state"] == "UNKNOWN"
    assert body["confirmation_outcome"] == "PENDING_HUMAN_CONFIRMATION"
    assert "excerpt" not in values and "text" not in values
