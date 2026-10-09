from __future__ import annotations

import asyncio
import os
import socket
import time
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from threading import Thread
from typing import cast
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
from app.modules.dce.application.handlers import ExpireDceStagedObjectHandler
from app.modules.dce.application.upload import MalwareScanResult
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.quarantine import (
    ClamdTcpMalwareScanAdapter,
    LocalQuarantineStorageAdapter,
)
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
from app.modules.pricing.application.case_contract_change_commands import (
    CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC,
)
from app.modules.pricing.application.case_contract_change_evidence_upload import (
    CaseContractChangeEvidenceUploadService,
)
from app.modules.pricing.infrastructure.case_contract_change_evidence_repository import (
    SqlAlchemyCaseContractChangeEvidenceRepository,
)
from app.modules.pricing.infrastructure.case_contract_change_reader import (
    SqlAlchemyCaseContractChangeReader,
)
from app.modules.pricing.infrastructure.models.case_contract_change import (
    CaseContractChangeActionExecutionEvidenceLinkRecord,
    CaseContractChangeActionExecutionRecord,
    CaseContractChangeActionImpactLinkRecord,
    CaseContractChangeActionImpactRelationRecord,
    CaseContractChangeActionRecord,
    CaseContractChangeApplicabilityRecord,
    CaseContractChangeEngagementLinkRecord,
    CaseContractChangeEventRecord,
    CaseContractChangeEvidenceObjectRecord,
    CaseContractChangeExternalConfirmationRecord,
    CaseContractChangeImpactDeclarationRecord,
)
from app.modules.pricing.infrastructure.models.contract_instrument_version import (
    ContractInstrumentVersionRecord,
)
from app.modules.submission.application.commands import PrepareSubmissionPackageCommand
from app.modules.submission.application.service import SubmissionPackageService, submission_handlers
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.persistence.models import OutboxMessageRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    AssignmentScope,
    DataClassification,
    OperationalProfile,
)
from app.workers.dce_retention import DceRetentionWorker
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
from tests.support.quarantine_crash import kill_local_quarantine_write


class TokenResolver:
    def __init__(self, actors: dict[str, ActorContext]) -> None:
        self.actors = actors

    def resolve(self, *, access_token: str) -> ActorContext:
        return self.actors[access_token]


class C5StaticInspector:
    async def detect_media_type(self, *, storage_key: str) -> str:
        return "application/pdf"


EICAR_TEST_CONTENT = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"


class C5StaticScanner:
    def __init__(
        self,
        verdict: str = "CLEAN",
        *,
        real_scanner: ClamdTcpMalwareScanAdapter | None = None,
        error_scanner: ClamdTcpMalwareScanAdapter | None = None,
    ) -> None:
        self.verdict = verdict
        self.real_scanner = real_scanner
        self.error_scanner = error_scanner
        self.observed_verdicts: list[str] = []

    async def scan(self, *, storage_key: str) -> MalwareScanResult:
        if self.verdict == "ERROR" and self.error_scanner is not None:
            result = await self.error_scanner.scan(storage_key=storage_key)
        elif self.verdict == "CLEAN" and self.real_scanner is not None:
            result = await self.real_scanner.scan(storage_key=storage_key)
        else:
            result = MalwareScanResult(
                verdict=self.verdict,
                scanner_name="test-clamd",
                scanner_signature_version="test-signatures",
                scanned_at=datetime.now(tz=UTC),
            )
        self.observed_verdicts.append(result.verdict)
        return result


class FailOnceC5DeleteStorage:
    def __init__(self, *, storage: LocalQuarantineStorageAdapter, fail_storage_key: str) -> None:
        self.storage = storage
        self.fail_storage_key = fail_storage_key
        self.failed = False

    async def delete(self, *, storage_key: str) -> None:
        if storage_key == self.fail_storage_key and not self.failed:
            self.failed = True
            raise OSError("synthetic private-storage delete failure")
        await self.storage.delete(storage_key=storage_key)

    async def delete_partials(self, *, storage_key: str) -> int:
        return await self.storage.delete_partials(storage_key=storage_key)


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
    security_runtime = ConsultationSecurityRuntime(context_resolver=resolver, policy=policy)
    app = FastAPI()
    app.include_router(
        build_patron_contract_baseline_impact_router(
            service=ContractBaselineImpactReadService(
                session_factory=session_factory, policy=policy
            ),
            write_service=ContractBaselineImpactWriteService(dispatcher=dispatcher, policy=policy),
            security_runtime=security_runtime,
        )
    )
    app.include_router(
        build_patron_decision_router(
            service=PatronDecisionDossierService(
                reader=SqlAlchemyDecisionDossierReader(session_factory), policy=policy
            ),
            lifecycle_service=PatronDecisionLifecycleService(dispatcher=dispatcher, policy=policy),
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
        assert unknown_link.json()["detail"] == "CONTRACT_PROOF_REQUIRES_HUMAN_REVIEW_STATE"
        linked = client.post(link_path, headers=headers, json=link_payload)
        assert linked.status_code == 201, linked.text
        link_replay = client.post(link_path, headers=headers, json=link_payload)
        assert link_replay.status_code == 200
        assert link_replay.json()["replayed"] is True
        dossier = client.get(f"/api/v1/patron/cases/{case_id}/decision-dossier", headers=headers)
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
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE case_handover_snapshots CASCADE"))
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
    database_engine, session_factory, tmp_path, request: pytest.FixtureRequest
):
    preserve_c5_restore_fixture = (
        os.environ.get("SMART_AO_TEST_PRESERVE_C5_RESTORE_FIXTURE") == "1"
        and os.environ.get("SMART_AO_TEST_DISPOSABLE_DATABASE") == "1"
    )

    def clear_c5_records() -> None:
        if preserve_c5_restore_fixture:
            return
        with database_engine.begin() as connection:
            connection.execute(
                sa.text(
                    "TRUNCATE TABLE case_contract_change_external_confirmations, "
                    "case_contract_change_action_execution_evidence_links, "
                    "case_contract_change_evidence_objects, "
                    "case_contract_change_action_executions CASCADE"
                )
            )

    request.addfinalizer(clear_c5_records)
    if not preserve_c5_restore_fixture:
        with database_engine.begin() as connection:
            connection.execute(
                sa.text(
                    "TRUNCATE TABLE case_contract_change_external_confirmations, "
                    "case_contract_change_action_execution_evidence_links, "
                    "case_contract_change_evidence_objects, "
                    "case_contract_change_action_executions CASCADE"
                )
            )
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
        selected_context = session.get(DecisionContextRecord, a1_decision.selected_final_context_id)
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
        assert (
            b1_client.post(
                "/api/v1/patron/case-outcomes",
                headers={"Authorization": "Bearer patron"},
                json=outcome_payload,
            ).status_code
            == 201
        )
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
    evidence_storage_root = Path(
        os.getenv("SMART_AO_TEST_C5_QUARANTINE_ROOT", str(tmp_path / "c5-evidence"))
    )
    evidence_storage = LocalQuarantineStorageAdapter(root=evidence_storage_root)
    clamd_host = os.getenv("SMART_AO_C5_TEST_CLAMD_HOST")
    clamd_port = int(os.getenv("SMART_AO_C5_TEST_CLAMD_PORT", "3310"))
    c5_scanner = C5StaticScanner(
        real_scanner=(
            ClamdTcpMalwareScanAdapter(
                storage=evidence_storage,
                host=clamd_host,
                port=clamd_port,
                timeout_seconds=5,
            )
            if clamd_host
            else None
        ),
        error_scanner=(
            ClamdTcpMalwareScanAdapter(
                storage=evidence_storage,
                host=clamd_host,
                port=clamd_port + 1,
                timeout_seconds=1,
            )
            if clamd_host
            else None
        ),
    )
    evidence_repository = SqlAlchemyCaseContractChangeEvidenceRepository(
        session_factory=session_factory
    )
    evidence_upload_service = CaseContractChangeEvidenceUploadService(
        repository=evidence_repository,
        policy=AuthorizationPolicy(),
        storage=evidence_storage,
        inspector=C5StaticInspector(),
        scanner=c5_scanner,
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
            evidence_upload_service=evidence_upload_service,
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
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", access_log=False)
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
            assert projection["a1_engagements_state"] == "KNOWN"
            assert projection["a1_engagements"] == condition_sources
            assert projection["engagement_linkage_state"] == "UNKNOWN"
            assert projection["engagement_linkage_history"] == []

            linkage_path = f"{base}/{event_id}/engagement-links"
            unknown_linkage_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "linkage_id": str(uuid4()),
                "expected_revision": 0,
                "state": "UNKNOWN",
                "selected_sources": [],
                "rationale": "Le Patron n’a pas encore identifié l’engagement touché.",
                "unknown_reason": "Le périmètre de l’instruction reste à rapprocher.",
            }
            unknown_linkage = client.post(
                linkage_path, headers=headers, json=unknown_linkage_payload
            )
            unknown_linkage_replay = client.post(
                linkage_path, headers=headers, json=unknown_linkage_payload
            )
            assert unknown_linkage.status_code == 201, unknown_linkage.text
            assert unknown_linkage_replay.status_code == 200
            assert unknown_linkage_replay.json()["replayed"] is True

            impact_path = f"{base}/{event_id}/impact-declarations"
            unknown_c2_impact_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "declaration_id": str(uuid4()),
                "linkage_id": unknown_linkage_payload["linkage_id"],
                "source": condition_sources[0],
                "expected_revision": 0,
                "axis": "COST",
                "impact_state": "DECLARED",
                "impact_summary": "Coût de mobilisation complémentaire.",
                "impact_unknown_reason": None,
                "measurement_state": "DECLARED",
                "value_as_declared": "0.00",
                "currency_code": "EUR",
                "unit": None,
                "measurement_unknown_reason": None,
                "assumptions": ["Zéro saisi explicitement, sans chiffrage système."],
                "source_refs": ["os://reference/14"],
                "evidence_refs": ["document://impact/estimate-01"],
                "rationale": "Le Patron consigne une estimation déclarée sur la source choisie.",
            }
            blocked_by_unknown_c2 = client.post(
                impact_path, headers=headers, json=unknown_c2_impact_payload
            )
            assert blocked_by_unknown_c2.status_code == 422
            assert blocked_by_unknown_c2.json()["detail"] == "C2_LINKAGE_NOT_CURRENT_OR_LINKED"

            selected_source = condition_sources[0]
            linkage_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "linkage_id": str(uuid4()),
                "expected_revision": 1,
                "state": "LINKED",
                "selected_sources": [selected_source],
                "rationale": "Le Patron relie l’instruction à cette condition A1 du snapshot B1.",
                "unknown_reason": None,
            }
            linked = client.post(linkage_path, headers=headers, json=linkage_payload)
            linked_replay = client.post(linkage_path, headers=headers, json=linkage_payload)
            assert linked.status_code == 201, linked.text
            assert linked_replay.status_code == 200
            assert linked_replay.json()["replayed"] is True

            unknown_impact_source_payload = {
                **unknown_c2_impact_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "declaration_id": str(uuid4()),
                "linkage_id": linkage_payload["linkage_id"],
                "axis": "CAPACITY",
                "impact_state": "UNKNOWN",
                "impact_summary": None,
                "impact_unknown_reason": "La charge de moyens du changement n’est pas établie.",
                "measurement_state": "UNKNOWN",
                "value_as_declared": None,
                "currency_code": None,
                "unit": None,
                "measurement_unknown_reason": None,
                "evidence_refs": [],
            }
            unknown_impact = client.post(
                impact_path, headers=headers, json=unknown_impact_source_payload
            )
            unknown_impact_replay = client.post(
                impact_path, headers=headers, json=unknown_impact_source_payload
            )
            assert unknown_impact.status_code == 201, unknown_impact.text
            assert unknown_impact_replay.status_code == 200
            assert unknown_impact_replay.json()["replayed"] is True

            declared_impact_payload = {
                **unknown_c2_impact_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "declaration_id": str(uuid4()),
                "linkage_id": linkage_payload["linkage_id"],
                "expected_revision": 0,
            }
            declared_impact = client.post(
                impact_path, headers=headers, json=declared_impact_payload
            )
            declared_impact_replay = client.post(
                impact_path, headers=headers, json=declared_impact_payload
            )
            assert declared_impact.status_code == 201, declared_impact.text
            assert declared_impact_replay.status_code == 200
            assert declared_impact_replay.json()["replayed"] is True

            unknown_measurement_payload = {
                **declared_impact_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "declaration_id": str(uuid4()),
                "expected_revision": 1,
                "impact_summary": "La mobilisation supplémentaire est identifiée.",
                "measurement_state": "UNKNOWN",
                "value_as_declared": None,
                "currency_code": None,
                "measurement_unknown_reason": "Aucun devis n’a confirmé le montant.",
            }
            unknown_measurement = client.post(
                impact_path, headers=headers, json=unknown_measurement_payload
            )
            assert unknown_measurement.status_code == 201, unknown_measurement.text
            impact_revision_conflict = client.post(
                impact_path,
                headers=headers,
                json={
                    **declared_impact_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "declaration_id": str(uuid4()),
                    "expected_revision": 0,
                },
            )
            assert impact_revision_conflict.status_code == 422
            assert (
                impact_revision_conflict.json()["detail"]
                == "CONTRACT_CHANGE_IMPACT_VERSION_CONFLICT"
            )

            forged_c3_source = client.post(
                impact_path,
                headers=headers,
                json={
                    **declared_impact_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "declaration_id": str(uuid4()),
                    "expected_revision": 2,
                    "source": {**selected_source, "requirement_revision": 2},
                },
            )
            assert forged_c3_source.status_code == 422
            assert forged_c3_source.json()["detail"] == "A1_SOURCE_NOT_SELECTED_IN_C2"

            with (
                Session(database_engine) as session,
                pytest.raises(sa.exc.DBAPIError),
                session.begin_nested(),
            ):
                session.execute(
                    sa.insert(CaseContractChangeImpactDeclarationRecord).values(
                        id=uuid4(),
                        tenant_id=patron.tenant_id,
                        case_id=case_id,
                        event_id=event_id,
                        linkage_id=UUID(linkage_payload["linkage_id"]),
                        condition_id=UUID(selected_source["condition_id"]),
                        impact_id=UUID(selected_source["impact_id"]),
                        impact_revision=selected_source["impact_revision"],
                        source_a1_json={**selected_source, "requirement_revision": 2},
                        axis="COST",
                        revision=99,
                        impact_state="DECLARED",
                        impact_summary="Source forgée pour la preuve SQL.",
                        impact_unknown_reason=None,
                        measurement_state="DECLARED",
                        value_as_declared="1.00",
                        currency_code="EUR",
                        unit=None,
                        measurement_unknown_reason=None,
                        assumptions_json=[],
                        source_refs_json=["os://reference/14"],
                        evidence_refs_json=["document://impact/forged"],
                        rationale="Doit être refusé par la garde SQL C2/C3.",
                        actor_id=patron.actor_id,
                        membership_id=patron.membership_id,
                        command_id=uuid4(),
                        idempotency_key=uuid4(),
                        correlation_id=uuid4(),
                    )
                )

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

            c4_path = f"{base}/{event_id}/actions/{action_payload['action_id']}/impact-links"
            c4_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "relation_id": str(uuid4()),
                "expected_revision": 0,
                "state": "LINKED",
                "declaration_ids": [
                    declared_impact_payload["declaration_id"],
                    unknown_impact_source_payload["declaration_id"],
                ],
                "rationale": "Le Patron rattache l’action à ces deux impacts déclarés.",
                "unknown_reason": None,
            }
            c4_recorded = client.post(c4_path, headers=headers, json=c4_payload)
            c4_replay = client.post(c4_path, headers=headers, json=c4_payload)
            assert c4_recorded.status_code == 201, c4_recorded.text
            assert c4_replay.status_code == 200
            assert c4_replay.json()["replayed"] is True
            evidence_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "evidence_object_id": str(uuid4()),
                "c4_relation_id": c4_payload["relation_id"],
                "evidence_kind": "EXECUTION_EVIDENCE",
                "expected_byte_size": len(b"%PDF-1.7\\nexecution proof\\n"),
            }
            evidence_path = (
                f"{base}/{event_id}/actions/{action_payload['action_id']}/evidence-objects"
            )
            evidence_intent = client.post(evidence_path, headers=headers, json=evidence_payload)
            assert evidence_intent.status_code == 201, evidence_intent.text
            evidence_upload = client.put(
                f"{evidence_path}/{evidence_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": evidence_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=b"%PDF-1.7\\nexecution proof\\n",
            )
            assert evidence_upload.status_code == 200, evidence_upload.text
            assert evidence_upload.json()["state"] == "CLEAN"
            assert evidence_upload.json()["version"] == 1
            assert (
                evidence_upload.json()["sha256"]
                == sha256(b"%PDF-1.7\\nexecution proof\\n").hexdigest()
            )
            evidence_intent_replay = client.post(
                evidence_path, headers=headers, json=evidence_payload
            )
            assert evidence_intent_replay.status_code == 200
            assert evidence_intent_replay.json()["replayed"] is True
            assert evidence_intent_replay.json()["state"] == "CLEAN"
            evidence_upload_replay = client.put(
                f"{evidence_path}/{evidence_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": evidence_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=b"%PDF-1.7\\nexecution proof\\n",
            )
            assert evidence_upload_replay.status_code == 200
            assert evidence_upload_replay.json()["sha256"] == evidence_upload.json()["sha256"]
            changed_retry = client.put(
                f"{evidence_path}/{evidence_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": evidence_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=b"%PDF-1.7\\nother bytes\\n",
            )
            assert changed_retry.status_code == 409
            assert "storage_key" not in evidence_upload.json()
            real_clamd_enabled = c5_scanner.real_scanner is not None
            infected_content = (
                EICAR_TEST_CONTENT if real_clamd_enabled else b"%PDF-1.7\\ninfected proof\\n"
            )
            rejected_evidence_payload = {
                **evidence_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "evidence_object_id": str(uuid4()),
                "expected_byte_size": len(infected_content),
            }
            c5_scanner.verdict = "CLEAN" if real_clamd_enabled else "INFECTED"
            rejected_intent = client.post(
                evidence_path, headers=headers, json=rejected_evidence_payload
            )
            assert rejected_intent.status_code == 201
            rejected_upload = client.put(
                f"{evidence_path}/{rejected_evidence_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": rejected_evidence_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=infected_content,
            )
            assert c5_scanner.observed_verdicts[-1] == "INFECTED"
            assert rejected_upload.status_code == 422

            rejected_scanner_error_payload = {
                **evidence_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "evidence_object_id": str(uuid4()),
                "expected_byte_size": len(b"%PDF-1.7\\nscanner unavailable\\n"),
            }
            c5_scanner.verdict = "ERROR"
            scanner_error_intent = client.post(
                evidence_path, headers=headers, json=rejected_scanner_error_payload
            )
            assert scanner_error_intent.status_code == 201
            scanner_error_upload = client.put(
                f"{evidence_path}/{rejected_scanner_error_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": rejected_scanner_error_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=b"%PDF-1.7\\nscanner unavailable\\n",
            )
            assert c5_scanner.observed_verdicts[-1] == "ERROR"
            assert scanner_error_upload.status_code == 422
            assert scanner_error_upload.json()["detail"] == "UPLOAD_REJECTED"
            c5_scanner.verdict = "CLEAN"
            crashed_uploads = []
            crash_bytes = b"%PDF-1.7\ncrash-recovery fixture\n"
            for after_rename in (False, True, True):
                crash_payload = {
                    **evidence_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "correlation_id": str(uuid4()),
                    "evidence_object_id": str(uuid4()),
                    "expected_byte_size": len(crash_bytes),
                }
                crash_intent = client.post(evidence_path, headers=headers, json=crash_payload)
                assert crash_intent.status_code == 201, crash_intent.text
                crash_id = UUID(crash_payload["evidence_object_id"])
                crash_target = evidence_repository.get_target(
                    tenant_id=patron.tenant_id,
                    case_id=case_id,
                    event_id=event_id,
                    action_id=UUID(action_payload["action_id"]),
                    evidence_object_id=crash_id,
                )
                assert crash_target is not None
                assert evidence_repository.claim(evidence_object_id=crash_id)
                kill_local_quarantine_write(
                    root=evidence_storage_root,
                    storage_key=crash_target.storage_key,
                    after_rename=after_rename,
                )
                crash_path = asyncio.run(
                    evidence_storage.local_path(storage_key=crash_target.storage_key)
                )
                if after_rename:
                    assert crash_path.read_bytes() == crash_bytes
                else:
                    assert not crash_path.exists()
                    assert list(crash_path.parent.glob(f".{crash_path.name}.*.part"))
                crashed_uploads.append(crash_target)

            recovery_dispatcher = CommandDispatcher(
                session_factory=session_factory,
                handlers={
                    "ExpireDceStagedObject": ExpireDceStagedObjectHandler(),
                    **case_contract_change_handlers(),
                },
            )
            retry_storage = FailOnceC5DeleteStorage(
                storage=evidence_storage,
                fail_storage_key=crashed_uploads[-1].storage_key,
            )
            recovery_worker = DceRetentionWorker(
                session_factory=session_factory,
                dispatcher=recovery_dispatcher,
                storage=cast(LocalQuarantineStorageAdapter, retry_storage),
            )
            recovery_now = max(item.expires_at for item in crashed_uploads) + timedelta(seconds=1)
            recovery_result = asyncio.run(recovery_worker.run_once(now=recovery_now))
            assert recovery_result.expired == len(crashed_uploads)
            assert recovery_result.published == len(crashed_uploads) - 1
            assert recovery_result.retried == 1
            for crash_target in crashed_uploads[:-1]:
                crash_path = asyncio.run(
                    evidence_storage.local_path(storage_key=crash_target.storage_key)
                )
                assert not crash_path.exists()
                assert not list(crash_path.parent.glob(f".{crash_path.name}.*.part"))
                with session_factory() as session:
                    recovered_record = session.get(
                        CaseContractChangeEvidenceObjectRecord,
                        crash_target.evidence_object_id,
                    )
                assert recovered_record is not None
                assert recovered_record.state == "REJECTED"
            failed_delete_target = crashed_uploads[-1]
            failed_delete_path = asyncio.run(
                evidence_storage.local_path(storage_key=failed_delete_target.storage_key)
            )
            assert failed_delete_path.exists()
            with session_factory() as session:
                retry_messages = list(
                    session.scalars(
                        sa.select(OutboxMessageRecord).where(
                            OutboxMessageRecord.topic
                            == CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC
                        )
                    )
                )
            failed_delete_message = next(
                message
                for message in retry_messages
                if message.payload_json["data"]["evidence_object_id"]
                == str(failed_delete_target.evidence_object_id)
            )
            assert failed_delete_message.status == "RETRY"
            assert failed_delete_message.attempt_count == 1
            retry_result = asyncio.run(
                recovery_worker.run_once(now=recovery_now + timedelta(seconds=31))
            )
            assert retry_result.published == 1
            assert retry_result.retried == 0
            for crash_target in crashed_uploads:
                crash_path = asyncio.run(
                    evidence_storage.local_path(storage_key=crash_target.storage_key)
                )
                assert not crash_path.exists()
                assert not list(crash_path.parent.glob(f".{crash_path.name}.*.part"))
                with session_factory() as session:
                    recovered_record = session.get(
                        CaseContractChangeEvidenceObjectRecord,
                        crash_target.evidence_object_id,
                    )
                assert recovered_record is not None
                assert recovered_record.state == "REJECTED"
            clean_evidence_record = evidence_repository.get_target(
                tenant_id=patron.tenant_id,
                case_id=case_id,
                event_id=event_id,
                action_id=UUID(action_payload["action_id"]),
                evidence_object_id=UUID(str(evidence_payload["evidence_object_id"])),
            )
            assert clean_evidence_record is not None
            assert clean_evidence_record.state == "CLEAN"
            clean_evidence_path = asyncio.run(
                evidence_storage.local_path(storage_key=clean_evidence_record.storage_key)
            )
            assert clean_evidence_path.read_bytes() == b"%PDF-1.7\\nexecution proof\\n"
            with session_factory() as session:
                c5_cleanup_events_before_replay = session.scalar(
                    sa.select(sa.func.count())
                    .select_from(OutboxMessageRecord)
                    .where(
                        OutboxMessageRecord.topic == CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC
                    )
                )
            asyncio.run(recovery_worker.run_once(now=recovery_now + timedelta(minutes=1)))
            with session_factory() as session:
                c5_cleanup_events_after_replay = session.scalar(
                    sa.select(sa.func.count())
                    .select_from(OutboxMessageRecord)
                    .where(
                        OutboxMessageRecord.topic == CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC
                    )
                )
            assert c5_cleanup_events_after_replay == c5_cleanup_events_before_replay == 3

            c5_path = f"{base}/{event_id}/actions/{action_payload['action_id']}/execution-acts"
            c5_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "act_id": str(uuid4()),
                "c4_relation_id": c4_payload["relation_id"],
                "expected_revision": 0,
                "declared_state": "DECLARED_PARTIAL",
                "declared_summary": "Une partie de l’action a été réalisée.",
                "unknown_reason": None,
                "evidence_refs": [],
                "evidence_object_ids": [evidence_payload["evidence_object_id"]],
                "external_confirmation_state": "UNKNOWN",
                "external_confirmation_note": None,
            }
            with session_factory() as session:
                evidence_record = session.get(
                    CaseContractChangeEvidenceObjectRecord,
                    UUID(str(evidence_payload["evidence_object_id"])),
                )
                assert evidence_record is not None
                evidence_storage_key = evidence_record.storage_key
            evidence_path_on_disk = asyncio.run(
                evidence_storage.local_path(storage_key=evidence_storage_key)
            )
            original_evidence_bytes = evidence_path_on_disk.read_bytes()
            evidence_path_on_disk.write_bytes(b"corrupted evidence bytes")
            hash_mismatch = client.post(
                c5_path,
                headers=headers,
                json={
                    **c5_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                },
            )
            assert hash_mismatch.status_code == 422
            assert hash_mismatch.json()["detail"] == "C5_EVIDENCE_SOURCE_NOT_VERIFIED"
            evidence_path_on_disk.write_bytes(original_evidence_bytes)
            c5_recorded = client.post(c5_path, headers=headers, json=c5_payload)
            assert c5_recorded.status_code == 201, c5_recorded.text
            c5_unverified_confirmation = client.post(
                c5_path,
                headers=headers,
                json={
                    **c5_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                    "external_confirmation_state": "CONFIRMED",
                },
            )
            assert c5_unverified_confirmation.status_code == 422
            c5_replay = client.post(c5_path, headers=headers, json=c5_payload)
            assert c5_replay.status_code == 200
            assert c5_replay.json()["replayed"] is True
            external_evidence_payload = {
                **evidence_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "evidence_object_id": str(uuid4()),
                "evidence_kind": "EXTERNAL_CONFIRMATION",
                "expected_byte_size": len(b"%PDF-1.7\\nexternal acknowledgement\\n"),
            }
            external_intent = client.post(
                evidence_path, headers=headers, json=external_evidence_payload
            )
            assert external_intent.status_code == 201, external_intent.text
            external_upload = client.put(
                f"{evidence_path}/{external_evidence_payload['evidence_object_id']}/content",
                headers={
                    **headers,
                    "Idempotency-Key": external_evidence_payload["idempotency_key"],
                    "Content-Type": "application/octet-stream",
                },
                content=b"%PDF-1.7\\nexternal acknowledgement\\n",
            )
            assert external_upload.status_code == 200, external_upload.text
            external_confirmation_path = f"{c5_path}/{c5_payload['act_id']}/external-confirmations"
            external_confirmation_payload = {
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "correlation_id": str(uuid4()),
                "confirmation_id": str(uuid4()),
                "c4_relation_id": c4_payload["relation_id"],
                "evidence_object_id": external_evidence_payload["evidence_object_id"],
                "expected_revision": 0,
                "received_at": "2026-10-03T16:00:00Z",
                "external_party": "Maîtrise d’œuvre",
                "rationale": "Le Patron relie l’accusé externe reçu à cette action.",
            }
            external_confirmation = client.post(
                external_confirmation_path,
                headers=headers,
                json=external_confirmation_payload,
            )
            assert external_confirmation.status_code == 201, external_confirmation.text
            external_confirmation_replay = client.post(
                external_confirmation_path,
                headers=headers,
                json=external_confirmation_payload,
            )
            assert external_confirmation_replay.status_code == 200
            assert external_confirmation_replay.json()["replayed"] is True
            external_confirmation_conflict = client.post(
                external_confirmation_path,
                headers=headers,
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                },
            )
            assert external_confirmation_conflict.status_code == 422
            assert external_confirmation_conflict.json()["detail"] == (
                "C5_EXTERNAL_CONFIRMATION_VERSION_CONFLICT"
            )
            external_confirmation_wrong_kind = client.post(
                external_confirmation_path,
                headers=headers,
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                    "evidence_object_id": evidence_payload["evidence_object_id"],
                    "expected_revision": 1,
                },
            )
            assert external_confirmation_wrong_kind.status_code == 422
            assert external_confirmation_wrong_kind.json()["detail"] == (
                "C5_EXTERNAL_CONFIRMATION_SOURCE_NOT_VERIFIED"
            )
            c5_bad_parent = client.post(
                c5_path,
                headers=headers,
                json={
                    **c5_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                    "c4_relation_id": str(uuid4()),
                    "evidence_object_ids": [],
                },
            )
            assert c5_bad_parent.status_code == 422
            assert c5_bad_parent.json()["detail"] == (
                "C5_ACTION_OR_EXACT_C4_RELATION_NOT_FOUND_OR_FORBIDDEN"
            )
            c5_reference_payload = {
                **c5_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "act_id": str(uuid4()),
                "expected_revision": 1,
                "declared_state": "UNKNOWN",
                "declared_summary": None,
                "unknown_reason": "La réalisation n’est pas établie.",
                "evidence_refs": ["document://declared/not-verified"],
                "evidence_object_ids": [],
                "external_confirmation_state": "NOT_CONFIRMED",
                "external_confirmation_note": "Aucun accusé externe reçu à cette date.",
            }
            c5_reference = client.post(c5_path, headers=headers, json=c5_reference_payload)
            assert c5_reference.status_code == 201, c5_reference.text
            c5_revision_conflict = client.post(
                c5_path,
                headers=headers,
                json={
                    **c5_reference_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                    "expected_revision": 1,
                },
            )
            assert c5_revision_conflict.status_code == 422
            assert c5_revision_conflict.json()["detail"] == "C5_ACTION_EXECUTION_VERSION_CONFLICT"
            c4_unknown_payload = {
                **c4_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "relation_id": str(uuid4()),
                "expected_revision": 1,
                "state": "UNKNOWN",
                "declaration_ids": [],
                "rationale": "Le Patron ne peut pas encore déterminer le lien.",
                "unknown_reason": "La portée de l’action doit être précisée.",
            }
            c4_unknown = client.post(c4_path, headers=headers, json=c4_unknown_payload)
            assert c4_unknown.status_code == 201, c4_unknown.text
            c4_not_applicable_payload = {
                **c4_unknown_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "relation_id": str(uuid4()),
                "expected_revision": 2,
                "state": "NOT_APPLICABLE",
                "rationale": "Après vérification, cette action n’est pas liée à un impact C3.",
                "unknown_reason": "L’action concerne une formalité indépendante.",
            }
            c4_not_applicable = client.post(
                c4_path, headers=headers, json=c4_not_applicable_payload
            )
            assert c4_not_applicable.status_code == 201, c4_not_applicable.text
            c4_bad_revision = client.post(
                c4_path,
                headers=headers,
                json={
                    **c4_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "relation_id": str(uuid4()),
                    "expected_revision": 0,
                },
            )
            assert c4_bad_revision.status_code == 422
            assert c4_bad_revision.json()["detail"] == (
                "CONTRACT_CHANGE_ACTION_IMPACT_VERSION_CONFLICT"
            )

            final = client.get(base, headers=headers)
            assert final.status_code == 200, final.text
            final_event = final.json()["events"][0]
            assert final_event["actions"][0]["state"] == "RECORDED"
            c4_history = final_event["action_impact_relations"]
            assert [item["state"] for item in c4_history] == ["LINKED", "UNKNOWN", "NOT_APPLICABLE"]
            assert c4_history[0]["relation_id"] == c4_payload["relation_id"]
            assert c4_history[0]["declaration_ids"] == c4_payload["declaration_ids"]
            assert c4_history[0]["projection_state"] == "CURRENT"
            assert c4_history[1]["declaration_ids"] == []
            assert c4_history[1]["unknown_reason"] == c4_unknown_payload["unknown_reason"]
            assert c4_history[2]["declaration_ids"] == []
            assert c4_history[2]["unknown_reason"] == c4_not_applicable_payload["unknown_reason"]
            c5_history = final_event["action_execution_acts"]
            assert [item["evidence_state"] for item in c5_history] == ["RETRIEVED", "REFERENCED"]
            assert [item["external_confirmation_state"] for item in c5_history] == [
                "CONFIRMED",
                "NOT_CONFIRMED",
            ]
            assert all(item["c4_relation_id"] == c4_payload["relation_id"] for item in c5_history)
            assert all(item["c4_projection_state"] == "SUPERSEDED" for item in c5_history)
            assert c5_history[0]["declared_state"] == "DECLARED_PARTIAL"
            assert c5_history[1]["declared_state"] == "UNKNOWN"
            assert (
                c5_history[0]["evidence_objects"][0]["evidence_object_id"]
                == (evidence_payload["evidence_object_id"])
            )
            assert (
                c5_history[0]["evidence_objects"][0]["sha256"] == evidence_upload.json()["sha256"]
            )
            assert c5_history[1]["evidence_objects"] == []
            assert len(c5_history[0]["external_confirmation_acts"]) == 1
            assert (
                c5_history[0]["external_confirmation_acts"][0]["confirmation_id"]
                == (external_confirmation_payload["confirmation_id"])
            )
            assert (
                c5_history[0]["evidence_objects"][0]["evidence_object_id"]
                == (evidence_payload["evidence_object_id"])
            )
            assert (
                c5_history[0]["evidence_objects"][0]["sha256"] == evidence_upload.json()["sha256"]
            )
            assert c5_history[1]["evidence_objects"] == []
            assert len(c5_history[0]["external_confirmation_acts"]) == 1
            assert (
                c5_history[0]["external_confirmation_acts"][0]["confirmation_id"]
                == (external_confirmation_payload["confirmation_id"])
            )
            assert final_event["actions"][0]["state"] == "RECORDED"
            assert final_event["a1_engagements"] == condition_sources
            assert final_event["engagement_linkage_state"] == "LINKED"
            assert [item["state"] for item in final_event["engagement_linkage_history"]] == [
                "UNKNOWN",
                "LINKED",
            ]
            assert final_event["engagement_linkage_history"][1]["selected_sources"] == [
                selected_source
            ]
            stale_selection_payload = {
                **linkage_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "linkage_id": str(uuid4()),
                "expected_revision": 2,
                "selected_sources": [{**selected_source, "requirement_revision": 2}],
            }
            stale_selection = client.post(
                linkage_path, headers=headers, json=stale_selection_payload
            )
            assert stale_selection.status_code == 422
            assert stale_selection.json()["detail"] == "A1_SOURCE_NOT_IN_HANDOVER_SNAPSHOT"
            impact_history = final_event["impact_declarations"]
            declared_cost = next(
                item for item in impact_history if item["axis"] == "COST" and item["revision"] == 1
            )
            unknown_cost_measurement = next(
                item for item in impact_history if item["axis"] == "COST" and item["revision"] == 2
            )
            unknown_capacity = next(item for item in impact_history if item["axis"] == "CAPACITY")
            assert declared_cost["value_as_declared"] == "0.00"
            assert declared_cost["currency_code"] == "EUR"
            assert declared_cost["linkage_state"] == "CURRENT"
            assert unknown_cost_measurement["impact_state"] == "DECLARED"
            assert unknown_cost_measurement["measurement_state"] == "UNKNOWN"
            assert unknown_cost_measurement["value_as_declared"] is None
            assert unknown_cost_measurement["measurement_unknown_reason"] == (
                "Aucun devis n’a confirmé le montant."
            )
            assert unknown_capacity["impact_state"] == "UNKNOWN"
            assert unknown_capacity["impact_unknown_reason"] == (
                "La charge de moyens du changement n’est pas établie."
            )

            superseding_c2_payload = {
                **unknown_linkage_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "linkage_id": str(uuid4()),
                "expected_revision": 2,
            }
            superseding_c2 = client.post(linkage_path, headers=headers, json=superseding_c2_payload)
            assert superseding_c2.status_code == 201, superseding_c2.text
            stale_c3_payload = {
                **declared_impact_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "declaration_id": str(uuid4()),
                "expected_revision": 2,
            }
            stale_c3 = client.post(impact_path, headers=headers, json=stale_c3_payload)
            assert stale_c3.status_code == 422
            assert stale_c3.json()["detail"] == "C2_LINKAGE_NOT_CURRENT_OR_LINKED"
            after_c2_supersession = client.get(base, headers=headers).json()["events"][0]
            assert after_c2_supersession["engagement_linkage_state"] == "UNKNOWN"
            assert all(
                item["linkage_state"] == "REVIEW_REQUIRED"
                for item in after_c2_supersession["impact_declarations"]
            )
            assert after_c2_supersession["action_impact_relations"][0]["projection_state"] == (
                "REVIEW_REQUIRED"
            )
            stale_c4_c3 = client.post(
                c4_path,
                headers=headers,
                json={
                    **c4_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "relation_id": str(uuid4()),
                    "expected_revision": 3,
                },
            )
            assert stale_c4_c3.status_code == 422
            assert stale_c4_c3.json()["detail"] == "C3_LINKAGE_NOT_CURRENT_OR_LINKED"
            assert final_event["applicability_state"] == "APPLICABLE_TO_HANDOVER"
            assert final_event["applicability_history"][0]["contract_instrument_version_id"] == str(
                instrument_id
            )
            assert final_event["applicability_history"][0]["delta_state"] == "DECLARED"
            assert "aucun coût" in final_event["applicability_history"][0]["delta_note"]
            assert final_event["actions"][0]["state"] == "RECORDED"

            stale_review_payload = {
                **review_payload,
                "command_id": str(uuid4()),
                "idempotency_key": str(uuid4()),
                "review_id": str(uuid4()),
                "expected_revision": 1,
                "decision": "NEEDS_CLARIFICATION",
                "delta_state": "UNKNOWN",
                "delta_note": None,
                "rationale": "La revue initiale doit être clarifiée.",
                "evidence_refs": ["document://review/clarification"],
            }
            stale_review = client.post(review_path, headers=headers, json=stale_review_payload)
            assert stale_review.status_code == 201, stale_review.text
            c4_stale_review = client.post(
                c4_path,
                headers=headers,
                json={
                    **c4_unknown_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "relation_id": str(uuid4()),
                    "expected_revision": 3,
                },
            )
            assert c4_stale_review.status_code == 422
            assert c4_stale_review.json()["detail"] == (
                "CONTRACT_CHANGE_ACTION_APPLICABILITY_STALE"
            )
            after_c1_review = client.get(base, headers=headers).json()["events"][0]
            assert all(
                relation["projection_state"] == "REVIEW_REQUIRED"
                for relation in after_c1_review["action_impact_relations"]
            )
            assert (
                final_event["actions"][0]["due_date_absence_reason"]
                == "Aucune date d’action validée."
            )
            assert final_event["handover_snapshot_id"] == str(handover_id)
            assert final_event["offer_package_id"] == str(package_id)
            assert (
                handover["snapshot"]["decision"]["condition_sources"][0]["impact_id"]
                == a1["impact_id"]
            )

            resolver.actors["collaborator"] = replace(
                patron,
                actor_kind=ActorKind.COLLABORATEUR,
                capabilities=capabilities_for(ActorKind.COLLABORATEUR),
            )
            collaborator_read = client.get(base, headers={"Authorization": "Bearer collaborator"})
            assert collaborator_read.status_code == 403
            collaborator_write = client.post(
                linkage_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **linkage_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                },
            )
            assert collaborator_write.status_code == 403
            collaborator_c3 = client.post(
                impact_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **declared_impact_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "declaration_id": str(uuid4()),
                },
            )
            assert collaborator_c3.status_code == 403
            collaborator_c4 = client.post(
                c4_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **c4_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "relation_id": str(uuid4()),
                },
            )
            assert collaborator_c4.status_code == 403
            collaborator_c5 = client.post(
                c5_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **c5_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                },
            )
            assert collaborator_c5.status_code == 403
            collaborator_evidence = client.post(
                evidence_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **evidence_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "evidence_object_id": str(uuid4()),
                },
            )
            assert collaborator_evidence.status_code == 403
            collaborator_confirmation = client.post(
                external_confirmation_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                },
            )
            assert collaborator_confirmation.status_code == 403
            collaborator_evidence_intent = client.post(
                evidence_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **evidence_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "evidence_object_id": str(uuid4()),
                },
            )
            assert collaborator_evidence_intent.status_code == 403
            collaborator_external_confirmation = client.post(
                external_confirmation_path,
                headers={"Authorization": "Bearer collaborator"},
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                },
            )
            assert collaborator_external_confirmation.status_code == 403
            foreign_read = client.get(base, headers={"Authorization": "Bearer foreign"})
            assert foreign_read.status_code == 200
            assert foreign_read.json() == {"case_id": str(case_id), "events": []}
            foreign_write = client.post(
                linkage_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **linkage_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                },
            )
            assert foreign_write.status_code == 422
            foreign_c5 = client.post(
                c5_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **c5_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "act_id": str(uuid4()),
                },
            )
            assert foreign_c5.status_code == 422
            foreign_evidence = client.post(
                evidence_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **evidence_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "evidence_object_id": str(uuid4()),
                },
            )
            assert foreign_evidence.status_code == 422
            foreign_confirmation = client.post(
                external_confirmation_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                },
            )
            assert foreign_confirmation.status_code == 422
            foreign_evidence_intent = client.post(
                evidence_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **evidence_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "evidence_object_id": str(uuid4()),
                },
            )
            assert foreign_evidence_intent.status_code == 422
            foreign_external_confirmation = client.post(
                external_confirmation_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **external_confirmation_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "confirmation_id": str(uuid4()),
                },
            )
            assert foreign_external_confirmation.status_code == 422
            foreign_c3 = client.post(
                impact_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **declared_impact_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "declaration_id": str(uuid4()),
                },
            )
            assert foreign_c3.status_code == 422
            foreign_c4 = client.post(
                c4_path,
                headers={"Authorization": "Bearer foreign"},
                json={
                    **c4_payload,
                    "command_id": str(uuid4()),
                    "idempotency_key": str(uuid4()),
                    "relation_id": str(uuid4()),
                },
            )
            assert foreign_c4.status_code == 422
    finally:
        server.should_exit = True
        thread.join(timeout=5)

    with Session(database_engine) as session:
        decision = session.get(DecisionRecord, UUID(a1["decision_id"]))
        condition = session.get(DecisionConditionRecord, UUID(a1["condition_id"]))
        impact = session.get(ContractBaselineDeviationImpactRecord, UUID(a1["impact_id"]))
        assert decision is not None and decision.outcome == "CONDITIONAL_GO"
        assert condition is not None and condition.status == "OPEN"
        assert impact is not None and impact.status == "HUMAN_REVIEW_REQUIRED"
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEventRecord)
                .where(
                    CaseContractChangeEventRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEventRecord.case_id == case_id,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEngagementLinkRecord)
                .where(
                    CaseContractChangeEngagementLinkRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEngagementLinkRecord.case_id == case_id,
                    CaseContractChangeEngagementLinkRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeImpactDeclarationRecord)
                .where(
                    CaseContractChangeImpactDeclarationRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeImpactDeclarationRecord.case_id == case_id,
                    CaseContractChangeImpactDeclarationRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionImpactRelationRecord)
                .where(
                    CaseContractChangeActionImpactRelationRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeActionImpactRelationRecord.case_id == case_id,
                    CaseContractChangeActionImpactRelationRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionImpactLinkRecord)
                .where(
                    CaseContractChangeActionImpactLinkRecord.relation_id
                    == UUID(str(c4_payload["relation_id"]))
                )
            )
            == 2
        )

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
            sa.update(CaseContractChangeImpactDeclarationRecord)
            .where(
                CaseContractChangeImpactDeclarationRecord.id
                == declared_impact_payload["declaration_id"]
            )
            .values(impact_summary="Réécriture interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeImpactDeclarationRecord).where(
                CaseContractChangeImpactDeclarationRecord.id
                == declared_impact_payload["declaration_id"]
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeEngagementLinkRecord).where(
                CaseContractChangeEngagementLinkRecord.id == linkage_payload["linkage_id"]
            )
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

    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeActionImpactRelationRecord)
            .where(
                CaseContractChangeActionImpactRelationRecord.id
                == UUID(str(c4_payload["relation_id"]))
            )
            .values(rationale="Réécriture interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeActionImpactRelationRecord).where(
                CaseContractChangeActionImpactRelationRecord.id
                == UUID(str(c4_payload["relation_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeActionExecutionRecord)
            .where(CaseContractChangeActionExecutionRecord.id == UUID(str(c5_payload["act_id"])))
            .values(declared_summary="Réécriture interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeActionExecutionRecord).where(
                CaseContractChangeActionExecutionRecord.id == UUID(str(c5_payload["act_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeEvidenceObjectRecord)
            .where(
                CaseContractChangeEvidenceObjectRecord.id
                == UUID(str(evidence_payload["evidence_object_id"]))
            )
            .values(sha256="0" * 64)
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeEvidenceObjectRecord).where(
                CaseContractChangeEvidenceObjectRecord.id
                == UUID(str(evidence_payload["evidence_object_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeExternalConfirmationRecord).where(
                CaseContractChangeExternalConfirmationRecord.id
                == UUID(str(external_confirmation_payload["confirmation_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeExternalConfirmationRecord)
            .where(
                CaseContractChangeExternalConfirmationRecord.id
                == UUID(str(external_confirmation_payload["confirmation_id"]))
            )
            .values(rationale="Réécriture interdite")
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeActionExecutionEvidenceLinkRecord)
            .where(
                CaseContractChangeActionExecutionEvidenceLinkRecord.act_id
                == UUID(str(c5_payload["act_id"]))
            )
            .values(position=4)
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeActionExecutionEvidenceLinkRecord).where(
                CaseContractChangeActionExecutionEvidenceLinkRecord.act_id
                == UUID(str(c5_payload["act_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.delete(CaseContractChangeActionImpactLinkRecord).where(
                CaseContractChangeActionImpactLinkRecord.relation_id
                == UUID(str(c4_payload["relation_id"]))
            )
        )
    with (
        Session(database_engine) as session,
        pytest.raises(sa.exc.DBAPIError),
        session.begin_nested(),
    ):
        session.execute(
            sa.update(CaseContractChangeEngagementLinkRecord)
            .where(CaseContractChangeEngagementLinkRecord.id == linkage_payload["linkage_id"])
            .values(rationale="Réécriture interdite")
        )
    with Session(database_engine) as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEventRecord)
                .where(
                    CaseContractChangeEventRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEventRecord.case_id == case_id,
                    CaseContractChangeEventRecord.id == event_id,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeApplicabilityRecord)
                .where(
                    CaseContractChangeApplicabilityRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeApplicabilityRecord.case_id == case_id,
                    CaseContractChangeApplicabilityRecord.event_id == event_id,
                )
            )
            == 2
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionRecord)
                .where(
                    CaseContractChangeActionRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeActionRecord.case_id == case_id,
                    CaseContractChangeActionRecord.event_id == event_id,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEngagementLinkRecord)
                .where(
                    CaseContractChangeEngagementLinkRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEngagementLinkRecord.case_id == case_id,
                    CaseContractChangeEngagementLinkRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeImpactDeclarationRecord)
                .where(
                    CaseContractChangeImpactDeclarationRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeImpactDeclarationRecord.case_id == case_id,
                    CaseContractChangeImpactDeclarationRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionImpactRelationRecord)
                .where(
                    CaseContractChangeActionImpactRelationRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeActionImpactRelationRecord.case_id == case_id,
                    CaseContractChangeActionImpactRelationRecord.event_id == event_id,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionExecutionRecord)
                .where(
                    CaseContractChangeActionExecutionRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeActionExecutionRecord.case_id == case_id,
                    CaseContractChangeActionExecutionRecord.event_id == event_id,
                )
            )
            == 2
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEvidenceObjectRecord)
                .where(
                    CaseContractChangeEvidenceObjectRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEvidenceObjectRecord.case_id == case_id,
                    CaseContractChangeEvidenceObjectRecord.event_id == event_id,
                )
            )
            == 7
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeEvidenceObjectRecord)
                .where(
                    CaseContractChangeEvidenceObjectRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeEvidenceObjectRecord.case_id == case_id,
                    CaseContractChangeEvidenceObjectRecord.event_id == event_id,
                    CaseContractChangeEvidenceObjectRecord.state == "REJECTED",
                )
            )
            == 5
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionExecutionEvidenceLinkRecord)
                .where(
                    CaseContractChangeActionExecutionEvidenceLinkRecord.tenant_id
                    == patron.tenant_id,
                    CaseContractChangeActionExecutionEvidenceLinkRecord.case_id == case_id,
                    CaseContractChangeActionExecutionEvidenceLinkRecord.event_id == event_id,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeExternalConfirmationRecord)
                .where(
                    CaseContractChangeExternalConfirmationRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeExternalConfirmationRecord.case_id == case_id,
                    CaseContractChangeExternalConfirmationRecord.event_id == event_id,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseContractChangeActionImpactLinkRecord)
                .where(
                    CaseContractChangeActionImpactLinkRecord.tenant_id == patron.tenant_id,
                    CaseContractChangeActionImpactLinkRecord.case_id == case_id,
                    CaseContractChangeActionImpactLinkRecord.event_id == event_id,
                    CaseContractChangeActionImpactLinkRecord.relation_id
                    == UUID(str(c4_payload["relation_id"])),
                )
            )
            == 2
        )
    if preserve_c5_restore_fixture:
        with session_factory() as session:
            preserved_clean = session.get(
                CaseContractChangeEvidenceObjectRecord,
                UUID(str(evidence_payload["evidence_object_id"])),
            )
        assert preserved_clean is not None and preserved_clean.state == "CLEAN"
        preserved_path = asyncio.run(
            evidence_storage.local_path(storage_key=preserved_clean.storage_key)
        )
        assert sha256(preserved_path.read_bytes()).hexdigest() == preserved_clean.sha256
    else:
        with database_engine.begin() as connection:
            connection.execute(
                sa.text(
                    "TRUNCATE TABLE case_contract_change_external_confirmations, "
                    "case_contract_change_action_execution_evidence_links, "
                    "case_contract_change_evidence_objects, "
                    "case_contract_change_action_executions CASCADE"
                )
            )
