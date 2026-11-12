from datetime import UTC, datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.pricing.application.payment_cycle_commands import (
    RecordPaymentPostReceptionCycleCommand,
)
from app.modules.pricing.application.payment_cycle_handler import payment_cycle_handlers
from app.modules.pricing.infrastructure.case_closure_reader import SqlAlchemyCaseClosureReader
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from tests.db.test_regulatory_profile_persistence import _case


def test_exact_payment_declarations_are_append_only_scoped_and_replayable(session_factory):
    from app.modules.pricing.application.case_closure import closure_handlers
    from app.modules.pricing.application.case_closure_commands import RecordPaymentFactCommand
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier

    tenant, case, cycle = uuid4(), uuid4(), uuid4()
    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug=f"closure-{tenant.hex[:12]}", lifecycle="ACTIVE"))
        s.flush()
        s.add(_case(tenant_id=tenant, case_id=case, marker="c"))
    dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers={**payment_cycle_handlers(), **closure_handlers()}
    )
    ctx = CommandContext(
        tenant_id=tenant,
        actor_id=uuid4(),
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(UTC),
        identity_id=uuid4(),
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case,
        correlation_id=uuid4(),
    )
    dispatcher.dispatch(
        context=ctx,
        command=RecordPaymentPostReceptionCycleCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            cycle_id=cycle,
            case_id=case,
            source_refs=["ccap://synthetic/p12"],
            trigger_event="INVOICE",
            status="REVIEW_REQUIRED",
        ),
    )

    def view():
        with session_factory() as s:
            return closure_dossier(s, tenant, case)

    def fact(kind, amount, parent=None):
        return RecordPaymentFactCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            fact_id=uuid4(),
            case_id=case,
            cycle_id=cycle,
            kind=kind,
            amount_minor=amount,
            currency_code="EUR",
            declared_date="2026-10-25",
            source_refs=["statement://synthetic/1"],
            evidence_refs=["proof://synthetic/1"],
            human_confirmed=True,
            justification="Pièce relue humainement.",
            expected_dossier_sha256=view()["dossier_sha256"],
            compared_to_fact_id=parent,
        )

    expected = fact("PAYMENT_EXPECTED", 100000)
    dispatcher.dispatch(context=ctx, command=expected)
    assert view()["financial_observations"]["collection_state"] == "UNKNOWN"
    actual = fact("COLLECTION_RECORDED", 60000, expected.fact_id)
    dispatcher.dispatch(context=ctx, command=actual)
    assert dispatcher.dispatch(context=ctx, command=actual).replayed
    assert view()["financial_observations"]["comparisons"][0]["difference_minor"] == -40000
    with pytest.raises(CommandExecutionError, match="CLOSURE_VIEW_CONFLICT"):
        dispatcher.dispatch(
            context=ctx,
            command=fact("COLLECTION_RECORDED", 1).model_copy(
                update={"expected_dossier_sha256": expected.expected_dossier_sha256}
            ),
        )
    foreign = fact("COLLECTION_RECORDED", 1, uuid4())
    with pytest.raises(CommandExecutionError, match="PAYMENT_COMPARISON_NOT_FOUND_OR_FORBIDDEN"):
        dispatcher.dispatch(context=ctx, command=foreign)
    mismatch = fact("COLLECTION_RECORDED", 1, expected.fact_id).model_copy(
        update={"currency_code": "USD"}
    )
    with pytest.raises(CommandExecutionError, match="PAYMENT_COMPARISON_INCOMPATIBLE"):
        dispatcher.dispatch(context=ctx, command=mismatch)
    with session_factory() as s:
        assert closure_dossier(s, uuid4(), case) is None
        with pytest.raises(sa.exc.DBAPIError):
            s.execute(
                sa.text("UPDATE payment_cycle_facts SET amount_minor=1 WHERE id=:id"),
                {"id": actual.fact_id},
            )
        s.rollback()
    assert view()["financial_observations"]["settlement_state"] == "UNKNOWN"
    from app.modules.pricing.application.payment_cycle_commands import (
        QualifyPaymentPostReceptionCycleCommand,
    )

    dispatcher.dispatch(
        context=ctx,
        command=QualifyPaymentPostReceptionCycleCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            case_id=case,
            cycle_id=cycle,
            cash_assumption="Hypothèse changée synthétiquement.",
        ),
    )
    changed = view()
    assert all(f["context_state"] == "REVIEW_REQUIRED" for f in changed["facts"])
    with pytest.raises(CommandExecutionError, match="PAYMENT_COMPARISON_SOURCE_CHANGED"):
        dispatcher.dispatch(context=ctx, command=fact("COLLECTION_RECORDED", 1, expected.fact_id))


def test_reception_reserve_exit_and_execution_rex_use_native_records(session_factory):
    from app.modules.patron_action.application.case_interview_commands import (
        RecordCaseInterviewCommand,
    )
    from app.modules.patron_action.application.case_interview_handler import case_interview_handlers
    from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
    from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord
    from app.modules.pricing.application.case_closure import closure_handlers
    from app.modules.pricing.application.case_closure_commands import (
        RecordClosureActCommand,
        RecordClosureObligationCommand,
        RecordExecutionRexCommand,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_commands import (
        TransitionPostReceptionObligationCommand,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_handler import (
        post_reception_obligation_transition_handlers,
    )
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier

    tenant, case = uuid4(), uuid4()
    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug=f"exit-{tenant.hex[:12]}", lifecycle="ACTIVE"))
        s.flush()
        row = _case(tenant_id=tenant, case_id=case, marker="e")
        row.scope_json = {"lot_numbers": ["01"]}
        s.add(row)
    ctx = CommandContext(
        tenant_id=tenant,
        actor_id=uuid4(),
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(UTC),
        identity_id=uuid4(),
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case,
        correlation_id=uuid4(),
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            **closure_handlers(),
            **post_reception_obligation_transition_handlers(),
            **case_interview_handlers(),
        },
    )

    def view():
        with session_factory() as s:
            return closure_dossier(s, tenant, case)

    def review(**updates):
        return dict(
            expected_dossier_sha256=view()["dossier_sha256"],
            human_confirmed=True,
            justification="Relecture humaine des pièces.",
            responsible="Conducteur synthétique",
            expected_evidence="PV signé synthétique",
            acknowledged_open_obligation_ids=[],
            comparisons=[],
            **updates,
        )

    act = RecordClosureActCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=uuid4(),
        case_id=case,
        act_kind="WORK_RECEPTION",
        reception_outcome="WITH_RESERVATIONS",
        summary="Réception déclarée avec réserve.",
        source_refs=["pv://synthetic/p1"],
        evidence_refs=["preuve://synthetic/p1"],
        closure_review=review(),
    )
    dispatcher.dispatch(context=ctx, command=act)
    obligation = RecordClosureObligationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=case,
        obligation_id=uuid4(),
        obligation_type="RESERVES_LIFTING",
        origin_reception_act_id=act.act_id,
        summary="Corriger finition.",
        source_refs=["pv://synthetic/p1"],
        closure_review=review(),
    )
    dispatcher.dispatch(context=ctx, command=obligation)
    assert view()["obligations"][0]["responsible"] == "Conducteur synthétique"
    exit_act = RecordClosureActCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=uuid4(),
        case_id=case,
        act_kind="CONTRACT_EXIT",
        summary="Sortie administrative déclarée.",
        source_refs=["sortie://synthetic/p1"],
        evidence_refs=["preuve://synthetic/p2"],
        closure_review=review(),
    )
    with pytest.raises(CommandExecutionError, match="OPEN_OBLIGATIONS_REQUIRE_ACKNOWLEDGEMENT"):
        dispatcher.dispatch(context=ctx, command=exit_act)
    dispatcher.dispatch(
        context=ctx,
        command=TransitionPostReceptionObligationCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            case_id=case,
            obligation_id=obligation.obligation_id,
            transition_id=uuid4(),
            expected_revision=0,
            resulting_status="COMPLETED",
            rationale="Levée déclarée avec preuve référencée.",
            evidence_refs=["pv://synthetic/levee"],
        ),
    )
    with pytest.raises(CommandExecutionError, match="CLOSURE_VIEW_CONFLICT"):
        dispatcher.dispatch(context=ctx, command=exit_act)
    exit_act = exit_act.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "closure_review": exit_act.closure_review.model_copy(
                update={"expected_dossier_sha256": view()["dossier_sha256"]}
            ),
        }
    )
    dispatcher.dispatch(context=ctx, command=exit_act)
    rex = RecordExecutionRexCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=case,
        rex_id=uuid4(),
        exit_act_id=exit_act.act_id,
        publish_to_rex=True,
        lot_reference="01",
        scope="LOT_PATTERN",
        validation="APPROVED",
        observation="Finition reprise après réserve.",
        consequence="Mobilisation additionnelle déclarée.",
        follow_up="Prévoir contrôle de finition.",
        source_locator="pv://synthetic/p1",
        human_confirmed=True,
        justification="Enseignement relu humainement.",
        expected_dossier_sha256=view()["dossier_sha256"],
    )
    dispatcher.dispatch(context=ctx, command=rex)
    assert dispatcher.dispatch(context=ctx, command=rex).replayed
    interview = RecordCaseInterviewCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=case,
        interview_id=uuid4(),
        held_on="2026-10-25",
        expires_on="2027-01-01",
        source_locator="interview://synthetic",
        rationale="Enseignements d’exécution relus.",
    )
    dispatcher.dispatch(context=ctx, command=interview)
    with session_factory() as s:
        row = s.get(CaseRexRecord, rex.rex_id)
        assert row.p7_result_id is None and row.execution_exit_act_id == exit_act.act_id
        snap = s.get(CaseInterviewRecord, interview.interview_id).snapshot_json["rex"][0]
        assert snap["execution_exit_act_id"] == str(exit_act.act_id)
        assert "human_justification" not in snap["execution_source"]
    with session_factory() as s:
        with pytest.raises(sa.exc.DBAPIError):
            s.execute(
                sa.text("UPDATE case_rex SET observation=:value WHERE id=:id"),
                {"value": "historique effacé", "id": rex.rex_id},
            )
        s.rollback()
    from app.modules.pricing.application.case_closure_commands import (
        RecordExecutionTeachingReuseCommand,
    )

    target = uuid4()
    with session_factory.begin() as s:
        s.add(_case(tenant_id=tenant, case_id=target, marker="t"))
    with session_factory() as s:
        target_view = closure_dossier(s, tenant, target)
    reuse = RecordExecutionTeachingReuseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=target,
        target_case_id=target,
        source_case_id=case,
        source_interview_id=interview.interview_id,
        source_rex_id=rex.rex_id,
        applicability_id=uuid4(),
        decision="APPLICABLE",
        rationale="Réemploi décidé humainement pour le contrôle de finition.",
        target_source_locator="cctp://target/section1",
        human_confirmed=True,
        expected_target_dossier_sha256=target_view["dossier_sha256"],
    )
    result = dispatcher.dispatch(context=ctx, command=reuse)
    assert result.result_code == "CASE_TEACHING_APPLICABILITY_RECORDED"
    assert dispatcher.dispatch(context=ctx, command=reuse).replayed
    from app.modules.case.infrastructure.models.case import CaseRecord

    with session_factory.begin() as s:
        s.get(CaseRecord, target).dce_freshness = "REVIEW_REQUIRED"
    with session_factory() as s:
        changed = closure_dossier(s, tenant, target)
        assert changed["reuse_history"][0]["context_state"] == "REVIEW_REQUIRED"
    next_reuse = reuse.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "applicability_id": uuid4(),
            "expected_target_dossier_sha256": changed["dossier_sha256"],
        }
    )
    with pytest.raises(CommandExecutionError, match="EXECUTION_REX_TARGET_REVIEW_REQUIRED"):
        dispatcher.dispatch(context=ctx, command=next_reuse)
    with session_factory.begin() as s:
        s.get(CaseRecord, target).dce_freshness = "NO_DCE"
    with session_factory.begin() as s:
        from app.modules.case.infrastructure.models.case import CaseRecord

        row = s.get(CaseRecord, case)
        row.scope_fingerprint = "z" * 64
    reuse = reuse.model_copy(
        update={"command_id": uuid4(), "idempotency_key": uuid4(), "applicability_id": uuid4()}
    )
    with pytest.raises(CommandExecutionError, match="EXECUTION_REX_SOURCE_CHANGED"):
        dispatcher.dispatch(context=ctx, command=reuse)
    assert str(obligation.obligation_id) in view()["open_obligation_ids"]
    assert view()["legal_effect_state"] == "UNKNOWN"


def test_closure_http_enforces_finance_role_mfa_and_exact_receipts(session_factory):
    from dataclasses import replace
    from typing import cast

    from app.interfaces.http.routes.case_closure import build_case_closure_router
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.modules.pricing.application.case_closure import CaseClosureService, closure_handlers
    from app.platform.security.authenticated_context import AuthenticationContextResolver
    from app.platform.security.authorization import AuthorizationPolicy
    from app.platform.security.context import ActorKind
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tests.db.test_case_handover_http_e2e import TokenResolver
    from tests.db.test_regulatory_profile_persistence import _actor

    tenant, case = uuid4(), uuid4()
    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug=f"closure-http-{tenant.hex[:12]}", lifecycle="ACTIVE"))
        s.flush()
        s.add(_case(tenant_id=tenant, case_id=case, marker="h"))
    now = datetime.now(UTC)
    patron = replace(_actor(tenant, case), authenticated_at=now, mfa_verified_at=now)
    resolver = TokenResolver(
        {
            "patron": patron,
            "driver": replace(patron, actor_kind=ActorKind.COLLABORATEUR),
            "no-mfa": replace(patron, mfa_verified_at=None),
            "foreign": replace(patron, tenant_id=uuid4()),
        }
    )
    policy = AuthorizationPolicy()
    service = CaseClosureService(
        reader=SqlAlchemyCaseClosureReader(session_factory),
        dispatcher=CommandDispatcher(session_factory=session_factory, handlers=closure_handlers()),
        policy=policy,
    )
    app = FastAPI()
    app.include_router(
        build_case_closure_router(
            service=service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=cast(AuthenticationContextResolver, resolver), policy=policy
            ),
        )
    )
    client = TestClient(app)
    url = f"/api/v1/patron/cases/{case}/closure"
    assert client.get(url, headers={"Authorization": "Bearer driver"}).status_code == 403
    assert client.get(url, headers={"Authorization": "Bearer foreign"}).status_code == 404
    view = client.get(url, headers={"Authorization": "Bearer patron"})
    assert view.status_code == 200
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        fact_id=str(uuid4()),
        cycle_id=str(uuid4()),
        kind="PAYMENT_EXPECTED",
        amount_minor=12300,
        currency_code="EUR",
        declared_date="2026-10-25",
        source_refs=["invoice://synthetic"],
        evidence_refs=["proof://synthetic"],
        justification="Relecture humaine",
        human_confirmed=True,
        expected_dossier_sha256=view.json()["dossier_sha256"],
    )
    assert (
        client.post(
            url + "/payment-facts", json=body, headers={"Authorization": "Bearer no-mfa"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            url + "/payment-facts",
            json={**body, "human_confirmed": False},
            headers={"Authorization": "Bearer patron"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            url + "/payment-facts", json=body, headers={"Authorization": "Bearer patron"}
        ).status_code
        == 404
    )


def test_nonempty_downgrade_is_refused_and_legacy_cycle_survives_roundtrip(session_factory):
    from alembic import command
    from alembic.config import Config
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    # This migration fixture is independent of workflow test order.
    from datetime import date

    from app.modules.pricing.infrastructure.models.payment_cycle_fact import PaymentCycleFactRecord
    from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
        PaymentPostReceptionCycleRecord,
    )

    tenant_id, case_id, cycle_id = uuid4(), uuid4(), uuid4()
    with session_factory.begin() as s:
        s.add(
            TenantRecord(id=tenant_id, slug="migration-" + tenant_id.hex[:12], lifecycle="ACTIVE")
        )
        s.flush()
        s.add(_case(tenant_id=tenant_id, case_id=case_id, marker="n"))
        s.flush()
        s.add(
            PaymentPostReceptionCycleRecord(
                id=cycle_id,
                tenant_id=tenant_id,
                case_id=case_id,
                source_refs_json=["ccap://migration/1"],
                trigger_event="RECEPTION",
                status="REVIEW_REQUIRED",
                actor_id=uuid4(),
            )
        )
        s.flush()
        s.add(
            PaymentCycleFactRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=case_id,
                cycle_id=cycle_id,
                kind="PAYMENT_EXPECTED",
                amount_minor=100,
                currency_code="EUR",
                declared_date=date(2026, 10, 25),
                source_refs_json=["source://migration/1"],
                evidence_refs_json=["proof://migration/1"],
                justification="Fixture de migration synthétique.",
                source_snapshot_json={"case_source": None},
                actor_id=uuid4(),
            )
        )
    with session_factory() as s:
        head_before = s.scalar(sa.text("SELECT version_num FROM alembic_version"))
    with pytest.raises(RuntimeError, match="PAYMENT_FACT_HISTORY_DOWNGRADE_REFUSED"):
        command.downgrade(config, "20261025_0144")
    with session_factory.begin() as s:
        assert s.scalar(sa.text("SELECT version_num FROM alembic_version")) == head_before
        s.execute(sa.text("TRUNCATE tenants,identities CASCADE"))
    command.downgrade(config, "20261025_0144")
    tenant, case, cycle = uuid4(), uuid4(), uuid4()
    from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
        PaymentPostReceptionCycleRecord,
    )

    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug="legacy-" + tenant.hex[:12], lifecycle="ACTIVE"))
        s.flush()
        s.add(_case(tenant_id=tenant, case_id=case, marker="m"))
        s.flush()
        s.add(
            PaymentPostReceptionCycleRecord(
                id=cycle,
                tenant_id=tenant,
                case_id=case,
                source_refs_json=["ccap://legacy/section12"],
                trigger_event="RECEPTION",
                status="REVIEW_REQUIRED",
                actor_id=uuid4(),
            )
        )
    command.upgrade(config, "head")
    with session_factory() as s:
        assert s.get(PaymentPostReceptionCycleRecord, cycle).source_refs_json == [
            "ccap://legacy/section12"
        ]
        assert s.scalar(sa.text("SELECT count(*) FROM payment_cycle_facts")) == 0


def test_native_payment_writer_waits_for_the_case_review_lock(session_factory):
    from app.modules.case.infrastructure.models.case import CaseRecord

    tenant, case = uuid4(), uuid4()
    with session_factory.begin() as s:
        s.add(TenantRecord(id=tenant, slug="lock-" + tenant.hex[:12], lifecycle="ACTIVE"))
        s.flush()
        s.add(_case(tenant_id=tenant, case_id=case, marker="l"))
    from sqlalchemy.orm import sessionmaker

    engine = sa.create_engine(
        session_factory.kw["bind"].url, connect_args={"options": "-c lock_timeout=150ms"}
    )
    other = sessionmaker(engine, expire_on_commit=False)
    dispatcher = CommandDispatcher(session_factory=other, handlers=payment_cycle_handlers())
    command = RecordPaymentPostReceptionCycleCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        cycle_id=uuid4(),
        case_id=case,
        source_refs=["source://lock"],
        trigger_event="INVOICE",
        status="REVIEW_REQUIRED",
    )
    context = CommandContext(
        tenant_id=tenant,
        actor_id=uuid4(),
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(UTC),
        identity_id=uuid4(),
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case,
        correlation_id=uuid4(),
    )
    try:
        with session_factory() as locked:
            locked.scalar(
                sa.select(CaseRecord)
                .where(CaseRecord.tenant_id == tenant, CaseRecord.id == case)
                .with_for_update()
            )
            with pytest.raises(CommandExecutionError) as failure:
                dispatcher.dispatch(context=context, command=command)
            assert isinstance(failure.value.__cause__, sa.exc.OperationalError)
            assert "lock timeout" in str(failure.value.__cause__)
            locked.rollback()
        assert (
            dispatcher.dispatch(context=context, command=command).result_code
            == "PAYMENT_CYCLE_RECORDED"
        )
    finally:
        engine.dispose()
