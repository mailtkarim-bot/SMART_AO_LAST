from dataclasses import replace
from datetime import date
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.application.order import CaseOrderService, case_order_handlers
from app.modules.patron_action.application.order_commands import (
    RecordCaseDispositionCommand,
    RecordCaseOrderCommand,
    RecordCaseP6ControlCommand,
    RecordCaseP7ResultCommand,
    RecordCaseRetentionCommand,
    RecordCaseRexCommand,
    RequestCaseExportCommand,
)
from app.modules.patron_action.application.outcome import CaseOutcomeService, case_outcome_handlers
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.infrastructure.models import (
    CaseDispositionRecord,
    CaseExportRequestRecord,
    CaseOrderRecord,
    CaseP6ControlRecord,
    CaseP7ResultRecord,
    CaseRetentionRecord,
    CaseRexRecord,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorKind

from tests.application.test_collab_work_task import NOW, _seed


def _services(session_factory):
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={**case_outcome_handlers(), **case_order_handlers()},
    )
    policy = AuthorizationPolicy()
    return (
        CaseOutcomeService(dispatcher=dispatcher, session_factory=session_factory, policy=policy),
        CaseOrderService(dispatcher=dispatcher, session_factory=session_factory, policy=policy),
    )


def _patron(session_factory):
    actor, _assignment_id, case_id, _requirement_id = _seed(session_factory)
    with session_factory.begin() as session:
        case = session.get(CaseRecord, case_id)
        assert case is not None
        case.scope_kind = "MULTI_LOT"
        case.scope_json = {"lot_numbers": ["01"]}
    return replace(
        actor,
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
    ), case_id


def test_won_outcome_becomes_one_order_and_one_p6_with_stable_replay(session_factory):
    actor, case_id = _patron(session_factory)
    outcome_service, order_service = _services(session_factory)
    outcome_id = uuid4()
    outcome_command = RecordCaseOutcomeCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        outcome_id=outcome_id,
        case_id=case_id,
        lot_reference="01",
        outcome="WON",
        source_locator="boamp://result/01",
    )
    outcome_service.execute(actor=actor, command=outcome_command, now=NOW)
    collaborator = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        order_service.record_order(
            actor=collaborator,
            command=RecordCaseOrderCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                order_id=uuid4(),
                outcome_id=outcome_id,
                case_id=case_id,
                decision="ACCEPTED",
                rationale="Accès collaborateur interdit.",
            ),
            now=NOW,
        )
    order_command = RecordCaseOrderCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        order_id=uuid4(),
        outcome_id=outcome_id,
        case_id=case_id,
        decision="ACCEPTED",
        rationale="Le lot est retenu par le Patron.",
    )
    first = order_service.record_order(actor=actor, command=order_command, now=NOW)
    replay = order_service.record_order(actor=actor, command=order_command, now=NOW)
    assert first.result_code == replay.result_code == "CASE_ORDER_RECORDED"
    assert replay.replayed is True

    p6_command = RecordCaseP6ControlCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        p6_control_id=uuid4(),
        order_id=order_command.order_id,
        case_id=case_id,
        decision="APPROVED",
        reservations=["P6 à vérifier"],
        rationale="Le contrôle P6 est validé.",
    )
    p6_first = order_service.record_p6(actor=actor, command=p6_command, now=NOW)
    p6_replay = order_service.record_p6(actor=actor, command=p6_command, now=NOW)
    assert p6_first.result_code == p6_replay.result_code == "CASE_P6_RECORDED"
    assert p6_replay.replayed is True

    p7_command = RecordCaseP7ResultCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        p7_result_id=uuid4(),
        p6_control_id=p6_command.p6_control_id,
        case_id=case_id,
        result="UNKNOWN",
        reason="Le retour d'exécution n'est pas encore rapproché.",
        reservations=["Réception à confirmer"],
    )
    p7_first = order_service.record_p7(actor=actor, command=p7_command, now=NOW)
    p7_replay = order_service.record_p7(actor=actor, command=p7_command, now=NOW)
    assert p7_first.result_code == p7_replay.result_code == "CASE_P7_RECORDED"
    assert p7_replay.replayed is True

    rex_command = RecordCaseRexCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        rex_id=uuid4(),
        p7_result_id=p7_command.p7_result_id,
        case_id=case_id,
        motif="UNKNOWN",
        scope="CASE_ONLY",
        validation="PENDING",
        observation="Le retour n'est pas encore rapproché.",
        consequence="La clôture reste à vérifier.",
        follow_up="Relancer le donneur d'ordre.",
    )
    rex_first = order_service.record_rex(actor=actor, command=rex_command, now=NOW)
    rex_replay = order_service.record_rex(actor=actor, command=rex_command, now=NOW)
    assert rex_first.result_code == rex_replay.result_code == "CASE_REX_RECORDED"
    assert rex_replay.replayed is True
    listed_rex = order_service.list_rex(actor=actor, case_id=case_id, now=NOW)
    assert len(listed_rex) == 1 and listed_rex[0].scope == "CASE_ONLY"
    with pytest.raises(CommandExecutionError, match="ENTERPRISE_REX_REQUIRES_SOURCE_AND_APPROVAL"):
        order_service.record_rex(
            actor=actor,
            command=RecordCaseRexCommand(
                **{
                    **rex_command.model_dump(),
                    "rex_id": uuid4(),
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "scope": "ENTERPRISE_PATTERN",
                    "validation": "APPROVED",
                }
            ),
            now=NOW,
        )

    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseOrderRecord)
                .where(CaseOrderRecord.case_id == case_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseP6ControlRecord)
                .where(CaseP6ControlRecord.case_id == case_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseP7ResultRecord)
                .where(CaseP7ResultRecord.case_id == case_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseRexRecord)
                .where(CaseRexRecord.case_id == case_id)
            )
            == 1
        )


def test_order_and_p6_refuse_non_won_or_rejected_facts(session_factory):
    actor, case_id = _patron(session_factory)
    outcome_service, order_service = _services(session_factory)
    lost_id = uuid4()
    outcome_service.execute(
        actor=actor,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            outcome_id=lost_id,
            case_id=case_id,
            lot_reference="01",
            outcome="LOST",
        ),
        now=NOW,
    )
    with pytest.raises(CommandExecutionError, match="ONLY_WON_OUTCOMES_ORDERABLE"):
        order_service.record_order(
            actor=actor,
            command=RecordCaseOrderCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                order_id=uuid4(),
                outcome_id=lost_id,
                case_id=case_id,
                decision="ACCEPTED",
                rationale="Tentative interdite.",
            ),
            now=NOW,
        )
    won_id = uuid4()
    outcome_service.execute(
        actor=actor,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            outcome_id=won_id,
            case_id=case_id,
            lot_reference="01",
            outcome="WON",
            source_locator="boamp://result/rejected",
        ),
        now=NOW,
    )
    rejected = RecordCaseOrderCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        order_id=uuid4(),
        outcome_id=won_id,
        case_id=case_id,
        decision="REJECTED",
        rationale="Le lot est écarté.",
    )
    order_service.record_order(actor=actor, command=rejected, now=NOW)
    with pytest.raises(CommandExecutionError, match="ORDER_NOT_ACCEPTED"):
        order_service.record_p6(
            actor=actor,
            command=RecordCaseP6ControlCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                p6_control_id=uuid4(),
                order_id=rejected.order_id,
                case_id=case_id,
                decision="REJECTED",
                rationale="Aucun contrôle après écart.",
            ),
            now=NOW,
        )


def _completed_p7(order_service, outcome_service, *, actor, case_id, result="COMPLETED"):
    outcome_id = uuid4()
    outcome_service.execute(
        actor=actor,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            outcome_id=outcome_id,
            case_id=case_id,
            lot_reference="01",
            outcome="WON",
            source_locator="boamp://result/closure",
        ),
        now=NOW,
    )
    order_id = uuid4()
    order_service.record_order(
        actor=actor,
        command=RecordCaseOrderCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            order_id=order_id,
            outcome_id=outcome_id,
            case_id=case_id,
            decision="ACCEPTED",
            rationale="Commande validée pour preuve de fermeture.",
        ),
        now=NOW,
    )
    p6_id = uuid4()
    order_service.record_p6(
        actor=actor,
        command=RecordCaseP6ControlCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            p6_control_id=p6_id,
            order_id=order_id,
            case_id=case_id,
            decision="APPROVED",
            rationale="P6 validé pour preuve de fermeture.",
        ),
        now=NOW,
    )
    p7_id = uuid4()
    order_service.record_p7(
        actor=actor,
        command=RecordCaseP7ResultCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            p7_result_id=p7_id,
            p6_control_id=p6_id,
            case_id=case_id,
            result=result,
            source_locator="boamp://execution/closure" if result == "COMPLETED" else None,
            reason="Le résultat demeure à rapprocher." if result != "COMPLETED" else None,
        ),
        now=NOW,
    )
    return p7_id


def test_case_disposition_is_append_only_and_blocks_open_litigation(session_factory):
    actor, case_id = _patron(session_factory)
    outcome_service, order_service = _services(session_factory)
    p7_id = _completed_p7(order_service, outcome_service, actor=actor, case_id=case_id)
    suspension = RecordCaseDispositionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        disposition_id=uuid4(),
        case_id=case_id,
        state="SUSPENDED",
        reason_code="OPEN_LITIGATION",
        rationale="Le litige doit être traité avant fermeture.",
    )
    suspension_result = order_service.record_disposition(actor=actor, command=suspension, now=NOW)
    assert suspension_result.result_code == "CASE_DISPOSITION_RECORDED"
    assert (
        order_service.record_disposition(actor=actor, command=suspension, now=NOW).replayed is True
    )
    with pytest.raises(CommandExecutionError, match="CASE_LITIGATION_OPEN"):
        order_service.record_disposition(
            actor=actor,
            command=RecordCaseDispositionCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                disposition_id=uuid4(),
                case_id=case_id,
                state="CLOSED",
                reason_code="FINISHED",
                rationale="Fermeture interdite tant que le litige est ouvert.",
                p7_result_id=p7_id,
            ),
            now=NOW,
        )
    order_service.record_disposition(
        actor=actor,
        command=RecordCaseDispositionCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            disposition_id=uuid4(),
            case_id=case_id,
            state="RESUMED",
            reason_code="LITIGATION_RESOLVED",
            rationale="Le litige est résolu avec preuve conservée.",
        ),
        now=NOW,
    )
    closure = RecordCaseDispositionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        disposition_id=uuid4(),
        case_id=case_id,
        state="CLOSED",
        reason_code="FINISHED",
        rationale="P7 terminé, l'affaire peut être clôturée.",
        p7_result_id=p7_id,
    )
    assert order_service.record_disposition(actor=actor, command=closure, now=NOW).result_code == (
        "CASE_DISPOSITION_RECORDED"
    )
    assert order_service.record_disposition(actor=actor, command=closure, now=NOW).replayed is True
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseDispositionRecord)
                .where(CaseDispositionRecord.case_id == case_id)
            )
            == 3
        )


def test_case_closure_refuses_unknown_p7(session_factory):
    actor, case_id = _patron(session_factory)
    outcome_service, order_service = _services(session_factory)
    p7_id = _completed_p7(
        order_service, outcome_service, actor=actor, case_id=case_id, result="UNKNOWN"
    )
    with pytest.raises(CommandExecutionError, match="P7_NOT_COMPLETED"):
        order_service.record_disposition(
            actor=actor,
            command=RecordCaseDispositionCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                disposition_id=uuid4(),
                case_id=case_id,
                state="CLOSED",
                reason_code="FINISHED",
                rationale="La fermeture ne doit pas présumer un résultat inconnu.",
                p7_result_id=p7_id,
            ),
            now=NOW,
        )


def test_case_export_request_and_retention_are_separate_append_only_facts(session_factory):
    actor, case_id = _patron(session_factory)
    _outcome_service, order_service = _services(session_factory)
    export = RequestCaseExportCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        export_request_id=uuid4(),
        case_id=case_id,
        artifact_kind="CASE_DOSSIER",
        recipient_label="Conducteur de travaux",
        purpose="Préparer la passation du dossier, sans attester de réception.",
    )
    first_export = order_service.request_export(actor=actor, command=export, now=NOW)
    assert first_export.result_code == "CASE_EXPORT_REQUESTED"
    assert order_service.request_export(actor=actor, command=export, now=NOW).replayed is True
    retention = RecordCaseRetentionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        retention_id=uuid4(),
        case_id=case_id,
        evidence_locator="case://evidence/p7/01",
        retention_basis="MARKET_RECORD",
        retain_until=date(2036, 1, 1),
        rationale="Conserver la preuve de résultat avec le dossier de marché.",
    )
    first_retention = order_service.record_retention(actor=actor, command=retention, now=NOW)
    assert first_retention.result_code == "CASE_RETENTION_RECORDED"
    assert order_service.record_retention(actor=actor, command=retention, now=NOW).replayed is True
    collaborator = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        order_service.request_export(
            actor=collaborator,
            command=RequestCaseExportCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                export_request_id=uuid4(),
                case_id=case_id,
                artifact_kind="AUDIT_TRAIL",
                purpose="Tentative collaborateur interdite.",
            ),
            now=NOW,
        )
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseExportRequestRecord)
                .where(CaseExportRequestRecord.case_id == case_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseRetentionRecord)
                .where(CaseRetentionRecord.case_id == case_id)
            )
            == 1
        )
