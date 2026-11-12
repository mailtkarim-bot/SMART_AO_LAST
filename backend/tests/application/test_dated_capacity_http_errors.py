from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_capacity import build_patron_capacity_router
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)
from app.platform.security.authorization import AuthorizationPolicy
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "error,status",
    [
        (CommandInProgressError("command receipt is already being processed"), 503),
        (CommandExecutionError("command persistence failed before commit"), 503),
        (IdempotencyKeyReusedError("idempotency key was reused with another request"), 409),
        (CommandExecutionError("CAPACITY_REVISION_CONFLICT"), 409),
        (CommandExecutionError("NOT_FOUND_OR_FORBIDDEN"), 404),
    ],
)
def test_uncertain_execution_never_becomes_editable_validation_failure(error, status):
    def fail(**kwargs):
        raise error

    app = FastAPI()
    app.include_router(
        build_patron_capacity_router(
            service=SimpleNamespace(record=fail),
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=SimpleNamespace(
                    resolve=lambda **kwargs: SimpleNamespace(mfa_verified_at=datetime.now(UTC))
                ),
                policy=AuthorizationPolicy(),
            ),
        )
    )
    response = TestClient(app).post(
        f"/api/v1/patron/cases/{uuid4()}/capacity",
        headers={"Authorization": "Bearer synthetic"},
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            run_id=str(uuid4()),
            expected_revision=0,
            context_sha256="a" * 64,
            demands=None,
            supplies=None,
            justification="Essai synthétique",
            human_confirmed=True,
        ),
    )
    assert response.status_code == status
