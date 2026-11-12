from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from tests.application.test_analysis_assessment import fields
from tests.db.test_case_analysis_summary_sql import dossier as _dossier
from tests.db.test_case_analysis_summary_sql import read, risk_items
from tests.db.test_knowledge_source_freshness import NOW


@pytest.fixture
def dossier(session_factory):
    return _dossier.__wrapped__(session_factory)


def context(seed):
    return CommandContext(
        tenant_id=seed[0],
        actor_id=uuid4(),
        actor_kind="PATRON_ADMIN",
        membership_id=uuid4(),
        received_at=NOW,
        case_id=seed[1],
    )


def test_assessment_is_idempotent_revisioned_and_read_back(session_factory, dossier):
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.modules.case.infrastructure.analysis_assessment_handler import (
        RecordAnalysisAssessmentHandler,
    )

    seed, risk = dossier
    item = risk_items(read(session_factory, seed))[0]
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisAssessment": RecordAnalysisAssessmentHandler()},
    )
    command = RecordAnalysisAssessmentCommand(
        **dict(
            fields(),
            case_id=seed[1],
            point_id=risk,
            source_context_sha256=item["source_context_sha256"],
        )
    )
    actor = context(seed)
    first = dispatcher.dispatch(command=command, context=actor)
    retry = dispatcher.dispatch(command=command, context=actor)
    assert retry.aggregate_refs == first.aggregate_refs
    assert first.event_ids == ()
    assert retry.event_ids == ()
    item = risk_items(read(session_factory, seed))[0]
    assert item["human_assessment"]["revision"] == 1
    assert item["human_assessment"]["expected_evidence"] == "Attestation du fournisseur"
    assert item["human_assessment"]["residual_risk_state"] == "UNKNOWN"
    stale = command.model_copy(
        update=dict(command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4())
    )
    with pytest.raises(CommandExecutionError, match="STALE_ASSESSMENT_REVISION"):
        dispatcher.dispatch(command=stale, context=actor)


def record_setup(factory, dossier):
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.modules.case.infrastructure.analysis_assessment_handler import (
        RecordAnalysisAssessmentHandler,
    )

    seed, risk = dossier
    item = risk_items(read(factory, seed))[0]
    command = RecordAnalysisAssessmentCommand(
        **dict(
            fields(),
            case_id=seed[1],
            point_id=risk,
            source_context_sha256=item["source_context_sha256"],
        )
    )
    dispatcher = CommandDispatcher(
        session_factory=factory,
        handlers={"RecordAnalysisAssessment": RecordAnalysisAssessmentHandler()},
    )
    return seed, command, dispatcher, context(seed)


@pytest.mark.parametrize("identical", [True, False])
def test_concurrent_requests_never_create_two_first_revisions(session_factory, dossier, identical):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    barrier = Barrier(2)

    def send(index):
        candidate = (
            command
            if identical or index == 0
            else command.model_copy(
                update=dict(command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4())
            )
        )
        barrier.wait(timeout=10)
        try:
            return dispatcher.dispatch(command=candidate, context=actor)
        except CommandExecutionError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(send, [0, 1]))
    with session_factory() as s:
        assert (
            s.scalar(sa.select(sa.func.count()).select_from(Act).where(Act.case_id == seed[1])) == 1
        )
    if identical:
        assert sum(r.replayed for r in results) == 1
    else:
        assert "STALE_ASSESSMENT_REVISION" in results


@pytest.mark.parametrize("change", ["scope", "source", "tenant", "point"])
def test_invalid_context_refused_and_prior_values_not_transferred(session_factory, dossier, change):
    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )
    from app.modules.case.infrastructure.models.case import CaseRecord

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    dispatcher.dispatch(command=command, context=actor)
    if change == "scope":
        with session_factory.begin() as s:
            s.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == seed[1])
                .values(scope_fingerprint="e" * 64, scope_json={"lot": "9"})
            )
    elif change == "source":
        from datetime import timedelta

        from app.modules.dce.infrastructure.models.dce_extraction import (
            DceDocumentExtractionRecord as Extraction,
        )
        from tests.db.test_candidate_retrieval_sql import _clone

        with session_factory.begin() as s:
            old = s.get(Extraction, seed[4])
            s.add(
                _clone(
                    old,
                    id=uuid4(),
                    extractor_version=str(uuid4()),
                    created_at=NOW + timedelta(seconds=5),
                    status="REVIEW_REQUIRED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC",
                )
            )
    elif change == "tenant":
        from dataclasses import replace

        actor = replace(actor, tenant_id=uuid4())
    else:
        command = command.model_copy(update=dict(point_id=uuid4()))
    candidate = command.model_copy(
        update=dict(
            command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4(), expected_revision=1
        )
    )
    with pytest.raises(CommandExecutionError):
        dispatcher.dispatch(command=candidate, context=actor)
    if change in {"scope", "source"}:
        item = risk_items(read(session_factory, seed))[0]
        assert item["human_assessment"]["state"] == "REVIEW_REQUIRED"
        assert item["human_assessment"]["expected_evidence"] is None
        assert item["human_assessment"]["justification"] is None
    with session_factory() as s:
        assert (
            s.scalar(sa.select(sa.func.count()).select_from(Act).where(Act.case_id == seed[1])) == 1
        )


def test_assessment_sql_is_append_only_and_downgrade_refuses_data(
    session_factory, dossier, database_engine
):
    import importlib.util
    from pathlib import Path

    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )
    from sqlalchemy.exc import DBAPIError

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    dispatcher.dispatch(command=command, context=actor)
    for statement in [sa.update(Act).values(justification="modifié"), sa.delete(Act)]:
        with session_factory() as s, pytest.raises(DBAPIError, match="APPEND_ONLY"):
            s.execute(statement)
    spec = importlib.util.spec_from_file_location(
        "act_migration",
        Path(__file__).parents[2] / "alembic/versions/20261020_0137_case_analysis_assessments.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with (
        database_engine.begin() as connection,
        Operations.context(MigrationContext.configure(connection)),
        pytest.raises(RuntimeError, match="DOWNGRADE_FORBIDDEN"),
    ):
        module.downgrade()


def test_next_revision_preserves_history_and_exact_predecessor(session_factory, dossier):
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    dispatcher.dispatch(command=command, context=actor)
    second = RecordAnalysisAssessmentCommand(
        **dict(
            command.model_dump(),
            command_id=uuid4(),
            idempotency_key=uuid4(),
            assessment_id=uuid4(),
            expected_revision=1,
            residual_risk_state="DECLARED",
            residual_risk="Délai résiduel déclaré de deux jours",
            unknown_reason=None,
        )
    )
    dispatcher.dispatch(command=second, context=actor)
    with session_factory() as s:
        rows = s.scalars(sa.select(Act).where(Act.case_id == seed[1]).order_by(Act.revision)).all()
        assert len(rows) == 2 and rows[1].previous_assessment_id == rows[0].id
        assert rows[0].residual_risk_state == "UNKNOWN"
    item = risk_items(read(session_factory, seed))[0]
    assert item["human_assessment"]["revision"] == 2
    assert item["human_assessment"]["residual_risk"] == second.residual_risk


def test_http_act_mfa_permissions_receipt_and_conflicts(session_factory, dossier):
    from dataclasses import replace
    from types import SimpleNamespace

    from app.interfaces.http.routes.case_analysis_summary import build_case_analysis_summary_router
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.platform.security.authorization import AuthorizationPolicy
    from app.platform.security.capabilities import Capability, capabilities_for
    from app.platform.security.context import ActorKind
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tests.api.test_case_dce_reading_routes import _Resolver

    seed, command, dispatcher, _ = record_setup(session_factory, dossier)
    actor = replace(
        _Resolver().resolve(access_token="test-token"),
        tenant_id=seed[0],
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
    )
    from datetime import UTC, datetime

    actor = replace(
        actor, mfa_verified_at=datetime.now(tz=UTC), authenticated_at=datetime.now(tz=UTC)
    )
    current = [actor]

    def owner(**kw):
        with session_factory() as s:
            return s.scalar(sa.select(CaseRecord.tenant_id).where(CaseRecord.id == kw["case_id"]))

    app = FastAPI()
    app.include_router(
        build_case_analysis_summary_router(
            runtime=SimpleNamespace(
                dispatcher=dispatcher,
                get_case_tenant_id=owner,
                get_case_analysis_summary=lambda **kw: read(session_factory, seed),
            ),
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=SimpleNamespace(resolve=lambda **kw: current[0]),
                policy=AuthorizationPolicy(),
            ),
        )
    )
    client = TestClient(app)
    url = f"/api/v1/cases/{seed[1]}/analysis-assessments"
    headers = {"Authorization": "Bearer test-token"}
    body = command.model_dump(mode="json")
    body.pop("case_id")
    for blocked, status in [
        (replace(actor, tenant_id=uuid4()), 404),
        (replace(actor, actor_kind=ActorKind.COLLABORATEUR), 403),
        (replace(actor, mfa_verified_at=None), 403),
        (replace(actor, capabilities=actor.capabilities - {Capability.PRICING_WRITE}), 403),
        (replace(actor, capabilities=actor.capabilities - {Capability.DECISION_RISK_WRITE}), 403),
    ]:
        current[0] = blocked
        response = client.post(url, json=body, headers=headers)
        assert response.status_code == status and "expected_evidence" not in response.json()
    current[0] = actor
    first = client.post(url, json=body, headers=headers)
    assert first.status_code == 201, first.text
    assert client.post(url, json=body, headers=headers).status_code == 200
    conflicting = dict(body, justification="Payload discordant")
    assert client.post(url, json=conflicting, headers=headers).status_code == 409
    stale = dict(
        body, command_id=str(uuid4()), idempotency_key=str(uuid4()), assessment_id=str(uuid4())
    )
    assert client.post(url, json=stale, headers=headers).status_code == 409


def test_native_point_is_locked_through_assessment_insert(session_factory, dossier):
    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )
    from app.modules.decision.infrastructure.models.risk import DecisionRiskRecord
    from sqlalchemy.exc import DBAPIError
    from sqlalchemy.orm import Session

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    observed = []

    def check_lock(session, flush_context, instances):
        if any(isinstance(obj, Act) for obj in session.new):
            blocked = False
            with session_factory().bind.connect() as other:
                try:
                    other.execute(
                        sa.select(DecisionRiskRecord.id)
                        .where(DecisionRiskRecord.id == command.point_id)
                        .with_for_update(nowait=True)
                    )
                except DBAPIError as error:
                    blocked = getattr(error.orig, "sqlstate", None) == "55P03"
            observed.append(blocked)
            assert blocked, "NATIVE_POINT_NOT_LOCKED"

    sa.event.listen(Session, "before_flush", check_lock)
    try:
        dispatcher.dispatch(command=command, context=actor)
    finally:
        sa.event.remove(Session, "before_flush", check_lock)
    assert observed == [True]


def test_requirement_mutex_covers_first_confirmation(session_factory, tmp_path):
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.modules.case.infrastructure.analysis_assessment_handler import (
        RecordAnalysisAssessmentHandler,
    )
    from app.modules.case.infrastructure.models.analysis_assessment import (
        AnalysisAssessmentRecord as Act,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
    from sqlalchemy.exc import DBAPIError
    from sqlalchemy.orm import Session
    from tests.db.test_case_analysis_summary_sql import requirements_dossier

    seed = requirements_dossier.__wrapped__(session_factory, tmp_path)
    item = next(i for a in read(session_factory, seed)["axes"] for i in a["items"])
    command = RecordAnalysisAssessmentCommand(
        **dict(
            fields(),
            case_id=seed[1],
            point_kind="REQUIREMENT",
            point_id=item["item_id"],
            source_context_sha256=item["source_context_sha256"],
        )
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisAssessment": RecordAnalysisAssessmentHandler()},
    )
    seen = []

    def check_lock(session, *args):
        if any(isinstance(obj, Act) for obj in session.new):
            with session_factory().bind.connect() as other:
                with pytest.raises(DBAPIError) as error:
                    other.execute(
                        sa.select(DceRequirementRecord.id)
                        .where(DceRequirementRecord.id == command.point_id)
                        .with_for_update(nowait=True)
                    )
                assert error.value.orig.sqlstate == "55P03"
            seen.append(True)

    sa.event.listen(Session, "before_flush", check_lock)
    try:
        dispatcher.dispatch(command=command, context=context(seed))
    finally:
        sa.event.remove(Session, "before_flush", check_lock)
    assert seen == [True]


def test_retry_after_version_replacement_is_a_reconcilable_source_conflict(
    session_factory, dossier
):
    from hashlib import sha256

    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from tests.db.test_candidate_retrieval_sql import _clone

    seed, command, dispatcher, actor = record_setup(session_factory, dossier)
    with session_factory.begin() as s:
        original = s.get(DceVersionRecord, seed[2])
        replacement = uuid4()
        s.add(
            _clone(
                original, id=replacement, corpus_hash=sha256(str(replacement).encode()).hexdigest()
            )
        )
        s.flush()
        s.execute(
            sa.update(CaseRecord)
            .where(CaseRecord.id == seed[1])
            .values(applicable_dce_version_id=replacement, dce_freshness="REVIEW_REQUIRED")
        )
    with pytest.raises(CommandExecutionError, match="STALE_SOURCE_CONTEXT"):
        dispatcher.dispatch(command=command, context=actor)
