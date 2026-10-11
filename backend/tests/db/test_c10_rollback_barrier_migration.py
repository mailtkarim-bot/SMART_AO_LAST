"""C10 legacy rollback barriers upgrade and downgrade reversibly."""

from uuid import uuid4

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.preparation.infrastructure.models.preparation import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationReadinessRecord,
    PreparationResponsePlanRecord,
)
from app.modules.submission.infrastructure.models import SubmissionPackageRecord
from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
from sqlalchemy.orm import Session, sessionmaker
from tests.application.test_collab_capability import _seed
from tests.support.database import ALEMBIC_INI, DATABASE_URL

_C10_TRIGGERS = {
    "c10_submission_candidate_rollback_guard",
    "c10_submission_authorization_rollback_guard",
    "c10_submission_export_rollback_guard",
}


def _trigger_names(engine: sa.Engine) -> set[str]:
    with engine.connect() as connection:
        return set(
            connection.scalars(
                sa.text(
                    "SELECT tgname FROM pg_trigger "
                    "WHERE NOT tgisinternal AND tgname LIKE 'c10_submission_%_rollback_guard'"
                )
            )
        )


def test_c10_rollback_barriers_upgrade_downgrade_and_reupgrade(database_engine: sa.Engine) -> None:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)

    assert EXPECTED_ALEMBIC_HEAD == "20261010_0136"
    assert _trigger_names(database_engine) == _C10_TRIGGERS

    command.downgrade(config, "20261009_0135")
    assert _trigger_names(database_engine) == set()

    command.upgrade(config, "head")
    assert _trigger_names(database_engine) == _C10_TRIGGERS


def test_c10_rollback_barrier_cannot_be_downgraded_with_a_response_plan(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    actor, assignment_id, case_id, *_ = _seed(session_factory)
    package_id, plan_id = uuid4(), uuid4()

    with session_factory.begin() as session:
        dce_version_id = session.scalar(
            sa.select(CaseRecord.applicable_dce_version_id).where(
                CaseRecord.tenant_id == actor.tenant_id,
                CaseRecord.id == case_id,
            )
        )
        session.add(
            PreparationPackageRecord(
                id=package_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                assignment_id=assignment_id,
                dce_version_id=dce_version_id,
                state="IN_PREPARATION",
                aggregate_revision=0,
                created_by_actor_id=actor.actor_id,
                membership_id=actor.membership_id,
            )
        )
        session.add(
            PreparationResponsePlanRecord(
                id=uuid4(),
                tenant_id=actor.tenant_id,
                plan_id=plan_id,
                package_id=package_id,
                dce_version_id=dce_version_id,
                version=1,
                state="SOURCES_CURRENT",
                content_json={},
                plan_sha256="a" * 64,
                source_evidence_json=[],
                source_evidence_sha256="b" * 64,
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )

    with pytest.raises(
        sa.exc.DBAPIError, match="C10_SUBMISSION_ROLLBACK_BARRIER_DOWNGRADE_BLOCKED"
    ):
        command.downgrade(config, "20261009_0135")

    assert _trigger_names(database_engine) == _C10_TRIGGERS
    with database_engine.connect() as connection:
        assert connection.scalar(sa.text("SELECT version_num FROM alembic_version")) == (
            EXPECTED_ALEMBIC_HEAD
        )


def test_c10_rollback_barrier_cannot_be_downgraded_with_schema3_candidate(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    actor, assignment_id, case_id, *_ = _seed(session_factory)
    package_id, readiness_id, document_id, candidate_id = (uuid4() for _ in range(4))

    with session_factory.begin() as session:
        dce_version_id = session.scalar(
            sa.select(CaseRecord.applicable_dce_version_id).where(
                CaseRecord.tenant_id == actor.tenant_id,
                CaseRecord.id == case_id,
            )
        )
        session.add(
            PreparationPackageRecord(
                id=package_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                assignment_id=assignment_id,
                dce_version_id=dce_version_id,
                state="IN_PREPARATION",
                aggregate_revision=0,
                created_by_actor_id=actor.actor_id,
                membership_id=actor.membership_id,
            )
        )
        session.add(
            PreparationReadinessRecord(
                id=readiness_id,
                tenant_id=actor.tenant_id,
                package_id=package_id,
                revision=1,
                state="READY",
                blocker_codes_json=[],
                warning_codes_json=[],
                checked_requirement_count=0,
                checked_task_count=0,
                input_manifest_sha256="a" * 64,
                evaluator_id="rollback-test",
                evaluator_version="1",
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.add(
            GeneratedTechnicalDocumentRecord(
                id=document_id,
                tenant_id=actor.tenant_id,
                package_id=package_id,
                readiness_id=readiness_id,
                version=1,
                document_kind="TECHNICAL_RESPONSE",
                state="GENERATED",
                content_sha256="b" * 64,
                storage_key=f"generated-documents/{document_id}.md",
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.execute(sa.select(sa.func.set_config("smartao.c10_candidate_qualified", "1", True)))
        session.add(
            SubmissionPackageRecord(
                id=candidate_id,
                tenant_id=actor.tenant_id,
                preparation_package_id=package_id,
                case_id=case_id,
                dce_version_id=dce_version_id,
                technical_document_id=document_id,
                technical_document_version=1,
                financial_snapshot_id=None,
                financial_snapshot_revision=None,
                version=1,
                state="PRET_CONTROLE",
                manifest_sha256="c" * 64,
                manifest_json={"schema_version": 3, "preparation_source": {}},
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )

    with pytest.raises(
        sa.exc.DBAPIError, match="C10_SUBMISSION_ROLLBACK_BARRIER_DOWNGRADE_BLOCKED"
    ):
        command.downgrade(config, "20261009_0135")

    assert _trigger_names(database_engine) == _C10_TRIGGERS
    with database_engine.connect() as connection:
        assert connection.scalar(sa.text("SELECT version_num FROM alembic_version")) == (
            EXPECTED_ALEMBIC_HEAD
        )
