# ruff: noqa: E501, I001
from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.interfaces.http.routes.patron_contract_execution_evidence import (
    build_patron_contract_execution_evidence_router,
)
from app.modules.pricing.public.contract_execution_evidence_contracts import (
    ContractExecutionEvidenceTimelineSupersessionEvent,
    DeclareContractInstrumentSupersessionRequest,
    RecordContractExecutionEvidenceRequest,
    RecordContractExecutionEvidenceRequalificationRequest,
    RecordContractInstrumentVersionRequest,
)
from app.platform.security.context import ActorContext, ActorKind, MembershipState


class Resolver:
    def __init__(self, actor_kind):
        self.actor_kind = actor_kind

    def resolve(self, *, access_token: str):
        actor_id = uuid4()
        now = datetime.now(tz=UTC)
        return ActorContext(
            actor_id=actor_id,
            identity_id=actor_id,
            tenant_id=uuid4(),
            membership_id=uuid4(),
            actor_kind=self.actor_kind,
            membership_state=MembershipState.ACTIVE,
            capabilities=frozenset(),
            assigned_case_ids=frozenset(),
            session_id=uuid4(),
            authenticated_at=now,
            mfa_verified_at=now,
            correlation_id=uuid4(),
        )


class Dispatcher:
    def __init__(self):
        self.command = None

    def dispatch(self, *, command, context):
        self.command = command
        return SimpleNamespace(
            command_id=str(command.command_id),
            idempotency_key=str(command.idempotency_key),
            result_code=(
                "CONTRACT_INSTRUMENT_VERSION_RECORDED"
                if command.command_type == "RecordContractInstrumentVersion"
                else "CONTRACT_INSTRUMENT_SUPERSESSION_DECLARED"
                if command.command_type == "DeclareContractInstrumentSupersession"
                else "CONTRACT_EXECUTION_EVIDENCE_REQUALIFICATION_RECORDED"
                if command.command_type == "RecordContractExecutionEvidenceRequalification"
                else "CONTRACT_EXECUTION_EVIDENCE_RECORDED"
            ),
            replayed=False,
            aggregate_refs=(),
        )


class ReadService:
    def list_for_case(self, *, actor, case_id):
        return (
            SimpleNamespace(
                id=uuid4(),
                case_id=case_id,
                act_kind="WORK_RECEPTION",
                reception_outcome="UNDER_RESERVATIONS",
                summary="PV de réception signé",
                source_refs_json=["ccap://clause/24"],
                evidence_refs_json=["document://pv/sha256:abc"],
                declared_event_date=date(2026, 9, 27),
                case_dce_version_id_at_recording=None,
                contract_instrument_version_id=None,
                actor_id=actor.actor_id,
                created_at=datetime.now(tz=UTC),
                version_relation="UNKNOWN",
            ),
        )


class InstrumentVersionReadService:
    def list_for_case(self, *, actor, case_id):
        return (
            SimpleNamespace(
                id=uuid4(),
                case_id=case_id,
                instrument_kind="SIGNED_CONTRACT",
                version_reference="MARCHE-SIGNE-2026",
                source_refs_json=["contract://initial"],
                evidence_refs_json=["document://signed/sha256:abc"],
                actor_id=actor.actor_id,
                created_at=datetime.now(tz=UTC),
            ),
        )


class SupersessionReadService:
    def list_for_case(self, *, actor, case_id):
        now = datetime.now(tz=UTC)
        return (
            SimpleNamespace(
                record=SimpleNamespace(
                    id=uuid4(),
                    case_id=case_id,
                    rationale="Avenant déclaré reçu",
                    actor_id=actor.actor_id,
                    created_at=now,
                ),
                replacing_version=SimpleNamespace(
                    id=uuid4(),
                    instrument_kind="AMENDMENT",
                    version_reference="AVENANT-2",
                ),
                replaced_version=SimpleNamespace(
                    id=uuid4(),
                    instrument_kind="SIGNED_CONTRACT",
                    version_reference="MARCHE-1",
                ),
            ),
        )


class RequalificationReadService:
    def list_for_case(self, *, actor, case_id):
        now = datetime.now(tz=UTC)
        return (
            SimpleNamespace(
                record=SimpleNamespace(
                    id=uuid4(),
                    case_id=case_id,
                    revision=1,
                    decision="RELINKED_TO_DECLARED_VERSION",
                    resulting_contract_instrument_version_id=uuid4(),
                    rationale="Référence relue par le Patron",
                    actor_id=actor.actor_id,
                    created_at=now,
                ),
                act=SimpleNamespace(
                    id=uuid4(), act_kind="RIGHTS_PRESERVATION", summary="Réserve envoyée"
                ),
                supersession=SimpleNamespace(id=uuid4()),
                resulting_version=SimpleNamespace(
                    instrument_kind="AMENDMENT", version_reference="AVENANT-2"
                ),
            ),
        )


class TimelineReadService:
    def list_for_case(self, *, actor, case_id):
        return (
            {
                "event_type": "INSTRUMENT_SUPERSESSION",
                "event_id": uuid4(),
                "case_id": case_id,
                "revision": 1,
                "status": "SUPERSEDED",
                "status_origin": "PATRON_DECLARATION",
                "actor_id": actor.actor_id,
                "recorded_at": datetime.now(tz=UTC),
                "supersession_id": uuid4(),
                "rationale": "Avenant déclaré remplaçant",
                "replacing": {
                    "contract_instrument_version_id": uuid4(),
                    "instrument_kind": "AMENDMENT",
                    "version_reference": "AVENANT-2",
                    "source_refs": ["contract://avenant/2"],
                    "evidence_refs": ["document://avenant/2"],
                },
                "replaced": {
                    "contract_instrument_version_id": uuid4(),
                    "instrument_kind": "SIGNED_CONTRACT",
                    "version_reference": "MARCHE-1",
                    "source_refs": ["contract://marche/1"],
                    "evidence_refs": ["document://marche/1"],
                },
            },
        )


def test_patron_can_record_and_read_human_declared_evidence_without_legal_conclusion():
    case_id, act_id = uuid4(), uuid4()
    dispatcher = Dispatcher()
    router = build_patron_contract_execution_evidence_router(
        dispatcher=dispatcher,
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)),
    )
    request = RecordContractExecutionEvidenceRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=act_id,
        act_kind="WORK_RECEPTION",
        reception_outcome="UNDER_RESERVATIONS",
        summary="PV de réception signé",
        source_refs=("ccap://clause/24",),
        evidence_refs=("document://pv/sha256:abc",),
        declared_event_date=date(2026, 9, 27),
    )

    receipt = router.routes[0].endpoint(case_id, request, authorization="Bearer token")
    listed = router.routes[1].endpoint(case_id, authorization="Bearer token")

    assert receipt.status_code == 201
    assert dispatcher.command.act_kind == "WORK_RECEPTION"
    assert dispatcher.command.reception_outcome == "UNDER_RESERVATIONS"
    assert not hasattr(dispatcher.command, "deadline")
    assert listed[0].evidence_refs == ["document://pv/sha256:abc"]
    assert listed[0].declared_event_date == date(2026, 9, 27)
    assert listed[0].reception_outcome == "UNDER_RESERVATIONS"
    assert listed[0].version_relation == "UNKNOWN"
    assert not hasattr(listed[0], "legal_conclusion")


def test_collaborator_cannot_create_or_read_contract_execution_evidence():
    dispatcher = Dispatcher()
    router = build_patron_contract_execution_evidence_router(
        dispatcher=dispatcher,
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.COLLABORATEUR)),
    )
    request = RecordContractExecutionEvidenceRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        act_id=uuid4(),
        act_kind="RIGHTS_PRESERVATION",
        summary="Réserve envoyée",
        source_refs=("ccap://clause/18",),
        evidence_refs=("document://courrier/sha256:abc",),
    )

    with pytest.raises(HTTPException) as write_error:
        router.routes[0].endpoint(uuid4(), request, authorization="Bearer token")
    with pytest.raises(HTTPException) as read_error:
        router.routes[1].endpoint(uuid4(), authorization="Bearer token")
    instrument_request = RecordContractInstrumentVersionRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        contract_instrument_version_id=uuid4(),
        instrument_kind="SIGNED_CONTRACT",
        version_reference="MARCHE-SIGNE-2026",
        source_refs=("contract://initial",),
        evidence_refs=("document://signed/sha256:abc",),
    )
    with pytest.raises(HTTPException) as instrument_write_error:
        router.routes[2].endpoint(uuid4(), instrument_request, authorization="Bearer token")
    with pytest.raises(HTTPException) as instrument_read_error:
        router.routes[3].endpoint(uuid4(), authorization="Bearer token")
    supersession_request = DeclareContractInstrumentSupersessionRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        supersession_id=uuid4(),
        replacing_contract_instrument_version_id=uuid4(),
        replaced_contract_instrument_version_id=uuid4(),
        rationale="Avenant reçu selon le Patron",
    )
    with pytest.raises(HTTPException) as supersession_write_error:
        router.routes[4].endpoint(uuid4(), supersession_request, authorization="Bearer token")
    with pytest.raises(HTTPException) as supersession_read_error:
        router.routes[5].endpoint(uuid4(), authorization="Bearer token")
    requalification_request = RecordContractExecutionEvidenceRequalificationRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        requalification_id=uuid4(),
        act_id=uuid4(),
        supersession_id=uuid4(),
        expected_revision=0,
        decision="NEEDS_CLARIFICATION",
        rationale="Pièce supplémentaire attendue",
    )
    with pytest.raises(HTTPException) as requalification_write_error:
        router.routes[6].endpoint(uuid4(), requalification_request, authorization="Bearer token")
    with pytest.raises(HTTPException) as requalification_read_error:
        router.routes[7].endpoint(uuid4(), authorization="Bearer token")
    with pytest.raises(HTTPException) as timeline_read_error:
        router.routes[8].endpoint(uuid4(), authorization="Bearer token")
    assert write_error.value.status_code == 403
    assert read_error.value.status_code == 403
    assert instrument_write_error.value.status_code == 403
    assert instrument_read_error.value.status_code == 403
    assert supersession_write_error.value.status_code == 403
    assert supersession_read_error.value.status_code == 403
    assert requalification_write_error.value.status_code == 403
    assert requalification_read_error.value.status_code == 403
    assert timeline_read_error.value.status_code == 403
    assert dispatcher.command is None


def test_patron_can_declare_and_read_a_sourced_contract_instrument_version():
    case_id, version_id = uuid4(), uuid4()
    dispatcher = Dispatcher()
    router = build_patron_contract_execution_evidence_router(
        dispatcher=dispatcher,
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)),
    )
    request = RecordContractInstrumentVersionRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        contract_instrument_version_id=version_id,
        instrument_kind="AMENDMENT",
        version_reference="AVENANT-2-SIGNE",
        source_refs=("contract://amendment/2",),
        evidence_refs=("document://amendment/2",),
    )
    receipt = router.routes[2].endpoint(case_id, request, authorization="Bearer token")
    listed = router.routes[3].endpoint(case_id, authorization="Bearer token")
    assert receipt.status_code == 201
    assert dispatcher.command.version_reference == "AVENANT-2-SIGNE"
    assert listed[0].version_reference == "MARCHE-SIGNE-2026"
    assert listed[0].source_refs == ["contract://initial"]


def test_patron_can_declare_and_read_an_append_only_supersession():
    case_id = uuid4()
    dispatcher = Dispatcher()
    router = build_patron_contract_execution_evidence_router(
        dispatcher=dispatcher,
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)),
    )
    request = DeclareContractInstrumentSupersessionRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        supersession_id=uuid4(),
        replacing_contract_instrument_version_id=uuid4(),
        replaced_contract_instrument_version_id=uuid4(),
        rationale="Le Patron déclare l’avenant comme remplaçant la version antérieure.",
    )

    receipt = router.routes[4].endpoint(case_id, request, authorization="Bearer token")
    listed = router.routes[5].endpoint(case_id, authorization="Bearer token")

    assert receipt.status_code == 201
    assert dispatcher.command.replacing_contract_instrument_version_id == (
        request.replacing_contract_instrument_version_id
    )
    assert listed[0].replacing_version_reference == "AVENANT-2"
    assert listed[0].replaced_version_reference == "MARCHE-1"
    assert listed[0].rationale == "Avenant déclaré reçu"


def test_patron_can_record_and_read_a_requalification_without_legal_conclusion():
    case_id = uuid4()
    dispatcher = Dispatcher()
    router = build_patron_contract_execution_evidence_router(
        dispatcher=dispatcher,
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)),
    )
    request = RecordContractExecutionEvidenceRequalificationRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        requalification_id=uuid4(),
        act_id=uuid4(),
        supersession_id=uuid4(),
        expected_revision=0,
        decision="RELINKED_TO_DECLARED_VERSION",
        resulting_contract_instrument_version_id=uuid4(),
        rationale="Le Patron rattache l’acte à une version déclarée différente.",
    )

    receipt = router.routes[6].endpoint(case_id, request, authorization="Bearer token")
    listed = router.routes[7].endpoint(case_id, authorization="Bearer token")

    assert receipt.status_code == 201
    assert dispatcher.command.expected_revision == 0
    assert dispatcher.command.decision == "RELINKED_TO_DECLARED_VERSION"
    assert receipt.body
    assert listed[0].decision == "RELINKED_TO_DECLARED_VERSION"
    assert listed[0].resulting_version_reference == "AVENANT-2"
    assert listed[0].rationale == "Référence relue par le Patron"


def test_patron_timeline_keeps_supersession_as_a_distinct_human_event():
    router = build_patron_contract_execution_evidence_router(
        dispatcher=Dispatcher(),
        service=ReadService(),
        instrument_version_service=InstrumentVersionReadService(),
        supersession_service=SupersessionReadService(),
        requalification_service=RequalificationReadService(),
        timeline_service=TimelineReadService(),
        security_runtime=SimpleNamespace(context_resolver=Resolver(ActorKind.PATRON_ADMIN)),
    )

    response = router.routes[8].endpoint(uuid4(), authorization="Bearer token")
    event = ContractExecutionEvidenceTimelineSupersessionEvent.model_validate(response[0])

    assert event.event_type == "INSTRUMENT_SUPERSESSION"
    assert event.status == "SUPERSEDED"
    assert event.status_origin == "PATRON_DECLARATION"
    assert event.replacing.version_reference == "AVENANT-2"
    assert event.replaced.version_reference == "MARCHE-1"


def test_request_bounds_reference_size_and_count():
    with pytest.raises(ValidationError):
        RecordContractExecutionEvidenceRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            act_id=uuid4(),
            act_kind="WORK_RECEPTION",
            summary="PV",
            source_refs=("s" * 1001,),
            evidence_refs=("document://pv",),
        )
    with pytest.raises(ValidationError):
        RecordContractExecutionEvidenceRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            act_id=uuid4(),
            act_kind="WORK_RECEPTION",
            summary="PV",
            source_refs=tuple(f"source://{index}" for index in range(33)),
            evidence_refs=("document://pv",),
        )
