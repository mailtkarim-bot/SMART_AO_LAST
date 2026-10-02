from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
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
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
    DceRequirementConfirmationRecord,
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
    DecisionConditionContractEvidenceLinkRecord,
    DecisionConditionRecord,
    DecisionRecord,
)
from app.modules.decision.infrastructure.repositories import (
    SqlAlchemyDecisionLifecycleRepository,
    SqlAlchemyDecisionRepository,
)
from app.modules.decision.infrastructure.verified_context_reader import (
    SqlAlchemyDecisionVerifiedContextReader,
)
from app.modules.enterprise.public.business_method_profile_contracts import (
    AdoptBusinessMethodProfileRequest,
    BusinessMethodProfileContent,
    PublishBusinessMethodProfileRequest,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.context import ActorContext, ActorKind
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from tests.api.test_dce_requirement_confirmation_api import _seed_requirement_and_case
from tests.db.test_business_method_profile_persistence import _seed as seed_profile_principal
from tests.db.test_regulatory_profile_persistence import _case as seed_manual_case


class Resolver:
    def __init__(self, actor: ActorContext):
        self.actor = actor

    def resolve(self, *, access_token: str) -> ActorContext:
        assert access_token == "a1-test-token"
        return self.actor


def _run_a1_on_second_profile(
    client: TestClient,
    *,
    headers: dict[str, str],
    case_id,
    requirement_id,
    proof_id,
    profile_ref: dict[str, object],
    actor_id,
):
    created = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions",
        json={"command_id": str(uuid4()), "idempotency_key": str(uuid4())},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    decision_id = created.json()["decision_id"]
    frozen = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/context",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "context_id": str(uuid4()),
            "expected_revision": created.json()["version"],
            "rationale": "Même parcours A1 sous une seconde méthode entreprise.",
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
                    "aggregate_id": str(proof_id),
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
        headers=headers,
    )
    assert frozen.status_code == 200, frozen.text
    condition_id = uuid4()
    finalized = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/go-no-go",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_revision": frozen.json()["version"],
            "displayed_fingerprint": frozen.json()["fingerprint"],
            "outcome": "CONDITIONAL_GO",
            "justification": "Même impact déclaré ; application de la méthode v2.",
            "conditions": [
                {
                    "condition_id": str(condition_id),
                    "label": "Revoir l’impact déclaré sous la méthode v2",
                    "owner_actor_id": str(actor_id),
                    "due_date_absence_reason": "Date non déterminée",
                    "failure_consequence": "Réexamen Patron",
                }
            ],
        },
        headers=headers,
    )
    assert finalized.status_code == 200, finalized.text
    link_body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "link_id": str(uuid4()),
        "contract_impact_id": str(proof_id),
        "proof_revision": 1,
        "expected_decision_revision": finalized.json()["version"],
    }
    link_path = (
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/conditions/"
        f"{condition_id}/contract-evidence"
    )
    linked = client.post(link_path, json=link_body, headers=headers)
    assert linked.status_code == 201, linked.text
    replay = client.post(link_path, json=link_body, headers=headers)
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    dossier = client.get(f"/api/v1/patron/cases/{case_id}/decision-dossier", headers=headers)
    assert dossier.status_code == 200, dossier.text
    body = dossier.json()
    assert body["outcome"] == "CONDITIONAL_GO"
    assert body["conditions"][0]["status"] == "OPEN"
    assert len(body["contract_evidence_links"]) == 1
    link = body["contract_evidence_links"][0]
    assert link["profile_version_id"] == str(profile_ref["aggregate_id"])
    assert link["profile_version"] == profile_ref["aggregate_revision"]
    assert link["profile_content_sha256"] == profile_ref["content_hash"]
    return decision_id, finalized.json()["version"], body


def test_a1_http_postgres_chain_is_idempotent_tenant_scoped_and_does_not_promote(
    database_engine, session_factory
):
    now = datetime.now(tz=UTC)
    tenant_id, company_id, _initial_case_id, actor, profile_service = seed_profile_principal(
        database_engine, session_factory
    )
    actor = replace(actor, authenticated_at=now, mfa_verified_at=now)
    requirement_id, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    with Session(database_engine) as session:
        baseline_observation_id = session.scalar(
            select(DceRequirementRecord.source_observation_id).where(
                DceRequirementRecord.tenant_id == tenant_id,
                DceRequirementRecord.id == requirement_id,
            )
        )
    confirmation_id = uuid4()
    with Session(database_engine) as session, session.begin():
        session.add(
            DceRequirementConfirmationRecord(
                id=confirmation_id,
                tenant_id=tenant_id,
                requirement_id=requirement_id,
                revision=1,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
                confirmed_by_actor_id=actor.actor_id,
            )
        )
        session.flush()
        session.add(
            DceRequirementConfirmationCurrentRecord(
                tenant_id=tenant_id,
                requirement_id=requirement_id,
                confirmation_id=confirmation_id,
                revision=1,
                outcome="CONFIRMED",
            )
        )

    profile = BusinessMethodProfileContent.model_validate(
        {"terminology": {}, "additional_checks": []}
    )
    published = profile_service.publish(
        actor=actor,
        command=PublishBusinessMethodProfileRequest(
            command_id=uuid4(), idempotency_key=uuid4(), expected_version=0, profile=profile
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

    policy = AuthorizationPolicy()
    lifecycle_repository = SqlAlchemyDecisionLifecycleRepository()
    condition_repository = SqlAlchemyDecisionConditionRepository()

    def decision_repository_factory(session):
        return SqlAlchemyDecisionRepository(session)

    handlers = {
        **contract_baseline_handlers(),
        **decision_lifecycle_handlers(
            lifecycle_repository=lifecycle_repository,
            repository_factory=decision_repository_factory,
            condition_repository=condition_repository,
        ),
        **decision_finalization_handlers(
            repository_factory=decision_repository_factory,
            verified_context_reader=SqlAlchemyDecisionVerifiedContextReader(),
            condition_repository=condition_repository,
        ),
    }
    dispatcher = CommandDispatcher(session_factory=session_factory, handlers=handlers)
    resolver = Resolver(actor)
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
    client = TestClient(app, raise_server_exceptions=False)
    headers = {"Authorization": "Bearer a1-test-token"}

    proof_id = uuid4()
    impact_body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "proof_id": str(proof_id),
        "dce_requirement_id": str(requirement_id),
        "dce_requirement_revision": 1,
        "baseline_source_refs": [
            "CCAP · article 4 · page 12",
            f"DCE_REQUIREMENT:{requirement_id}@1",
        ],
        "baseline_statement": "Délai de paiement déclaré dans le CCAP.",
        "deviation_statement": "Écart à examiner par le Patron.",
        "impact_statement": "Effet de trésorerie déclaré, non calculé.",
    }
    impact_path = f"/api/v1/patron/cases/{case_id}/contract-baseline-impacts"
    stale_requirement = client.post(
        impact_path,
        json={
            **impact_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "proof_id": str(uuid4()),
            "dce_requirement_revision": 2,
        },
        headers=headers,
    )
    assert stale_requirement.status_code == 409
    assert stale_requirement.json()["detail"] == "DCE_REQUIREMENT_NOT_CURRENTLY_CONFIRMED"
    recorded = client.post(impact_path, json=impact_body, headers=headers)
    assert recorded.status_code == 201, recorded.text
    replay = client.post(impact_path, json=impact_body, headers=headers)
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    persisted_impact = client.get(impact_path, headers=headers)
    assert persisted_impact.status_code == 200
    assert persisted_impact.json()["items"][0]["baseline_observation_id"] == str(
        baseline_observation_id
    )

    created = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions",
        json={"command_id": str(uuid4()), "idempotency_key": str(uuid4())},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    decision_id = created.json()["decision_id"]
    profile_version_id = str(profile_ref["aggregate_id"])
    missing_profile = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/context",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "context_id": str(uuid4()),
            "expected_revision": created.json()["version"],
            "rationale": "Contexte A1 incomplet.",
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
                    "aggregate_id": str(proof_id),
                    "aggregate_revision": 1,
                    "reference_role": "DECLARED_IMPACT",
                },
            ],
        },
        headers=headers,
    )
    assert missing_profile.status_code == 422
    assert missing_profile.json()["detail"] == "ADOPTED_BUSINESS_METHOD_PROFILE_REFERENCE_REQUIRED"

    frozen = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/context",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "context_id": str(uuid4()),
            "expected_revision": created.json()["version"],
            "rationale": "Contexte A1 sourcé.",
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
                    "aggregate_id": str(proof_id),
                    "aggregate_revision": 1,
                    "reference_role": "DECLARED_IMPACT",
                },
                {
                    "aggregate_type": "BUSINESS_METHOD_PROFILE",
                    "aggregate_id": profile_version_id,
                    "aggregate_revision": 1,
                    "content_hash": profile_ref["content_hash"],
                    "reference_role": "ADOPTED_METHOD",
                },
            ],
        },
        headers=headers,
    )
    assert frozen.status_code == 200, frozen.text
    condition_id = uuid4()
    finalized = client.post(
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/go-no-go",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_revision": frozen.json()["version"],
            "displayed_fingerprint": frozen.json()["fingerprint"],
            "outcome": "CONDITIONAL_GO",
            "justification": "Décision Patron conditionnelle.",
            "conditions": [
                {
                    "condition_id": str(condition_id),
                    "label": "Vérifier l’impact déclaré",
                    "owner_actor_id": str(actor.actor_id),
                    "due_date_absence_reason": "Date non déterminée",
                    "failure_consequence": "Réexamen Patron",
                }
            ],
        },
        headers=headers,
    )
    assert finalized.status_code == 200, finalized.text
    assert finalized.json()["outcome"] == "CONDITIONAL_GO"
    with Session(database_engine) as session:
        selected_context_id = session.scalar(
            select(DecisionRecord.selected_final_context_id).where(
                DecisionRecord.tenant_id == tenant_id,
                DecisionRecord.id == decision_id,
            )
        )
    assert selected_context_id is not None
    unknown_proof_id = uuid4()
    with Session(database_engine) as session, session.begin():
        session.add(
            ContractBaselineDeviationImpactRecord(
                id=unknown_proof_id,
                tenant_id=tenant_id,
                case_id=case_id,
                baseline_observation_id=uuid4(),
                dce_requirement_id=requirement_id,
                dce_requirement_revision=1,
                proof_revision=1,
                baseline_source_refs_json=[f"DCE_REQUIREMENT:{requirement_id}@1"],
                baseline_statement="Source d’incertitude déclarée.",
                deviation_statement=None,
                impact_statement=None,
                status="UNKNOWN",
                created_by_actor_id=actor.actor_id,
            )
        )
    link_body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "link_id": str(uuid4()),
        "contract_impact_id": str(proof_id),
        "proof_revision": 1,
        "expected_decision_revision": finalized.json()["version"],
    }
    link_path = (
        f"/api/v1/patron/cases/{case_id}/decisions/{decision_id}/conditions/"
        f"{condition_id}/contract-evidence"
    )
    unknown_link = client.post(
        link_path,
        json={
            **link_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "link_id": str(uuid4()),
            "contract_impact_id": str(unknown_proof_id),
        },
        headers=headers,
    )
    assert unknown_link.status_code == 422
    assert unknown_link.json()["detail"] == "CONTRACT_PROOF_REQUIRES_HUMAN_REVIEW_STATE"
    linked = client.post(link_path, json=link_body, headers=headers)
    assert linked.status_code == 201, linked.text
    link_replay = client.post(link_path, json=link_body, headers=headers)
    assert link_replay.status_code == 200
    assert link_replay.json()["replayed"] is True

    dossier = client.get(f"/api/v1/patron/cases/{case_id}/decision-dossier", headers=headers)
    assert dossier.status_code == 200, dossier.text
    body = dossier.json()
    assert body["outcome"] == "CONDITIONAL_GO"
    assert body["conditions"][0]["status"] == "OPEN"
    assert len(body["contract_evidence_links"]) == 1
    link = body["contract_evidence_links"][0]
    assert link["dce_requirement_id"] == str(requirement_id)
    assert link["contract_impact_id"] == str(proof_id)
    assert link["profile_version_id"] == profile_version_id

    profile_two = BusinessMethodProfileContent.model_validate(
        {
            "terminology": {"lot": "Zone travaux"},
            "additional_checks": [
                {"key": "supply_chain", "label": "Approvisionnement à confirmer", "axis": "PARTNER"}
            ],
        }
    )
    published_two = profile_service.publish(
        actor=actor,
        command=PublishBusinessMethodProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            expected_version=1,
            profile=profile_two,
        ).to_command(company_id=company_id),
        now=now,
    )
    profile_two_ref = published_two.aggregate_refs[0]
    case_two_id = uuid4()
    with Session(database_engine) as session, session.begin():
        original_case = session.scalar(
            select(CaseRecord).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
        )
        assert original_case is not None
        second_case = seed_manual_case(tenant_id=tenant_id, case_id=case_two_id, marker="g")
        second_case.consultation_id = original_case.consultation_id
        second_case.applicable_dce_version_id = original_case.applicable_dce_version_id
        second_case.dce_freshness = "CURRENT"
        session.add(second_case)
    profile_service.adopt(
        actor=actor,
        command=AdoptBusinessMethodProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            expected_adoption_revision=0,
            profile_version_id=profile_two_ref["aggregate_id"],
            profile_version=profile_two_ref["aggregate_revision"],
            profile_content_sha256=profile_two_ref["content_hash"],
        ).to_command(case_id=case_two_id),
        now=now,
    )
    proof_two_id = uuid4()
    impact_two = client.post(
        f"/api/v1/patron/cases/{case_two_id}/contract-baseline-impacts",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "proof_id": str(proof_two_id),
            "dce_requirement_id": str(requirement_id),
            "dce_requirement_revision": 1,
            "baseline_source_refs": [
                "CCAP · article 4 · page 12",
                f"DCE_REQUIREMENT:{requirement_id}@1",
            ],
            "baseline_statement": "Délai de paiement déclaré dans le CCAP.",
            "deviation_statement": "Écart à examiner par le Patron.",
            "impact_statement": "Effet de trésorerie déclaré, non calculé.",
        },
        headers=headers,
    )
    assert impact_two.status_code == 201, impact_two.text
    _decision_two_id, _decision_two_revision, dossier_two = _run_a1_on_second_profile(
        client,
        headers=headers,
        case_id=case_two_id,
        requirement_id=requirement_id,
        proof_id=proof_two_id,
        profile_ref=profile_two_ref,
        actor_id=actor.actor_id,
    )
    assert profile_two_ref["aggregate_id"] != profile_ref["aggregate_id"]
    assert profile_two_ref["content_hash"] != profile_ref["content_hash"]
    assert dossier_two["contract_evidence_links"][0]["profile_version"] == 2
    old_dossier_after_adoption = client.get(
        f"/api/v1/patron/cases/{case_id}/decision-dossier", headers=headers
    )
    assert old_dossier_after_adoption.status_code == 200
    old_snapshot = old_dossier_after_adoption.json()
    assert old_snapshot["outcome"] == "CONDITIONAL_GO"
    assert old_snapshot["aggregate_revision"] == finalized.json()["version"]
    assert old_snapshot["contract_evidence_links"][0]["profile_version_id"] == profile_version_id
    assert (
        old_snapshot["contract_evidence_links"][0]["profile_content_sha256"]
        == profile_ref["content_hash"]
    )

    resolver.actor = replace(actor, actor_kind=ActorKind.COLLABORATEUR)
    role_refused = client.post(
        link_path, json={**link_body, "idempotency_key": str(uuid4())}, headers=headers
    )
    assert role_refused.status_code == 403
    foreign_tenant_id = uuid4()
    with Session(database_engine) as session, session.begin():
        session.add(
            TenantRecord(
                id=foreign_tenant_id,
                slug=f"foreign-{foreign_tenant_id.hex[:12]}",
                lifecycle="ACTIVE",
            )
        )
    resolver.actor = replace(actor, tenant_id=foreign_tenant_id)
    tenant_refused = client.post(
        link_path, json={**link_body, "idempotency_key": str(uuid4())}, headers=headers
    )
    assert tenant_refused.status_code == 404

    with Session(database_engine) as session:
        root = session.execute(
            select(DecisionConditionRecord.status).where(
                DecisionConditionRecord.tenant_id == tenant_id,
                DecisionConditionRecord.id == condition_id,
            )
        ).scalar_one()
        outcome = session.execute(
            select(ContractBaselineDeviationImpactRecord.status).where(
                ContractBaselineDeviationImpactRecord.tenant_id == tenant_id,
                ContractBaselineDeviationImpactRecord.id == proof_id,
            )
        ).scalar_one()
        count = session.execute(
            select(DecisionConditionContractEvidenceLinkRecord.id).where(
                DecisionConditionContractEvidenceLinkRecord.tenant_id == tenant_id,
                DecisionConditionContractEvidenceLinkRecord.condition_id == condition_id,
            )
        ).all()
    assert root == "OPEN"
    assert outcome == "HUMAN_REVIEW_REQUIRED"
    assert len(count) == 1
    with pytest.raises(DBAPIError), Session(database_engine) as session, session.begin():
        session.execute(
            update(DecisionConditionContractEvidenceLinkRecord)
            .where(
                DecisionConditionContractEvidenceLinkRecord.tenant_id == tenant_id,
                DecisionConditionContractEvidenceLinkRecord.id == UUID(link_body["link_id"]),
            )
            .values(proof_revision=2)
        )
