from __future__ import annotations

import json
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_business_method_profiles import (
    build_patron_business_method_profile_router,
)
from app.modules.enterprise.application.business_method_profile_handler import (
    BusinessMethodProfileAdoptionProjection,
    BusinessMethodProfileVersionProjection,
)
from app.modules.enterprise.public.business_method_profile_contracts import (
    AdoptBusinessMethodProfileRequest,
    BusinessMethodProfileContent,
    PublishBusinessMethodProfileRequest,
)
from app.platform.security.authorization import AuthorizationPolicyPort
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import HTTPException
from fastapi.routing import APIRoute

NOW = datetime(2026, 10, 1, 12, tzinfo=UTC)


class _Resolver:
    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "profile-test-token"
        actor_id = uuid4()
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
            authenticated_at=NOW,
            mfa_verified_at=NOW,
            correlation_id=uuid4(),
        )


class _Service:
    def publish(self, *, actor, command, now):
        self.company_id = command.company_id
        self.profile = command.profile
        return _result(replayed=getattr(self, "replay", False))

    def versions(self, *, actor, company_id, now):
        return (
            BusinessMethodProfileVersionProjection(
                profile_version_id=uuid4(),
                version=1,
                schema_version=1,
                profile=BusinessMethodProfileContent().model_dump(mode="json"),
                content_sha256="a" * 64,
            ),
        )

    def adopt(self, *, actor, command, now):
        self.case_id = command.case_id
        return _result(replayed=getattr(self, "replay", False))

    def current_adoption(self, *, actor, case_id, now):
        return BusinessMethodProfileAdoptionProjection(
            adoption_id=uuid4(),
            case_id=case_id,
            adoption_revision=1,
            profile_version_id=uuid4(),
            profile_version=1,
            profile_content_sha256="a" * 64,
        )


def _result(*, replayed: bool = False):
    return SimpleNamespace(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        result_code="BUSINESS_METHOD_PROFILE_PUBLISHED",
        aggregate_refs=[{"aggregate_id": str(uuid4()), "aggregate_revision": 1}],
        event_ids=[uuid4()],
        replayed=replayed,
    )


def _routes(service):
    router = build_patron_business_method_profile_router(
        service=cast(object, service),
        security_runtime=ConsultationSecurityRuntime(
            context_resolver=cast(object, _Resolver()),
            policy=cast(AuthorizationPolicyPort, object()),
        ),
    )
    return {route.name: route for route in router.routes if isinstance(route, APIRoute)}


def test_profile_endpoints_publish_replay_read_and_adopt_exact_versions() -> None:
    service = _Service()
    routes = _routes(service)
    authorization = "Bearer profile-test-token"
    company_id, case_id = uuid4(), uuid4()
    publish = routes["publish_profile"].endpoint
    publish_request = PublishBusinessMethodProfileRequest.model_validate(
        {
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "expected_version": 0,
            "profile": {"terminology": {"lot": "Zone travaux"}},
        }
    )
    response = publish(company_id, publish_request, authorization)
    assert response.status_code == 201
    assert service.company_id == company_id
    assert service.profile.terminology == {"lot": "Zone travaux"}

    service.replay = True
    replay = publish(company_id, publish_request, authorization)
    assert replay.status_code == 200
    assert json.loads(replay.body)["replayed"] is True

    listed = routes["list_profile_versions"].endpoint(company_id, authorization)
    assert listed.versions[0].content_sha256 == "a" * 64

    service.replay = False
    adopt_request = AdoptBusinessMethodProfileRequest.model_validate(
        {
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "expected_adoption_revision": 0,
            "profile_version_id": uuid4(),
            "profile_version": 1,
            "profile_content_sha256": "a" * 64,
        }
    )
    adopted = routes["adopt_profile"].endpoint(case_id, adopt_request, authorization)
    assert adopted.status_code == 201
    assert service.case_id == case_id
    assert routes["get_current_adoption"].endpoint(case_id, authorization).case_id == case_id


def test_profile_endpoint_requires_bearer_and_rejects_configuration_overrides() -> None:
    routes = _routes(_Service())
    request = PublishBusinessMethodProfileRequest.model_validate(
        {
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "expected_version": 0,
            "profile": {},
        }
    )
    with pytest.raises(HTTPException) as error:
        routes["publish_profile"].endpoint(uuid4(), request, None)
    assert error.value.status_code == 401

    with pytest.raises(ValueError):
        BusinessMethodProfileContent.model_validate(
            {
                "additional_checks": [
                    {
                        "key": "override_go",
                        "label": "Forcer P3",
                        "axis": "COST",
                        "required": True,
                    }
                ]
            }
        )
