from uuid import uuid4

import pytest
from app.modules.decision.domain.submission_gate import evaluate_submission_gate
from app.modules.submission.infrastructure.decision_gate_reader import (
    SqlAlchemySubmissionDecisionGateReader,
)
from tests.db.test_commitment_card_workflow import (
    finalize,
    prepare_decision,
)
from tests.db.test_commitment_card_workflow import (
    workflow as native_workflow,
)


@pytest.fixture
def workflow(session_factory, tmp_path):
    return native_workflow.__wrapped__(session_factory, tmp_path)


def test_submission_refuses_a_replaced_frozen_assessment_even_after_condition_satisfaction(
    session_factory, workflow
):
    w = workflow
    decision, frozen = prepare_decision(w)
    condition, final = finalize(w, decision, frozen)
    resolved = w.client.post(
        w.url + f"/decisions/{decision}/conditions/{condition}/resolve",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            transition_id=str(uuid4()),
            expected_revision=final["version"],
            target_status="SATISFIED",
            evidence_reference="Plan synthétique accepté humainement",
        ),
    )
    assert resolved.status_code == 200, resolved.text
    reader = SqlAlchemySubmissionDecisionGateReader()
    with session_factory() as session:
        snapshot = reader.read(session=session, tenant_id=w.actor.tenant_id, case_id=w.case)
        assert snapshot is not None
        assert evaluate_submission_gate(snapshot).can_submit
    changed = w.assessment.model_copy(
        update=dict(
            command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4(), expected_revision=1
        )
    )
    w.dispatcher.dispatch(command=changed, context=w.context)
    with session_factory() as session:
        snapshot = reader.read(session=session, tenant_id=w.actor.tenant_id, case_id=w.case)
        assert snapshot is not None
        gate = evaluate_submission_gate(snapshot)
        assert not gate.can_submit
        assert "DECISION_CONTEXT_NOT_FROZEN" in gate.reasons
