from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from app.modules.pricing.application.case_contract_change import (
    CaseContractChangeService,
    case_contract_change_handlers,
)
from app.modules.pricing.application.case_contract_change_commands import (
    RecordCaseContractChangeActionCommand,
    RecordCaseContractChangeApplicabilityCommand,
    RecordCaseContractChangeEventCommand,
)
from app.modules.pricing.infrastructure.case_contract_change_reader import (
    SqlAlchemyCaseContractChangeReader,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy
from tests.db.test_operational_handover_workflow import dossier as seed_handover
from tests.db.test_operational_handover_workflow import publish_fixture


def ids():
    return dict(command_id=uuid4(), idempotency_key=uuid4(), correlation_id=uuid4())


@pytest.fixture
def workflow(session_factory, tmp_path):
    d = seed_handover.__wrapped__(session_factory, tmp_path)
    _, view = publish_fixture(session_factory, d)
    service = CaseContractChangeService(
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=case_contract_change_handlers(storage=d.service._storage),
        ),
        reader=SqlAlchemyCaseContractChangeReader(session_factory, storage=d.service._storage),
        policy=AuthorizationPolicy(),
    )
    context = dict(
        expected_view_sha256=view["view_sha256"],
        point_ids=[UUID(view["snapshot"]["operational_review"]["points"][0]["point_id"])],
        justification="Source et instruction rapprochées humainement.",
        human_confirmed=True,
        publish=True,
    )
    event = uuid4()
    command = RecordCaseContractChangeEventCommand(
        **ids(),
        event_id=event,
        case_id=d.case,
        handover_snapshot_id=view["snapshot_id"],
        change_kind="ORDER_OF_SERVICE",
        contract_instrument_version_id=d.instrument,
        issuer="Maître ouvrage synthétique",
        summary="Accès déplacé en phase travaux.",
        scope_note="Lot01 : détour pour livraison.",
        source_refs=["instruction://synthetic/v1"],
        evidence_refs=["courrier://synthetic/v1"],
        declared_received_at=datetime.now(UTC),
        operational_context=context,
    )
    return SimpleNamespace(
        d=d, view=view, service=service, context=context, event=event, command=command
    )


def test_change_follows_the_exact_handover_and_safe_published_action(session_factory, workflow):
    w = workflow
    d = w.d
    now = datetime.now(UTC)
    first = w.service.record(actor=d.patron, command=w.command, now=now)
    assert first.result_code == "CASE_CONTRACT_CHANGE_EVENT_RECORDED"
    assert w.service.record(actor=d.patron, command=w.command, now=now).replayed is True
    review = uuid4()
    w.service.record(
        actor=d.patron,
        now=now,
        command=RecordCaseContractChangeApplicabilityCommand(
            **ids(),
            case_id=d.case,
            event_id=w.event,
            review_id=review,
            handover_snapshot_id=w.view["snapshot_id"],
            contract_instrument_version_id=d.instrument,
            expected_revision=0,
            decision="APPLICABLE_TO_HANDOVER",
            delta_state="DECLARED",
            delta_note="Livraison par accès secondaire au lieu de l’accès initial.",
            rationale="Instruction relue contre offre.",
            evidence_refs=["instruction://synthetic/v1"],
            operational_review=w.context,
        ),
    )
    action = uuid4()
    w.service.record(
        actor=d.patron,
        now=now,
        command=RecordCaseContractChangeActionCommand(
            **ids(),
            case_id=d.case,
            event_id=w.event,
            action_id=action,
            applicability_review_id=review,
            expected_revision=0,
            action_summary="Revoir le plan de livraison.",
            evidence_refs=["instruction://synthetic/v1"],
            due_date_absence_reason="Date déclarée encore inconnue.",
            operational_details=dict(
                responsible="Conducteur affecté",
                expected_evidence="Plan de circulation actualisé",
                human_confirmed=True,
                publish=True,
                justification="Action opérationnelle à suivre.",
            ),
        ),
    )
    rows = w.service.list_operational_for_case(actor=d.driver, case_id=d.case, now=now)
    assert len(rows) == 1
    row = rows[0]
    assert row["actions"][0]["operational_details"]["responsible"] == "Conducteur affecté"
    assert (
        row["actions"][0]["operational_details"]["expected_evidence"]
        == "Plan de circulation actualisé"
    )
    assert (
        row["operational_context"]["points"][0]["statement"]
        == w.view["snapshot"]["operational_review"]["points"][0]["statement"]
    )
    assert row["source_state"] == "CURRENT"
    assert row["legal_effect_state"] == "UNKNOWN" and row["financial_content"] == "NOT_INCLUDED"
    assert (
        row["operational_timeline"] and row["applicability_history"][0]["delta_state"] == "DECLARED"
    )


def make_client(w, tmp_path):
    from typing import cast

    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_case_contract_changes import (
        build_operational_case_contract_change_router,
        build_patron_case_contract_change_router,
    )
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
    from app.modules.pricing.application.case_contract_change_evidence_upload import (
        CaseContractChangeEvidenceUploadService,
    )
    from app.modules.pricing.infrastructure.case_contract_change_evidence_repository import (
        SqlAlchemyCaseContractChangeEvidenceRepository,
    )
    from app.platform.security.authenticated_context import AuthenticationContextResolver
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from tests.db.test_case_handover_http_e2e import C5StaticInspector, C5StaticScanner

    storage = LocalQuarantineStorageAdapter(root=tmp_path / "private-c5")
    upload = CaseContractChangeEvidenceUploadService(
        repository=SqlAlchemyCaseContractChangeEvidenceRepository(
            session_factory=w.service._dispatcher._session_factory
        ),
        policy=AuthorizationPolicy(),
        storage=storage,
        inspector=C5StaticInspector(),
        scanner=C5StaticScanner(),
    )
    security = ConsultationSecurityRuntime(
        context_resolver=cast(AuthenticationContextResolver, w.d.resolver),
        policy=AuthorizationPolicy(),
    )
    app = FastAPI()
    app.include_router(
        build_patron_case_contract_change_router(
            service=w.service, evidence_upload_service=upload, security_runtime=security
        )
    )
    app.include_router(
        build_operational_case_contract_change_router(service=w.service, security_runtime=security)
    )
    return TestClient(app), storage


def test_real_native_upload_and_public_declaration_keep_private_bytes_private(
    session_factory, workflow, tmp_path
):
    import hashlib

    from app.modules.pricing.application.case_contract_change_commands import (
        RecordCaseContractChangeActionImpactRelationCommand,
    )

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    row = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))[0]
    action = UUID(row["actions"][0]["action_id"])
    relation = uuid4()
    w.service.record(
        actor=w.d.patron,
        now=datetime.now(UTC),
        command=RecordCaseContractChangeActionImpactRelationCommand(
            **ids(),
            case_id=w.d.case,
            event_id=w.event,
            action_id=action,
            relation_id=relation,
            expected_revision=0,
            state="UNKNOWN",
            rationale="Conséquence économique non évaluée.",
            unknown_reason="Aucun chiffrage couvert déduit.",
        ),
    )
    client, storage = make_client(w, tmp_path)
    root = f"/api/v1/patron/cases/{w.d.case}/contract-change-events/{w.event}/actions/{action}"
    content = b"%PDF-1.7 synthetic revised access plan"
    evidence = uuid4()
    identity = ids()
    prepare = client.post(
        root + "/evidence-objects",
        headers=w.d.headers,
        json={
            **{key: str(value) for key, value in identity.items()},
            "evidence_object_id": str(evidence),
            "c4_relation_id": str(relation),
            "evidence_kind": "EXECUTION_EVIDENCE",
            "expected_byte_size": len(content),
        },
    )
    assert prepare.status_code == 201, prepare.text
    uploaded = client.put(
        root + f"/evidence-objects/{evidence}/content",
        headers={
            **w.d.headers,
            "Content-Type": "application/octet-stream",
            "Idempotency-Key": str(identity["idempotency_key"]),
        },
        content=content,
    )
    assert uploaded.status_code == 200, uploaded.text
    assert uploaded.json()["sha256"] == hashlib.sha256(content).hexdigest()
    body = {
        **{key: str(value) for key, value in ids().items()},
        "act_id": str(uuid4()),
        "c4_relation_id": str(relation),
        "expected_revision": 0,
        "declared_state": "DECLARED_PERFORMED",
        "declared_summary": "Plan d’accès actualisé, vérification terrain à confirmer.",
        "evidence_refs": ["plan://synthetic/v2"],
        "evidence_object_ids": [str(evidence)],
        "external_confirmation_state": "UNKNOWN",
        "operational_publication": {
            "human_confirmed": True,
            "publish": True,
            "justification": "Déclaration opérationnelle à relire.",
        },
    }
    result = client.post(root + "/execution-acts", headers=w.d.headers, json=body)
    assert result.status_code == 201, result.text
    assert client.post(root + "/execution-acts", headers=w.d.headers, json=body).status_code == 200
    private = client.get(
        f"/api/v1/patron/cases/{w.d.case}/contract-change-events", headers=w.d.headers
    ).json()["events"][0]
    assert private["action_execution_acts"][0]["evidence_state"] == "RETRIEVED"
    public = client.get(
        f"/api/v1/cases/{w.d.case}/contract-change-events", headers=w.d.driver_headers
    )
    assert public.status_code == 200, public.text
    act = public.json()["events"][0]["action_execution_acts"][0]
    assert (
        act["evidence_retrieval_state"] == "UNKNOWN"
        and act["external_confirmation_state"] == "UNKNOWN"
    )
    assert "storage_key" not in public.text and uploaded.json()["sha256"] not in public.text
    assert "evidence_objects" not in public.text


@pytest.mark.parametrize("fault", ["view", "point", "mfa", "role", "private_text"])
def test_refusals_do_not_create_a_change(session_factory, workflow, fault):
    from dataclasses import replace

    import sqlalchemy as sa
    from app.modules.pricing.infrastructure.models.case_contract_change import (
        CaseContractChangeEventRecord,
    )
    from app.platform.events.dispatcher import CommandExecutionError

    w = workflow
    actor = w.d.patron
    command = w.command
    if fault == "view":
        command = command.model_copy(
            update={
                "operational_context": command.operational_context.model_copy(
                    update={"expected_view_sha256": "f" * 64}
                )
            }
        )
    if fault == "point":
        command = command.model_copy(
            update={
                "operational_context": command.operational_context.model_copy(
                    update={"point_ids": [uuid4()]}
                )
            }
        )
    if fault == "mfa":
        actor = replace(actor, mfa_verified_at=None)
    if fault == "role":
        actor = w.d.driver
    if fault == "private_text":
        command = command.model_copy(
            update={"summary": "La marge privée cible est de 28 pour cent."}
        )
    with pytest.raises((CommandExecutionError, PermissionError)):
        w.service.record(actor=actor, command=command, now=datetime.now(UTC))
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseContractChangeEventRecord))
            == 0
        )


def test_replaced_contract_reopens_sources_without_rewriting_history(session_factory, workflow):
    from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
        ContractInstrumentSupersessionRecord,
    )
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    before = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))[0]
    replacement = uuid4()
    with session_factory.begin() as session:
        session.add(
            ContractInstrumentVersionRecord(
                id=replacement,
                tenant_id=w.d.patron.tenant_id,
                case_id=w.d.case,
                instrument_kind="AMENDMENT",
                version_reference="Avenant synthétique v2",
                source_refs_json=["avenant://synthetic/v2"],
                evidence_refs_json=["document://synthetic/v2"],
                actor_id=w.d.patron.actor_id,
            )
        )
        session.flush()
        session.add(
            ContractInstrumentSupersessionRecord(
                id=uuid4(),
                tenant_id=w.d.patron.tenant_id,
                case_id=w.d.case,
                replacing_contract_instrument_version_id=replacement,
                replaced_contract_instrument_version_id=w.d.instrument,
                rationale="Remplacement déclaré à requalifier.",
                actor_id=w.d.patron.actor_id,
            )
        )
    after = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))[0]
    assert after["source_state"] == "REVIEW_REQUIRED"
    assert after["operational_context"] == before["operational_context"]
    assert after["actions"][0]["source_state"] == "REVIEW_REQUIRED"
    assert after["actions"][0]["action_id"] == before["actions"][0]["action_id"]
    assert len(after["applicability_history"]) == len(before["applicability_history"])
    body = w.command.model_copy(
        update={"command_id": uuid4(), "idempotency_key": uuid4(), "event_id": uuid4()}
    )
    from app.platform.events.dispatcher import CommandExecutionError

    with pytest.raises(CommandExecutionError, match="SOURCE_CONFLICT"):
        w.service.record(actor=w.d.patron, command=body, now=datetime.now(UTC))


def test_foreign_role_cannot_read_private_changes_or_the_published_case(
    session_factory, workflow, tmp_path
):
    from dataclasses import replace

    from app.platform.security.context import OperationalProfile

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    client, _ = make_client(w, tmp_path)
    private = client.get(
        f"/api/v1/patron/cases/{w.d.case}/contract-change-events", headers=w.d.driver_headers
    )
    assert private.status_code == 403 and private.json() == {"detail": "FORBIDDEN"}
    w.d.resolver.actors["driver"] = replace(w.d.driver, assignment_scopes=())
    hidden = client.get(
        f"/api/v1/cases/{w.d.case}/contract-change-events", headers=w.d.driver_headers
    )
    assert hidden.status_code == 403 and hidden.json() == {"detail": "FORBIDDEN"}
    w.d.resolver.actors["driver"] = replace(
        w.d.driver, operational_profile=OperationalProfile.EXPERT
    )
    assert (
        client.get(
            f"/api/v1/cases/{w.d.case}/contract-change-events", headers=w.d.driver_headers
        ).status_code
        == 403
    )


def requalify_on_replacement(session_factory, w):
    from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
        ContractInstrumentSupersessionRecord,
    )
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )
    from tests.db.test_operational_handover_workflow import publication_body

    replacement = uuid4()
    with session_factory.begin() as session:
        session.add(
            ContractInstrumentVersionRecord(
                id=replacement,
                tenant_id=w.d.patron.tenant_id,
                case_id=w.d.case,
                instrument_kind="AMENDMENT",
                version_reference="Avenant de requalification",
                source_refs_json=["avenant://requalification/v2"],
                evidence_refs_json=["document://requalification/v2"],
                actor_id=w.d.patron.actor_id,
            )
        )
        session.flush()
        session.add(
            ContractInstrumentSupersessionRecord(
                id=uuid4(),
                tenant_id=w.d.patron.tenant_id,
                case_id=w.d.case,
                replacing_contract_instrument_version_id=replacement,
                replaced_contract_instrument_version_id=w.d.instrument,
                rationale="Remplacement explicitement déclaré.",
                actor_id=w.d.patron.actor_id,
            )
        )
    w.d.instrument = replacement
    option = next(
        row
        for row in w.d.client.get(
            f"/api/v1/patron/cases/{w.d.case}/p7-handover/contracts", headers=w.d.headers
        ).json()["items"]
        if row["instrument_version_id"] == str(replacement)
    )
    body = publication_body(w.d, w.view["manifest_sha256"], option)
    body["operational_review"]["expected_handover_revision"] = 1
    response = w.d.client.post(
        f"/api/v1/patron/cases/{w.d.case}/p7-handover", headers=w.d.headers, json=body
    )
    assert response.status_code == 201, response.text
    view = w.d.client.get(
        f"/api/v1/cases/{w.d.case}/p7-handover/{body['snapshot_id']}", headers=w.d.driver_headers
    ).json()
    review = uuid4()
    context = {
        **w.context,
        "expected_view_sha256": view["view_sha256"],
        "point_ids": [UUID(view["snapshot"]["operational_review"]["points"][0]["point_id"])],
    }
    w.service.record(
        actor=w.d.patron,
        now=datetime.now(UTC),
        command=RecordCaseContractChangeApplicabilityCommand(
            **ids(),
            case_id=w.d.case,
            event_id=w.event,
            review_id=review,
            handover_snapshot_id=view["snapshot_id"],
            contract_instrument_version_id=replacement,
            expected_revision=1,
            decision="APPLICABLE_TO_HANDOVER",
            delta_state="DECLARED",
            delta_note="Accès revu sous la version déclarée suivante.",
            rationale="Sources explicitement requalifiées.",
            evidence_refs=["avenant://requalification/v2"],
            operational_review=context,
        ),
    )
    return view, review


def test_requalification_does_not_transfer_an_old_action_or_authorize_its_execution(
    session_factory, workflow
):
    from app.modules.pricing.application.case_contract_change_commands import (
        RecordCaseContractChangeActionExecutionCommand,
        RecordCaseContractChangeActionImpactRelationCommand,
    )
    from app.platform.events.dispatcher import CommandExecutionError

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    before = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))[0]
    old_action = UUID(before["actions"][0]["action_id"])
    relation = uuid4()
    w.service.record(
        actor=w.d.patron,
        now=datetime.now(UTC),
        command=RecordCaseContractChangeActionImpactRelationCommand(
            **ids(),
            case_id=w.d.case,
            event_id=w.event,
            action_id=old_action,
            relation_id=relation,
            expected_revision=0,
            state="UNKNOWN",
            rationale="À revoir.",
            unknown_reason="Impact non établi.",
        ),
    )
    view, review = requalify_on_replacement(session_factory, w)
    after = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))[0]
    assert after["source_state"] == "CURRENT" and len(after["applicability_history"]) == 2
    assert after["operational_context"] == before["operational_context"]
    assert after["current_operational_context"]["handover_snapshot_id"] == view["snapshot_id"]
    assert after["actions"][0]["source_state"] == "REVIEW_REQUIRED"
    with pytest.raises(CommandExecutionError, match="SOURCE_CONFLICT"):
        w.service.record(
            actor=w.d.patron,
            now=datetime.now(UTC),
            command=RecordCaseContractChangeActionExecutionCommand(
                **ids(),
                case_id=w.d.case,
                event_id=w.event,
                action_id=old_action,
                act_id=uuid4(),
                c4_relation_id=relation,
                expected_revision=0,
                declared_state="DECLARED_PARTIAL",
                declared_summary="Ancienne action non requalifiée.",
                operational_publication={
                    "human_confirmed": True,
                    "publish": True,
                    "justification": "Relecture opérationnelle.",
                },
            ),
        )


def test_captured_handover_dependencies_are_locked_even_without_declared_contract(
    session_factory, workflow, monkeypatch
):
    import sqlalchemy as sa
    from app.modules.pricing.infrastructure import operational_change_sources as module
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )
    from sqlalchemy.exc import OperationalError

    w = workflow
    original = module.current_handover_view
    observed = []

    def inspect(session, snapshot, *, storage):
        with pytest.raises(OperationalError) as failure, session_factory.begin() as competitor:
            competitor.scalar(
                sa.select(ContractInstrumentVersionRecord)
                .where(ContractInstrumentVersionRecord.id == w.d.instrument)
                .with_for_update(nowait=True)
            )
        assert failure.value.orig.sqlstate == "55P03"
        observed.append(True)
        return original(session, snapshot, storage=storage)

    monkeypatch.setattr(module, "current_handover_view", inspect)
    w.service.record(
        actor=w.d.patron,
        command=w.command.model_copy(update={"contract_instrument_version_id": None}),
        now=datetime.now(UTC),
    )
    assert observed


def test_operational_history_is_append_only_and_nonempty_downgrade_is_refused(
    session_factory, workflow
):
    import sqlalchemy as sa
    from alembic import command as migration
    from alembic.config import Config
    from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
    from sqlalchemy.exc import DBAPIError
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    for statement in [
        "UPDATE case_contract_change_events SET operational_context_json=NULL",
        "DELETE FROM case_contract_change_actions",
    ]:
        with pytest.raises(DBAPIError), session_factory.begin() as session:
            session.execute(sa.text(statement))
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="OPERATIONAL_CHANGE_HISTORY_DOWNGRADE_REFUSED"):
        migration.downgrade(cfg, "20261025_0143")
    with session_factory.begin() as session:
        assert (
            session.scalar(sa.text("SELECT version_num FROM alembic_version"))
            == EXPECTED_ALEMBIC_HEAD
        )
        assert session.scalar(sa.text("SELECT count(*) FROM case_contract_change_events")) == 1
        session.execute(sa.text("TRUNCATE case_contract_change_events CASCADE"))
    migration.downgrade(cfg, "20261025_0143")
    migration.upgrade(cfg, "head")
    with session_factory() as session:
        assert (
            session.scalar(sa.text("SELECT version_num FROM alembic_version"))
            == EXPECTED_ALEMBIC_HEAD
        )
        assert session.scalar(sa.text("SELECT count(*) FROM case_handover_snapshots")) == 1


def test_a_second_real_synthetic_tenant_never_reads_or_writes_the_first_case(
    session_factory, workflow, tmp_path
):
    from dataclasses import replace

    from app.platform.events.dispatcher import CommandExecutionError
    from tests.db.test_case_handover_http_e2e import _seed_handover_sources

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    foreign, other_case, _, _, _ = _seed_handover_sources(session_factory, tmp_path / "tenant2")
    foreign = replace(
        foreign, authenticated_at=datetime.now(UTC), mfa_verified_at=datetime.now(UTC)
    )
    assert foreign.tenant_id != w.d.patron.tenant_id and other_case != w.d.case
    assert w.service.list_for_case(actor=foreign, case_id=w.d.case, now=datetime.now(UTC)) == ()
    assert (
        w.service.list_operational_for_case(actor=foreign, case_id=w.d.case, now=datetime.now(UTC))
        == ()
    )
    with pytest.raises(CommandExecutionError, match="NOT_FOUND_OR_FORBIDDEN"):
        w.service.record(
            actor=foreign,
            command=w.command.model_copy(
                update={"command_id": uuid4(), "idempotency_key": uuid4(), "event_id": uuid4()}
            ),
            now=datetime.now(UTC),
        )
    own = w.service.list_for_case(actor=w.d.patron, case_id=w.d.case, now=datetime.now(UTC))
    assert len(own) == 1 and len(own[0]["actions"]) == 1


def test_closure_actions_reuse_change_source_invalidation(session_factory, workflow):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    with session_factory() as session:
        before = closure_dossier(session, w.d.patron.tenant_id, w.d.case)
    assert len(before["change_actions"]) == 1
    assert before["change_actions"][0]["context_state"] == "UNKNOWN"
    with session_factory.begin() as session:
        case = session.get(CaseRecord, w.d.case)
        case.dce_freshness = "REVIEW_REQUIRED"
    with session_factory() as session:
        after = closure_dossier(session, w.d.patron.tenant_id, w.d.case)
        assert after["change_actions"][0]["context_state"] == "REVIEW_REQUIRED"
        assert after["change_actions"][0]["id"] == before["change_actions"][0]["id"]
        assert after["dossier_sha256"] != before["dossier_sha256"]
        assert closure_dossier(session, uuid4(), w.d.case) is None


def test_closure_keeps_requalified_old_action_separate(session_factory, workflow):
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    requalify_on_replacement(session_factory, w)
    with session_factory() as session:
        dossier = closure_dossier(session, w.d.patron.tenant_id, w.d.case)
    assert len(dossier["change_actions"]) == 1
    assert dossier["change_actions"][0]["context_state"] == "REVIEW_REQUIRED"


def test_closure_comparison_reopens_after_handover_revision_without_case_replacement(
    session_factory, workflow
):
    from copy import deepcopy

    from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
    from app.modules.pricing.application.case_closure import closure_handlers
    from app.modules.pricing.application.case_closure_commands import (
        RecordClosureActCommand,
        RecordClosureObligationCommand,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_commands import (
        TransitionPostReceptionObligationCommand,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_handler import (
        post_reception_obligation_transition_handlers,
    )
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier
    from app.platform.events.dispatcher import CommandContext

    w = workflow
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={**closure_handlers(), **post_reception_obligation_transition_handlers()},
    )
    ctx = CommandContext(
        tenant_id=w.d.patron.tenant_id,
        actor_id=w.d.patron.actor_id,
        actor_kind="PATRON_ADMIN",
        membership_id=w.d.patron.membership_id,
        received_at=datetime.now(UTC),
    )

    def read():
        with session_factory() as session:
            return closure_dossier(session, w.d.patron.tenant_id, w.d.case)

    def write(comparisons, source_ref="pv://synthetic"):
        command = RecordClosureActCommand(
            **ids(),
            act_id=uuid4(),
            case_id=w.d.case,
            act_kind="WORK_RECEPTION",
            reception_outcome="WITH_RESERVATIONS",
            summary="Acte synthétique.",
            source_refs=[source_ref],
            evidence_refs=["proof://synthetic"],
            closure_review=dict(
                expected_dossier_sha256=read()["dossier_sha256"],
                human_confirmed=True,
                justification="Revue de référence exacte.",
                comparisons=comparisons,
            ),
        )
        dispatcher.dispatch(command=command, context=ctx)
        return str(command.act_id)

    reception = write([])
    source = read()
    expected = next(x for x in source["reference_options"] if x["kind"] == "CHANGE_ACTION")
    actual = next(
        x for x in source["reference_options"] if x["kind"] == "ACT" and x["record_id"] == reception
    )
    linked = write(
        [
            dict(
                expected={k: expected[k] for k in ("kind", "record_id", "sha256")},
                actual={k: actual[k] for k in ("kind", "record_id", "sha256")},
                note="Lien humain déclaré.",
            )
        ]
    )
    obligation = uuid4()
    dispatcher.dispatch(
        command=RecordClosureObligationCommand(
            **ids(),
            case_id=w.d.case,
            obligation_id=obligation,
            obligation_type="RESERVES_LIFTING",
            origin_reception_act_id=UUID(linked),
            summary="Réserve déclarée levée dans la fixture.",
            source_refs=["pv://synthetic"],
            closure_review=dict(
                expected_dossier_sha256=read()["dossier_sha256"],
                human_confirmed=True,
                justification="Source de réserve relue.",
                comparisons=[],
            ),
        ),
        context=ctx,
    )
    dispatcher.dispatch(
        command=TransitionPostReceptionObligationCommand(
            **ids(),
            case_id=w.d.case,
            obligation_id=obligation,
            transition_id=uuid4(),
            expected_revision=0,
            resulting_status="COMPLETED",
            rationale="Levée déclarée synthétique.",
            evidence_refs=["proof://synthetic"],
        ),
        context=ctx,
    )
    assert str(obligation) not in read()["open_obligation_ids"]
    before = read()
    captured = deepcopy(next(x for x in before["acts"] if x["id"] == linked)["closure_review_json"])
    with session_factory.begin() as session:
        prior = session.get(CaseHandoverSnapshotRecord, UUID(w.view["snapshot_id"]))
        values = {c.name: deepcopy(getattr(prior, c.name)) for c in prior.__table__.columns}
        values.update(id=uuid4(), revision=prior.revision + 1)
        for key in ("command_id", "idempotency_key", "correlation_id"):
            if key in values:
                values[key] = uuid4()
        session.add(CaseHandoverSnapshotRecord(**values))
    after = read()
    assert next(x for x in after["acts"] if x["id"] == reception)["context_state"] == "CURRENT"
    changed = next(x for x in after["acts"] if x["id"] == linked)
    assert changed["context_state"] == "REVIEW_REQUIRED"
    assert changed["closure_review_json"] == captured

    reserve = next(x for x in after["obligations"] if x["id"] == str(obligation))
    assert reserve["declared_status"] == "COMPLETED"
    assert reserve["context_state"] == reserve["origin_context_state"] == "REVIEW_REQUIRED"
    assert str(obligation) in after["open_obligation_ids"]
    from app.platform.events.dispatcher import CommandExecutionError

    with pytest.raises(CommandExecutionError, match="OPEN_OBLIGATIONS_REQUIRE_ACKNOWLEDGEMENT"):
        dispatcher.dispatch(
            command=RecordClosureActCommand(
                **ids(),
                case_id=w.d.case,
                act_id=uuid4(),
                act_kind="CONTRACT_EXIT",
                summary="Sortie à refuser malgré la levée historique.",
                source_refs=["exit://synthetic"],
                evidence_refs=["proof://synthetic"],
                closure_review=dict(
                    expected_dossier_sha256=after["dossier_sha256"],
                    human_confirmed=True,
                    justification="Ancien consentement non transférable.",
                    comparisons=[],
                    acknowledged_open_obligation_ids=[],
                ),
            ),
            context=ctx,
        )

    # Requalification creates fresh declarations; the invalidated history stays open.
    def reserve_command(origin_id):
        return RecordClosureObligationCommand(
            **ids(),
            case_id=w.d.case,
            obligation_id=uuid4(),
            obligation_type="RESERVES_LIFTING",
            origin_reception_act_id=UUID(origin_id),
            summary="Nouvelle réserve synthétique sur réception relue.",
            source_refs=["pv://synthetic/v2"],
            closure_review=dict(
                expected_dossier_sha256=read()["dossier_sha256"],
                human_confirmed=True,
                justification="Nouveau consentement explicite V2.",
                comparisons=[],
            ),
        )

    with pytest.raises(
        CommandExecutionError, match="CLOSURE_COMPARISON_SOURCE_CHANGED_OR_FORBIDDEN"
    ):
        dispatcher.dispatch(command=reserve_command(linked), context=ctx)
    fresh_reception = write([], "pv://synthetic/v2")
    fresh_reserve = reserve_command(fresh_reception)
    dispatcher.dispatch(command=fresh_reserve, context=ctx)
    qualified = read()
    old = next(x for x in qualified["acts"] if x["id"] == linked)
    assert old["closure_review_json"] == captured
    assert old["context_state"] == "REVIEW_REQUIRED"
    fresh_act = next(x for x in qualified["acts"] if x["id"] == fresh_reception)
    assert fresh_act["source_refs_json"] == ["pv://synthetic/v2"]
    assert fresh_act["closure_review_json"]["human_confirmed"] is True
    assert (
        fresh_act["closure_review_json"]["expected_dossier_sha256"]
        != captured["expected_dossier_sha256"]
    )
    new = next(x for x in qualified["obligations"] if x["id"] == str(fresh_reserve.obligation_id))
    assert new["context_state"] == "CURRENT"
    assert new["declared_status"] != "COMPLETED"
    assert new["closure_review_json"]["human_confirmed"] is True
    assert new["closure_review_json"]["justification"] == "Nouveau consentement explicite V2."
    assert str(obligation) in qualified["open_obligation_ids"]
    assert str(fresh_reserve.obligation_id) in qualified["open_obligation_ids"]

    import json
    import os
    from pathlib import Path

    if destination := os.environ.get("SMART_AO_L11_ACTION_PROOF_DIR"):
        target = Path(destination)
        target.mkdir(parents=True, exist_ok=True)
        (target / "before.json").write_text(json.dumps(before, ensure_ascii=False, indent=2))
        (target / "after.json").write_text(json.dumps(after, ensure_ascii=False, indent=2))


def test_closure_checks_declared_change_contract_even_when_offer_bytes_are_unread(
    session_factory, workflow
):
    from app.modules.pricing.infrastructure.case_closure_reader import closure_dossier
    from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
        ContractInstrumentSupersessionRecord,
    )
    from app.modules.pricing.infrastructure.models.contract_instrument_version import (
        ContractInstrumentVersionRecord,
    )
    from tests.db.test_candidate_retrieval_sql import _clone

    w = workflow
    other, replacement = uuid4(), uuid4()
    with session_factory.begin() as session:
        original = session.get(ContractInstrumentVersionRecord, w.d.instrument)
        session.add(_clone(original, id=other, version_reference="Other declared instrument"))
        session.add(
            _clone(
                original,
                id=replacement,
                instrument_kind="AMENDMENT",
                version_reference="Replacement declared instrument",
            )
        )
    w.d.instrument = other
    w.command = w.command.model_copy(update={"contract_instrument_version_id": other})
    test_change_follows_the_exact_handover_and_safe_published_action(session_factory, w)
    with session_factory.begin() as session:
        session.add(
            ContractInstrumentSupersessionRecord(
                id=uuid4(),
                tenant_id=w.d.patron.tenant_id,
                case_id=w.d.case,
                replaced_contract_instrument_version_id=other,
                replacing_contract_instrument_version_id=replacement,
                rationale="Replacement synthetic",
                actor_id=w.d.patron.actor_id,
            )
        )
    with session_factory() as session:
        dossier = closure_dossier(session, w.d.patron.tenant_id, w.d.case)
    assert dossier["change_actions"][0]["context_state"] == "REVIEW_REQUIRED"
