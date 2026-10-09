from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from app.modules.membership.application.collab_capability import (
    CollaboratorCapabilityAssessmentService,
)
from app.modules.membership.application.collab_capability_commands import (
    ProposeCapabilityForCaseCommand,
)
from app.modules.membership.application.collab_capability_ports import (
    AssignmentProjection,
    CollaboratorCapabilityAssessmentProjection,
)
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind

from tests.support.actors import make_actor_context

NOW = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)


def _service(
    reader: Mock, dispatcher: Mock, policy: Mock
) -> CollaboratorCapabilityAssessmentService:
    return CollaboratorCapabilityAssessmentService(
        reader=reader,
        dispatcher=dispatcher,
        policy=policy,
    )


def _authorized_policy() -> Mock:
    policy = Mock()
    policy.authorize.return_value = SimpleNamespace(allowed=True)
    return policy


def test_facade_proposes_through_reader_port_and_dispatcher() -> None:
    actor = make_actor_context(actor_kind=ActorKind.COLLABORATEUR)
    case_id = uuid4()
    assignment_id = uuid4()
    reader = Mock()
    reader.require_active_assignment.return_value = AssignmentProjection(
        id=assignment_id,
        case_id=case_id,
    )
    dispatcher = Mock()
    command = ProposeCapabilityForCaseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        proposal_id=uuid4(),
        case_id=case_id,
        assignment_id=assignment_id,
        capability_id=uuid4(),
        capability_version_id=uuid4(),
        requirement_id=uuid4(),
        justification="Synthetic human proposal",
    )

    result = _service(reader, dispatcher, _authorized_policy()).propose_capability(
        actor=actor,
        command=command,
        now=NOW,
    )

    assert result is dispatcher.dispatch.return_value
    reader.require_active_assignment.assert_called_once_with(
        tenant_id=actor.tenant_id,
        membership_id=actor.membership_id,
        case_id=case_id,
        assignment_id=assignment_id,
        required_action=Capability.PREPARATION_CAPABILITY_PROPOSE.value,
        received_at=NOW,
    )
    dispatcher.dispatch.assert_called_once()
    dispatched = dispatcher.dispatch.call_args.kwargs["command"]
    assert dispatched.proposal_id != command.proposal_id
    from uuid import NAMESPACE_URL, uuid5

    assert dispatched.proposal_id == uuid5(
        NAMESPACE_URL, f"case-capability-proposal:{actor.tenant_id}:{command.command_id}"
    )


def test_facade_reads_assessments_after_assignment_preflight() -> None:
    actor = make_actor_context(actor_kind=ActorKind.COLLABORATEUR)
    case_id = uuid4()
    assignment_id = uuid4()
    reader = Mock()
    reader.require_active_assignment.return_value = AssignmentProjection(
        id=assignment_id,
        case_id=case_id,
    )
    expected = CollaboratorCapabilityAssessmentProjection(proposals=(), gaps=())
    reader.read_assessments.return_value = expected

    result = _service(reader, Mock(), _authorized_policy()).read_assessments(
        actor=actor,
        case_id=case_id,
        assignment_id=assignment_id,
        now=NOW,
    )

    assert result == expected
    reader.read_assessments.assert_called_once_with(
        tenant_id=actor.tenant_id,
        case_id=case_id,
        assignment_id=assignment_id,
        evaluated_at=NOW,
    )


def test_facade_rejects_non_collaborator_before_using_reader() -> None:
    actor = make_actor_context(actor_kind=ActorKind.PATRON_ADMIN)
    reader = Mock()
    policy = _authorized_policy()

    try:
        _service(reader, Mock(), policy).read_assessments(
            actor=actor,
            case_id=uuid4(),
            assignment_id=uuid4(),
            now=NOW,
        )
    except PermissionError as error:
        assert str(error) == "COLLABORATOR_REQUIRED"
    else:
        raise AssertionError("expected a permission error")

    reader.require_active_assignment.assert_not_called()
    policy.authorize.assert_not_called()


def test_facade_case_only_read_uses_server_resolved_assignment() -> None:
    actor = make_actor_context(actor_kind=ActorKind.COLLABORATEUR)
    case_id, assignment_id = uuid4(), uuid4()
    reader, dispatcher = Mock(), Mock()
    reader.require_active_assignment.return_value = AssignmentProjection(
        id=assignment_id, case_id=case_id
    )
    reader.read_assessments.return_value = CollaboratorCapabilityAssessmentProjection(
        proposals=(), gaps=()
    )
    _service(reader, dispatcher, _authorized_policy()).read_assessments(
        actor=actor, case_id=case_id, now=NOW
    )
    assert reader.require_active_assignment.call_args.kwargs["assignment_id"] is None
    reader.read_assessments.assert_called_once_with(
        tenant_id=actor.tenant_id, case_id=case_id, assignment_id=assignment_id, evaluated_at=NOW
    )
    dispatcher.dispatch.assert_not_called()
