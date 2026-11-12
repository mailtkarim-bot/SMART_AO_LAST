from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.application.analysis_summary import AXES
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from tests.application.test_analysis_dossier import treatment
from tests.db.test_analysis_assessment_sql import record_setup
from tests.db.test_case_analysis_summary_sql import dossier as base_dossier


@pytest.fixture
def dossier(session_factory):
    return base_dossier.__wrapped__(session_factory)


def test_prepare_treat_review_and_invalidate_exact_dossier(session_factory, dossier):
    from app.bootstrap.application import AppRuntime
    from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
    from app.modules.case.infrastructure.analysis_assessment_handler import (
        RecordAnalysisAssessmentHandler,
    )
    from app.modules.case.infrastructure.analysis_dossier_handler import (
        RecordAnalysisDossierHandler,
    )

    seed, point, _, actor = record_setup(session_factory, dossier)
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory),
            "RecordAnalysisAssessment": RecordAnalysisAssessmentHandler(),
        },
    )
    runtime = SimpleNamespace(session_factory=session_factory)

    def read():
        return AppRuntime.get_case_analysis_summary(runtime, tenant_id=seed[0], case_id=seed[1])

    axes = [
        dict(
            code=c,
            state="UNKNOWN",
            note="Source/portée à instruire",
            follow_up="Le Patron relit les pièces",
            responsible="SELF",
        )
        for c, _ in AXES
    ]

    def command(summary, phase, revision):
        return RecordAnalysisDossierCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            review_id=uuid4(),
            case_id=seed[1],
            expected_revision=revision,
            dossier_sha256=summary["dossier_sha256"],
            phase=phase,
            axes=axes,
            justification="Relecture humaine synthétique",
            human_confirmed=True,
        )

    first = command(read(), "PREPARED", 0)
    dispatcher.dispatch(command=first, context=actor)
    assert dispatcher.dispatch(command=first, context=actor).replayed
    with pytest.raises(CommandExecutionError, match="UNPREPARED_POINTS"):
        dispatcher.dispatch(command=command(read(), "REVIEWED", 1), context=actor)
    dispatcher.dispatch(
        command=point.model_copy(
            update={
                "treatment": __import__(
                    "app.modules.case.application.analysis_dossier", fromlist=["AnalysisTreatment"]
                ).AnalysisTreatment(**treatment())
            }
        ),
        context=actor,
    )
    assert read()["dossier_review"]["state"] == "REVIEW_REQUIRED"
    second = command(read(), "PREPARED", 1)
    dispatcher.dispatch(command=second, context=actor)
    reviewed = command(read(), "REVIEWED", 2)
    dispatcher.dispatch(command=reviewed, context=actor)
    summary = read()
    assert (
        summary["dossier_review"]["state"] == "CURRENT"
        and summary["dossier_review"]["phase"] == "REVIEWED"
    )
    assert summary["analysis_complete"] is False
    from app.modules.case.infrastructure.models.case import CaseRecord

    with session_factory.begin() as s:
        s.get(CaseRecord, seed[1]).dce_freshness = "REVIEW_REQUIRED"
    summary = read()
    assert (
        summary["dossier_review"]["state"] == "REVIEW_REQUIRED"
        and summary["dossier_review"]["axes"] == []
    )
    history = AppRuntime.get_case_analysis_dossier_history(
        runtime, tenant_id=seed[0], case_id=seed[1]
    )
    assert history["entries"][0]["state"] == "HISTORICAL"
    assert history["entries"][0]["snapshot"]["dce_version_id"] == str(seed[2])
    assert history["entries"][0]["snapshot"]["analysis_complete"] is False
    assert history["entries"][0]["snapshot"]["axes"]
    with session_factory.begin() as s, pytest.raises(sa.exc.DBAPIError, match="APPEND_ONLY"):
        s.execute(
            sa.text(
                "UPDATE case_analysis_dossier_reviews SET justification='rewrite' WHERE case_id=:id"
            ),
            {"id": seed[1]},
        )


def test_dossier_locks_draft_financial_snapshot_against_concurrent_publication(
    session_factory, dossier
):
    from app.bootstrap.application import AppRuntime
    from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
    from app.modules.case.infrastructure.analysis_dossier_handler import (
        RecordAnalysisDossierHandler,
    )
    from app.modules.case.infrastructure.models.analysis_dossier import (
        AnalysisDossierReviewRecord as Review,
    )
    from app.modules.pricing.infrastructure.models import FinancialReportSnapshotRecord as Snapshot
    from sqlalchemy.orm import Session
    from tests.db.test_knowledge_source_freshness import NOW

    seed, _, _, actor = record_setup(session_factory, dossier)
    snapshot_id = uuid4()
    with session_factory.begin() as s:
        s.add(
            Snapshot(
                id=snapshot_id,
                tenant_id=seed[0],
                case_id=seed[1],
                state="DRAFT",
                currency_code="EUR",
                ruleset_version=1,
                aggregate_revision=0,
                calculated_at=NOW,
                published_at=None,
                sales_total_minor=0,
                direct_cost_total_minor=0,
                overhead_total_minor=0,
                subcontracting_total_minor=0,
                contingency_total_minor=0,
                gross_margin_minor=0,
                gross_margin_rate_bps=0,
                forecast_cashflow_minor=0,
            )
        )
    summary = AppRuntime.get_case_analysis_summary(
        SimpleNamespace(session_factory=session_factory), tenant_id=seed[0], case_id=seed[1]
    )
    cmd = RecordAnalysisDossierCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        review_id=uuid4(),
        case_id=seed[1],
        expected_revision=0,
        dossier_sha256=summary["dossier_sha256"],
        phase="PREPARED",
        axes=[
            dict(
                code=c, state="UNKNOWN", note="A instruire", follow_up="Relire", responsible="SELF"
            )
            for c, _ in AXES
        ],
        justification="Préparation",
        human_confirmed=True,
    )
    observed = []

    def check_lock(session, *args):
        if any(isinstance(row, Review) for row in session.new):
            with session_factory().bind.connect() as other:
                try:
                    other.execute(
                        sa.select(Snapshot.id)
                        .where(Snapshot.id == snapshot_id)
                        .with_for_update(nowait=True)
                    )
                    blocked = False
                except sa.exc.DBAPIError as error:
                    blocked = getattr(error.orig, "sqlstate", None) == "55P03"
            observed.append(blocked)
            assert blocked, "FINANCIAL_PUBLICATION_NOT_LOCKED"

    sa.event.listen(Session, "before_flush", check_lock)
    try:
        CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory)},
        ).dispatch(command=cmd, context=actor)
    finally:
        sa.event.remove(Session, "before_flush", check_lock)
    assert observed == [True]


def test_review_phase_and_populated_downgrade_are_enforced_in_postgresql(session_factory, dossier):
    from alembic import command as migration
    from alembic.config import Config
    from app.bootstrap.application import AppRuntime
    from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
    from app.modules.case.infrastructure.analysis_dossier_handler import (
        RecordAnalysisDossierHandler,
    )
    from app.modules.case.infrastructure.models.analysis_dossier import (
        AnalysisDossierReviewRecord as Review,
    )
    from tests.db.test_candidate_retrieval_sql import _clone
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    seed, _, _, actor = record_setup(session_factory, dossier)
    summary = AppRuntime.get_case_analysis_summary(
        SimpleNamespace(session_factory=session_factory), tenant_id=seed[0], case_id=seed[1]
    )
    cmd = RecordAnalysisDossierCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        review_id=uuid4(),
        case_id=seed[1],
        expected_revision=0,
        dossier_sha256=summary["dossier_sha256"],
        phase="PREPARED",
        axes=[
            dict(code=c, state="UNKNOWN", note="Inconnu", follow_up="Relire", responsible="SELF")
            for c, _ in AXES
        ],
        justification="Préparer",
        human_confirmed=True,
    )
    CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory)},
    ).dispatch(command=cmd, context=actor)
    with session_factory() as s:
        row = s.get(Review, (seed[0], cmd.review_id))
    with (
        pytest.raises(sa.exc.DBAPIError, match="ANALYSIS_DOSSIER_PHASE"),
        session_factory.begin() as s,
    ):
        s.add(
            _clone(row, id=uuid4(), phase="REVIEWED", command_id=uuid4(), idempotency_key=uuid4())
        )
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(sa.exc.DBAPIError, match="ANALYSIS_DOSSIER_PRESENT_DOWNGRADE_FORBIDDEN"):
        migration.downgrade(config, "20261020_0137")


@pytest.mark.parametrize("identical", [True, False])
def test_concurrent_dossier_preparations_have_one_first_revision(
    session_factory, dossier, identical
):
    from concurrent.futures import ThreadPoolExecutor

    from app.bootstrap.application import AppRuntime
    from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
    from app.modules.case.infrastructure.analysis_dossier_handler import (
        RecordAnalysisDossierHandler,
    )
    from app.modules.case.infrastructure.models.analysis_dossier import (
        AnalysisDossierReviewRecord as Review,
    )

    seed, _, _, actor = record_setup(session_factory, dossier)
    summary = AppRuntime.get_case_analysis_summary(
        SimpleNamespace(session_factory=session_factory), tenant_id=seed[0], case_id=seed[1]
    )
    cmd = RecordAnalysisDossierCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        review_id=uuid4(),
        case_id=seed[1],
        expected_revision=0,
        dossier_sha256=summary["dossier_sha256"],
        phase="PREPARED",
        axes=[
            dict(code=c, state="UNKNOWN", note="Inconnu", follow_up="Relire", responsible="SELF")
            for c, _ in AXES
        ],
        justification="Préparer",
        human_confirmed=True,
    )
    other = (
        cmd
        if identical
        else cmd.model_copy(
            update=dict(command_id=uuid4(), idempotency_key=uuid4(), review_id=uuid4())
        )
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory)},
    )

    def execute(value):
        try:
            return dispatcher.dispatch(command=value, context=actor)
        except CommandExecutionError as error:
            return str(error)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(execute, [cmd, other]))
    assert sum(isinstance(v, str) for v in results) == (0 if identical else 1)
    with session_factory() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count()).select_from(Review).where(Review.case_id == seed[1])
            )
            == 1
        )


def test_history_pagination_preserves_scope_and_snapshot_integrity(session_factory, dossier):
    from app.bootstrap.application import AppRuntime
    from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
    from app.modules.case.infrastructure.analysis_dossier_handler import (
        RecordAnalysisDossierHandler,
    )

    seed, _, _, actor = record_setup(session_factory, dossier)
    runtime = SimpleNamespace(session_factory=session_factory)
    summary = AppRuntime.get_case_analysis_summary(runtime, tenant_id=seed[0], case_id=seed[1])
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory)},
    )
    for revision in range(22):
        cmd = RecordAnalysisDossierCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            review_id=uuid4(),
            case_id=seed[1],
            expected_revision=revision,
            dossier_sha256=summary["dossier_sha256"],
            phase="PREPARED",
            axes=[
                dict(
                    code=c, state="UNKNOWN", note="Inconnu", follow_up="Relire", responsible="SELF"
                )
                for c, _ in AXES
            ],
            justification="Préparer",
            human_confirmed=True,
        )
        dispatcher.dispatch(command=cmd, context=actor)
    first = AppRuntime.get_case_analysis_dossier_history(
        runtime, tenant_id=seed[0], case_id=seed[1]
    )
    assert len(first["entries"]) == 20
    second = AppRuntime.get_case_analysis_dossier_history(
        runtime, tenant_id=seed[0], case_id=seed[1], before_revision=first["next_before_revision"]
    )
    assert len(second["entries"]) == 2 and second["next_before_revision"] is None
    assert {e["revision"] for e in first["entries"] + second["entries"]} == set(range(1, 23))
    assert (
        AppRuntime.get_case_analysis_dossier_history(runtime, tenant_id=uuid4(), case_id=seed[1])[
            "entries"
        ]
        == []
    )
    with session_factory.begin() as s:
        s.execute(sa.text("SET session_replication_role = replica"))
        s.execute(
            sa.text(
                "UPDATE case_analysis_dossier_reviews SET snapshot_json='{}'::jsonb "
                "WHERE case_id=:id AND revision=22"
            ),
            {"id": seed[1]},
        )
    with pytest.raises(ValueError, match="HISTORICAL_DOSSIER_INTEGRITY_UNPROVEN"):
        AppRuntime.get_case_analysis_dossier_history(runtime, tenant_id=seed[0], case_id=seed[1])
