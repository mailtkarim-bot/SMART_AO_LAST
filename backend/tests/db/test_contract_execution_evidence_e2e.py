# ruff: noqa: E501, I001
from datetime import UTC, date, datetime
from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.application.commands import LinkCaseDceVersionCommand
from app.modules.case.application.link_dce_version_handler import LinkCaseDceVersionHandler
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.pricing.application.contract_execution_evidence_commands import (
    DeclareContractInstrumentSupersessionCommand,
    RecordContractExecutionEvidenceCommand,
    RecordContractExecutionEvidenceRequalificationCommand,
    RecordContractInstrumentVersionCommand,
)
from app.modules.pricing.application.contract_execution_evidence_handler import (
    contract_execution_evidence_handlers,
)
from app.modules.pricing.application.contract_execution_evidence_read_handler import (
    ContractExecutionEvidenceReadService,
    ContractInstrumentSupersessionReadService,
    ContractInstrumentVersionReadService,
)
from app.modules.pricing.application.contract_execution_evidence_requalification_handler import (
    contract_execution_evidence_requalification_handlers,
)
from app.modules.pricing.application.contract_execution_evidence_requalification_read_handler import (
    ContractExecutionEvidenceRequalificationReadService,
)
from app.modules.pricing.application.contract_execution_evidence_timeline_read_handler import (
    ContractExecutionEvidenceTimelineReadService,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence import (
    ContractExecutionEvidenceRecord,
)
from app.modules.pricing.infrastructure.models.contract_execution_evidence_requalification import (
    ContractExecutionEvidenceRequalificationRecord,
)
from app.modules.pricing.application.contract_instrument_version_handler import (
    contract_instrument_version_handlers,
)
from app.modules.pricing.application.contract_instrument_supersession_handler import (
    contract_instrument_supersession_handlers,
)
from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
    ContractInstrumentSupersessionRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.context import ActorKind
from tests.db.test_regulatory_profile_persistence import _case


def test_contract_execution_evidence_is_tenant_scoped_append_only_and_idempotent(
    database_engine, session_factory
) -> None:
    tenant_id, foreign_tenant_id, case_id, foreign_case_id, actor_id = (
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with Session(database_engine) as session:
        session.add_all(
            [
                TenantRecord(id=tenant_id, slug=f"ce-{tenant_id.hex[:10]}", lifecycle="ACTIVE"),
                TenantRecord(
                    id=foreign_tenant_id,
                    slug=f"ce-{foreign_tenant_id.hex[:10]}",
                    lifecycle="ACTIVE",
                ),
            ]
        )
        session.flush()
        session.add_all(
            [
                _case(tenant_id=tenant_id, case_id=case_id, marker="e"),
                _case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="f"),
            ]
        )
        session.commit()

    command = RecordContractExecutionEvidenceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=uuid4(),
        case_id=case_id,
        act_kind="RIGHTS_PRESERVATION",
        summary="Réserve envoyée au maître d’ouvrage",
        source_refs=("ccap://version/3/clause/18",),
        evidence_refs=("document://courrier/sha256:abc", "document://accuse/sha256:def"),
        declared_event_date=date(2026, 9, 27),
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=contract_execution_evidence_handlers()
    )
    context = CommandContext(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(tz=UTC),
        identity_id=actor_id,
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case_id,
        correlation_id=uuid4(),
    )
    first = dispatcher.dispatch(command=command, context=context)
    replay = dispatcher.dispatch(command=command, context=context)
    assert first.result_code == "CONTRACT_EXECUTION_EVIDENCE_RECORDED"
    assert replay.replayed is True

    foreign_context = CommandContext(
        tenant_id=foreign_tenant_id,
        actor_id=actor_id,
        actor_kind="PATRON_ADMIN",
        received_at=datetime.now(tz=UTC),
        identity_id=actor_id,
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case_id,
        correlation_id=uuid4(),
    )
    cross_tenant_command = command.model_copy(
        update={"command_id": uuid4(), "idempotency_key": uuid4(), "act_id": uuid4()}
    )
    with pytest.raises(CommandExecutionError, match="CASE_NOT_FOUND_OR_FORBIDDEN"):
        dispatcher.dispatch(command=cross_tenant_command, context=foreign_context)

    service = ContractExecutionEvidenceReadService(session_factory=session_factory)
    actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
    )
    foreign_actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=foreign_tenant_id
    )
    projection = service.list_for_case(actor=actor, case_id=case_id)
    assert len(projection) == 1
    assert projection[0].record.evidence_refs_json == list(command.evidence_refs)
    assert projection[0].record.declared_event_date == date(2026, 9, 27)
    assert projection[0].version_relation == "UNKNOWN"
    assert projection[0].record.contract_instrument_version_id is None
    assert projection[0].contract_instrument_version is None
    assert service.list_for_case(actor=foreign_actor, case_id=case_id) == ()

    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(ContractExecutionEvidenceRecord)
            .where(ContractExecutionEvidenceRecord.id == command.act_id)
            .values(summary="Réécriture interdite")
        )
    with Session(database_engine) as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(ContractExecutionEvidenceRecord))
            == 1
        )


def test_rectification_keeps_act_source_version_and_requests_requalification(
    database_engine, session_factory
) -> None:
    tenant_id, case_id, other_case_id, consultation_id, v1_id, v2_id, actor_id = (
        uuid4() for _ in range(7)
    )
    now = datetime.now(tz=UTC)
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"ce-version-{tenant_id.hex[:10]}", lifecycle="ACTIVE")
        )
        session.flush()
        session.add(
            ConsultationRecord(
                id=consultation_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="d" * 64,
                buyer_legal_name="Acheteur test",
                buyer_normalized_id="ACHETEUR-TEST",
                external_reference="RECT-01",
                object_label="Travaux test",
                location_label="Lyon",
                source_channel="MANUAL_UPLOAD",
                source_reference="Fixture versionnée",
                source_received_at=now,
                lifecycle="OPEN",
                freshness="CURRENT",
                metadata_history_json=[],
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
        session.flush()
        v1 = DceVersionRecord(
            id=v1_id,
            tenant_id=tenant_id,
            aggregate_revision=1,
            consultation_id=consultation_id,
            corpus_hash="1" * 64,
            predecessor_dce_version_id=None,
            provenance_channel="MANUAL_UPLOAD",
            provenance_reference="DCE initial",
            provenance_url=None,
            source_received_at=now,
            lifecycle="ADMITTED",
            integrity="VERIFIED",
            classification_readiness="CLASSIFIED",
            analysis_readiness="READY_FOR_ANALYSIS",
            withdrawal_source=None,
            withdrawal_reason=None,
            superseded_at=None,
            withdrawn_at=None,
            created_by_actor_id=None,
            updated_by_actor_id=None,
        )
        v2 = DceVersionRecord(
            id=v2_id,
            tenant_id=tenant_id,
            aggregate_revision=1,
            consultation_id=consultation_id,
            corpus_hash="2" * 64,
            predecessor_dce_version_id=v1_id,
            provenance_channel="RECTIFICATION",
            provenance_reference="Rectificatif 1",
            provenance_url=None,
            source_received_at=now,
            lifecycle="ADMITTED",
            integrity="VERIFIED",
            classification_readiness="CLASSIFIED",
            analysis_readiness="READY_FOR_ANALYSIS",
            withdrawal_source=None,
            withdrawal_reason=None,
            superseded_at=None,
            withdrawn_at=None,
            created_by_actor_id=None,
            updated_by_actor_id=None,
        )
        case = _case(tenant_id=tenant_id, case_id=case_id, marker="v")
        other_case = _case(tenant_id=tenant_id, case_id=other_case_id, marker="x")
        case.consultation_id = consultation_id
        case.applicable_dce_version_id = v1_id
        case.dce_freshness = "CURRENT"
        session.add_all([v1, v2])
        session.flush()
        session.add_all([case, other_case])
        session.commit()

    actor_context = CommandContext(
        tenant_id=tenant_id,
        actor_id=actor_id,
        actor_kind="PATRON_ADMIN",
        received_at=now,
        identity_id=actor_id,
        membership_id=uuid4(),
        session_id=uuid4(),
        case_id=case_id,
        correlation_id=uuid4(),
    )
    instrument_version_command = RecordContractInstrumentVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        contract_instrument_version_id=uuid4(),
        case_id=case_id,
        instrument_kind="SIGNED_CONTRACT",
        version_reference="MARCHE-SIGNE-2026-04-12",
        source_refs=("contract://document/marche-2026",),
        evidence_refs=("document://marche/sha256:def",),
    )
    instrument_dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=contract_instrument_version_handlers()
    )
    version_result = instrument_dispatcher.dispatch(
        command=instrument_version_command, context=actor_context
    )
    assert version_result.result_code == "CONTRACT_INSTRUMENT_VERSION_RECORDED"
    assert (
        instrument_dispatcher.dispatch(
            command=instrument_version_command, context=actor_context
        ).replayed
        is True
    )
    other_case_version_command = RecordContractInstrumentVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        contract_instrument_version_id=uuid4(),
        case_id=other_case_id,
        instrument_kind="SIGNED_CONTRACT",
        version_reference="MARCHE-AUTRE-AFFAIRE",
        source_refs=("contract://other-case",),
        evidence_refs=("document://other-case",),
    )
    instrument_dispatcher.dispatch(
        command=other_case_version_command,
        context=replace(actor_context, case_id=other_case_id),
    )
    version_reader = ContractInstrumentVersionReadService(session_factory=session_factory)
    registered_versions = version_reader.list_for_case(
        actor=SimpleNamespace(
            actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
        ),
        case_id=case_id,
    )
    assert len(registered_versions) == 1
    assert registered_versions[0].source_refs_json == ["contract://document/marche-2026"]
    duplicate_reference = instrument_version_command.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "contract_instrument_version_id": uuid4(),
        }
    )
    with pytest.raises(
        CommandExecutionError, match="CONTRACT_INSTRUMENT_VERSION_REFERENCE_ALREADY_RECORDED"
    ):
        instrument_dispatcher.dispatch(command=duplicate_reference, context=actor_context)
    command = RecordContractExecutionEvidenceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=uuid4(),
        case_id=case_id,
        act_kind="RIGHTS_PRESERVATION",
        summary="Réserve liée au DCE initial",
        source_refs=("dce-version://initial/clause/18",),
        evidence_refs=("document://reserve/sha256:abc",),
        declared_event_date=date(2026, 9, 28),
        contract_instrument_version_id=instrument_version_command.contract_instrument_version_id,
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=contract_execution_evidence_handlers()
    )
    dispatcher.dispatch(command=command, context=actor_context)
    service = ContractExecutionEvidenceReadService(session_factory=session_factory)
    actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=tenant_id
    )
    original = service.list_for_case(actor=actor, case_id=case_id)[0]
    assert original.version_relation == "MATCHES_CASE_CURRENT"
    assert original.contract_instrument_version_relation == "DECLARED"
    assert original.record.case_dce_version_id_at_recording == v1_id

    amendment_command = RecordContractInstrumentVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        contract_instrument_version_id=uuid4(),
        case_id=case_id,
        instrument_kind="AMENDMENT",
        version_reference="AVENANT-1-2026-09-29",
        source_refs=("contract://amendment/1",),
        evidence_refs=("document://amendment/1/sha256:abc",),
    )
    instrument_dispatcher.dispatch(command=amendment_command, context=actor_context)
    supersession_dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers=contract_instrument_supersession_handlers(),
    )
    cross_case_declaration = DeclareContractInstrumentSupersessionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        supersession_id=uuid4(),
        case_id=case_id,
        replacing_contract_instrument_version_id=other_case_version_command.contract_instrument_version_id,
        replaced_contract_instrument_version_id=instrument_version_command.contract_instrument_version_id,
        rationale="Tentative inter-Affaire refusée",
    )
    with pytest.raises(
        CommandExecutionError,
        match="CONTRACT_INSTRUMENT_VERSION_NOT_FOUND_OR_FORBIDDEN",
    ):
        supersession_dispatcher.dispatch(command=cross_case_declaration, context=actor_context)
    non_amendment_declaration = cross_case_declaration.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "supersession_id": uuid4(),
            "replacing_contract_instrument_version_id": instrument_version_command.contract_instrument_version_id,
            "replaced_contract_instrument_version_id": amendment_command.contract_instrument_version_id,
        }
    )
    with pytest.raises(
        CommandExecutionError,
        match="CONTRACT_INSTRUMENT_REPLACING_VERSION_MUST_BE_AMENDMENT",
    ):
        supersession_dispatcher.dispatch(command=non_amendment_declaration, context=actor_context)
    declaration = DeclareContractInstrumentSupersessionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        supersession_id=uuid4(),
        case_id=case_id,
        replacing_contract_instrument_version_id=amendment_command.contract_instrument_version_id,
        replaced_contract_instrument_version_id=instrument_version_command.contract_instrument_version_id,
        rationale="Déclaration Patron sourcée à partir de l’avenant enregistré.",
    )
    assert supersession_dispatcher.dispatch(
        command=declaration, context=actor_context
    ).result_code == "CONTRACT_INSTRUMENT_SUPERSESSION_DECLARED"
    assert supersession_dispatcher.dispatch(command=declaration, context=actor_context).replayed is True
    duplicate_declaration = declaration.model_copy(
        update={"command_id": uuid4(), "idempotency_key": uuid4(), "supersession_id": uuid4()}
    )
    with pytest.raises(
        CommandExecutionError,
        match="CONTRACT_INSTRUMENT_SUPERSESSION_ALREADY_RECORDED",
    ):
        supersession_dispatcher.dispatch(command=duplicate_declaration, context=actor_context)
    assert len(version_reader.list_for_case(actor=actor, case_id=case_id)) == 2
    after_amendment = service.list_for_case(actor=actor, case_id=case_id)[0]
    assert after_amendment.contract_instrument_version_relation == "REVIEW_REQUIRED"
    assert after_amendment.record.contract_instrument_version_id == (
        instrument_version_command.contract_instrument_version_id
    )
    assert after_amendment.record.summary == command.summary
    declaration_reader = ContractInstrumentSupersessionReadService(session_factory=session_factory)
    declarations = declaration_reader.list_for_case(actor=actor, case_id=case_id)
    assert len(declarations) == 1
    assert declarations[0].replacing_version.version_reference == "AVENANT-1-2026-09-29"
    assert declarations[0].replaced_version.version_reference == "MARCHE-SIGNE-2026-04-12"
    assert declaration_reader.list_for_case(
        actor=SimpleNamespace(
            actor_kind=ActorKind.PATRON_ADMIN,
            membership_id=uuid4(),
            tenant_id=uuid4(),
        ),
        case_id=case_id,
    ) == ()
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(ContractInstrumentSupersessionRecord)
            .where(ContractInstrumentSupersessionRecord.id == declaration.supersession_id)
            .values(rationale="Historique réécrit")
        )

    requalification_dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers=contract_execution_evidence_requalification_handlers(),
    )
    first_requalification = RecordContractExecutionEvidenceRequalificationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        requalification_id=uuid4(),
        case_id=case_id,
        act_id=command.act_id,
        supersession_id=declaration.supersession_id,
        expected_revision=0,
        decision="RELINKED_TO_DECLARED_VERSION",
        resulting_contract_instrument_version_id=amendment_command.contract_instrument_version_id,
        rationale="Le Patron relie la déclaration à l’avenant référencé, sans conclure son applicabilité.",
    )
    assert requalification_dispatcher.dispatch(
        command=first_requalification, context=actor_context
    ).result_code == "CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION_RECORDED"
    assert requalification_dispatcher.dispatch(
        command=first_requalification, context=actor_context
    ).replayed is True
    stale_requalification = first_requalification.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "requalification_id": uuid4(),
            "expected_revision": 0,
        }
    )
    with pytest.raises(
        CommandExecutionError,
        match="CONTRACT_EXECUTION_REQUALIFICATION_REVISION_CONFLICT",
    ):
        requalification_dispatcher.dispatch(command=stale_requalification, context=actor_context)
    other_case_requalification = first_requalification.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "requalification_id": uuid4(),
            "case_id": other_case_id,
        }
    )
    with pytest.raises(
        CommandExecutionError,
        match="CONTRACT_EXECUTION_EVIDENCE_NOT_FOUND_OR_FORBIDDEN",
    ):
        requalification_dispatcher.dispatch(command=other_case_requalification, context=actor_context)

    follow_up_requalification = RecordContractExecutionEvidenceRequalificationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        requalification_id=uuid4(),
        case_id=case_id,
        act_id=command.act_id,
        supersession_id=declaration.supersession_id,
        expected_revision=1,
        decision="NEEDS_CLARIFICATION",
        resulting_contract_instrument_version_id=None,
        rationale="Il manque une pièce pour terminer la revue humaine.",
    )
    requalification_dispatcher.dispatch(
        command=follow_up_requalification, context=actor_context
    )
    retained_requalification = RecordContractExecutionEvidenceRequalificationCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        requalification_id=uuid4(),
        case_id=case_id,
        act_id=command.act_id,
        supersession_id=declaration.supersession_id,
        expected_revision=2,
        decision="RETAINED_AS_DECLARED",
        resulting_contract_instrument_version_id=None,
        rationale="Le Patron conserve la référence initiale pour cette déclaration.",
    )
    requalification_dispatcher.dispatch(
        command=retained_requalification, context=actor_context
    )
    requalification_reader = ContractExecutionEvidenceRequalificationReadService(
        session_factory=session_factory
    )
    requalifications = requalification_reader.list_for_case(actor=actor, case_id=case_id)
    assert [item.record.revision for item in requalifications] == [1, 2, 3]
    assert [item.record.decision for item in requalifications] == [
        "RELINKED_TO_DECLARED_VERSION",
        "NEEDS_CLARIFICATION",
        "RETAINED_AS_DECLARED",
    ]
    assert requalifications[0].resulting_version.version_reference == "AVENANT-1-2026-09-29"
    assert requalifications[1].resulting_version is None
    assert requalifications[2].resulting_version.id == instrument_version_command.contract_instrument_version_id
    assert service.list_for_case(actor=actor, case_id=case_id)[0].contract_instrument_version_relation == (
        "REVIEW_REQUIRED"
    )
    assert requalification_reader.list_for_case(
        actor=SimpleNamespace(
            actor_kind=ActorKind.PATRON_ADMIN,
            membership_id=uuid4(),
            tenant_id=uuid4(),
        ),
        case_id=case_id,
    ) == ()
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(ContractExecutionEvidenceRequalificationRecord)
            .where(
                ContractExecutionEvidenceRequalificationRecord.id
                == first_requalification.requalification_id
            )
            .values(rationale="Réécriture interdite")
        )

    with Session(database_engine) as session:
        old_version = session.get(DceVersionRecord, v1_id)
        old_version.lifecycle = "SUPERSEDED"
        old_version.superseded_at = now
        old_version.aggregate_revision += 1
        session.commit()
    after_rectificatif = service.list_for_case(actor=actor, case_id=case_id)[0]
    assert after_rectificatif.version_relation == "REVIEW_REQUIRED"

    link_dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={LinkCaseDceVersionCommand.command_type: LinkCaseDceVersionHandler()},
    )
    link_dispatcher.dispatch(
        command=LinkCaseDceVersionCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            case_id=case_id,
            dce_version_id=v2_id,
            expected_case_revision=1,
            reason="Rectificatif reçu et rattaché",
        ),
        context=actor_context,
    )
    after_case_link = service.list_for_case(actor=actor, case_id=case_id)[0]
    assert after_case_link.version_relation == "REVIEW_REQUIRED"
    assert after_case_link.record.case_dce_version_id_at_recording == v1_id
    assert after_case_link.record.summary == command.summary
    assert after_case_link.contract_instrument_version.instrument_kind == "SIGNED_CONTRACT"
    assert (
        after_case_link.contract_instrument_version.version_reference == "MARCHE-SIGNE-2026-04-12"
    )
    assert after_case_link.contract_instrument_version.source_refs_json == [
        "contract://document/marche-2026"
    ]
    timeline = ContractExecutionEvidenceTimelineReadService(
        session_factory=session_factory
    ).list_for_case(actor=actor, case_id=case_id)
    assert [event["event_type"] for event in timeline] == [
        "EXECUTION_EVIDENCE",
        "INSTRUMENT_SUPERSESSION",
        "EVIDENCE_REQUALIFICATION",
        "EVIDENCE_REQUALIFICATION",
        "EVIDENCE_REQUALIFICATION",
    ]
    assert [event["revision"] for event in timeline] == [1, 1, 1, 2, 3]
    assert timeline[1]["status"] == "SUPERSEDED"
    assert timeline[1]["status_origin"] == "PATRON_DECLARATION"
    assert timeline[2]["status"] == "RELINKED_TO_DECLARED_VERSION"
    assert timeline[3]["status"] == "NEEDS_CLARIFICATION"
    assert timeline[4]["status"] == "RETAINED_AS_DECLARED"
    foreign_actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN, membership_id=uuid4(), tenant_id=uuid4()
    )
    assert version_reader.list_for_case(actor=foreign_actor, case_id=case_id) == ()
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(ContractInstrumentVersionRecord)
            .where(
                ContractInstrumentVersionRecord.id
                == instrument_version_command.contract_instrument_version_id
            )
            .values(version_reference="Réécriture interdite")
        )
