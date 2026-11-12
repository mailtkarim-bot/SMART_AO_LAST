"""Published cost provenance to dated declarations, with no inherited consent."""

from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

from tests.db.test_l06_allocation_publication import publication_path
from tests.db.test_pricing_positions import workflow as workflow


def cash_path(session_factory, workflow):
    from app.interfaces.http.routes.cash_schedule import build_cash_schedule_router
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.modules.pricing.application.case_closure import CaseClosureService
    from app.modules.pricing.infrastructure.cash_schedule import (
        RecordCashScheduleHandler,
        SqlAlchemyCashScheduleReader,
    )
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy

    client, actor, case, report = workflow
    report_url, _, _ = publication_path(session_factory, workflow)
    policy = AuthorizationPolicy()
    client.app.include_router(
        build_cash_schedule_router(
            service=CaseClosureService(
                reader=SqlAlchemyCashScheduleReader(session_factory),
                dispatcher=CommandDispatcher(
                    session_factory=session_factory,
                    handlers={"RecordCashSchedule": RecordCashScheduleHandler()},
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
    root = f"/api/v1/patron/cases/{case}/cash-schedule"
    headers = {"Authorization": "Bearer synthetic"}

    def read():
        response = client.get(root, headers=headers)
        assert response.status_code == 200, response.text
        assert response.headers["cache-control"] == "no-store"
        return response.json()

    initial = read()
    source = next(s for s in initial["sources"] if s["id"].startswith("LINE:"))
    assert source.get("financial_report") == dict(
        report_id=str(report), revision=2, state="PUBLISHED"
    )
    assert source["amount_minor"] == 12000 and source["declared_date"] is None
    body = dict(
        case_id=str(case),
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=0,
        expected_view_sha256=initial["view_sha256"],
        human_confirmed=True,
        justification="Rapport publié relu, aucune échéance déduite.",
        declaration=dict(
            period_start="2026-11-01",
            period_end="2026-11-30",
            status="ACTIVE",
            assumptions="Coût publié sans date de paiement ni solde réel connus.",
            openings=[],
            flows=[
                dict(
                    flow_id=str(uuid4()),
                    direction="OUTFLOW",
                    currency_code="EUR",
                    amount_minor=12000,
                    declared_date=None,
                    source_refs=source["source_refs"],
                    native_source_id=source["id"],
                )
            ],
        ),
    )

    def post(payload):
        return client.post(root, headers=headers, json=payload)

    duplicate = deepcopy(body)
    duplicate["declaration"]["flows"].append(
        {**duplicate["declaration"]["flows"][0], "flow_id": str(uuid4())}
    )
    assert post(duplicate).status_code == 422
    missing = deepcopy(body)
    missing["human_confirmed"] = False
    assert post(missing).status_code == 422
    first = post(body)
    assert first.status_code == 201, first.text
    assert post(body).status_code == 200
    current = read()
    row = current["current"]
    assert row["projection"]["currencies"][0]["closing_minor"] is None
    assert row["declaration"]["flows"][0]["declared_date"] is None
    assert (
        row["source_snapshot"]["source_details"][source["id"]]["financial_report"]
        == source["financial_report"]
    )
    revised = deepcopy(body)
    revised.update(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=1,
        expected_view_sha256=current["view_sha256"],
        justification="Nouvelle hypothèse humaine de date, sans certitude de paiement.",
    )
    revised["declaration"]["assumptions"] = (
        "15 novembre déclaré sous hypothèse; solde initial encore inconnu."
    )
    revised["declaration"]["flows"][0]["declared_date"] = "2026-11-15"
    assert post(revised).status_code == 201
    assert read()["current"]["projection"]["currencies"][0]["closing_minor"] is None
    # A second native publication replaces the source catalogue, not the human declaration.
    from app.modules.dce.application.commands import CreateFinancialReportDraftCommand
    from app.modules.membership.application.financial_report_draft import (
        CreateFinancialReportDraftHandler,
        PatronFinancialReportDraftCreationService,
    )
    from app.modules.membership.infrastructure.financial_draft_case_reader import (
        SqlAlchemyFinancialDraftCaseReader,
    )
    from tests.application.test_financial_report_draft_lines import _command, _service

    creation = PatronFinancialReportDraftCreationService(
        reader=SqlAlchemyFinancialDraftCaseReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"CreateFinancialReportDraft": CreateFinancialReportDraftHandler()},
        ),
        policy=policy,
    )
    receipt = creation.create(
        actor=actor,
        command=CreateFinancialReportDraftCommand(
            case_id=case, command_id=uuid4(), idempotency_key=uuid4()
        ),
        now=datetime.now(UTC),
    )
    new_report = UUID(receipt.aggregate_refs[0]["aggregate_id"])
    _service(session_factory).add_line(
        actor=actor,
        command=_command(case, new_report).model_copy(
            update=dict(
                category="DIRECT_COST", amount_minor=16000, label="Coût remplacé synthétique"
            )
        ),
        now=datetime.now(UTC),
    )
    new_url = report_url.replace(str(report), str(new_report))
    pub = client.post(
        new_url + "/publications",
        headers=headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4()), expected_revision=1),
    )
    assert pub.status_code == 201, pub.text
    stale = read()
    assert stale["current"]["context_state"] == "REVIEW_REQUIRED"
    assert stale["current"]["projection"]["currencies"][0]["closing_minor"] is None
    assert stale["current"]["declaration"] == revised["declaration"]
    fresh = next(s for s in stale["sources"] if s["id"].startswith("LINE:"))
    assert fresh["financial_report"]["report_id"] == str(new_report)
    old_source = deepcopy(revised)
    old_source.update(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        expected_revision=2,
        expected_view_sha256=stale["view_sha256"],
    )
    assert post(old_source).status_code == 404
    final = deepcopy(old_source)
    final["declaration"]["flows"][0].update(
        amount_minor=16000,
        declared_date="2026-11-20",
        native_source_id=fresh["id"],
        source_refs=fresh["source_refs"],
    )
    final["declaration"]["openings"] = [
        dict(
            currency_code="EUR",
            amount_minor=1000,
            source_refs=["opening://synthetic-human-hypothesis"],
        )
    ]
    final.update(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        revision_id=str(uuid4()),
        justification="Nouvelle source relue et nouveaux consentement/date/solde déclarés.",
    )
    final["declaration"]["assumptions"] = (
        "Solde1000 et date20 novembre hypothétiques, ni banque ni trésorerie certaine."
    )
    result = post(final)
    assert result.status_code == 201, result.text
    assert post(final).status_code == 200
    last = read()
    assert last["current"]["projection"]["currencies"][0]["closing_minor"] == "-15000"
    assert len(last["history"]) == 3
    assert last["history"][1]["source_snapshot"]["source_details"][source["id"]][
        "financial_report"
    ]["report_id"] == str(report)
    assert last["history"][1]["context_state"] == "REVIEW_REQUIRED"
    assert (
        client.get(report_url, headers=headers).json()["summary"]["direct_cost_total_minor"]
        == 12000
    )
    from dataclasses import replace

    from app.platform.security.context import ActorKind
    from tests.application.test_financial_report_draft_lines import _seed_draft

    other = _seed_draft(session_factory)[0]
    other = replace(other, authenticated_at=datetime.now(UTC), mfa_verified_at=datetime.now(UTC))
    for foreign in [replace(actor, actor_kind=ActorKind.COLLABORATEUR), other]:
        client.position_actor_holder.actor = foreign
        denied = client.get(root, headers=headers)
        assert denied.status_code in (403, 404)
        assert str(new_report) not in denied.text and "16000" not in denied.text
        refused = dict(
            final, command_id=str(uuid4()), idempotency_key=str(uuid4()), revision_id=str(uuid4())
        )
        assert post(refused).status_code in (403, 404)
    client.position_actor_holder.actor = actor
    assert read()["revision"] == 3
    return root, last


def test_published_cost_to_cash_requires_dates_and_new_source_review(session_factory, workflow):
    cash_path(session_factory, workflow)
