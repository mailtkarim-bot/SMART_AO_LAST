from uuid import uuid4

import pytest
from app.modules.decision.infrastructure.repositories import SqlAlchemyDecisionLifecycleRepository
from tests.db.test_commitment_card_workflow import workflow as native_workflow


@pytest.fixture
def workflow(session_factory, tmp_path):
    return native_workflow.__wrapped__(session_factory, tmp_path)


@pytest.mark.parametrize("boundary", ["commit", "rollback", "close"])
def test_source_cache_does_not_cross_transaction_or_session_reset(
    session_factory, workflow, boundary
):
    w = workflow
    repo = SqlAlchemyDecisionLifecycleRepository()

    def valid(session):
        return repo.context_reference_is_valid(
            session=session,
            tenant_id=w.actor.tenant_id,
            case_id=w.case,
            aggregate_type="ANALYSIS_ASSESSMENT",
            aggregate_id=w.assessment.assessment_id,
            aggregate_revision=1,
            content_hash=w.assessment.source_context_sha256,
        )

    with session_factory() as session:
        assert valid(session)
        getattr(session, boundary)()
        changed = w.assessment.model_copy(
            update=dict(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                assessment_id=uuid4(),
                expected_revision=1,
            )
        )
        w.dispatcher.dispatch(command=changed, context=w.context)
        assert not valid(session)


def test_source_scope_refreshes_even_with_a_retained_orm_identity(session_factory, workflow):
    from app.modules.case.infrastructure.models.case import CaseRecord

    w = workflow
    repo = SqlAlchemyDecisionLifecycleRepository()

    def valid(session):
        return repo.context_reference_is_valid(
            session=session,
            tenant_id=w.actor.tenant_id,
            case_id=w.case,
            aggregate_type="ANALYSIS_ASSESSMENT",
            aggregate_id=w.assessment.assessment_id,
            aggregate_revision=1,
            content_hash=w.assessment.source_context_sha256,
        )

    with session_factory() as session:
        retained = session.get(CaseRecord, w.case)
        assert valid(session)
        session.commit()
        with session_factory.begin() as writer:
            changed = writer.get(CaseRecord, w.case)
            changed.scope_fingerprint = "9" * 64
            changed.scope_json = {"lot": "9"}
        assert not valid(session)
        assert retained.scope_fingerprint == "9" * 64
