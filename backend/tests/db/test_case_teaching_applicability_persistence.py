from dataclasses import replace
from datetime import UTC, date, datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.patron_action.application.case_interview_commands import RecordCaseInterviewCommand
from app.modules.patron_action.application.case_interview_handler import case_interview_handlers
from app.modules.patron_action.application.order import case_order_handlers
from app.modules.patron_action.application.order_commands import (
    RecordCaseOrderCommand,
    RecordCaseP6ControlCommand,
    RecordCaseP7ResultCommand,
    RecordCaseRexCommand,
)
from app.modules.patron_action.application.outcome import case_outcome_handlers
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.application.teaching_applicability_commands import (
    RecordCaseTeachingApplicabilityCommand,
)
from app.modules.patron_action.application.teaching_applicability_handler import (
    CaseTeachingApplicabilityService,
    case_teaching_applicability_handlers,
)
from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
from app.modules.patron_action.infrastructure.models.teaching_applicability import (
    CaseTeachingApplicabilityRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case

NOW = datetime(2026, 9, 30, 12, tzinfo=UTC)


def _seed(database_engine):
    tenant_id, source_case_id, target_case_id = uuid4(), uuid4(), uuid4()
    actor_id, membership_id = uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"app-{tenant_id.hex[:10]}", lifecycle="ACTIVE")
        )
        session.flush()
        source_case = _case(tenant_id=tenant_id, case_id=source_case_id, marker="s")
        target_case = _case(tenant_id=tenant_id, case_id=target_case_id, marker="t")
        for case in (source_case, target_case):
            case.scope_kind = "MULTI_LOT"
            case.scope_json = {"lot_numbers": ["01"]}
        session.add_all((source_case, target_case))
        session.commit()
    context = CommandContext(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_kind=ActorKind.PATRON_ADMIN.value,
        received_at=NOW,
        identity_id=actor_id,
        membership_id=membership_id,
        session_id=uuid4(),
        case_id=source_case_id,
        correlation_id=uuid4(),
    )
    actor = ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=frozenset({Capability.PATRON_ACTION_READ, Capability.PATRON_ACTION_WRITE}),
        assigned_case_ids=frozenset(),
        session_id=context.session_id,
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=context.correlation_id,
    )
    return tenant_id, source_case_id, target_case_id, context, actor


def _dispatcher(session_factory):
    return CommandDispatcher(
        session_factory=session_factory,
        handlers={
            **case_order_handlers(),
            **case_outcome_handlers(),
            **case_interview_handlers(),
            **case_teaching_applicability_handlers(),
        },
    )


def _record_source(
    dispatcher, context, source_case_id, *, scope="LOT_PATTERN", validation="APPROVED"
):
    outcome_id, order_id, p6_id, p7_id = uuid4(), uuid4(), uuid4(), uuid4()
    dispatcher.dispatch(
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            outcome_id=outcome_id,
            case_id=source_case_id,
            lot_reference="01",
            outcome="WON",
            source_locator="notification://source/1",
            reservations=[],
            unknown_reason=None,
        ),
        context=context,
    )
    dispatcher.dispatch(
        command=RecordCaseOrderCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            order_id=order_id,
            outcome_id=outcome_id,
            case_id=source_case_id,
            decision="ACCEPTED",
            rationale="Commande source rapprochée",
        ),
        context=context,
    )
    dispatcher.dispatch(
        command=RecordCaseP6ControlCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            p6_control_id=p6_id,
            order_id=order_id,
            case_id=source_case_id,
            decision="APPROVED",
            reservations=[],
            rationale="Revue source P6",
        ),
        context=context,
    )
    dispatcher.dispatch(
        command=RecordCaseP7ResultCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            p7_result_id=p7_id,
            p6_control_id=p6_id,
            case_id=source_case_id,
            result="COMPLETED",
            source_locator="proof://source/p7",
            reason=None,
            reservations=[],
        ),
        context=context,
    )
    rex_id = uuid4()
    dispatcher.dispatch(
        command=RecordCaseRexCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            rex_id=rex_id,
            p7_result_id=p7_id,
            case_id=source_case_id,
            motif="KNOWN",
            scope=scope,
            validation=validation,
            observation="Contrainte de coordination sourcée",
            consequence="Ordonnancement à contrôler",
            follow_up="Vérifier au lancement",
            source_locator="dce://source/section-4",
        ),
        context=context,
    )
    interview_id = uuid4()
    dispatcher.dispatch(
        command=RecordCaseInterviewCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            interview_id=interview_id,
            case_id=source_case_id,
            held_on=date(2026, 9, 29),
            source_locator="entretien://source/2026-09-29",
            rationale="Revue Patron de l’enseignement",
            expires_on=date(2027, 3, 30),
        ),
        context=context,
    )
    return interview_id, rex_id


def _command(
    target_case_id, source_case_id, source_interview_id, source_rex_id, *, decision="APPLICABLE"
):
    return RecordCaseTeachingApplicabilityCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        applicability_id=uuid4(),
        target_case_id=target_case_id,
        source_case_id=source_case_id,
        source_interview_id=source_interview_id,
        source_rex_id=source_rex_id,
        decision=decision,
        rationale="Le contexte de lot cible reprend la contrainte décrite.",
        target_source_locator="dce://target/cctp/lot-01",
    )


def test_applicability_copies_exact_teaching_snapshot_and_replays_once(
    database_engine, session_factory
) -> None:
    tenant_id, source_case_id, target_case_id, context, actor = _seed(database_engine)
    dispatcher = _dispatcher(session_factory)
    interview_id, rex_id = _record_source(dispatcher, context, source_case_id)
    command = _command(target_case_id, source_case_id, interview_id, rex_id)

    source_snapshot_before = None
    with Session(database_engine) as session:
        source_snapshot_before = session.scalar(
            sa.select(CaseInterviewRecord.snapshot_json).where(
                CaseInterviewRecord.tenant_id == tenant_id,
                CaseInterviewRecord.id == interview_id,
            )
        )
    service = CaseTeachingApplicabilityService(
        dispatcher=dispatcher, session_factory=session_factory, policy=AuthorizationPolicy()
    )
    recorded = service.record_applicability(actor=actor, command=command, now=NOW)
    replayed = service.record_applicability(actor=actor, command=command, now=NOW)

    assert recorded.result_code == "CASE_TEACHING_APPLICABILITY_RECORDED"
    assert replayed.replayed is True
    with Session(database_engine) as session:
        act = session.scalar(
            sa.select(CaseTeachingApplicabilityRecord).where(
                CaseTeachingApplicabilityRecord.tenant_id == tenant_id,
                CaseTeachingApplicabilityRecord.id == command.applicability_id,
            )
        )
        source_snapshot_after = session.scalar(
            sa.select(CaseInterviewRecord.snapshot_json).where(
                CaseInterviewRecord.tenant_id == tenant_id,
                CaseInterviewRecord.id == interview_id,
            )
        )
        assert act is not None
        assert act.source_snapshot_json == source_snapshot_before["rex"][0]
        assert act.source_validity_at_recording == "USABLE"
        assert source_snapshot_after == source_snapshot_before
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseTeachingApplicabilityRecord)
                .where(
                    CaseTeachingApplicabilityRecord.tenant_id == tenant_id,
                    CaseTeachingApplicabilityRecord.target_case_id == target_case_id,
                )
            )
            == 1
        )

    sources = service.list_sources(actor=actor, target_case_id=target_case_id, now=NOW)
    acts = service.list_for_case(actor=actor, target_case_id=target_case_id, now=NOW)
    assert len(sources) == 1 and sources[0].can_assess is True
    assert len(acts) == 1
    assert acts[0].source_validity == "USABLE"
    assert acts[0].record.source_snapshot_json == source_snapshot_before["rex"][0]

    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        service.list_sources(
            actor=replace(actor, actor_kind=ActorKind.COLLABORATEUR),
            target_case_id=target_case_id,
            now=NOW,
        )


@pytest.mark.parametrize(
    ("scope", "validation", "decision", "error"),
    [
        ("LOT_PATTERN", "PENDING", "APPLICABLE", "REX_APPROVAL_REQUIRED_FOR_APPLICABILITY"),
        ("CASE_ONLY", "APPROVED", "APPLICABLE", "CASE_ONLY_TEACHING_CANNOT_CROSS_CASES"),
    ],
)
def test_applicability_refuses_unapproved_or_out_of_scope_teaching(
    database_engine, session_factory, scope, validation, decision, error
) -> None:
    tenant_id, source_case_id, target_case_id, context, _ = _seed(database_engine)
    dispatcher = _dispatcher(session_factory)
    interview_id, rex_id = _record_source(
        dispatcher, context, source_case_id, scope=scope, validation=validation
    )

    with pytest.raises(CommandExecutionError, match=error):
        dispatcher.dispatch(
            command=_command(
                target_case_id, source_case_id, interview_id, rex_id, decision=decision
            ),
            context=context,
        )

    with Session(database_engine) as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseTeachingApplicabilityRecord)
                .where(CaseTeachingApplicabilityRecord.tenant_id == tenant_id)
            )
            == 0
        )


def test_applicability_refuses_a_source_or_target_from_another_tenant(
    database_engine, session_factory
) -> None:
    tenant_id, source_case_id, target_case_id, context, _ = _seed(database_engine)
    dispatcher = _dispatcher(session_factory)
    interview_id, rex_id = _record_source(dispatcher, context, source_case_id)
    foreign_tenant_id, foreign_case_id = uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(
                id=foreign_tenant_id,
                slug=f"foreign-{foreign_tenant_id.hex[:8]}",
                lifecycle="ACTIVE",
            )
        )
        session.flush()
        session.add(_case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="f"))
        session.commit()

    command = _command(foreign_case_id, source_case_id, interview_id, rex_id)
    with pytest.raises(CommandExecutionError, match="SOURCE_OR_TARGET_CASE_NOT_FOUND_OR_FORBIDDEN"):
        dispatcher.dispatch(command=command, context=context)

    with Session(database_engine) as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseTeachingApplicabilityRecord)
                .where(CaseTeachingApplicabilityRecord.tenant_id == tenant_id)
            )
            == 0
        )
