import pytest
from tests.db.test_commitment_card_workflow import workflow as native_workflow


@pytest.fixture
def workflow(session_factory, tmp_path):
    return native_workflow.__wrapped__(session_factory, tmp_path)


def test_migration_roundtrip_preserves_preexisting_human_acts(session_factory, workflow):
    from alembic import command as migration
    from alembic.config import Config
    from app.modules.case.infrastructure.models.analysis_assessment import AnalysisAssessmentRecord
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    w = workflow
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    migration.downgrade(config, "20261023_0141")
    migration.upgrade(config, "head")
    with session_factory() as session:
        act = session.get(AnalysisAssessmentRecord, (w.actor.tenant_id, w.assessment.assessment_id))
        assert act.treatment_json["hypotheses"] == "Deux rotations de livraison"
