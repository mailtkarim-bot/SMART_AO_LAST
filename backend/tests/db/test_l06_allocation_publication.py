"""Native publication and subsequent human allocations remain distinct facts."""

from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import pytest
from tests.db.test_pricing_positions import source_setup
from tests.db.test_pricing_positions import workflow as workflow


def attach_publication(session_factory, workflow):
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_financial_reports import (
        build_patron_financial_report_router,
    )
    from app.modules.membership.application.financial_report import PatronFinancialReportService
    from app.modules.membership.application.financial_report_publication import (
        PatronFinancialReportPublicationService,
        PublishFinancialReportHandler,
    )
    from app.modules.membership.infrastructure.financial_report_reader import (
        SqlAlchemyFinancialReportReader,
    )
    from app.modules.membership.infrastructure.financial_report_snapshot_reader import (
        SqlAlchemyFinancialReportSnapshotReader,
    )
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy
    from tests.application.test_financial_report_draft_lines import _service

    client, actor, case, report = workflow
    policy = AuthorizationPolicy()
    client.app.include_router(
        build_patron_financial_report_router(
            service=PatronFinancialReportService(
                reader=SqlAlchemyFinancialReportReader(session_factory), policy=policy
            ),
            line_service=_service(session_factory),
            draft_creation_service=None,
            publication_service=PatronFinancialReportPublicationService(
                reader=SqlAlchemyFinancialReportSnapshotReader(session_factory),
                dispatcher=CommandDispatcher(
                    session_factory=session_factory,
                    handlers={"PublishFinancialReport": PublishFinancialReportHandler()},
                ),
                policy=policy,
            ),
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=SimpleNamespace(
                    resolve=lambda **kw: client.position_actor_holder.actor
                ),
                policy=policy,
            ),
        )
    )
    return f"/api/v1/patron/cases/{case}/financial-reports/{report}"


def publication_path(session_factory, workflow):
    client, actor, case, report = workflow
    report_url = attach_publication(session_factory, workflow)
    url, _, body, read, cost = source_setup(session_factory, workflow)
    headers = {"Authorization": "Bearer synthetic"}

    def allocate(index, amount, justification):
        data = read()
        row = data["positions"][index]
        source = next(c for c in data["sources"]["costs"] if c["line_id"] == cost["line_id"])
        payload = dict(
            body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            record_id=str(uuid4()),
            expected_revision=row["revision"],
            position_context_sha256=row["position_context_sha256"],
            cost_refs=[
                dict(
                    line_id=source["line_id"],
                    report_revision=source["report_revision"],
                    allocated_amount_minor=amount,
                )
            ],
            justification=justification,
        )
        endpoint = f"{url}/{row['position_id']}/reviews"
        return client.post(endpoint, json=payload, headers=headers), endpoint, payload

    previous_payloads = []
    for index, amount in enumerate(["4500", "6500"]):
        result, _, payload = allocate(index, amount, "Hypothèse initiale, transport inconnu")
        previous_payloads.append(payload)
        assert result.status_code == 201, result.text
    publication = dict(command_id=str(uuid4()), idempotency_key=str(uuid4()), expected_revision=1)
    response = client.post(report_url + "/publications", json=publication, headers=headers)
    assert response.status_code == 201, response.text
    assert (
        client.post(report_url + "/publications", json=publication, headers=headers).status_code
        == 200
    )
    published = client.get(report_url, headers=headers)
    assert published.status_code == 200, published.text
    assert published.headers["cache-control"] == "no-store"
    original = published.json()
    assert original["summary"]["direct_cost_total_minor"] == 12000
    assert original["aggregate_revision"] == 2
    invalid = read()
    assert all(
        r["state"] == "REVIEW_REQUIRED" and r["declared_cost_minor"] is None
        for r in invalid["positions"]
    )
    assert all(r["coverage_state"] == "UNKNOWN" for r in invalid["positions"])
    assert (
        next(c for c in invalid["sources"]["costs"] if c["line_id"] == cost["line_id"])[
            "allocation_summary"
        ]["state"]
        == "UNKNOWN"
    )
    stale = dict(
        previous_payloads[0],
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        record_id=str(uuid4()),
        expected_revision=1,
    )
    endpoint = f"{url}/{invalid['positions'][0]['position_id']}/reviews"
    assert client.post(endpoint, json=stale, headers=headers).status_code == 409
    for index, amount in enumerate(["5000", "7000"]):
        result, endpoint, payload = allocate(
            index,
            amount,
            "Nouvelle revue sur publication exacte, aucun accord repris; transport UNKNOWN",
        )
        assert result.status_code == 201, result.text
        assert client.post(endpoint, json=payload, headers=headers).status_code == 200
    result, _, _ = allocate(0, "5001", "Dépassement refusé")
    assert result.status_code == 422
    result, _, _ = allocate(
        0, "4000", "Répartition révisée explicitement après publication; reste non affecté"
    )
    assert result.status_code == 201, result.text
    current = read()
    assert [r["declared_cost_minor"] for r in current["positions"]] == ["4000", "7000"]
    source = next(c for c in current["sources"]["costs"] if c["line_id"] == cost["line_id"])
    assert (
        source["report_id"] == str(report)
        and source["report_revision"] == 2
        and source["report_state"] == "PUBLISHED"
    )
    assert source["allocation_summary"]["allocated_amount_minor"] == "11000"
    assert source["allocation_summary"]["remaining_amount_minor"] == "1000"
    for row in current["positions"]:
        assert row["coverage_state"] == row["applicability"] == "UNKNOWN"
        assert "TRANSPORT_UNKNOWN" in row["limitations"]
    history = client.get(
        f"{url}/{current['positions'][0]['position_id']}/history", headers=headers
    ).json()
    assert [e["snapshot"]["costs"][0]["allocated_amount_minor"] for e in history["entries"]] == [
        "4000",
        "5000",
        "4500",
    ]
    assert [e["snapshot"]["costs"][0]["report_state"] for e in history["entries"]] == [
        "PUBLISHED",
        "PUBLISHED",
        "DRAFT",
    ]
    assert client.get(report_url, headers=headers).json() == original
    return report_url, url, current


def test_allocations_revised_after_publication_require_fresh_reviews_without_double_count(
    session_factory, workflow
):
    publication_path(session_factory, workflow)


@pytest.mark.parametrize("boundary", ["role", "tenant"])
def test_published_cost_allocations_remain_private(session_factory, workflow, boundary):
    from app.platform.security.context import ActorKind

    client, actor, case, report = workflow
    report_url, url, current = publication_path(session_factory, workflow)
    client.position_actor_holder.actor = (
        replace(actor, actor_kind=ActorKind.COLLABORATEUR)
        if boundary == "role"
        else replace(actor, tenant_id=uuid4())
    )
    for target in [report_url, url, f"{url}/{current['positions'][0]['position_id']}/history"]:
        response = client.get(target, headers={"Authorization": "Bearer synthetic"})
        assert response.status_code in (403, 404)
        assert str(report) not in response.text
        assert "12000" not in response.text
