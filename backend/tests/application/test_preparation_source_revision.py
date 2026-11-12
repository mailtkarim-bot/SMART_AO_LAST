"""Generation must use the same reviewed requirement facts as its readiness."""

from dataclasses import replace
from uuid import uuid4

import pytest
from app.modules.dce.application.commands import RecordDceRequirementConfirmationCommand
from app.modules.dce.application.handlers import RecordDceRequirementConfirmationHandler
from app.modules.dce.application.requirement_confirmation import DceRequirementConfirmationService
from app.modules.preparation.application.commands import GenerateTechnicalDocumentCommand
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.context import ActorKind

from tests.application.test_collab_work_task import NOW, _seed
from tests.application.test_preparation_completeness import (
    _confirm_requirement,
    _dce_version_id,
    _enable_preparation_scope,
    _readiness_command,
    preparation_service,  # noqa: F401
)


def test_changed_confirmation_cannot_reuse_readiness(preparation_service, session_factory):  # noqa: F811
    actor, assignment, case, requirement = _seed(session_factory)
    actor = _enable_preparation_scope(session_factory, actor, assignment)
    _confirm_requirement(session_factory, actor=actor, requirement_id=requirement)
    package = uuid4()
    preparation_service.execute(
        actor=actor,
        now=NOW,
        command=_readiness_command(
            actor=actor,
            assignment_id=assignment,
            case_id=case,
            dce_version_id=_dce_version_id(session_factory, actor.tenant_id),
            package_id=package,
            expected_revision=0,
        ),
    )
    confirmations = DceRequirementConfirmationService(
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementConfirmation": RecordDceRequirementConfirmationHandler()
            },
        ),
    )
    confirmations.confirm(
        actor=replace(actor, actor_kind=ActorKind.PATRON_ADMIN),
        now=NOW,
        command=RecordDceRequirementConfirmationCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            confirmation_id=uuid4(),
            requirement_id=requirement,
            expected_confirmation_revision=1,
            outcome="NOT_APPLICABLE",
            reason_code="PATRON_NOT_APPLICABLE",
        ),
    )
    with pytest.raises(CommandExecutionError, match="PREPARATION_READINESS_STALE"):
        preparation_service.execute(
            actor=actor,
            now=NOW,
            command=GenerateTechnicalDocumentCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                package_id=package,
                document_id=uuid4(),
                expected_revision=1,
                readiness_revision=1,
                document_kind="TECHNICAL_RESPONSE",
            ),
        )


@pytest.mark.parametrize("locked", ["requirement", "confirmation"])
def test_generation_refuses_competing_requirement_review(
    preparation_service,  # noqa: F811
    session_factory,
    locked,
):
    import sqlalchemy as sa
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationCurrentRecord,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord

    actor, assignment, case, requirement = _seed(session_factory)
    actor = _enable_preparation_scope(session_factory, actor, assignment)
    _confirm_requirement(session_factory, actor=actor, requirement_id=requirement)
    package = uuid4()
    preparation_service.execute(
        actor=actor,
        now=NOW,
        command=_readiness_command(
            actor=actor,
            assignment_id=assignment,
            case_id=case,
            dce_version_id=_dce_version_id(session_factory, actor.tenant_id),
            package_id=package,
            expected_revision=0,
        ),
    )
    command = GenerateTechnicalDocumentCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        package_id=package,
        document_id=uuid4(),
        expected_revision=1,
        readiness_revision=1,
        document_kind="TECHNICAL_RESPONSE",
    )
    with session_factory.begin() as competing:
        if locked == "requirement":
            competing.scalar(
                sa.select(DceRequirementRecord)
                .where(DceRequirementRecord.id == requirement)
                .with_for_update()
            )
        else:
            competing.scalar(
                sa.select(DceRequirementConfirmationCurrentRecord)
                .where(DceRequirementConfirmationCurrentRecord.requirement_id == requirement)
                .with_for_update()
            )
        with pytest.raises(CommandExecutionError, match="VERSION_CONFLICT"):
            preparation_service.execute(actor=actor, now=NOW, command=command)
    assert (
        preparation_service.execute(actor=actor, now=NOW, command=command).result_code
        == "TECHNICAL_DOCUMENT_GENERATED"
    )
