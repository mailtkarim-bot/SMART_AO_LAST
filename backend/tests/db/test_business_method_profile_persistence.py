from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from app.modules.case.infrastructure.models.business_method_profile_adoption import (
    CaseBusinessMethodProfileAdoptionRecord,
)
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.decision.infrastructure.repositories import SqlAlchemyDecisionLifecycleRepository
from app.modules.enterprise.application.business_method_profile_handler import (
    BusinessMethodProfileService,
    business_method_profile_handlers,
)
from app.modules.enterprise.infrastructure.models.business_method_profile import (
    EnterpriseBusinessMethodProfileVersionRecord,
)
from app.modules.enterprise.infrastructure.models.enterprise import EnterpriseCompanyRecord
from app.modules.enterprise.public.business_method_profile_contracts import (
    AdoptBusinessMethodProfileRequest,
    BusinessMethodProfileContent,
    PublishBusinessMethodProfileRequest,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from app.platform.security.models import IdentityRecord, TenantMembershipRecord
from sqlalchemy import delete, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case

NOW = datetime(2026, 10, 1, 12, tzinfo=UTC)


def _seed(database_engine, session_factory):
    tenant_id, company_id, case_id = uuid4(), uuid4(), uuid4()
    actor_id, membership_id = uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(
                id=tenant_id,
                slug=f"bmp-{tenant_id.hex[:10]}",
                lifecycle="ACTIVE",
            )
        )
        session.flush()
        session.add(
            IdentityRecord(
                id=actor_id,
                email_normalized=f"{actor_id.hex}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.flush()
        session.add(
            TenantMembershipRecord(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=actor_id,
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        session.add(
            EnterpriseCompanyRecord(
                id=company_id,
                tenant_id=tenant_id,
                aggregate_revision=0,
                legal_name="Entreprise de test",
                trade_name=None,
                siren="123456789",
                siret="12345678900012",
                vat_number="FR123456789",
                address_line1="1 rue du Test",
                postal_code="75001",
                city="Paris",
                country_code="FR",
            )
        )
        session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="a"))
        session.commit()
    actor = ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset({case_id}),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers=business_method_profile_handlers(),
    )
    service = BusinessMethodProfileService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    return tenant_id, company_id, case_id, actor, service


def test_profile_publish_adoption_context_reference_and_idempotent_replay(
    database_engine, session_factory
):
    tenant_id, company_id, case_id, actor, service = _seed(database_engine, session_factory)
    profile = BusinessMethodProfileContent.model_validate(
        {
            "terminology": {"lot": "Zone travaux"},
            "additional_checks": [
                {"key": "site_access", "label": "Accès au site occupé", "axis": "CONTRACT"}
            ],
        }
    )
    publish = PublishBusinessMethodProfileRequest(
        command_id=uuid4(), idempotency_key=uuid4(), expected_version=0, profile=profile
    )
    command = publish.to_command(company_id=company_id)
    first = service.publish(actor=actor, command=command, now=NOW)
    replay = service.publish(actor=actor, command=command, now=NOW)
    assert first.result_code == "BUSINESS_METHOD_PROFILE_PUBLISHED"
    assert not first.replayed
    assert replay.replayed
    profile_ref = first.aggregate_refs[0]

    adoption_request = AdoptBusinessMethodProfileRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_adoption_revision=0,
        profile_version_id=profile_ref["aggregate_id"],
        profile_version=profile_ref["aggregate_revision"],
        profile_content_sha256=profile_ref["content_hash"],
    )
    adoption_command = adoption_request.to_command(case_id=case_id)
    adoption = service.adopt(actor=actor, command=adoption_command, now=NOW)
    adoption_replay = service.adopt(actor=actor, command=adoption_command, now=NOW)
    current = service.current_adoption(actor=actor, case_id=case_id, now=NOW)
    assert adoption.result_code == "BUSINESS_METHOD_PROFILE_ADOPTED"
    assert adoption_replay.replayed
    assert current is not None
    assert current.profile_version_id == command.profile_version_id
    assert current.profile_content_sha256 == profile_ref["content_hash"]

    with Session(database_engine) as session:
        reader = SqlAlchemyDecisionLifecycleRepository()
        assert reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=command.profile_version_id,
            aggregate_revision=1,
            content_hash=current.profile_content_sha256,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=uuid4(),
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=command.profile_version_id,
            aggregate_revision=1,
            content_hash=current.profile_content_sha256,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=command.profile_version_id,
            aggregate_revision=1,
            content_hash="0" * 64,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=uuid4(),
            case_id=case_id,
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=command.profile_version_id,
            aggregate_revision=1,
            content_hash=current.profile_content_sha256,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=command.profile_version_id,
            aggregate_revision=1,
            content_hash=None,
        )


def test_profile_and_adoption_are_tenant_scoped_and_optimistically_versioned(
    database_engine, session_factory
):
    tenant_id, company_id, case_id, actor, service = _seed(database_engine, session_factory)
    empty_profile = BusinessMethodProfileContent()
    command = PublishBusinessMethodProfileRequest(
        command_id=uuid4(), idempotency_key=uuid4(), expected_version=0, profile=empty_profile
    ).to_command(company_id=company_id)
    published = service.publish(actor=actor, command=command, now=NOW)

    stale_publish = PublishBusinessMethodProfileRequest(
        command_id=uuid4(), idempotency_key=uuid4(), expected_version=0, profile=empty_profile
    ).to_command(company_id=company_id)
    with pytest.raises(CommandExecutionError, match="STALE_PROFILE_VERSION"):
        service.publish(actor=actor, command=stale_publish, now=NOW)

    profile_ref = published.aggregate_refs[0]
    adoption = AdoptBusinessMethodProfileRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_adoption_revision=0,
        profile_version_id=command.profile_version_id,
        profile_version=profile_ref["aggregate_revision"],
        profile_content_sha256=profile_ref["content_hash"],
    ).to_command(case_id=case_id)
    service.adopt(actor=actor, command=adoption, now=NOW)
    stale_adoption = AdoptBusinessMethodProfileRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_adoption_revision=0,
        profile_version_id=command.profile_version_id,
        profile_version=profile_ref["aggregate_revision"],
        profile_content_sha256=profile_ref["content_hash"],
    ).to_command(case_id=case_id)
    with pytest.raises(CommandExecutionError, match="STALE_PROFILE_ADOPTION"):
        service.adopt(actor=actor, command=stale_adoption, now=NOW)

    foreign_actor = replace(actor, tenant_id=uuid4())
    with pytest.raises(PermissionError, match="NOT_FOUND_OR_FORBIDDEN"):
        service.versions(actor=foreign_actor, company_id=company_id, now=NOW)
    collaborator = replace(actor, actor_kind=ActorKind.COLLABORATEUR)
    with pytest.raises(PermissionError, match="PATRON_REQUIRED"):
        service.publish(actor=collaborator, command=command, now=NOW)


def test_published_profile_and_adoption_rows_are_append_only(database_engine, session_factory):
    _, company_id, case_id, actor, service = _seed(database_engine, session_factory)
    command = PublishBusinessMethodProfileRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        expected_version=0,
        profile=BusinessMethodProfileContent(),
    ).to_command(company_id=company_id)
    result = service.publish(actor=actor, command=command, now=NOW)
    profile_hash = result.aggregate_refs[0]["content_hash"]
    service.adopt(
        actor=actor,
        command=AdoptBusinessMethodProfileRequest(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            expected_adoption_revision=0,
            profile_version_id=command.profile_version_id,
            profile_version=1,
            profile_content_sha256=profile_hash,
        ).to_command(case_id=case_id),
        now=NOW,
    )

    with pytest.raises(DBAPIError), Session(database_engine) as session, session.begin():
        session.execute(
            update(EnterpriseBusinessMethodProfileVersionRecord)
            .where(
                EnterpriseBusinessMethodProfileVersionRecord.id == command.profile_version_id
            )
            .values(version_number=2)
        )
    with pytest.raises(DBAPIError), Session(database_engine) as session, session.begin():
        session.execute(
            delete(CaseBusinessMethodProfileAdoptionRecord).where(
                CaseBusinessMethodProfileAdoptionRecord.case_id == case_id
            )
        )


def test_contract_proof_revision_is_tenant_case_scoped_and_append_only(
    database_engine, session_factory
):
    tenant_id, _, case_id, _, _ = _seed(database_engine, session_factory)
    proof_id = uuid4()
    with Session(database_engine) as session, session.begin():
        session.add(
            ContractBaselineDeviationImpactRecord(
                id=proof_id,
                tenant_id=tenant_id,
                case_id=case_id,
                baseline_observation_id=uuid4(),
                proof_revision=1,
                baseline_source_refs_json=["DCE_REQUIREMENT:source/lot-1"],
                baseline_statement="Exigence déclarée dans la version de consultation.",
                deviation_statement="Écart à vérifier par le Patron.",
                impact_statement="Impact déclaré, non calculé.",
                status="CONFIRMED",
                created_by_actor_id=uuid4(),
            )
        )
    reader = SqlAlchemyDecisionLifecycleRepository()
    with Session(database_engine) as session:
        assert reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            aggregate_type="CONTRACT_BASELINE_IMPACT",
            aggregate_id=proof_id,
            aggregate_revision=1,
            content_hash=None,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=uuid4(),
            aggregate_type="CONTRACT_BASELINE_IMPACT",
            aggregate_id=proof_id,
            aggregate_revision=1,
            content_hash=None,
        )
    with pytest.raises(DBAPIError), Session(database_engine) as session, session.begin():
        session.execute(
            update(ContractBaselineDeviationImpactRecord)
            .where(ContractBaselineDeviationImpactRecord.id == proof_id)
            .values(impact_statement="Mutation interdite")
        )


def test_baseline_impact_can_be_referenced_only_by_its_tenant_case_revision(
    database_engine, session_factory
):
    tenant_id, _, case_id, actor, _ = _seed(database_engine, session_factory)
    proof_id = uuid4()
    with Session(database_engine) as session, session.begin():
        session.add(
            ContractBaselineDeviationImpactRecord(
                id=proof_id,
                tenant_id=tenant_id,
                case_id=case_id,
                baseline_observation_id=uuid4(),
                proof_revision=1,
                baseline_source_refs_json=["DCE_REQUIREMENT:declared-source"],
                baseline_statement="Exigence sourcée.",
                deviation_statement="Écart soumis à revue.",
                impact_statement="Impact déclaré, non calculé.",
                status="CONFIRMED",
                created_by_actor_id=actor.actor_id,
            )
        )
    reader = SqlAlchemyDecisionLifecycleRepository()
    with Session(database_engine) as session:
        assert reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            aggregate_type="CONTRACT_BASELINE_IMPACT",
            aggregate_id=proof_id,
            aggregate_revision=1,
            content_hash=None,
        )
        assert not reader.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=uuid4(),
            aggregate_type="CONTRACT_BASELINE_IMPACT",
            aggregate_id=proof_id,
            aggregate_revision=1,
            content_hash=None,
        )
