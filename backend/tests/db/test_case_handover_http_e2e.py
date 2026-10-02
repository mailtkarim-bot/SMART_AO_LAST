from __future__ import annotations

import socket
import time
from dataclasses import replace
from datetime import UTC, datetime
from hashlib import sha256
from threading import Thread
from uuid import UUID, uuid4

import httpx
import pytest
import sqlalchemy as sa
import uvicorn
from app.interfaces.http.routes.case_handover import build_case_handover_routers
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_actions import build_patron_action_router
from app.interfaces.http.routes.patron_case_contract_changes import (
    build_patron_case_contract_change_router,
)
from app.interfaces.http.routes.patron_contract_baseline_impacts import (
    build_patron_contract_baseline_impact_router,
)
from app.interfaces.http.routes.patron_decisions import build_patron_decision_router
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.contract_baseline_handler import (
    ContractBaselineImpactReadService,
    ContractBaselineImpactWriteService,
    contract_baseline_handlers,
)
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.decision.application.finalize import (
    PatronDecisionFinalizationService,
    decision_finalization_handlers,
)
from app.modules.decision.application.lifecycle import (
    PatronDecisionLifecycleService,
    decision_lifecycle_handlers,
)
from app.modules.decision.application.patron_dossier import PatronDecisionDossierService
from app.modules.decision.infrastructure.condition_repository import (
    SqlAlchemyDecisionConditionRepository,
)
from app.modules.decision.infrastructure.dossier_reader import SqlAlchemyDecisionDossierReader
from app.modules.decision.infrastructure.models.decision import (
    DecisionConditionRecord,
    DecisionContextRecord,
    DecisionRecord,
)
from app.modules.decision.infrastructure.repositories import (
    SqlAlchemyDecisionLifecycleRepository,
    SqlAlchemyDecisionRepository,
)
from app.modules.decision.infrastructure.verified_context_reader import (
    SqlAlchemyDecisionVerifiedContextReader,
)
from app.modules.enterprise.application.business_method_profile_handler import (
    BusinessMethodProfileService,
    business_method_profile_handlers,
)
from app.modules.enterprise.infrastructure.models.enterprise import EnterpriseCompanyRecord
from app.modules.enterprise.public.business_method_profile_contracts import (
    AdoptBusinessMethodProfileRequest,
    BusinessMethodProfileContent,
    PublishBusinessMethodProfileRequest,
)
from app.modules.patron_action.application.case_handover import (
    CaseHandoverService,
    case_handover_handlers,
)
from app.modules.patron_action.application.outcome import CaseOutcomeService, case_outcome_handlers
from app.modules.patron_action.application.outcome_commands import RecordCaseOutcomeCommand
from app.modules.patron_action.application.service import PatronActionService
from app.modules.patron_action.application.transition_service import PatronActionTransitionService
from app.modules.patron_action.infrastructure.handover_reader import (
    SqlAlchemyCaseHandoverReader,
)
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.order import CaseOrderRecord
from app.modules.patron_action.infrastructure.models.p7 import CaseP7ResultRecord
from app.modules.preparation.application.service import PreparationService, preparation_handlers
from app.modules.preparation.infrastructure.dce_preparation_reader import (
    SqlAlchemyPreparationDceReader,
)
from app.modules.preparation.infrastructure.document_storage import LocalGeneratedDocumentStorage
from app.modules.preparation.infrastructure.models import PreparationPackageRecord
from app.modules.pricing.application.case_contract_change import (
    CaseContractChangeService,
    case_contract_change_handlers,
)
from app.modules.pricing.infrastructure.case_contract_change_reader import (
    SqlAlchemyCaseContractChangeReader,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEventRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.modules.submission.application.commands import PrepareSubmissionPackageCommand
from app.modules.submission.application.service import SubmissionPackageService, submission_handlers
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    AssignmentScope,
    DataClassification,
    OperationalProfile,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session, sessionmaker
from tests.application.test_collab_work_task import NOW
from tests.application.test_submission_package import (
    _authorize_package,
    _prepare_generated_document,
    _publish_snapshot,
    _ReadySubmissionDecisionGateReader,
)


class TokenResolver:
    def __init__(self, actors: dict[str, ActorContext]) -> None:
        self.actors = actors

    def resolve(self, *, access_token: str) -> ActorContext:
        return self.actors[access_token]


def _seed_handover_sources(session_factory: sessionmaker[Session], tmp_path):
    storage = LocalGeneratedDocumentStorage(root=tmp_path / "generated")
    gate = _ReadySubmissionDecisionGateReader()
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            **preparation_handlers(storage=storage, dce_reader=SqlAlchemyPreparationDceReader()),
            **submission_handlers(decision_gate_reader=gate),
            **case_outcome_handlers(),
            **case_handover_handlers(),
        },
    )
    preparation = PreparationService(
        session_factory=session_factory,
        dispatcher=dispatcher,
        policy=AuthorizationPolicy(),
        storage=storage,
    )
    submission = SubmissionPackageService(
        session_factory=session_factory,
        dispatcher=dispatcher,
        policy=AuthorizationPolicy(),
        storage=storage,
        decision_gate_reader=gate,
    )
    patron, preparation_id, case_id = _prepare_generated_document(
        (preparation, submission), session_factory
    )
    with session_factory.begin() as session:
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == patron.tenant_id, CaseRecord.id == case_id
            )
        )
        assert case is not None
        case.scope_kind = "MULTI_LOT"
        case.scope_json = {"lot_numbers": ["01"]}
    _publish_snapshot(session_factory, tenant_id=patron.tenant_id, case_id=case_id)
    with session_factory() as session:
        package = session.get(PreparationPackageRecord, preparation_id)
        assert package is not None
        expected_revision = package.aggregate_revision
    prepared = submission.prepare(
        actor=patron,
        command=PrepareSubmissionPackageCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            preparation_package_id=preparation_id,
            expected_preparation_revision=expected_revision,
        ),
        now=NOW,
    )
    package_id = __import__("uuid").UUID(prepared.aggregate_refs[0]["aggregate_id"])
    _authorize_package(submission, patron, package_id)
    return patron, case_id, package_id, dispatcher, storage


def _record_a1_source_condition(session_factory, *, actor: ActorContext, case_id):
    """Create the real A1 source→impact→condition chain before B1 snapshots it."""
    now = datetime.now(tz=UTC)
    actor = replace(actor, authenticated_at=now, mfa_verified_at=now)
    company_id = uuid4()
    with session_factory.begin() as session:
        case = session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == actor.tenant_id, CaseRecord.id == case_id
            )
        )
        assert case is not None
        requirement_id = session.scalar(
            sa.select(DceRequirementRecord.id)
            .where(
                DceRequirementRecord.tenant_id == actor.tenant_id,
                DceRequirementRecord.dce_version_id == case.applicable_dce_version_id,
            )
            .order_by(DceRequirementRecord.id)
            .limit(1)
        )
        assert requirement_id is not None
        siren = f"{actor.tenant_id.int % 1_000_000_000:09d}"
        session.add(
            EnterpriseCompanyRecord(
                id=company_id,
                tenant_id=actor.tenant_id,
                aggregate_revision=0,
                legal_name="Entreprise fixture Q1",
                trade_name=None,
                siren=siren,
                siret=f"{siren}00001",
                vat_number=f"FR{siren}12345",
                address_line1="1 rue de la Fixture",
                postal_code="75001",
                city="Paris",
                country_code="FR",
            )
        )

    policy = AuthorizationPolicy()
    lifecycle_repository = SqlAlchemyDecisionLifecycleRepository()

    def decision_repository_factory(session):
        return SqlAlchemyDecisionRepository(session)

    handlers = {
        **business_method_profile_handlers(),
        **contract_baseline_handlers(),
        **decision_lifecycle_handlers(
            lifecycle_repository=lifecycle_repository,
            repository_factory=decision_repository_factory,
            condition_repository=SqlAlchemyDecisionConditionRepository(),
        ),
        **decision_finalization_handlers(
            repository_factory=decision_repository_factory,
            verified_context_reader=SqlAlchemyDecisionVerifiedContextReader(),
            condition_repository=SqlAlchemyDecisionConditionRepository(),
        ),
    }
    dispatcher = CommandDispatcher(session_factory=session_factory, handlers=handlers)
    profile_service = BusinessMethodProfileService(
        dispatcher=dispatcher, session_factory=session_factory, policy=policy
    )
    published = profile_service.publish(
        actor=actor,
        command=PublishBusinessMethodProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            expected_version=0,
            profile=BusinessMethodProfileContent.model_validate(
                {"terminology": {}, "additional_checks": []}
            ),
        ).to_command(company_id=company_id),
        now=now,
    )
    profile_ref = published.aggregate_refs[0]
    profile_service.adopt(
        actor=actor,
        command=AdoptBusinessMethodProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            expected_adoption_revision=0,
            profile_version_id=profile_ref["aggregate_id"],
            profile_version=profile_ref["aggregate_revision"],
            profile_content_sha256=profile_ref["content_hash"],
        ).to_command(case_id=case_id),
        now=now,
    )

    resolver = TokenResolver({"patron": actor})
    security_runtime = ConsultationSecurityRuntime(
        context_resolver=resolver, policy=policy
    )
    app = FastAPI()
    app.include_router(
        build_patron_contract_baseline_impact_router(
            service=ContractBaselineImpactReadService(
                session_factory=session_factory, policy=policy
            ),
            write_service=ContractBaselineImpactWriteService(
                dispatcher=dispatcher, policy=policy
            ),
            security_runtime=security_runtime,
        )
    )
    app.include_router(
        build_patron_decision_router(
            service=PatronDecisionDossierService(
                reader=SqlAlchemyDecisionDossierReader(session_factory), policy=policy
            ),
            lifecycle_service=PatronDecisionLifecycleService(
                dispatcher=dispatcher, policy=policy
            ),
            finalization_service=PatronDecisionFinalizationService(
                dispatcher=dispatcher, policy=policy
            ),
            security_runtime=security_runtime,
        )
    )

    with TestClient(app, raise_server_exceptions=False) as client:
        headers = {"Authorization": "Bearer patron"}
        impact_id = uuid4()
        impact_path = f"/api/v1/patron/cases/{case_id}/contract-baseline-impacts"
        impact_payload = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "proof_id": str(impact_id),
            "dce_requirement_id": str(requirement_id),
            "dce_requirement_revision": 1,
            "baseline_source_refs": [f"DCE_REQUIREMENT:{requirement_id}@1"],
            "baseline_statement": "Clause source déclarée dans la fixture Q1.",
            "deviation_statement": "Écart à examiner par le Patron.",
            "impact_statement": "Impact déclaré ; aucun calcul financier.",
        }
        response = client.post(
            impact_path,
            headers=headers,
            json=impact_payload,
        )
        assert response.status_code == 201, response.text
        impact_replay = client.post(impact_path, headers=headers, json=impact_payload)
        assert impact_replay.status_code == 200
        assert impact_replay.json()["replayed"] is True

        created = client.post(
            f"/api/v1/patron/cases/{case_id}/decisions",
            headers=headers,
            json={"command_id": str(uuid4()), "idempotency_key": str(uuid4())},
        )
        assert created.status_code == 201, created.text
        decision_id = created.json()["decision_id"]
        frozen = client.post(
            f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/context",
            headers=headers,
            json={
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "context_id": str(uuid4()),
                "expected_revision": created.json()["version"],
                "rationale": "Évaluation sourcée de la fixture Q1.",
                "references": [
                    {
                        "aggregate_type": "CASE",
                        "aggregate_id": str(case_id),
                        "aggregate_revision": 1,
                        "reference_role": "SUBJECT",
                    },
                    {
                        "aggregate_type": "DCE_REQUIREMENT",
                        "aggregate_id": str(requirement_id),
                        "aggregate_revision": 1,
                        "reference_role": "REQUIREMENT",
                    },
                    {
                        "aggregate_type": "CONTRACT_BASELINE_IMPACT",
                        "aggregate_id": str(impact_id),
                        "aggregate_revision": 1,
                        "reference_role": "DECLARED_IMPACT",
                    },
                    {
                        "aggregate_type": "BUSINESS_METHOD_PROFILE",
                        "aggregate_id": str(profile_ref["aggregate_id"]),
                        "aggregate_revision": int(profile_ref["aggregate_revision"]),
                        "content_hash": str(profile_ref["content_hash"]),
                        "reference_role": "ADOPTED_METHOD",
                    },
                ],
            },
        )
        assert frozen.status_code == 200, frozen.text
        condition_id = uuid4()
        finalized = client.post(
            f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/go-no-go",
            headers=headers,
            json={
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "expected_revision": frozen.json()["version"],
                "displayed_fingerprint": frozen.json()["fingerprint"],
                "outcome": "CONDITIONAL_GO",
                "justification": "Condition de revue source-backed.",
                "conditions": [
                    {
                        "condition_id": str(condition_id),
                        "label": "Revoir l’impact après changement contractuel",
                        "owner_actor_id": str(actor.actor_id),
                        "due_date_absence_reason": "Date non déterminée.",
                        "failure_consequence": "Réexamen Patron.",
                    }
                ],
            },
        )
        assert finalized.status_code == 200, finalized.text
        unknown_impact_id = uuid4()
        with session_factory.begin() as session:
            session.add(
                ContractBaselineDeviationImpactRecord(
                    id=unknown_impact_id,
                    tenant_id=actor.tenant_id,
                    case_id=case_id,
                    baseline_observation_id=uuid4(),
                    dce_requirement_id=requirement_id,
                    dce_requirement_revision=1,
                    proof_revision=1,
                    baseline_source_refs_json=[f"DCE_REQUIREMENT:{requirement_id}@1"],
                    baseline_statement="Source inconnue conservée dans la fixture.",
                    deviation_statement=None,
                    impact_statement=None,
                    status="UNKNOWN",
                    created_by_actor_id=actor.actor_id,
                )
            )
        link_path = (
            f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/conditions/"
            f"{condition_id}/contract-evidence"
        )
        link_payload = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "link_id": str(uuid4()),
            "contract_impact_id": str(impact_id),
            "proof_revision": 1,
            "expected_decision_revision": finalized.json()["version"],
        }
        unknown_link = client.post(
            link_path,
            headers=headers,
            json={
                **link_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "link_id": str(uuid4()),
                "contract_impact_id": str(unknown_impact_id),
            },
        )
        assert unknown_link.status_code == 422
        assert (
            unknown_link.json()["detail"]
            == "CONTRACT_PROOF_REQUIRES_HUMAN_REVIEW_STATE"
        )
        linked = client.post(link_path, headers=headers, json=link_payload)
        assert linked.status_code == 201, linked.text
        link_replay = client.post(link_path, headers=headers, json=link_payload)
        assert link_replay.status_code == 200
        assert link_replay.json()["replayed"] is True
        dossier = client.get(
            f"/api/v1/patron/cases/{case_id}/decision-dossier", headers=headers
        )
        assert dossier.status_code == 200, dossier.text
        assert dossier.json()["conditions"][0]["status"] == "OPEN"
        assert len(dossier.json()["contract_evidence_links"]) == 1
        link = dossier.json()["contract_evidence_links"][0]
        assert link["dce_requirement_id"] == str(requirement_id)
        assert link["contract_impact_id"] == str(impact_id)
        assert link["profile_version_id"] == str(profile_ref["aggregate_id"])
        return {
            "requirement_id": str(requirement_id),
            "impact_id": str(impact_id),
            "decision_id": str(decision_id),
            "condition_id": str(condition_id),
            "profile_version_id": str(profile_ref["aggregate_id"]),
            "profile_version": int(profile_ref["aggregate_revision"]),
            "profile_hash": str(profile_ref["content_hash"]),
            "dossier": dossier.json(),
        }


def _seed_decision(session_factory: sessionmaker[Session], *, actor, case_id):
    decision_id, context_id, condition_id = uuid4(), uuid4(), uuid4()
    now = datetime.now(tz=UTC)
    with session_factory.begin() as session:
        session.add(
            DecisionRecord(
                id=decision_id,
                tenant_id=actor.tenant_id,
                decision_type="GO_NO_GO",
                subject_type="CASE",
                subject_id=case_id,
                case_id=case_id,
                scope_fingerprint="a" * 64,
                decision_key_hash=sha256(str(case_id).encode()).hexdigest(),
                cycle_number=1,
                lifecycle="DRAFT",
                outcome="UNDECIDED",
                validity="CURRENT",
                condition_status="OPEN",
                context_status="FROZEN",
                selected_final_context_id=None,
                successor_decision_id=None,
                final_justification=None,
                finalized_by_actor_id=None,
                finalized_at=None,
                aggregate_revision=1,
            )
        )
        session.flush()
        session.add(
            DecisionContextRecord(
                id=context_id,
                tenant_id=actor.tenant_id,
                decision_id=decision_id,
                sequence_number=1,
                context_fingerprint="b" * 64,
                canonical_context_json={"known": [], "risks": []},
                rationale="Contexte de recette.",
                unknowns_json=[],
                prepared_at=now,
                context_state="FROZEN",
                is_selected_final=True,
            )
        )
        session.add(
            DecisionConditionRecord(
                id=condition_id,
                tenant_id=actor.tenant_id,
                decision_id=decision_id,
                label="Réserve de lancement à lever",
                owner_actor_id=actor.actor_id,
                due_at=None,
                due_date_absence_reason="Date non définie.",
                failure_consequence="La condition reste à traiter.",
                status="OPEN",
                satisfied_evidence_ref_json=None,
                failure_reason=None,
                waiver_justification=None,
            )
        )
        decision = session.get(DecisionRecord, decision_id)
        assert decision is not None
        decision.lifecycle = "FINALIZED"
        decision.outcome = "CONDITIONAL_GO"
        decision.condition_status = "OPEN"
        decision.selected_final_context_id = context_id
        decision.final_justification = "Décision conditionnelle de recette."
        decision.finalized_by_actor_id = actor.actor_id
        decision.finalized_at = now
    return decision_id, context_id, condition_id


def test_http_p7_handover_is_exact_append_only_and_finance_redacted(
    database_engine, session_factory, tmp_path
):
    patron, case_id, package_id, dispatcher, storage = _seed_handover_sources(
        session_factory, tmp_path
    )
    outcome_service = CaseOutcomeService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    outcome_id = uuid4()
    outcome_service.execute(
        actor=patron,
        command=RecordCaseOutcomeCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            outcome_id=outcome_id,
            case_id=case_id,
            lot_reference="01",
            outcome="WON",
            source_locator="attribution://notification/lot-01",
        ),
        now=NOW,
    )
    _seed_decision(session_factory, actor=patron, case_id=case_id)
    service = CaseHandoverService(
        dispatcher=dispatcher,
        reader=SqlAlchemyCaseHandoverReader(session_factory),
        policy=AuthorizationPolicy(),
        storage=storage,
    )
    collaborator = replace(
        patron,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        operational_profile=OperationalProfile.RESPONSABLE,
        assignment_scopes=(
            AssignmentScope(
                case_id=case_id,
                allowed_actions=frozenset(
                    {
                        Capability.CASE_DCE_READ.value,
                    }
                ),
                allowed_classifications=frozenset({DataClassification.INTERNAL_OPERATIONAL}),
            ),
        ),
    )
    resolver = TokenResolver({"patron": patron, "conductor": collaborator})
    app = FastAPI()
    for router in build_case_handover_routers(
        service=service,
        security_runtime=ConsultationSecurityRuntime(
            context_resolver=resolver,
            policy=AuthorizationPolicy(),
        ),
    ):
        app.include_router(router)

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical", access_log=False)
    )
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 8
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started
    base = f"http://127.0.0.1:{port}/api/v1"
    try:
        with httpx.Client(timeout=5) as client:
            patron_headers = {"Authorization": "Bearer patron"}
            conductor_headers = {"Authorization": "Bearer conductor"}
            options = client.get(
                f"{base}/patron/cases/{case_id}/p7-handover-options", headers=patron_headers
            )
            assert options.status_code == 200, options.text
            assert len(options.json()["items"]) == 1
            option = options.json()["items"][0]
            assert option["submission_package_id"] == str(package_id)
            assert option["technical_document_sha256"]
            request = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "snapshot_id": str(uuid4()),
                "outcome_id": str(outcome_id),
                "submission_package_id": str(package_id),
            }
            first = client.post(
                f"{base}/patron/cases/{case_id}/p7-handover",
                headers=patron_headers,
                json=request,
            )
            replay = client.post(
                f"{base}/patron/cases/{case_id}/p7-handover",
                headers=patron_headers,
                json=request,
            )
            assert first.status_code == 201, first.text
            assert replay.status_code == 200
            assert replay.json()["replayed"] is True

            read = client.get(f"{base}/cases/{case_id}/p7-handover", headers=conductor_headers)
            assert read.status_code == 200, read.text
            item = read.json()["items"][0]
            snapshot = item["snapshot"]
            assert snapshot["p7_is_order_service"] is False
            assert snapshot["award"]["source_locator"] == "attribution://notification/lot-01"
            assert snapshot["decision"]["conditions_state"] == "KNOWN"
            assert snapshot["decision"]["open_conditions"][0]["status"] == "OPEN"
            assert snapshot["contract_comparison"]["state"] == "UNKNOWN"
            assert snapshot["offer"]["manifest_sha256"] == option["manifest_sha256"]
            assert (
                snapshot["offer"]["technical_document_sha256"]
                == option["technical_document_sha256"]
            )
            serialized = __import__("json").dumps(snapshot)
            assert "financial_snapshot_id" not in serialized
            assert "gross_margin" not in serialized
            assert "financial_content" in serialized
            download = client.get(
                f"{base}/cases/{case_id}/p7-handover/{item['snapshot_id']}/offer-document",
                headers=conductor_headers,
            )
            assert download.status_code == 200, download.text
            assert download.headers["content-type"].startswith("text/markdown")
            assert download.headers["x-content-sha256"] == option["technical_document_sha256"]
            assert b"financial_snapshot_id" not in download.content

            with pytest.raises(DBAPIError, match="append-only"), session_factory.begin() as session:
                row = session.get(CaseHandoverSnapshotRecord, item["snapshot_id"])
                assert row is not None
                row.snapshot_json = {"mutated": True}
            with session_factory() as session:
                assert session.scalar(sa.select(sa.func.count()).select_from(CaseOrderRecord)) == 0
                assert (
                    session.scalar(sa.select(sa.func.count()).select_from(CaseP7ResultRecord)) == 0
                )
                assert (
                    session.scalar(
                        sa.select(sa.func.count()).select_from(CaseHandoverSnapshotRecord)
                    )
                    == 1
                )

            no_assignment = replace(collaborator, assignment_scopes=())
            resolver.actors["unassigned"] = no_assignment
            refused = client.get(
                f"{base}/cases/{case_id}/p7-handover",
                headers={"Authorization": "Bearer unassigned"},
            )
            assert refused.status_code == 403
            resolver.actors["expert"] = replace(
                collaborator, operational_profile=OperationalProfile.EXPERT
            )
            profile_refused = client.get(
                f"{base}/cases/{case_id}/p7-handover",
                headers={"Authorization": "Bearer expert"},
            )
            assert profile_refused.status_code == 403
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def test_http_c1_keeps_unknown_until_patron_links_change_to_handover_and_records_action(
    database_engine, session_factory, tmp_path
):
    patron, case_id, package_id, dispatcher, storage = _seed_handover_sources(
        session_factory, tmp_path
    )
    a1 = _record_a1_source_condition(session_factory, actor=patron, case_id=case_id)
    with session_factory() as session:
        a1_decision = session.get(DecisionRecord, UUID(a1["decision_id"]))
        assert a1_decision is not None
        assert a1_decision.case_id == case_id
        assert a1_decision.validity == "CURRENT"
        assert a1_decision.selected_final_context_id is not None
        selected_context = session.get(
            DecisionContextRecord, a1_decision.selected_final_context_id
        )
        assert selected_context is not None
    outcome_id, handover_id = uuid4(), uuid4()
    outcome_service = CaseOutcomeService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    handover_service = CaseHandoverService(
        dispatcher=dispatcher,
        reader=SqlAlchemyCaseHandoverReader(session_factory),
        policy=AuthorizationPolicy(),
        storage=storage,
    )
    b1_resolver = TokenResolver({"patron": patron})
    b1_security = ConsultationSecurityRuntime(
        context_resolver=b1_resolver, policy=AuthorizationPolicy()
    )
    b1_app = FastAPI()
    for router in build_case_handover_routers(
        service=handover_service, security_runtime=b1_security
    ):
        b1_app.include_router(router)
    b1_app.include_router(
        build_patron_action_router(
            service=PatronActionService(
                session_factory=session_factory,
                dispatcher=dispatcher,
                policy=AuthorizationPolicy(),
            ),
            transition_service=PatronActionTransitionService(
                session_factory=session_factory,
                dispatcher=dispatcher,
                policy=AuthorizationPolicy(),
            ),
            outcome_service=outcome_service,
            security_runtime=b1_security,
        )
    )
    with TestClient(b1_app) as b1_client:
        outcome_payload = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "outcome_id": str(outcome_id),
            "case_id": str(case_id),
            "lot_reference": "01",
            "outcome": "WON",
            "source_locator": "attribution://notification/lot-01",
        }
        outcome_response = b1_client.post(
            "/api/v1/patron/case-outcomes",
            headers={"Authorization": "Bearer patron"},
            json=outcome_payload,
        )
        assert outcome_response.status_code == 201, outcome_response.text
        assert b1_client.post(
            "/api/v1/patron/case-outcomes",
            headers={"Authorization": "Bearer patron"},
            json=outcome_payload,
        ).status_code == 201
        handover_payload = {
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "snapshot_id": str(handover_id),
            "outcome_id": str(outcome_id),
            "submission_package_id": str(package_id),
        }
        handover_response = b1_client.post(
            f"/api/v1/patron/cases/{case_id}/p7-handover",
            headers={"Authorization": "Bearer patron"},
            json=handover_payload,
        )
        assert handover_response.status_code == 201, handover_response.text
        handover_replay = b1_client.post(
            f"/api/v1/patron/cases/{case_id}/p7-handover",
            headers={"Authorization": "Bearer patron"},
            json=handover_payload,
        )
        assert handover_replay.status_code == 200
        assert handover_replay.json()["replayed"] is True
        b1_read = b1_client.get(
            f"/api/v1/cases/{case_id}/p7-handover",
            headers={"Authorization": "Bearer patron"},
        )
        assert b1_read.status_code == 200, b1_read.text
        handover = b1_read.json()["items"][0]
        source_link = handover["snapshot"]["decision"]["condition_sources"][0]
        assert source_link["condition_id"] == a1["condition_id"]
        assert source_link["requirement_id"] == a1["requirement_id"]
        assert source_link["impact_id"] == a1["impact_id"]
        assert source_link["profile_version_id"] == a1["profile_version_id"]

    instrument_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            ContractInstrumentVersionRecord(
                id=instrument_id,
                tenant_id=patron.tenant_id,
                case_id=case_id,
                instrument_kind="SIGNED_CONTRACT",
                version_reference="CONTRAT-SIGNE-01",
                source_refs_json=["document://contract/signed-01"],
                evidence_refs_json=["sha256:" + "e" * 64],
                actor_id=patron.actor_id,
            )
        )

    c1_dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers=case_contract_change_handlers(),
    )
    service = CaseContractChangeService(
        dispatcher=c1_dispatcher,
        reader=SqlAlchemyCaseContractChangeReader(session_factory),
        policy=AuthorizationPolicy(),
    )
    foreign_patron = replace(patron, tenant_id=uuid4())
    resolver = TokenResolver({"patron": patron, "foreign": foreign_patron})
    app = FastAPI()
    for router in build_case_handover_routers(
        service=handover_service,
        security_runtime=ConsultationSecurityRuntime(
            context_resolver=resolver,
            policy=AuthorizationPolicy(),
        ),
    ):
        app.include_router(router)
    app.include_router(
        build_patron_case_contract_change_router(
            service=service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=resolver,
                policy=AuthorizationPolicy(),
            ),
        )
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical", access_log=False)
    )
    thread = Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 8
    while not server.started and thread.is_alive() and time.monotonic() < deadline:
        time.sleep(0.01)
    assert server.started
    base = f"http://127.0.0.1:{port}/api/v1/patron/cases/{case_id}/contract-change-events"
    headers = {"Authorization": "Bearer patron"}
    try:
        with httpx.Client(timeout=5) as client:
            handovers = client.get(
                f"{base.split('/patron/')[0]}/cases/{case_id}/p7-handover",
                headers=headers,
            )
            assert handovers.status_code == 200, handovers.text
            assert len(handovers.json()["items"]) == 1
            handover = handovers.json()["items"][0]
            condition_sources = handover["snapshot"]["decision"]["condition_sources"]
            assert len(condition_sources) == 1, handover["snapshot"]["decision"]
            assert condition_sources[0] == {
                "condition_id": a1["condition_id"],
                "requirement_id": a1["requirement_id"],
                "requirement_revision": 1,
                "impact_id": a1["impact_id"],
                "impact_revision": 1,
                "profile_version_id": a1["profile_version_id"],
                "profile_version": a1["profile_version"],
                "profile_sha256": a1["profile_hash"],
            }
            assert handover["snapshot"]["decision"]["open_conditions"][0]["status"] == "OPEN"

            event_id = uuid4()
            event_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "event_id": str(event_id),
                "handover_snapshot_id": str(handover_id),
                "change_kind": "ORDER_OF_SERVICE",
                "contract_instrument_version_id": None,
                "issuer": "Maître d’ouvrage (déclaré)",
                "summary": "Instruction de modification reçue",
                "scope_note": "Périmètre déclaré au lot 01 ; delta non évalué.",
                "source_refs": ["os://reference/14"],
                "evidence_refs": ["document://os/14"],
                "declared_received_at": NOW.isoformat(),
            }
            recorded_event = client.post(base, headers=headers, json=event_payload)
            assert recorded_event.status_code == 201, recorded_event.text
            assert recorded_event.json()["result_code"] == "CASE_CONTRACT_CHANGE_EVENT_RECORDED"
            event_replay = client.post(base, headers=headers, json=event_payload)
            assert event_replay.status_code == 200
            assert event_replay.json()["replayed"] is True

            initial = client.get(base, headers=headers)
            assert initial.status_code == 200, initial.text
            projection = initial.json()["events"][0]
            assert projection["handover_snapshot_id"] == str(handover_id)
            assert projection["outcome_id"] == str(outcome_id)
            assert projection["offer_package_id"] == str(package_id)
            assert projection["declared_instrument"] is None
            assert projection["applicability_state"] == "UNKNOWN"
            assert projection["actions"] == []

            action_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "action_id": str(uuid4()),
                "applicability_review_id": str(uuid4()),
                "expected_revision": 0,
                "action_summary": "Vérifier l’impact de l’instruction avec le Conducteur.",
                "evidence_refs": ["document://review/proof-01"],
                "due_at": None,
                "due_date_absence_reason": "Aucune date d’action validée.",
            }
            action_before_review = client.post(
                f"{base}/{event_id}/actions", headers=headers, json=action_payload
            )
            assert action_before_review.status_code == 422
            assert (
                action_before_review.json()["detail"]
                == "CONTRACT_CHANGE_NOT_APPLICABLE_TO_HANDOVER"
            )

            review_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "review_id": str(uuid4()),
                "handover_snapshot_id": str(handover_id),
                "contract_instrument_version_id": str(instrument_id),
                "expected_revision": 0,
                "decision": "APPLICABLE_TO_HANDOVER",
                "delta_state": "DECLARED",
                "delta_note": "Changement de phasage déclaré ; aucun coût ou délai recalculé.",
                "rationale": (
                    "Le Patron relie humainement l’instruction à cette version et cette passation."
                ),
                "evidence_refs": ["document://review/decision-source-01"],
            }
            review_path = f"{base}/{event_id}/applicability"
            first_review = client.post(review_path, headers=headers, json=review_payload)
            review_replay = client.post(review_path, headers=headers, json=review_payload)
            assert first_review.status_code == 201, first_review.text
            assert review_replay.status_code == 200
            assert review_replay.json()["replayed"] is True
            action_payload["applicability_review_id"] = review_payload["review_id"]
            action = client.post(f"{base}/{event_id}/actions", headers=headers, json=action_payload)
            action_replay = client.post(
                f"{base}/{event_id}/actions", headers=headers, json=action_payload
            )
            assert action.status_code == 201, action.text
            assert action_replay.status_code == 200
            assert action_replay.json()["replayed"] is True

            final = client.get(base, headers=headers)
            assert final.status_code == 200, final.text
            final_event = final.json()["events"][0]
            assert final_event["applicability_state"] == "APPLICABLE_TO_HANDOVER"
            assert final_event["applicability_history"][0]["contract_instrument_version_id"] == str(
                instrument_id
            )
            assert final_event["applicability_history"][0]["delta_state"] == "DECLARED"
            assert "aucun coût" in final_event["applicability_history"][0]["delta_note"]
            assert final_event["actions"][0]["state"] == "RECORDED"
            assert (
                final_event["actions"][0]["due_date_absence_reason"]
                == "Aucune date d’action validée."
            )
            assert final_event["handover_snapshot_id"] == str(handover_id)
            assert final_event["offer_package_id"] == str(package_id)
            assert handover["snapshot"]["decision"]["condition_sources"][0]["impact_id"] == a1[
                "impact_id"
            ]

            resolver.actors["collaborator"] = replace(
                patron,
                actor_kind=ActorKind.COLLABORATEUR,
                capabilities=capabilities_for(ActorKind.COLLABORATEUR),
            )
            collaborator_read = client.get(base, headers={"Authorization": "Bearer collaborator"})
            assert collaborator_read.status_code == 403
            foreign_read = client.get(base, headers={"Authorization": "Bearer foreign"})
            assert foreign_read.status_code == 200
            assert foreign_read.json() == {"case_id": str(case_id), "events": []}
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    with Session(database_engine) as session:
        decision = session.get(DecisionRecord, UUID(a1["decision_id"]))
        condition = session.get(DecisionConditionRecord, UUID(a1["condition_id"]))
        impact = session.get(
            ContractBaselineDeviationImpactRecord, UUID(a1["impact_id"])
        )
        assert decision is not None and decision.outcome == "CONDITIONAL_GO"
        assert condition is not None and condition.status == "OPEN"
        assert impact is not None and impact.status == "HUMAN_REVIEW_REQUIRED"
        assert session.scalar(
            sa.select(sa.func.count())
            .select_from(CaseContractChangeEventRecord)
            .where(
                CaseContractChangeEventRecord.tenant_id == patron.tenant_id,
                CaseContractChangeEventRecord.case_id == case_id,
            )
        ) == 1

    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeEventRecord)
            .where(CaseContractChangeEventRecord.id == event_id)
            .values(summary="Mutation interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeApplicabilityRecord)
            .where(CaseContractChangeApplicabilityRecord.id == review_payload["review_id"])
            .values(rationale="Réécriture interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeActionRecord)
            .where(CaseContractChangeActionRecord.id == action_payload["action_id"])
            .values(action_summary="Réécriture interdite")
        )
    with Session(database_engine) as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseContractChangeEventRecord))
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(CaseContractChangeApplicabilityRecord)
            )
            == 1
        )
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(CaseContractChangeActionRecord))
            == 1
        )
