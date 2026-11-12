"""Complete native financial workflow, synthetic multi-lot workbook only."""

from hashlib import sha256
from typing import Any, cast
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_pricing_import import build_patron_pricing_import_router
from app.modules.pricing.application.import_preview import PricingImportPreviewService
from app.modules.pricing.application.import_read import PricingImportReadService
from app.modules.pricing.infrastructure.import_reader import SqlAlchemyImportPreviewReader
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    PricingImportBatchRecord,
)
from app.platform.security.authorization import AuthorizationPolicy
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.application.test_financial_report_draft_lines import _seed_draft
from tests.application.test_pricing_import_commit import _command
from tests.application.test_pricing_import_commit import _service as commit_service
from tests.application.test_pricing_import_creation import _service as creation_service
from tests.application.test_pricing_workbook_completeness import HEADERS, workbook_payload


@pytest.fixture
def workflow(session_factory):
    actor, case, report, _ = _seed_draft(session_factory)

    class Resolver:
        def resolve(self, *, access_token):
            assert access_token == "synthetic"
            return actor

    app = FastAPI()
    app.include_router(
        build_patron_pricing_import_router(
            service=PricingImportPreviewService(policy=AuthorizationPolicy()),
            creation_service=creation_service(session_factory),
            read_service=PricingImportReadService(
                reader=SqlAlchemyImportPreviewReader(session_factory), policy=AuthorizationPolicy()
            ),
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=cast(Any, Resolver()), policy=AuthorizationPolicy()
            ),
        )
    )
    client = TestClient(app)
    return client, actor, case, report


def upload(client, case, payload):
    return client.post(
        f"/api/v1/patron/cases/{case}/pricing-import/preview",
        files={
            "upload": (
                "lots.xlsx",
                payload,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers={
            "Authorization": "Bearer synthetic",
            "X-Command-Id": str(uuid4()),
            "Idempotency-Key": str(uuid4()),
        },
    )


def test_workbook_preview_sources_survive_roundtrip_and_single_commit(session_factory, workflow):
    client, actor, case, report = workflow
    payload = workbook_payload(
        [
            ("Lot 1", [HEADERS, ["A", "Terrassement", 2, 10]]),
            ("Lot 2", [HEADERS, ["B", "Fondations", 3, 20]]),
        ]
    )
    response = upload(client, case, payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["row_count"] == 2 and data["total_minor"] == 8000
    assert data["rows"][0].get("source_locator") == dict(
        sheet="Lot 1",
        row=2,
        cells={"code": "A2", "designation": "B2", "quantity": "C2", "unit_price": "D2"},
    )
    batch = data["batch_id"]
    fetched = client.get(
        f"/api/v1/patron/cases/{case}/pricing-import/{batch}",
        headers={"Authorization": "Bearer synthetic"},
    )
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["rows"] == data["rows"]
    assert "source_sha256" not in fetched.json()
    with session_factory() as session:
        stored = session.scalar(
            sa.select(PricingImportBatchRecord).where(
                PricingImportBatchRecord.tenant_id == actor.tenant_id,
                PricingImportBatchRecord.id == batch,
            )
        )
        assert stored.source_sha256 == sha256(payload).hexdigest()
    command = _command(case, report, batch)
    service = commit_service(session_factory)
    from tests.application.test_financial_report_draft_lines import NOW

    first = service.commit(actor=actor, command=command, now=NOW)
    second = service.commit(actor=actor, command=command, now=NOW)
    assert not first.replayed and second.replayed
    with session_factory() as s:
        lines = list(
            s.scalars(
                sa.select(FinancialReportLineRecord).where(
                    FinancialReportLineRecord.snapshot_id == report
                )
            )
        )
        assert len(lines) == 2 and sum(x.amount_minor for x in lines) == 8000


def test_truncated_workbook_is_never_persisted_as_committable(
    session_factory, workflow, monkeypatch
):
    import app.modules.pricing.application.import_preview as module

    client, actor, case, _ = workflow
    monkeypatch.setattr(module, "MAX_ROWS", 1)
    payload = workbook_payload([("Lot", [HEADERS, ["A", "Un", 1, 10], ["B", "Deux", 2, 20]])])
    response = upload(client, case, payload)
    assert response.status_code == 422
    with session_factory() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(PricingImportBatchRecord)
                .where(PricingImportBatchRecord.tenant_id == actor.tenant_id)
            )
            == 0
        )
