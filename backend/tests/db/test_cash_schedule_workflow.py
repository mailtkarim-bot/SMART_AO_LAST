from copy import deepcopy
from uuid import uuid4

import pytest
import sqlalchemy as sa
from tests.db.test_transversal_affaire_workflow import affaire
from tests.support.transversal_affaire import shared_http


def test_native_cash_declaration_revision_recovery_and_source_change(
    session_factory, tmp_path, monkeypatch
):
    w = affaire.__wrapped__(session_factory, tmp_path)
    http = shared_http(session_factory, w, tmp_path, monkeypatch)
    root = f"/api/v1/patron/cases/{w.case_id}/cash-schedule"
    view = http.client.get(root, headers=http.patron_headers)
    assert view.status_code == 200, view.text
    assert view.json()["current"] is None
    assert http.client.get(root, headers=http.driver_headers).status_code == 403
    assert http.client.get(root).status_code == 401
    body = dict(
        case_id=str(w.case_id),
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=0,
        expected_view_sha256=view.json()["view_sha256"],
        human_confirmed=True,
        justification="Saisie synthétique relue.",
        declaration=dict(
            period_start="2026-11-01",
            period_end="2026-11-30",
            assumptions="Périmètre partiel et dates déclarées.",
            status="ACTIVE",
            openings=[
                dict(currency_code="EUR", amount_minor=0, source_refs=["balance://synthetic"])
            ],
            flows=[
                dict(
                    flow_id=str(uuid4()),
                    direction="OUTFLOW",
                    currency_code="EUR",
                    amount_minor=100,
                    declared_date="2026-11-02",
                    source_refs=["cost://synthetic"],
                )
            ],
        ),
    )
    assert http.client.post(root, headers=http.driver_headers, json=body).status_code == 403
    missing_consent = deepcopy(body)
    missing_consent["human_confirmed"] = False
    assert (
        http.client.post(root, headers=http.patron_headers, json=missing_consent).status_code == 422
    )
    first = http.client.post(root, headers=http.patron_headers, json=body)
    assert first.status_code == 201, first.text
    assert http.client.post(root, headers=http.patron_headers, json=body).json()["replayed"] is True
    current = http.client.get(root, headers=http.patron_headers).json()
    assert current["revision"] == 1 and len(current["history"]) == 1
    assert current["current"]["projection"]["currencies"][0]["closing_minor"] == "-100"
    stale = {
        **body,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "revision_id": str(uuid4()),
    }
    assert http.client.post(root, headers=http.patron_headers, json=stale).status_code == 409
    from app.modules.case.infrastructure.models.case import CaseRecord

    with session_factory.begin() as session:
        session.get(CaseRecord, w.case_id).scope_fingerprint = "f" * 64
    changed = http.client.get(root, headers=http.patron_headers).json()
    assert changed["current"]["context_state"] == "REVIEW_REQUIRED"
    assert changed["current"]["declaration"] == current["current"]["declaration"]
    revised = {**stale, "expected_revision": 1, "expected_view_sha256": changed["view_sha256"]}
    assert http.client.post(root, headers=http.patron_headers, json=revised).status_code == 201
    final = http.client.get(root, headers=http.patron_headers).json()
    assert final["revision"] == 2 and len(final["history"]) == 2
    assert final["history"][1]["context_state"] == "REVIEW_REQUIRED"
    from app.modules.pricing.infrastructure.models.cash_schedule import CashScheduleRevisionRecord

    with session_factory() as session:
        assert (
            len(
                session.scalars(
                    sa.select(CashScheduleRevisionRecord).where(
                        CashScheduleRevisionRecord.tenant_id == w.actor.tenant_id,
                        CashScheduleRevisionRecord.case_id == w.case_id,
                    )
                ).all()
            )
            == 2
        )
        with pytest.raises(sa.exc.DBAPIError):
            session.execute(sa.text("UPDATE cash_schedule_revisions SET justification='rewrite'"))
        session.rollback()
    http.client.close()


@pytest.fixture
def cash_context(session_factory, tmp_path, monkeypatch):
    w = affaire.__wrapped__(session_factory, tmp_path)
    http = shared_http(session_factory, w, tmp_path, monkeypatch)
    yield w, http, f"/api/v1/patron/cases/{w.case_id}/cash-schedule"
    http.client.close()


def cash_body(case_id, view):
    from app.modules.pricing.domain.cash_schedule import CashDeclaration
    from tests.application.test_cash_schedule import payload

    return dict(
        case_id=str(case_id),
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=view["revision"],
        expected_view_sha256=view["view_sha256"],
        human_confirmed=True,
        justification="Revue synthétique explicite.",
        declaration=CashDeclaration(**payload()).model_dump(mode="json"),
    )


def test_native_payment_sources_do_not_double_count_or_rewrite_facts(cash_context):
    w, http, root = cash_context
    closure = root.replace("cash-schedule", "closure")

    def post(path, body):
        result = http.client.post(closure + path, headers=http.patron_headers, json=body)
        assert result.status_code == 201, result.text

    def ids():
        return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))

    cycle = str(uuid4())
    post(
        "/cycles",
        dict(
            **ids(),
            cycle_id=cycle,
            source_refs=["contract://synthetic"],
            trigger_event="INVOICE",
            status="REVIEW_REQUIRED",
        ),
    )
    parent = None
    for kind in ("PAYMENT_EXPECTED", "COLLECTION_RECORDED"):
        fact = str(uuid4())
        post(
            "/payment-facts",
            dict(
                **ids(),
                fact_id=fact,
                cycle_id=cycle,
                kind=kind,
                amount_minor=100,
                currency_code="EUR",
                declared_date="2026-11-02",
                source_refs=["account://synthetic"],
                evidence_refs=["evidence://synthetic"],
                human_confirmed=True,
                justification="Constat déclaré synthétique.",
                expected_dossier_sha256=http.client.get(
                    closure, headers=http.patron_headers
                ).json()["dossier_sha256"],
                compared_to_fact_id=parent,
            ),
        )
        parent = fact
    view = http.client.get(root, headers=http.patron_headers).json()
    sources = [s for s in view["sources"] if s["id"].startswith("FACT:")]
    assert len(sources) == 2
    body = cash_body(w.case_id, view)
    base = body["declaration"]["flows"][0]
    body["declaration"]["flows"] = [
        {**base, "flow_id": str(uuid4()), "direction": "INFLOW", "native_source_id": s["id"]}
        for s in sources
    ]
    duplicate = http.client.post(root, headers=http.patron_headers, json=body)
    assert duplicate.status_code == 422
    assert duplicate.json()["detail"] == "CASH_NATIVE_SOURCE_DUPLICATED"
    body["declaration"]["flows"] = body["declaration"]["flows"][:1]
    body["declaration"]["flows"][0]["declared_date"] = "2026-11-03"
    mismatch = http.client.post(root, headers=http.patron_headers, json=body)
    assert mismatch.status_code == 422
    body["declaration"]["flows"][0]["declared_date"] = "2026-11-02"
    assert http.client.post(root, headers=http.patron_headers, json=body).status_code == 201


def test_cash_foreign_ids_do_not_become_a_tenant_existence_oracle(session_factory, cash_context):
    from uuid import UUID

    from app.modules.pricing.infrastructure.models.cash_schedule import CashScheduleRevisionRecord
    from app.platform.persistence.models import TenantRecord
    from tests.db.test_regulatory_profile_persistence import _case

    w, http, root = cash_context
    view = http.client.get(root, headers=http.patron_headers).json()
    body = cash_body(w.case_id, view)
    tenant, case_id = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(TenantRecord(id=tenant, slug=f"foreign-{tenant.hex}", lifecycle="ACTIVE"))
        session.flush()
        session.add(_case(tenant_id=tenant, case_id=case_id, marker="f"))
        session.flush()
        session.add(
            CashScheduleRevisionRecord(
                id=UUID(body["revision_id"]),
                tenant_id=tenant,
                case_id=case_id,
                revision=1,
                declaration_json=body["declaration"],
                source_snapshot_json={},
                justification="Foreign private declaration",
                human_confirmed=True,
                actor_id=uuid4(),
            )
        )
    foreign = root.replace(str(w.case_id), str(case_id))
    missing = root.replace(str(w.case_id), str(uuid4()))
    for url in (foreign, missing):
        get = http.client.get(url, headers=http.patron_headers)
        post = http.client.post(
            url, headers=http.patron_headers, json={**body, "case_id": url.split("/")[-2]}
        )
        assert get.status_code == post.status_code == 404
        assert get.json() == post.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    result = http.client.post(root, headers=http.patron_headers, json=body)
    assert result.status_code == 201, result.text


def test_cash_concurrency_unknown_retry_mfa_and_annulment(
    session_factory, cash_context, monkeypatch
):
    from concurrent.futures import ThreadPoolExecutor

    from app.modules.pricing.application.case_closure import CaseClosureService

    w, http, root = cash_context
    view = http.client.get(root, headers=http.patron_headers).json()
    one, two = cash_body(w.case_id, view), cash_body(w.case_id, view)

    def post(body):
        return http.client.post(root, headers=http.patron_headers, json=body)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(post, [one, two]))
    assert sorted(r.status_code for r in results) == [201, 409]
    view = http.client.get(root, headers=http.patron_headers).json()
    body = cash_body(w.case_id, view)
    original = CaseClosureService.record

    def receipt_lost(service, **kwargs):
        original(service, **kwargs)
        raise sa.exc.SQLAlchemyError("Synthetic receipt loss")

    with monkeypatch.context() as patch:
        patch.setattr(CaseClosureService, "record", receipt_lost)
        assert post(body).status_code == 503
    retry = post(body)
    assert retry.status_code == 200 and retry.json()["replayed"] is True
    view = http.client.get(root, headers=http.patron_headers).json()
    assert view["revision"] == 2
    cancel = cash_body(w.case_id, view)
    cancel["declaration"].update(status="CANCELLED", flows=[], openings=[])
    assert post(cancel).status_code == 201
    final = http.client.get(root, headers=http.patron_headers).json()
    assert final["revision"] == 3 and final["current"]["projection"]["status"] == "CANCELLED"
    assert final["history"][1]["declaration"]["status"] == "ACTIVE"
    from app.platform.security.models import AuthSessionRecord

    with session_factory.begin() as session:
        session.get(AuthSessionRecord, w.actor.session_id).mfa_verified_at = None
        session.get(AuthSessionRecord, w.actor.session_id).auth_strength = "PASSWORD"
    assert http.client.get(root, headers=http.patron_headers).status_code == 403
    assert post(cash_body(w.case_id, final)).status_code == 403
    from alembic import command
    from alembic.config import Config
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="CASH_SCHEDULE_HISTORY_DOWNGRADE_REFUSED"):
        command.downgrade(config, "20261027_0146")


def test_published_native_report_lines_keep_sale_and_cost_distinct(session_factory, cash_context):
    from datetime import UTC, datetime, timedelta

    from app.modules.pricing.infrastructure.models.financial import (
        FinancialReportLineRecord,
        FinancialReportSnapshotRecord,
    )

    w, http, root = cash_context

    def report(cost, offset):
        report_id, sale_id, cost_id = uuid4(), uuid4(), uuid4()
        with session_factory.begin() as session:
            now = datetime.now(UTC) + timedelta(seconds=offset)
            session.add(
                FinancialReportSnapshotRecord(
                    id=report_id,
                    tenant_id=w.actor.tenant_id,
                    case_id=w.case_id,
                    state="PUBLISHED",
                    currency_code="EUR",
                    ruleset_version=1,
                    aggregate_revision=1,
                    calculated_at=now,
                    published_at=now,
                    sales_total_minor=200,
                    direct_cost_total_minor=cost,
                    overhead_total_minor=0,
                    subcontracting_total_minor=0,
                    contingency_total_minor=0,
                    gross_margin_minor=200 - cost,
                    gross_margin_rate_bps=0,
                    forecast_cashflow_minor=0,
                )
            )
            session.flush()
            for line_id, category, amount in [
                (sale_id, "SALES", 200),
                (cost_id, "DIRECT_COST", cost),
            ]:
                session.add(
                    FinancialReportLineRecord(
                        id=line_id,
                        tenant_id=w.actor.tenant_id,
                        snapshot_id=report_id,
                        category=category,
                        label="Poste synthétique",
                        quantity_decimal="1",
                        unit="forfait",
                        amount_minor=amount,
                    )
                )
        return f"LINE:{sale_id}", f"LINE:{cost_id}"

    sale, cost = report(100, 0)
    view = http.client.get(root, headers=http.patron_headers).json()
    sources = {s["id"]: s for s in view["sources"]}
    assert sources[sale]["direction"] == "INFLOW" and sources[cost]["direction"] == "OUTFLOW"
    body = cash_body(w.case_id, view)
    body["declaration"]["flows"][0]["native_source_id"] = sale
    wrong = http.client.post(root, headers=http.patron_headers, json=body)
    assert wrong.status_code == 422 and wrong.json()["detail"] == "CASH_NATIVE_SOURCE_MISMATCH"
    body["declaration"]["flows"][0]["native_source_id"] = cost
    assert http.client.post(root, headers=http.patron_headers, json=body).status_code == 201
    report(125, 1)
    changed = http.client.get(root, headers=http.patron_headers).json()
    assert changed["current"]["context_state"] == "REVIEW_REQUIRED"
    assert changed["current"]["projection"]["currencies"][0]["closing_minor"] is None
