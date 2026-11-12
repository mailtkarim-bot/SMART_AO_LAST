"""Execution facts reach existing source-bound human treatment/review contracts."""

from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
from app.modules.case.application.analysis_dossier import RecordAnalysisDossierCommand
from app.modules.case.application.analysis_summary import AXES
from app.modules.case.infrastructure.analysis_assessment_handler import (
    RecordAnalysisAssessmentHandler,
)
from app.modules.case.infrastructure.analysis_dossier_handler import RecordAnalysisDossierHandler
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from tests.application.test_analysis_assessment import fields
from tests.db.test_analysis_assessment_sql import context
from tests.db.test_l04_multilot_pipeline import complete_dossier as _complete_dossier
from tests.db.test_l04_multilot_pipeline import read
from tests.support.database import ALEMBIC_INI, DATABASE_URL

EXECUTION_TYPES = {
    "TECHNICAL_PRESCRIPTION": "TECHNICAL",
    "LOGISTICS_CONSTRAINT": "CONSTRUCTIBILITY",
    "SCHEDULE_CONSTRAINT": "CAPACITY",
    "HSE_CONSTRAINT": "HSE",
    "PAYMENT_TERM_SIGNAL": "CASH",
    "ACCEPTANCE_TERM_SIGNAL": "RIGHTS",
}
EXPECTED_GAPS = {
    ("ccap.txt", 6): "PAYMENT_TERM_SIGNAL",
    ("ccap.txt", 7): "ACCEPTANCE_TERM_SIGNAL",
    ("cctp-lot-1.txt", 3): "TECHNICAL_PRESCRIPTION",
    ("cctp-lot-1.txt", 4): "LOGISTICS_CONSTRAINT",
    ("cctp-lot-2.txt", 3): "TECHNICAL_PRESCRIPTION",
    ("cctp-lot-2.txt", 4): "TECHNICAL_PRESCRIPTION",
    ("planning.txt", 1): "SCHEDULE_CONSTRAINT",
    ("planning.txt", 2): "SCHEDULE_CONSTRAINT",
    ("planning.txt", 3): "SCHEDULE_CONSTRAINT",
    ("pgc.txt", 1): "HSE_CONSTRAINT",
    ("pgc.txt", 2): "HSE_CONSTRAINT",
}


@pytest.fixture(params=["dce_l04_multilot", "dce_l04_execution_holdout"])
def execution_dossier(session_factory, tmp_path, request):
    return _complete_dossier.__wrapped__(session_factory, tmp_path, request)


def test_eleven_previous_gaps_have_source_type_axis_and_unknown_safeguards(
    session_factory, execution_dossier
):
    seed = execution_dossier
    summary = read(session_factory, seed)
    items = [i for a in summary["axes"] for i in a["items"]]
    assert len(items) == seed[4].get("expected_point_count", 32)
    actual = [i for i in items if i["native_type"] in EXECUTION_TYPES]
    assert len(actual) == seed[4].get("expected_execution_count", 11)
    for doc in seed[4]["documents"]:
        for fact in doc["facts"]:
            expected = (
                fact.get("expected_type")
                if str(fact.get("expected_kind", "")).startswith("DCE_")
                else EXPECTED_GAPS.get((doc["file"], fact["line"]))
                if seed[4]["purpose"] == "DEVELOPMENT_SYNTHETIC_ONLY"
                else None
            )
            if not expected:
                continue
            point = next(i for i in actual if i["source_excerpt"] == fact["quote"])
            assert point["native_type"] == expected
            assert point["source_state"] == "CURRENT_SOURCE"
            assert point["source_anchor"]["dce_document_id"] == seed[3][doc["file"]]
            assert point["source_anchor"]["source_sha256"] == doc["sha256"]
            assert point["source_anchor"]["locator"]["coordinates"]["line"] == fact["line"]
            assert any(
                point in a["items"]
                for a in summary["axes"]
                if a["code"] == EXECUTION_TYPES[expected]
            )
            assert point["applicability"] == "UNKNOWN"
            if "expected_lots" in fact:
                assert point["lot_numbers"] == fact["expected_lots"]
                assert point["lot_state"] == fact["expected_lot_state"]
            if "sans" in fact["quote"] or "interdit" in fact["quote"]:
                assert point["lot_state"] == "UNKNOWN"
    assert not summary["analysis_complete"]


def test_every_execution_point_can_be_treated_then_exact_dossier_reviewed(
    session_factory, execution_dossier, *, initial_revision=0
):
    seed = execution_dossier
    actor = context(seed)
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "RecordAnalysisAssessment": RecordAnalysisAssessmentHandler(),
            "RecordAnalysisDossier": RecordAnalysisDossierHandler(session_factory),
        },
    )

    def review(summary, phase, revision):
        return RecordAnalysisDossierCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            review_id=uuid4(),
            case_id=seed[1],
            expected_revision=revision,
            dossier_sha256=summary["dossier_sha256"],
            phase=phase,
            axes=[
                dict(
                    code=c,
                    state="UNKNOWN",
                    note="Axe relu sans conclure à une complétude",
                    follow_up="Le Patron complète les preuves manquantes",
                    responsible="SELF",
                )
                for c, _ in AXES
            ],
            justification="Revue humaine synthétique des pièces exactes",
            human_confirmed=True,
        )

    initial = read(session_factory, seed)
    prepare = review(initial, "PREPARED", initial_revision)
    dispatcher.dispatch(command=prepare, context=actor)
    with pytest.raises(CommandExecutionError, match="UNPREPARED_POINTS"):
        dispatcher.dispatch(
            command=review(read(session_factory, seed), "REVIEWED", initial_revision + 1),
            context=actor,
        )
    for axis in initial["axes"]:
        for point in axis["items"]:
            payload = fields()
            payload.update(
                point_kind="REQUIREMENT",
                point_id=point["item_id"],
                case_id=seed[1],
                source_context_sha256=point["source_context_sha256"],
                expected_evidence="Preuve documentaire à obtenir sur le point exact",
                treatment=dict(
                    axis_code=axis["code"],
                    applicability="UNKNOWN",
                    applicability_reason="Portée métier à confirmer humainement",
                    consequences=dict(
                        technical=None, price=None, delay=None, cash=None, contract=None
                    ),
                    unknown_reason="Aucune conséquence chiffrée ni échéance qualifiée",
                    action="Relire la prescription et demander la preuve attendue",
                    responsible="SELF",
                    due_at=None,
                ),
            )
            cmd = RecordAnalysisAssessmentCommand(**payload)
            dispatcher.dispatch(command=cmd, context=actor)
            assert dispatcher.dispatch(command=cmd, context=actor).replayed
    treated = read(session_factory, seed)
    assert treated["dossier_review"]["state"] == "REVIEW_REQUIRED"
    assert all(
        i["human_assessment"]["state"] == "CURRENT" for a in treated["axes"] for i in a["items"]
    )
    dispatcher.dispatch(command=review(treated, "PREPARED", initial_revision + 1), context=actor)
    cmd = review(read(session_factory, seed), "REVIEWED", initial_revision + 2)
    dispatcher.dispatch(command=cmd, context=actor)
    assert dispatcher.dispatch(command=cmd, context=actor).replayed
    final = read(session_factory, seed)
    assert (
        final["dossier_review"]["phase"] == "REVIEWED"
        and final["dossier_review"]["state"] == "CURRENT"
    )
    assert not final["analysis_complete"]


def test_populated_execution_downgrade_refuses_proof_loss(session_factory, execution_dossier):
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="L04_EXECUTION_SIGNALS_PRESENT"):
        command.downgrade(cfg, "20261020_0138")
    assert len(
        [i for a in read(session_factory, execution_dossier)["axes"] for i in a["items"]]
    ) == execution_dossier[4].get("expected_point_count", 32)


def test_schema_roundtrip_preserves_legacy_signals(session_factory, tmp_path):
    import sqlalchemy as sa
    from app.modules.dce.infrastructure.models.dce_rc_analysis import (
        DceRcRequirementObservationRecord,
    )
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
    from tests.application.test_dce_rc_analysis import (
        _extract_then_analyze,
        _seed_admitted_document,
    )

    # Other tests leave no claim about populated rollback; isolate this legacy-only case.
    with session_factory.begin() as s:
        s.execute(sa.text("TRUNCATE tenants, identities CASCADE"))
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, doc, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=b"Le DC1 est obligatoire."
    )
    _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant,
        document_id=doc,
        dce_version_id=version,
    )

    def rows():
        with session_factory() as s:
            return s.execute(
                sa.select(
                    DceRcRequirementObservationRecord.id, DceRcRequirementObservationRecord.excerpt
                ).where(DceRcRequirementObservationRecord.tenant_id == tenant)
            ).all()

    before = rows()
    assert len(before) == 1
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    command.downgrade(cfg, "20261020_0138")
    assert rows() == before
    command.upgrade(cfg, "head")
    assert rows() == before
