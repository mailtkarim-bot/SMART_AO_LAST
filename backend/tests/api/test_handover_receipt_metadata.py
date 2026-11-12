"""HTTP envelope serialization only; native workflow verifies permissions/effects."""

from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from app.interfaces.http.routes.case_handover import build_case_handover_routers
from app.modules.patron_action.application.handover_queries import CaseHandoverSnapshotProjection
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.api.test_preparation_routes import _headers, _runtime


def client(service):
    app = FastAPI()
    for router in build_case_handover_routers(service=service, security_runtime=_runtime()):
        app.include_router(router)
    return TestClient(app)


@pytest.mark.parametrize("receive", [False, True])
def test_handover_response_returns_stored_receipt_metadata_not_request_echo(receive):
    original, requested, key = uuid4(), uuid4(), uuid4()
    result = SimpleNamespace(
        status="SUCCEEDED",
        result_code="CASE_HANDOVER_RECEIPT_RECORDED"
        if receive
        else "CASE_HANDOVER_SNAPSHOT_RECORDED",
        replayed=True,
        command_id=str(original),
        idempotency_key=str(key),
    )
    service = SimpleNamespace(
        record=Mock(return_value=result), acknowledge=Mock(return_value=result)
    )
    body: dict[str, object] = dict(
        command_id=str(requested), idempotency_key=str(key), correlation_id=str(uuid4())
    )
    case = uuid4()
    if receive:
        body.update(
            receipt_id=str(uuid4()),
            expected_snapshot_revision=1,
            expected_view_sha256="a" * 64,
            receipt_kind="RECEIVED_WITH_GAPS",
            note="Dossier synthétique reçu avec manques.",
            human_confirmed=True,
        )
        path = f"/api/v1/cases/{case}/p7-handover/{uuid4()}/receipts"
    else:
        body.update(
            snapshot_id=str(uuid4()), outcome_id=str(uuid4()), submission_package_id=str(uuid4())
        )
        path = f"/api/v1/patron/cases/{case}/p7-handover"
    with client(service) as http:
        response = http.post(path, headers=_headers(), json=body)
    assert response.status_code == 200, response.text
    assert response.json()["command_id"] == str(original) != str(requested)
    assert response.json()["idempotency_key"] == str(key)
    assert response.headers.get("cache-control") == "no-store"


@pytest.mark.parametrize("kind", ["list", "exact", "history", "options"])
def test_handover_successful_reads_are_not_cached(kind):
    identifier, case = uuid4(), uuid4()
    row = CaseHandoverSnapshotProjection(
        id=identifier,
        outcome_id=uuid4(),
        lot_reference="1",
        submission_package_id=uuid4(),
        package_version=1,
        manifest_sha256="a" * 64,
        revision=1,
        created_at=datetime.now(UTC),
        snapshot_json={},
    )
    service = SimpleNamespace(
        read=Mock(return_value=(row,)),
        read_exact=Mock(return_value=row),
        history=Mock(return_value=(row,)),
        list_offer_options=Mock(return_value=()),
    )
    path = f"/api/v1/cases/{case}/p7-handover"
    if kind == "exact":
        path += f"/{identifier}"
    elif kind == "history":
        path += "/history"
    elif kind == "options":
        path = f"/api/v1/patron/cases/{case}/p7-handover-options"
    with client(service) as http:
        response = http.get(path, headers=_headers())
    assert response.status_code == 200, response.text
    assert response.headers.get("cache-control") == "no-store"
