from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.case_handover import build_case_handover_routers
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.patron_action.application.case_handover import CaseHandoverService
from app.modules.patron_action.application.outcome import CaseOutcomeService
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.infrastructure.handover_reader import SqlAlchemyCaseHandoverReader
from app.modules.patron_action.infrastructure.models.handover_receipt import (
    CaseHandoverReceiptRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
from app.platform.security.authenticated_context import AuthenticationContextResolver
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import (
    ActorKind,
    AssignmentScope,
    DataClassification,
    OperationalProfile,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.db.test_case_handover_http_e2e import (
    TokenResolver,
    _seed_decision,
    _seed_handover_sources,
)


@pytest.fixture
def dossier(session_factory, tmp_path):
    with session_factory.begin() as session:
        session.execute(sa.text("TRUNCATE tenants, identities CASCADE"))
    content = (
        "Offre synthétique lot 01. Les accès sont maintenus. "
        "Le transport est exclu de la fourniture."
    ).encode()
    patron, case, package, dispatcher, storage = _seed_handover_sources(
        session_factory, tmp_path, technical_content=content
    )
    now = datetime.now(UTC)
    patron = replace(patron, authenticated_at=now, mfa_verified_at=now)
    outcome = uuid4()
    CaseOutcomeService(
        dispatcher=dispatcher, session_factory=session_factory, policy=AuthorizationPolicy()
    ).execute(
        actor=patron,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            outcome_id=outcome,
            case_id=case,
            lot_reference="01",
            outcome="WON",
            source_locator="attribution://synthetic/01",
        ),
        now=now,
    )
    decision, context, condition = _seed_decision(session_factory, actor=patron, case_id=case)
    instrument = uuid4()
    with session_factory.begin() as session:
        row = ContractInstrumentVersionRecord(
            id=instrument,
            tenant_id=patron.tenant_id,
            case_id=case,
            instrument_kind="SIGNED_CONTRACT",
            version_reference="Contrat attribué synthétique v1",
            source_refs_json=["contract://synthetic/v1/section3"],
            evidence_refs_json=["document://synthetic/signed"],
            actor_id=patron.actor_id,
        )
        session.add(row)
    driver = replace(
        patron,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        operational_profile=OperationalProfile.RESPONSABLE,
        assignment_scopes=(
            AssignmentScope(
                case_id=case,
                allowed_actions=frozenset(
                    {Capability.CASE_DCE_READ.value, Capability.CASE_HANDOVER_RECEIPT_WRITE.value}
                ),
                allowed_classifications=frozenset({DataClassification.INTERNAL_OPERATIONAL}),
            ),
        ),
    )
    resolver = TokenResolver({"patron": patron, "driver": driver})
    service = CaseHandoverService(
        dispatcher=dispatcher,
        reader=SqlAlchemyCaseHandoverReader(session_factory, storage=storage),
        policy=AuthorizationPolicy(),
        storage=storage,
    )
    app = FastAPI()
    for router in build_case_handover_routers(
        service=service,
        security_runtime=ConsultationSecurityRuntime(
            context_resolver=cast(AuthenticationContextResolver, resolver),
            policy=AuthorizationPolicy(),
        ),
    ):
        app.include_router(router)
    return SimpleNamespace(
        patron=patron,
        driver=driver,
        resolver=resolver,
        case=case,
        package=package,
        outcome=outcome,
        condition=condition,
        instrument=instrument,
        service=service,
        client=TestClient(app),
        headers={"Authorization": "Bearer patron"},
        driver_headers={"Authorization": "Bearer driver"},
        content=content,
    )


def publication_body(d, manifest, contract):
    return dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        correlation_id=str(uuid4()),
        snapshot_id=str(uuid4()),
        outcome_id=str(d.outcome),
        submission_package_id=str(d.package),
        operational_review=dict(
            expected_source_context_sha256=d.client.get(
                f"/api/v1/patron/cases/{d.case}/p7-handover/contracts", headers=d.headers
            ).json()["source_context_sha256"],
            expected_handover_revision=0,
            expected_offer_manifest_sha256=manifest,
            contract_instrument_version_id=str(d.instrument),
            expected_contract_record_sha256=contract["record_sha256"],
            justification="Offre et contrat relus pour la passation opérationnelle.",
            human_confirmed=True,
            points=[
                dict(
                    point_id=str(uuid4()),
                    kind="EXCLUSION",
                    statement="Transport exclu; modalités à confirmer.",
                    offer_excerpt="Le transport est exclu de la fourniture.",
                    offer_locator="Offre §3",
                    contract_locator="Contrat §3",
                    difference_state="DECLARED_DIFFERENCE",
                    difference_note="La livraison sur site doit être clarifiée.",
                    responsible="Responsable logistique",
                    action="Obtenir une confirmation écrite du partenaire",
                    expected_evidence="Confirmation logistique",
                    criticality="CRITICAL",
                ),
                dict(
                    point_id=str(uuid4()),
                    kind="CONDITION",
                    condition_id=str(d.condition),
                    statement="Maintenir les accès en site occupé.",
                    offer_excerpt="Les accès sont maintenus.",
                    offer_locator="Offre §2",
                    contract_locator=None,
                    difference_state="UNKNOWN",
                    responsible="Conducteur affecté",
                    action="Faire valider le phasage",
                    expected_evidence="Plan de circulation",
                    criticality="CRITICAL",
                ),
            ],
        ),
    )


def test_compare_publish_receive_and_preserve_scope(session_factory, dossier):
    d = dossier
    url = f"/api/v1/patron/cases/{d.case}/p7-handover"
    options = d.client.get(url + "/contracts", headers=d.headers)
    assert options.status_code == 200, options.text
    contract = options.json()["items"][0]
    with session_factory() as session:
        from app.modules.submission.infrastructure.models import SubmissionPackageRecord

        offer = session.get(SubmissionPackageRecord, d.package)
        manifest = offer.manifest_sha256
    body = publication_body(d, manifest, contract)
    written = d.client.post(url, headers=d.headers, json=body)
    assert written.status_code == 201, written.text
    repeated = d.client.post(url, headers=d.headers, json=body)
    assert repeated.status_code == 200, repeated.text
    read = d.client.get(f"/api/v1/cases/{d.case}/p7-handover", headers=d.driver_headers)
    assert read.status_code == 200, read.text
    view = read.json()["items"][0]
    snapshot = view["snapshot"]
    assert snapshot["contract_comparison"]["state"] == "HUMAN_DECLARED_LINK"
    assert (
        snapshot["operational_review"]["points"][0]["statement"]
        == "Transport exclu; modalités à confirmer."
    )
    assert (
        snapshot["decision"]["open_conditions"][0]["label"] == "Maintenir les accès en site occupé."
    )
    assert (
        snapshot["offer_point_proofs"][body["operational_review"]["points"][0]["point_id"]]["state"]
        == "EXACT_BYTE_MATCH"
    )
    assert snapshot["contract_comparison"]["authority_state"] == "UNKNOWN"
    assert snapshot["p7_is_order_service"] is False
    receipt = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        correlation_id=str(uuid4()),
        receipt_id=str(uuid4()),
        expected_snapshot_revision=view["revision"],
        expected_view_sha256=view["view_sha256"],
        receipt_kind="RECEIVED_WITH_GAPS",
        note="Dossier reçu; points et inconnus conservés.",
        human_confirmed=True,
    )
    path = f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts"
    ack = d.client.post(path, headers=d.driver_headers, json=receipt)
    assert ack.status_code == 201, ack.text
    replay = d.client.post(path, headers=d.driver_headers, json=receipt)
    assert replay.status_code == 200, replay.text
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseHandoverReceiptRecord)) == 1
        )


def publish_fixture(session_factory, d):
    from app.modules.submission.infrastructure.models import SubmissionPackageRecord

    contract = d.client.get(
        f"/api/v1/patron/cases/{d.case}/p7-handover/contracts", headers=d.headers
    ).json()["items"][0]
    with session_factory() as session:
        manifest = session.get(SubmissionPackageRecord, d.package).manifest_sha256
    body = publication_body(d, manifest, contract)
    response = d.client.post(
        f"/api/v1/patron/cases/{d.case}/p7-handover", headers=d.headers, json=body
    )
    assert response.status_code == 201, response.text
    return body, d.client.get(
        f"/api/v1/cases/{d.case}/p7-handover", headers=d.driver_headers
    ).json()["items"][0]


def test_historical_won_cannot_publish_after_a_lost_outcome(session_factory, dossier):
    d = dossier
    body, view = publish_fixture(session_factory, d)
    from app.modules.patron_action.application.outcome import CaseOutcomeService
    from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand

    CaseOutcomeService(
        dispatcher=d.service._dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    ).execute(
        actor=d.patron,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            outcome_id=uuid4(),
            case_id=d.case,
            lot_reference="01",
            outcome="LOST",
            source_locator="attribution://synthetic/corrected",
        ),
        now=datetime.now(UTC),
    )
    body.update(command_id=str(uuid4()), idempotency_key=str(uuid4()), snapshot_id=str(uuid4()))
    body["operational_review"]["expected_handover_revision"] = 1
    response = d.client.post(
        f"/api/v1/patron/cases/{d.case}/p7-handover", headers=d.headers, json=body
    )
    assert response.status_code == 409, response.text
    options = d.client.get(f"/api/v1/patron/cases/{d.case}/p7-handover-options", headers=d.headers)
    assert options.json()["items"] == []


def test_file_tampering_invalidates_the_operational_view(session_factory, dossier):
    d = dossier
    body, view = publish_fixture(session_factory, d)
    from app.modules.preparation.infrastructure.models import GeneratedTechnicalDocumentRecord
    from app.modules.submission.infrastructure.models import SubmissionPackageRecord

    with session_factory() as session:
        package = session.get(SubmissionPackageRecord, d.package)
        document = session.get(GeneratedTechnicalDocumentRecord, package.technical_document_id)
    d.service._storage._path(document.storage_key).write_bytes(b"tampered synthetic file")
    reread = d.client.get(f"/api/v1/cases/{d.case}/p7-handover", headers=d.driver_headers)
    assert reread.json()["items"][0]["source_state"] == "REVIEW_REQUIRED"
    assert "OFFER_DOCUMENT_REVIEW_REQUIRED" in reread.json()["items"][0]["source_reasons"]


def receipt_body(view):
    return dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        correlation_id=str(uuid4()),
        receipt_id=str(uuid4()),
        expected_snapshot_revision=view["revision"],
        expected_view_sha256=view["view_sha256"],
        receipt_kind="RECEIVED_WITH_GAPS",
        note="Reçu avec les inconnus signalés.",
        human_confirmed=True,
    )


@pytest.mark.parametrize("fault", ["hash", "revision", "gaps", "profile", "assignment", "patron"])
def test_receipt_refuses_wrong_view_or_authority(session_factory, dossier, fault):
    d = dossier
    _, view = publish_fixture(session_factory, d)
    body = receipt_body(view)
    headers = d.driver_headers
    expected = 403
    if fault == "hash":
        body["expected_view_sha256"] = "0" * 64
        expected = 409
    elif fault == "revision":
        body["expected_snapshot_revision"] += 1
        expected = 409
    elif fault == "gaps":
        body["receipt_kind"] = "RECEIVED"
        expected = 422
    elif fault == "profile":
        d.resolver.actors["driver"] = replace(
            d.driver, operational_profile=OperationalProfile.EXPERT
        )
    elif fault == "assignment":
        d.resolver.actors["driver"] = replace(d.driver, assignment_scopes=())
    elif fault == "patron":
        headers = d.headers
    response = d.client.post(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts",
        headers=headers,
        json=body,
    )
    assert response.status_code == expected, response.text
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseHandoverReceiptRecord)) == 0
        )


def test_changed_payload_on_same_idempotency_key_is_conflict(session_factory, dossier):
    d = dossier
    body, _ = publish_fixture(session_factory, d)
    body["operational_review"]["justification"] = "Une autre justification humaine."
    response = d.client.post(
        f"/api/v1/patron/cases/{d.case}/p7-handover", headers=d.headers, json=body
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "IDEMPOTENCY_KEY_REUSED"


def test_receipt_is_append_only_and_revision_bound(session_factory, dossier):
    from sqlalchemy.exc import DBAPIError

    d = dossier
    _, view = publish_fixture(session_factory, d)
    body = receipt_body(view)
    path = f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts"
    response = d.client.post(path, headers=d.driver_headers, json=body)
    assert response.status_code == 201, response.text
    for statement in [
        "UPDATE case_handover_receipts SET note='modified'",
        "DELETE FROM case_handover_receipts",
    ]:
        with pytest.raises(DBAPIError, match="append-only"), session_factory.begin() as session:
            session.execute(sa.text(statement))
    with session_factory() as session:
        row = session.scalar(sa.select(CaseHandoverReceiptRecord))
        copied = {column.name: getattr(row, column.name) for column in row.__table__.columns}
    copied.update(id=uuid4(), command_id=uuid4(), idempotency_key=uuid4(), snapshot_revision=99)
    with pytest.raises(DBAPIError, match="revision mismatch"), session_factory.begin() as session:
        session.add(CaseHandoverReceiptRecord(**copied))


def test_declared_contract_replacement_invalidates_without_relinking(session_factory, dossier):
    from app.modules.pricing.infrastructure.models.contract_instrument_supersession import (
        ContractInstrumentSupersessionRecord,
    )

    d = dossier
    _, view = publish_fixture(session_factory, d)
    next_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            ContractInstrumentVersionRecord(
                id=next_id,
                tenant_id=d.patron.tenant_id,
                case_id=d.case,
                instrument_kind="AMENDMENT",
                version_reference="Avenant déclaré v2",
                source_refs_json=["contract://synthetic/v2"],
                evidence_refs_json=["proof://synthetic/v2"],
                actor_id=d.patron.actor_id,
            )
        )
        session.flush()
        session.add(
            ContractInstrumentSupersessionRecord(
                id=uuid4(),
                tenant_id=d.patron.tenant_id,
                case_id=d.case,
                replacing_contract_instrument_version_id=next_id,
                replaced_contract_instrument_version_id=d.instrument,
                rationale="Remplacement déclaré synthétique",
                actor_id=d.patron.actor_id,
            )
        )
    exact = d.client.get(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}", headers=d.driver_headers
    )
    current = exact.json()
    assert current["source_state"] == "REVIEW_REQUIRED"
    assert current["snapshot"]["contract_comparison"]["instrument_version_id"] == str(d.instrument)
    assert current["view_sha256"] != view["view_sha256"]
    response = d.client.post(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts",
        headers=d.driver_headers,
        json=receipt_body(view),
    )
    assert response.status_code == 409, response.text


@pytest.mark.parametrize("model_name", ["decision", "contract"])
def test_receipt_locks_its_referenced_sources(session_factory, dossier, monkeypatch, model_name):
    from app.modules.decision.infrastructure.models.decision import DecisionRecord
    from app.modules.patron_action.application import handover_receipt_handler as module
    from sqlalchemy.exc import OperationalError

    d = dossier
    _, view = publish_fixture(session_factory, d)
    original = module.current_handover_view
    observed = []

    def inspect_locks(session, snapshot, *, storage):
        model = DecisionRecord if model_name == "decision" else ContractInstrumentVersionRecord
        target_id = (
            view["snapshot"]["decision"]["decision_id"]
            if model_name == "decision"
            else d.instrument
        )
        with pytest.raises(OperationalError) as failure, session_factory.begin() as competitor:
            competitor.scalar(
                sa.select(model).where(model.id == target_id).with_for_update(nowait=True)
            )
        assert failure.value.orig.sqlstate == "55P03"
        observed.append(model_name)
        return original(session, snapshot, storage=storage)

    monkeypatch.setattr(module, "current_handover_view", inspect_locks)
    response = d.client.post(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts",
        headers=d.driver_headers,
        json=receipt_body(view),
    )
    assert response.status_code == 201, response.text
    assert observed == [model_name]


@pytest.mark.parametrize(
    "fault", ["mfa", "finance", "foreign_case", "foreign_tenant", "private_point"]
)
def test_publication_refuses_revoked_authority_and_private_content(session_factory, dossier, fault):
    d = dossier
    body, _ = publish_fixture(session_factory, d)
    path = f"/api/v1/patron/cases/{d.case}/p7-handover"
    expected = 403
    if fault == "mfa":
        d.resolver.actors["patron"] = replace(d.patron, mfa_verified_at=None)
    elif fault == "finance":
        d.resolver.actors["patron"] = replace(
            d.patron, capabilities=d.patron.capabilities - {Capability.PRICING_READ}
        )
    elif fault == "foreign_case":
        path = f"/api/v1/patron/cases/{uuid4()}/p7-handover"
        body.update(command_id=str(uuid4()), idempotency_key=str(uuid4()))
        expected = 422
    elif fault == "foreign_tenant":
        d.resolver.actors["patron"] = replace(d.patron, tenant_id=uuid4())
        body.update(command_id=str(uuid4()), idempotency_key=str(uuid4()))
        expected = 422
    else:
        body["operational_review"]["points"][0]["statement"] = (
            "La marge brute cible est de 23 pour cent."
        )
        expected = 422
    response = d.client.post(path, headers=d.headers, json=body)
    assert response.status_code == expected, response.text
    read = d.client.get(f"/api/v1/cases/{d.case}/p7-handover", headers=d.driver_headers)
    assert "marge brute cible" not in read.text


def test_migration_refuses_nonempty_downgrade_and_roundtrips_empty(session_factory, dossier):
    from alembic import command as migration
    from alembic.config import Config
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    d = dossier
    _, view = publish_fixture(session_factory, d)
    response = d.client.post(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}/receipts",
        headers=d.driver_headers,
        json=receipt_body(view),
    )
    assert response.status_code == 201, response.text
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="cannot downgrade"):
        migration.downgrade(config, "20261023_0142")
    with session_factory.begin() as session:
        assert (
            session.scalar(sa.text("SELECT version_num FROM alembic_version"))
            == EXPECTED_ALEMBIC_HEAD
        )
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseHandoverReceiptRecord)) == 1
        )
        session.execute(sa.text("TRUNCATE case_handover_receipts"))
    migration.downgrade(config, "20261023_0142")
    migration.upgrade(config, "head")
    with session_factory() as session:
        assert (
            session.scalar(sa.text("SELECT version_num FROM alembic_version"))
            == EXPECTED_ALEMBIC_HEAD
        )
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseHandoverReceiptRecord)) == 0
        )
        assert (
            d.client.get(
                f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}",
                headers=d.driver_headers,
            ).status_code
            == 200
        )


def test_receipt_limit_is_explicit_in_projection(session_factory, dossier):
    d = dossier
    _, view = publish_fixture(session_factory, d)
    with session_factory.begin() as session:
        for _ in range(101):
            session.add(
                CaseHandoverReceiptRecord(
                    id=uuid4(),
                    tenant_id=d.patron.tenant_id,
                    case_id=d.case,
                    snapshot_id=view["snapshot_id"],
                    snapshot_revision=view["revision"],
                    view_sha256=view["view_sha256"],
                    receipt_kind="RECEIVED_WITH_GAPS",
                    note="Reçu synthétique",
                    actor_id=d.driver.actor_id,
                    membership_id=d.driver.membership_id,
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                    correlation_id=uuid4(),
                )
            )
    response = d.client.get(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}", headers=d.driver_headers
    )
    assert len(response.json()["receipts"]) == 100
    assert response.json()["receipts_truncated"] is True


def test_normal_exact_history_return_the_same_hashed_operational_view(session_factory, dossier):
    from app.modules.patron_action.application.operational_handover import canonical_sha256

    d = dossier
    _, view = publish_fixture(session_factory, d)
    exact = d.client.get(
        f"/api/v1/cases/{d.case}/p7-handover/{view['snapshot_id']}", headers=d.driver_headers
    ).json()
    history = d.client.get(
        f"/api/v1/cases/{d.case}/p7-handover/history", headers=d.driver_headers
    ).json()["items"][0]
    assert view["snapshot"] == exact["snapshot"] == history["snapshot"]
    assert view["view_sha256"] == exact["view_sha256"] == history["view_sha256"]
    assert view["snapshot"]["offer"]["file_revalidation_state"] == "REVALIDATED_BYTES"
    assert (
        canonical_sha256(
            dict(
                snapshot_id=view["snapshot_id"],
                revision=view["revision"],
                snapshot=view["snapshot"],
                source_state=view["source_state"],
                source_reasons=view["source_reasons"],
            )
        )
        == view["view_sha256"]
    )


def test_publication_refuses_case_scope_changed_after_review(session_factory, dossier):
    from app.modules.case.infrastructure.models.case import CaseRecord

    d = dossier
    body, _ = publish_fixture(session_factory, d)
    body.update(command_id=str(uuid4()), idempotency_key=str(uuid4()), snapshot_id=str(uuid4()))
    body["operational_review"]["expected_handover_revision"] = 1
    with session_factory.begin() as session:
        case = session.get(CaseRecord, d.case)
        old_fingerprint = case.scope_fingerprint
        case.scope_json = {"lot_numbers": ["01", "02"]}
        case.scope_fingerprint = uuid4().hex * 2
        session.flush()
        assert case.scope_fingerprint != old_fingerprint
    response = d.client.post(
        f"/api/v1/patron/cases/{d.case}/p7-handover", headers=d.headers, json=body
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "HANDOVER_CASE_CONTEXT_CONFLICT"


def test_overlapping_offer_excerpts_are_ambiguous():
    from app.modules.patron_action.infrastructure.operational_handover import unique_excerpt_offsets

    assert unique_excerpt_offsets(b"zone zone zone", b"zone zone") == ("AMBIGUOUS", None, None)
    assert unique_excerpt_offsets(b"abc def", b"def") == ("EXACT_BYTE_MATCH", 4, 7)


def test_contract_options_refuse_a_case_outside_the_tenant(session_factory, dossier):
    d = dossier
    response = d.client.get(
        f"/api/v1/patron/cases/{uuid4()}/p7-handover/contracts", headers=d.headers
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "FORBIDDEN"}


@pytest.mark.parametrize("operation", ["options", "publish"])
def test_old_offer_cannot_be_selected_or_republished_under_a_new_dce(
    session_factory, dossier, operation
):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from app.modules.submission.infrastructure.models import SubmissionPackageRecord
    from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord
    from tests.db.test_candidate_retrieval_sql import _clone

    d = dossier
    replacement = uuid4()
    with session_factory.begin() as session:
        case = session.get(CaseRecord, d.case)
        package = session.get(SubmissionPackageRecord, d.package)
        assert case.applicable_dce_version_id == package.dce_version_id
        prior = session.get(DceVersionRecord, package.dce_version_id)
        session.add(
            _clone(prior, id=replacement, predecessor_dce_version_id=prior.id, corpus_hash="f" * 64)
        )
        session.flush()
        case.applicable_dce_version_id = replacement
        case.dce_freshness = "CURRENT"
        manifest = package.manifest_sha256
    with session_factory() as session:
        before = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(m))
            for m in (DomainEventRecord, OutboxMessageRecord)
        )
    if operation == "options":
        response = d.client.get(
            f"/api/v1/patron/cases/{d.case}/p7-handover-options", headers=d.headers
        )
        assert response.status_code == 200, response.text
        assert all(x["submission_package_id"] != str(d.package) for x in response.json()["items"])
    else:
        contract = d.client.get(
            f"/api/v1/patron/cases/{d.case}/p7-handover/contracts", headers=d.headers
        ).json()["items"][0]
        body = publication_body(d, manifest, contract)
        response = d.client.post(
            f"/api/v1/patron/cases/{d.case}/p7-handover", headers=d.headers, json=body
        )
        assert response.status_code == 409, response.text
        assert response.json()["detail"] == "HANDOVER_OFFER_VERSION_CONFLICT"
    with session_factory() as session:
        after = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(m))
            for m in (DomainEventRecord, OutboxMessageRecord)
        )
    assert after == before
