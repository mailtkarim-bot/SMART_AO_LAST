from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from tests.application.test_pricing_workbook_completeness import HEADERS, workbook_payload
from tests.db.test_pricing_workbook_pipeline import upload
from tests.db.test_pricing_workbook_pipeline import workflow as import_workflow


@pytest.fixture
def workflow(session_factory):
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_pricing_positions import (
        build_patron_pricing_positions_router,
    )
    from app.modules.pricing.infrastructure.position_handler import (
        RecordPricingPositionReviewHandler,
    )
    from app.modules.pricing.infrastructure.position_service import PricingPositionService
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy

    client, old_actor, case, report = import_workflow.__wrapped__(session_factory)
    actor = replace(
        old_actor, authenticated_at=datetime.now(UTC), mfa_verified_at=datetime.now(UTC)
    )
    service = PricingPositionService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordPricingPositionReview": RecordPricingPositionReviewHandler()},
        ),
        policy=AuthorizationPolicy(),
    )
    holder = SimpleNamespace(actor=actor)
    client.position_actor_holder = holder
    client.position_service = service
    resolver = SimpleNamespace(resolve=lambda **kwargs: holder.actor)
    client.app.include_router(
        build_patron_pricing_positions_router(
            service=service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=cast(Any, resolver), policy=AuthorizationPolicy()
            ),
        )
    )
    return client, actor, case, report


def test_imported_positions_start_unpriced_and_never_cost_zero(workflow):
    client, actor, case, report = workflow
    payload = workbook_payload(
        [("Lot 1", [HEADERS, ["A", "Pompe", 2, 100], ["B", "Transport", 1, 20]])]
    )
    result = upload(client, case, payload)
    assert result.status_code == 201
    batch = result.json()["batch_id"]
    response = client.get(
        f"/api/v1/patron/cases/{case}/pricing-import/{batch}/positions",
        headers={"Authorization": "Bearer synthetic"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data["positions"]) == 2
    assert all(
        p["cost_state"] == "UNKNOWN" and p["declared_cost_minor"] is None for p in data["positions"]
    )
    assert data["coverage_state"] == "UNKNOWN"
    assert all(row.get("import_origin", {}).get("state") == "UNKNOWN" for row in data["positions"])


def source_setup(session_factory, workflow, amount=12000):
    from tests.application.test_financial_report_draft_lines import (
        _command as financial_command,
    )
    from tests.application.test_financial_report_draft_lines import (
        _service as financial_service,
    )

    client, actor, case, report = workflow
    command = financial_command(case, report).model_copy(
        update=dict(category="DIRECT_COST", label="Pompe achetée", unit="u", amount_minor=amount)
    )
    financial_service(session_factory).add_line(actor=actor, command=command, now=datetime.now(UTC))
    result = upload(
        client,
        case,
        workbook_payload(
            [
                (
                    "Lot 1",
                    [
                        ["Code", "Désignation", "Unité", "Quantité", "Prix unitaire"],
                        ["A", "Pompe", "u", 2, 100],
                        ["B", "Transport", "forfait", 1, 20],
                    ],
                )
            ]
        ),
    )
    batch = result.json()["batch_id"]
    url = f"/api/v1/patron/cases/{case}/pricing-import/{batch}/positions"

    def read():
        response = client.get(url, headers={"Authorization": "Bearer synthetic"})
        assert response.status_code == 200, response.text
        return response.json()

    data = read()
    point = data["positions"][0]
    cost = next(c for c in data["sources"]["costs"] if c["label"] == "Pompe achetée")
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        record_id=str(uuid4()),
        expected_revision=0,
        position_context_sha256=point["position_context_sha256"],
        cost_refs=[dict(line_id=cost["line_id"], report_revision=cost["report_revision"])],
        requirement_id=None,
        requirement_revision=None,
        offer_price_id=None,
        offer_price_revision=None,
        scope_review_id=None,
        justification="Rattachement déclaré au poste exact; couverture non établie.",
        human_confirmed=True,
    )
    return url, point, body, read, cost


def test_registered_cost_links_are_revisioned_replayed_and_do_not_change_money(
    session_factory, workflow
):
    from app.modules.pricing.infrastructure.models import FinancialReportSnapshotRecord as Report

    client, actor, case, report = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    before = read()
    endpoint = f"{url}/{point['position_id']}/reviews"
    first = client.post(endpoint, json=body, headers={"Authorization": "Bearer synthetic"})
    assert first.status_code == 201, first.text
    retry = client.post(endpoint, json=body, headers={"Authorization": "Bearer synthetic"})
    assert retry.status_code == 200 and retry.json()["replayed"]
    current = read()["positions"][0]
    assert current["revision"] == 1 and current["declared_cost_minor"] == "12000"
    assert current["currency_code"] == "EUR" and current["coverage_state"] == "UNKNOWN"
    assert before["positions"][0]["import_source"]["total_minor"] == "20000"
    assert "source_sha256" not in current["import_source"]
    history = client.get(
        f"{url}/{point['position_id']}/history", headers={"Authorization": "Bearer synthetic"}
    ).json()
    assert len(history["entries"]) == 1 and history["entries"][0]["state"] == "HISTORICAL"
    assert "source_sha256" not in history["entries"][0]["snapshot"]["import"]
    with session_factory() as s:
        row = s.get(Report, report)
        assert row.direct_cost_total_minor == 12000 and row.sales_total_minor == 0
    conflict = client.post(
        endpoint,
        json=dict(
            body, command_id=str(uuid4()), idempotency_key=str(uuid4()), record_id=str(uuid4())
        ),
        headers={"Authorization": "Bearer synthetic"},
    )
    assert conflict.status_code == 409


def test_reused_cost_is_visible_without_double_counting(session_factory, workflow):
    client, _, _, _ = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    for row in read()["positions"]:
        payload = dict(
            body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            record_id=str(uuid4()),
            position_context_sha256=row["position_context_sha256"],
        )
        response = client.post(
            f"{url}/{row['position_id']}/reviews",
            json=payload,
            headers={"Authorization": "Bearer synthetic"},
        )
        assert response.status_code == 201, response.text
    for row in read()["positions"]:
        assert row["declared_cost_minor"] is None
        assert "COST_REUSE_REVIEW_REQUIRED" in row["limitations"]


def test_review_holds_the_import_mutex_until_its_snapshot_is_saved(session_factory, workflow):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from uuid import UUID

    import sqlalchemy as sa
    from app.modules.pricing.infrastructure.models.position_review import (
        PricingPositionReviewRecord as Review,
    )
    from tests.application.test_pricing_import_commit import (
        _command as commit_command,
    )
    from tests.application.test_pricing_import_commit import (
        _service as commit_service,
    )

    client, actor, case, report = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    body = dict(body, cost_refs=[])
    entered, release, committed = Event(), Event(), Event()

    def pause(mapper, connection, target):
        if target.id == UUID(body["record_id"]):
            entered.set()
            assert release.wait(5)

    def save():
        return client.post(
            f"{url}/{point['position_id']}/reviews",
            json=body,
            headers={"Authorization": "Bearer synthetic"},
        )

    def commit():
        result = commit_service(session_factory).commit(
            actor=actor,
            command=commit_command(
                case, report, UUID(url.split("/")[-2]), expected_report_revision=1
            ),
            now=datetime.now(UTC),
        )
        committed.set()
        return result

    sa.event.listen(Review, "before_insert", pause)
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(save)
            assert entered.wait(5)
            second = pool.submit(commit)
            blocked = not committed.wait(0.5)
            release.set()
            assert first.result(5).status_code == 201
            assert second.result(5).result_code == "PRICING_IMPORT_COMMITTED"
        assert blocked, "import advanced after source validation but before review insert"
    finally:
        release.set()
        sa.event.remove(Review, "before_insert", pause)


def test_money_above_javascript_integer_precision_is_returned_exactly(session_factory, workflow):
    client, *_ = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow, amount=9007199254740993)
    response = client.post(
        f"{url}/{point['position_id']}/reviews",
        json=body,
        headers={"Authorization": "Bearer synthetic"},
    )
    assert response.status_code == 201, response.text
    row = read()["positions"][0]
    assert row["declared_cost_minor"] == "9007199254740993"
    assert row["costs"][0]["amount_minor"] == "9007199254740993"


@pytest.mark.parametrize("change", ["report_revision", "case_scope"])
def test_source_changes_invalidate_current_costs_without_erasing_history(
    session_factory, workflow, change
):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from tests.application.test_financial_report_draft_lines import (
        _command as command,
    )
    from tests.application.test_financial_report_draft_lines import (
        _service as service,
    )

    client, actor, case, report = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    endpoint = f"{url}/{point['position_id']}/reviews"
    assert (
        client.post(endpoint, json=body, headers={"Authorization": "Bearer synthetic"}).status_code
        == 201
    )
    if change == "case_scope":
        with session_factory.begin() as s:
            row = s.get(CaseRecord, case)
            row.scope_json = {"lot": "autre"}
            row.scope_fingerprint = "f" * 64
    else:
        service(session_factory).add_line(
            actor=actor, command=command(case, report, expected_revision=1), now=datetime.now(UTC)
        )
    row = read()["positions"][0]
    assert (
        row["state"] == "REVIEW_REQUIRED"
        and row["declared_cost_minor"] is None
        and row["costs"] == []
    )
    assert row["justification"] is None and row["actor_id"] is None
    old = client.get(
        f"{url}/{point['position_id']}/history", headers={"Authorization": "Bearer synthetic"}
    ).json()["entries"][0]
    assert old["snapshot"]["costs"][0]["amount_minor"] == "12000" and old["state"] == "HISTORICAL"


@pytest.mark.parametrize(
    "change", ["foreign_cost", "sales_cost", "wrong_revision", "foreign_batch", "bad_base"]
)
def test_wrong_sources_never_create_a_review(session_factory, workflow, change):
    import sqlalchemy as sa
    from app.modules.pricing.infrastructure.models.position_review import (
        PricingPositionReviewRecord as Review,
    )
    from tests.application.test_financial_report_draft_lines import (
        _command as command,
    )
    from tests.application.test_financial_report_draft_lines import (
        _seed_draft,
    )
    from tests.application.test_financial_report_draft_lines import (
        _service as service,
    )

    client, actor, case, report = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    if change == "foreign_cost":
        other, foreign_case, foreign_report, _ = _seed_draft(session_factory)
        service(session_factory).add_line(
            actor=other,
            command=command(foreign_case, foreign_report).model_copy(
                update={"category": "DIRECT_COST"}
            ),
            now=datetime.now(UTC),
        )
        from app.modules.pricing.infrastructure.models import FinancialReportLineRecord as Line

        with session_factory() as s:
            foreign = s.scalar(sa.select(Line).where(Line.tenant_id == other.tenant_id))
        body = dict(body, cost_refs=[{"line_id": str(foreign.id), "report_revision": 1}])
    elif change == "sales_cost":
        service(session_factory).add_line(
            actor=actor, command=command(case, report, expected_revision=1), now=datetime.now(UTC)
        )
        from app.modules.pricing.infrastructure.models import FinancialReportLineRecord as Line

        with session_factory() as s:
            sales = s.scalar(
                sa.select(Line).where(Line.tenant_id == actor.tenant_id, Line.category == "SALES")
            )
        body = dict(body, cost_refs=[{"line_id": str(sales.id), "report_revision": 2}])
    elif change == "wrong_revision":
        body = dict(body, cost_refs=[dict(body["cost_refs"][0], report_revision=999)])
    elif change == "bad_base":
        body = dict(body, position_context_sha256="0" * 64)
    else:
        url = url.replace(url.split("/")[-2], str(uuid4()))
    response = client.post(
        f"{url}/{point['position_id']}/reviews",
        json=body,
        headers={"Authorization": "Bearer synthetic"},
    )
    assert response.status_code in (404, 409), response.text
    with session_factory() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(Review)
                .where(Review.tenant_id == actor.tenant_id)
            )
            == 0
        )


@pytest.mark.parametrize("change", ["role", "mfa", "capability"])
def test_financial_role_mfa_and_permissions_are_enforced_before_writes(
    session_factory, workflow, change
):
    from app.platform.security.capabilities import Capability
    from app.platform.security.context import ActorKind

    client, actor, *_ = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    if change == "role":
        other = replace(actor, actor_kind=ActorKind.COLLABORATEUR)
    elif change == "mfa":
        other = replace(actor, mfa_verified_at=None)
    else:
        other = replace(
            actor,
            capabilities=frozenset(
                c for c in actor.capabilities if c != Capability.FINANCIAL_REPORT_LINE_WRITE.value
            ),
        )
    client.position_actor_holder.actor = other
    response = client.post(
        f"{url}/{point['position_id']}/reviews",
        json=body,
        headers={"Authorization": "Bearer synthetic"},
    )
    assert response.status_code == 403, response.text
    if change == "role":
        assert client.get(url, headers={"Authorization": "Bearer synthetic"}).status_code == 403


def test_links_and_cost_references_are_append_only_and_downgrade_protected(
    session_factory, workflow
):
    from uuid import UUID

    import sqlalchemy as sa
    from alembic import command
    from alembic.config import Config
    from app.modules.pricing.infrastructure.models.position_review import (
        PricingPositionCostReferenceRecord as Ref,
    )
    from app.modules.pricing.infrastructure.models.position_review import (
        PricingPositionReviewRecord as Review,
    )
    from sqlalchemy.exc import DBAPIError
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    client, *_ = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    assert (
        client.post(
            f"{url}/{point['position_id']}/reviews",
            json=body,
            headers={"Authorization": "Bearer synthetic"},
        ).status_code
        == 201
    )
    for sql in [
        sa.update(Review)
        .where(Review.id == UUID(body["record_id"]))
        .values(justification="Réécriture"),
        sa.delete(Ref).where(Ref.review_id == UUID(body["record_id"])),
    ]:
        with pytest.raises(DBAPIError, match="APPEND_ONLY"), session_factory.begin() as s:
            s.execute(sql)
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="PRICING_POSITION_HISTORY_DOWNGRADE_REFUSED"):
        command.downgrade(cfg, "20261022_0140")
    assert read()["positions"][0]["revision"] == 1


def dce_workflow(session_factory, tmp_path, workflow, *, requirement=False):
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_pricing_import import build_patron_pricing_import_router
    from app.interfaces.http.routes.patron_pricing_positions import (
        build_patron_pricing_positions_router,
    )
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
    from app.modules.pricing.application.import_preview import PricingImportPreviewService
    from app.modules.pricing.infrastructure.models import FinancialReportSnapshotRecord as Report
    from app.modules.pricing.infrastructure.position_handler import (
        RecordPricingPositionReviewHandler,
    )
    from app.modules.pricing.infrastructure.position_service import PricingPositionService
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tests.application.test_dce_document_extraction import _seed_admitted_document
    from tests.application.test_pricing_import_creation import _service as create_service
    from tests.db.test_candidate_retrieval_sql import _clone
    from tests.db.test_case_analysis_summary_sql import requirements_dossier

    _, old_actor, old_case, old_report = workflow
    payload = workbook_payload(
        [
            (
                "Lot6",
                [
                    ["Code", "Désignation", "Unité", "Quantité", "Prix unitaire"],
                    ["BE", "Études de dimensionnement", "forfait", 1, 200],
                ],
            )
        ]
    )
    if requirement:
        tenant, case, version = requirements_dossier.__wrapped__(
            session_factory,
            tmp_path,
            source_bytes="Lot 6 : les notes de calcul doivent être fournies.".encode(),
            family="CCTP",
        )
        doc = None
    else:
        tenant, doc, version = _seed_admitted_document(
            session_factory,
            storage=LocalQuarantineStorageAdapter(root=tmp_path),
            source_bytes=payload,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        case = uuid4()
        with session_factory.begin() as s:
            template = s.get(CaseRecord, old_case)
            v = s.get(DceVersionRecord, version)
            s.add(
                _clone(
                    template,
                    id=case,
                    tenant_id=tenant,
                    consultation_id=v.consultation_id,
                    applicable_dce_version_id=version,
                    dce_freshness="CURRENT",
                )
            )
    report = uuid4()
    with session_factory.begin() as s:
        s.add(_clone(s.get(Report, old_report), id=report, tenant_id=tenant, case_id=case))
    actor = replace(
        old_actor,
        tenant_id=tenant,
        authenticated_at=datetime.now(UTC),
        mfa_verified_at=datetime.now(UTC),
        membership_id=uuid4(),
    )
    runtime = ConsultationSecurityRuntime(
        context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kwargs: actor)),
        policy=AuthorizationPolicy(),
    )
    app = FastAPI()
    app.include_router(
        build_patron_pricing_import_router(
            service=PricingImportPreviewService(policy=AuthorizationPolicy()),
            creation_service=create_service(session_factory),
            security_runtime=runtime,
        )
    )
    app.include_router(
        build_patron_pricing_positions_router(
            service=PricingPositionService(
                session_factory=session_factory,
                dispatcher=CommandDispatcher(
                    session_factory=session_factory,
                    handlers={"RecordPricingPositionReview": RecordPricingPositionReviewHandler()},
                ),
                policy=AuthorizationPolicy(),
            ),
            security_runtime=runtime,
        )
    )
    return TestClient(app), actor, case, report, payload, doc, version


def test_original_import_is_matched_only_by_hash_in_current_admitted_dce(
    session_factory, tmp_path, workflow
):
    client, actor, case, report, payload, doc, version = dce_workflow(
        session_factory, tmp_path, workflow
    )
    batch = upload(client, case, payload).json()["batch_id"]
    url = f"/api/v1/patron/cases/{case}/pricing-import/{batch}/positions"
    response = client.get(url, headers={"Authorization": "Bearer synthetic"})
    assert response.status_code == 200, response.text
    origin = response.json()["positions"][0]["import_origin"]
    assert (
        origin["state"] == "MATCHED_BY_HASH"
        and origin["document_id"] == str(doc)
        and origin["dce_version_id"] == str(version)
    )
    from hashlib import sha256

    assert sha256(payload).hexdigest() not in response.text


def test_confirmed_dce_obligation_uses_exact_anchor_and_rejects_stale_confirmation(
    session_factory, tmp_path, workflow
):
    import sqlalchemy as sa
    from app.modules.dce.application.commands import RecordDceRequirementConfirmationCommand
    from app.modules.dce.application.handlers import RecordDceRequirementConfirmationHandler
    from app.modules.dce.application.requirement_confirmation import (
        DceRequirementConfirmationService,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy

    client, actor, case, report, payload, doc, version = dce_workflow(
        session_factory, tmp_path, workflow, requirement=True
    )
    batch = upload(client, case, payload).json()["batch_id"]
    url = f"/api/v1/patron/cases/{case}/pricing-import/{batch}/positions"
    with session_factory() as s:
        req = s.scalar(
            sa.select(DceRequirementRecord).where(DceRequirementRecord.tenant_id == actor.tenant_id)
        )
    assert req is not None
    confirm = RecordDceRequirementConfirmationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        confirmation_id=uuid4(),
        requirement_id=req.id,
        expected_confirmation_revision=0,
        outcome="CONFIRMED",
        reason_code="SOURCE_REVIEWED",
    )
    service = DceRequirementConfirmationService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementConfirmation": RecordDceRequirementConfirmationHandler()
            },
        ),
        policy=AuthorizationPolicy(),
    )
    service.confirm(actor=actor, command=confirm, now=datetime.now(UTC))
    data = client.get(url, headers={"Authorization": "Bearer synthetic"}).json()
    source = data["sources"]["requirements"][0]
    point = data["positions"][0]
    assert source["source_anchor"]["dce_version_id"] == str(version)
    assert "notes de calcul" in source["excerpt"]
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        record_id=str(uuid4()),
        expected_revision=0,
        position_context_sha256=point["position_context_sha256"],
        cost_refs=[],
        requirement_id=source["requirement_id"],
        requirement_revision=source["revision"],
        offer_price_id=None,
        offer_price_revision=None,
        scope_review_id=None,
        justification="Études rattachées à la prescription confirmée du lot6.",
        human_confirmed=True,
    )
    endpoint = f"{url}/{point['position_id']}/reviews"
    assert (
        client.post(endpoint, json=body, headers={"Authorization": "Bearer synthetic"}).status_code
        == 201
    )
    service.confirm(
        actor=actor,
        command=confirm.model_copy(
            update=dict(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                confirmation_id=uuid4(),
                expected_confirmation_revision=1,
                outcome="NOT_APPLICABLE",
            )
        ),
        now=datetime.now(UTC),
    )
    after = client.get(url, headers={"Authorization": "Bearer synthetic"}).json()["positions"][0]
    assert after["state"] == "REVIEW_REQUIRED" and after["requirement"] is None


def test_partner_offer_exclusions_transport_expiry_and_price_revision_are_visible(
    session_factory, database_engine, workflow
):
    from datetime import date

    import sqlalchemy as sa
    from app.modules.partner.infrastructure.models.partner_event import (
        CasePartnerEventRecord as Receipt,
    )
    from app.modules.pricing.application.partner_offer_price_handler import (
        PartnerOfferPriceService,
        partner_offer_price_handlers,
    )
    from app.modules.pricing.application.partner_offer_scope_review_handler import (
        PartnerOfferScopeReviewService,
        partner_offer_scope_review_handlers,
    )
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy
    from tests.db.test_candidate_retrieval_sql import _clone
    from tests.db.test_partner_offer_price import _command as price_command
    from tests.db.test_partner_offer_scope_review import _command as scope_command
    from tests.db.test_partner_offer_scope_review import _offer, _receipt

    client, actor, case, report = workflow
    url, point, body, read, cost = source_setup(session_factory, workflow)
    old, partner = _receipt(
        database_engine, tenant_id=actor.tenant_id, case_id=case, actor=actor, label="DevisA"
    )
    first = uuid4()
    with session_factory.begin() as s:
        s.add(
            _clone(
                s.scalar(sa.select(Receipt).where(Receipt.event_id == old)),
                event_id=first,
                revision=2,
                valid_until=date(2020, 1, 1),
                validity_at_recording="EXPIRED",
                exclusions_state="DECLARED",
                exclusions_json=["Transport exclu", "Pose non comprise"],
            )
        )
    second, _ = _receipt(
        database_engine, tenant_id=actor.tenant_id, case_id=case, actor=actor, label="DevisB"
    )
    prices = PartnerOfferPriceService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory, handlers=partner_offer_price_handlers()
        ),
        policy=AuthorizationPolicy(),
    )
    price = price_command(case, first)
    prices.declare(actor=actor, command=price, now=datetime.now(UTC))
    scopes = PartnerOfferScopeReviewService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory, handlers=partner_offer_scope_review_handlers()
        ),
        policy=AuthorizationPolicy(),
    )
    review = scope_command(
        case,
        uuid4(),
        [first, second],
        offers=[
            _offer(first, transport_state="EXCLUDED").model_copy(
                update={"transport_note": "Transport à chiffrer séparément."}
            ),
            _offer(second),
        ],
    )
    scopes.record(actor=actor, command=review, now=datetime.now(UTC))
    data = read()
    offer = next(o for o in data["sources"]["offers"] if o["price_id"] == str(price.declaration_id))
    scope = next(s for s in data["sources"]["scopes"] if s["receipt_event_id"] == str(first))
    assert (
        offer["exclusions"] == ["Transport exclu", "Pose non comprise"]
        and scope["transport_state"] == "EXCLUDED"
    )
    body = dict(
        body,
        offer_price_id=offer["price_id"],
        offer_price_revision=offer["revision"],
        scope_review_id=scope["review_id"],
    )
    endpoint = f"{url}/{point['position_id']}/reviews"
    response = client.post(endpoint, json=body, headers={"Authorization": "Bearer synthetic"})
    assert response.status_code == 201, response.text
    current = read()["positions"][0]
    assert current["declared_cost_minor"] == "12000" and current["currency_code"] == "EUR"
    assert (
        current["offer"]["amount_as_declared"] == "1234,50"
        and current["offer"]["currency_code"] == "MAD"
    )
    assert {
        "TRANSPORT_NOT_INCLUDED",
        "OFFER_EXPIRED",
        "OFFER_EXCLUSIONS_PRESENT",
        "OFFER_CURRENCY_MISMATCH",
    } <= set(current["limitations"])
    prices.declare(
        actor=actor, command=price_command(case, first, expected_revision=1), now=datetime.now(UTC)
    )
    assert read()["positions"][0]["state"] == "REVIEW_REQUIRED"


def test_shared_cost_allocations_are_exact_bounded_and_historical(session_factory, workflow):
    client, _, _, _ = workflow
    url, _, body, read, cost = source_setup(session_factory, workflow)
    rows = read()["positions"]

    def allocate(row, amount, revision=0):
        return dict(
            body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            record_id=str(uuid4()),
            expected_revision=revision,
            position_context_sha256=row["position_context_sha256"],
            cost_refs=[
                dict(
                    line_id=cost["line_id"],
                    report_revision=cost["report_revision"],
                    allocated_amount_minor=amount,
                )
            ],
        )

    def post(row, payload):
        return client.post(
            f"{url}/{row['position_id']}/reviews",
            json=payload,
            headers={"Authorization": "Bearer synthetic"},
        )

    first = allocate(rows[0], "4500")
    response = post(rows[0], first)
    assert response.status_code == 201, response.text
    assert post(rows[0], first).status_code == 200
    changed_intent = dict(
        first, cost_refs=[dict(first["cost_refs"][0], allocated_amount_minor="4501")]
    )
    assert post(rows[0], changed_intent).status_code == 422
    assert post(rows[1], allocate(rows[1], "7501")).status_code == 422
    second = allocate(rows[1], "6500")
    assert post(rows[1], second).status_code == 201
    data = read()
    assert [r["declared_cost_minor"] for r in data["positions"]] == ["4500", "6500"]
    assert all(r["coverage_state"] == "UNKNOWN" for r in data["positions"])
    summary = next(c for c in data["sources"]["costs"] if c["line_id"] == cost["line_id"])[
        "allocation_summary"
    ]
    assert summary["allocated_amount_minor"] == "11000"
    assert summary["remaining_amount_minor"] == "1000"
    assert summary["state"] == "DECLARED"
    assert post(rows[0], allocate(rows[0], "5501", 1)).status_code == 422
    assert post(rows[0], allocate(rows[0], "5000", 1)).status_code == 201
    history = client.get(
        f"{url}/{rows[0]['position_id']}/history", headers={"Authorization": "Bearer synthetic"}
    ).json()
    assert [e["snapshot"]["costs"][0]["allocated_amount_minor"] for e in history["entries"]] == [
        "5000",
        "4500",
    ]


def test_allocation_summary_becomes_unknown_after_case_context_replaced(session_factory, workflow):
    from app.modules.case.infrastructure.models.case import CaseRecord

    client, _, _, _ = workflow
    url, row, body, read, cost = source_setup(session_factory, workflow)
    body["cost_refs"][0]["allocated_amount_minor"] = "4500"
    result = client.post(
        f"{url}/{row['position_id']}/reviews",
        json=body,
        headers={"Authorization": "Bearer synthetic"},
    )
    assert result.status_code == 201
    with session_factory.begin() as session:
        case = session.get(CaseRecord, workflow[2])
        case.scope_json = {"lot": "remplace"}
        case.scope_fingerprint = "f" * 64
    data = read()
    assert data["positions"][0]["state"] == "REVIEW_REQUIRED"
    summary = next(c for c in data["sources"]["costs"] if c["line_id"] == cost["line_id"])[
        "allocation_summary"
    ]
    assert summary["state"] == "UNKNOWN"
    assert summary["allocated_amount_minor"] is None
    assert summary["remaining_amount_minor"] is None


def test_concurrent_shared_allocations_never_exceed_the_source(session_factory, workflow):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    client, _, _, _ = workflow
    url, _, body, read, cost = source_setup(session_factory, workflow)
    rows = read()["positions"]
    barrier = Barrier(2)

    def allocate(row):
        payload = dict(
            body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            record_id=str(uuid4()),
            position_context_sha256=row["position_context_sha256"],
            cost_refs=[
                dict(
                    line_id=cost["line_id"],
                    report_revision=cost["report_revision"],
                    allocated_amount_minor="6001",
                )
            ],
        )
        barrier.wait(timeout=10)
        return client.post(
            f"{url}/{row['position_id']}/reviews",
            json=payload,
            headers={"Authorization": "Bearer synthetic"},
        ).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(allocate, rows))
    assert sorted(statuses) == [201, 422]
    assert sum(int(r["declared_cost_minor"] or 0) for r in read()["positions"]) == 6001


def test_new_financial_source_revision_never_inherits_previous_allocations(
    session_factory, workflow
):
    from tests.application.test_financial_report_draft_lines import _command, _service

    client, actor, case, report = workflow
    url, row, body, read, cost = source_setup(session_factory, workflow)
    body["cost_refs"][0]["allocated_amount_minor"] = "4500"
    endpoint = f"{url}/{row['position_id']}/reviews"
    headers = {"Authorization": "Bearer synthetic"}
    assert client.post(endpoint, json=body, headers=headers).status_code == 201
    _service(session_factory).add_line(
        actor=actor, command=_command(case, report, expected_revision=1), now=datetime.now(UTC)
    )
    fresh = read()
    assert fresh["positions"][0]["declared_cost_minor"] is None
    assert fresh["positions"][0]["state"] == "REVIEW_REQUIRED"
    source = next(c for c in fresh["sources"]["costs"] if c["line_id"] == cost["line_id"])
    assert source["allocation_summary"]["state"] == "UNKNOWN"
    payload = dict(
        body,
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        record_id=str(uuid4()),
        expected_revision=1,
        cost_refs=[
            dict(
                line_id=source["line_id"],
                report_revision=source["report_revision"],
                allocated_amount_minor="5000",
            )
        ],
        justification="Nouvelle revue et hypothèse explicite, aucun accord transféré",
    )
    assert client.post(endpoint, json=payload, headers=headers).status_code == 201
    current = read()
    source = next(c for c in current["sources"]["costs"] if c["line_id"] == cost["line_id"])
    assert source["allocation_summary"]["allocated_amount_minor"] == "5000"
    assert source["allocation_summary"]["remaining_amount_minor"] == "7000"
    history = client.get(f"{url}/{row['position_id']}/history", headers=headers).json()
    assert [e["snapshot"]["costs"][0]["allocated_amount_minor"] for e in history["entries"]] == [
        "5000",
        "4500",
    ]
