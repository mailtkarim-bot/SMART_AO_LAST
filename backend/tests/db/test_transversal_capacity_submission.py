"""A replaced native planning hypothesis invalidates P5 without changing gate rules."""

from uuid import uuid4

from app.modules.decision.domain.submission_gate import evaluate_submission_gate
from app.modules.optimization.application.dated_commands import RecordDatedCapacityCommand
from app.modules.optimization.infrastructure.dated_service import (
    DatedCapacityService,
    RecordDatedCapacityHandler,
)
from app.modules.submission.infrastructure.decision_gate_reader import (
    SqlAlchemySubmissionDecisionGateReader,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy
from tests.db.test_commitment_card_workflow import finalize, prepare_decision
from tests.db.test_commitment_card_workflow import workflow as native_workflow


def test_native_capacity_replacement_cannot_leave_p5_submittable(session_factory, tmp_path):
    w = native_workflow.__wrapped__(session_factory, tmp_path)
    service = DatedCapacityService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDatedCapacity": RecordDatedCapacityHandler()},
        ),
        policy=AuthorizationPolicy(),
    )
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    cmd = RecordDatedCapacityCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        case_id=w.case,
        expected_revision=0,
        context_sha256=service.read(actor=w.actor, case_id=w.case, now=now)["context_sha256"],
        demands=None,
        supplies=None,
        justification="Hypothèse de ressources encore inconnue, relue humainement.",
        human_confirmed=True,
    )
    service.record(actor=w.actor, command=cmd, now=now)
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
            evidence_reference="Preuve synthétique relue humainement.",
        ),
    )
    assert resolved.status_code == 200, resolved.text
    reader = SqlAlchemySubmissionDecisionGateReader()
    with session_factory() as s:
        source = reader.read(session=s, tenant_id=w.actor.tenant_id, case_id=w.case)
        assert source is not None
        assert evaluate_submission_gate(source).can_submit
    replacement = cmd.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "run_id": uuid4(),
            "expected_revision": 1,
        }
    )
    service.record(actor=w.actor, command=replacement, now=now)
    with session_factory() as s:
        source = reader.read(session=s, tenant_id=w.actor.tenant_id, case_id=w.case)
        assert source is not None
        gate = evaluate_submission_gate(source)
        assert not gate.can_submit, (
            "P5 ignored the replaced capacity selected in the frozen context"
        )
        assert "DECISION_CONTEXT_NOT_FROZEN" in gate.reasons
