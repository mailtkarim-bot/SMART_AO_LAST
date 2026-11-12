from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.bootstrap.application import AppRuntime, create_app
from app.interfaces.http.routes.authentication import AuthenticationHttpRuntime
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_rc_analysis import (
    DceRcAnalysisRunRecord,
    DceRcRequirementObservationRecord,
)
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationRecord,
)
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord,
    DceRequirementRecord,
    DceRequirementSourceRecord,
)
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.platform.security.authentication import AuthenticationService
from app.platform.security.models import (
    AuthSessionRecord,
    CaseAssignmentRecord,
    IdentityRecord,
    SecurityAuditEventRecord,
    TenantMembershipRecord,
)
from app.platform.security.tokens import JwtAccessTokenCodec
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 8, 14, 12, 0, tzinfo=UTC)


class FixedClock:
    def now(self) -> datetime:
        return NOW


class UnusedPasswordVerifier:
    def verify(self, *, password_hash: str, password: str) -> bool:
        return False


class UnusedTokenGenerator:
    def generate(self) -> str:
        return "unused-refresh-token"


@pytest.fixture(autouse=True)
def isolate_records(database_engine: sa.Engine) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))


def _seed_principal(
    engine: sa.Engine,
    *,
    role: str,
    tenant_id: UUID | None = None,
) -> tuple[UUID, UUID, UUID, UUID]:
    tenant_id = tenant_id or uuid4()
    identity_id, membership_id, session_id = uuid4(), uuid4(), uuid4()
    with engine.begin() as connection:
        connection.execute(
            sa.text("INSERT INTO tenants (id, slug, lifecycle) VALUES (:id, :slug, 'ACTIVE')"),
            {"id": tenant_id, "slug": f"tenant-{tenant_id.hex[:12]}"},
        )
        connection.execute(
            sa.insert(IdentityRecord).values(
                id=identity_id,
                email_normalized=f"user-{identity_id}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        connection.execute(
            sa.insert(TenantMembershipRecord).values(
                id=membership_id,
                tenant_id=tenant_id,
                identity_id=identity_id,
                role=role,
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        connection.execute(
            sa.insert(AuthSessionRecord).values(
                id=session_id,
                tenant_id=tenant_id,
                membership_id=membership_id,
                identity_id=identity_id,
                state="ACTIVE",
                auth_strength="MFA",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=NOW,
                revoked_at=None,
                revoke_reason=None,
            )
        )
    return tenant_id, identity_id, membership_id, session_id


def _seed_requirement_and_case(
    session_factory: sessionmaker[Session],
    *,
    tenant_id: UUID,
) -> tuple[UUID, UUID]:
    consultation_id, dce_version_id = uuid4(), uuid4()
    analysis_id, observation_id, run_id = uuid4(), uuid4(), uuid4()
    requirement_id, case_id = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(
            ConsultationRecord(
                id=consultation_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="a" * 64,
                buyer_legal_name="Ville de test",
                buyer_normalized_id="VILLE-TEST",
                external_reference="AO-2026-REQC",
                object_label="Réhabilitation école",
                location_label="Lille",
                source_channel="MANUAL_UPLOAD",
                source_reference="DCE test",
                source_received_at=NOW,
                lifecycle="OPEN",
                freshness="CURRENT",
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
        session.add(
            DceVersionRecord(
                id=dce_version_id,
                tenant_id=tenant_id,
                aggregate_revision=3,
                consultation_id=consultation_id,
                corpus_hash="b" * 64,
                predecessor_dce_version_id=None,
                provenance_channel="MANUAL_UPLOAD",
                provenance_reference=None,
                provenance_url=None,
                source_received_at=NOW,
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
        )
        session.flush()
        session.add(
            DceRcAnalysisRunRecord(
                id=analysis_id,
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                input_manifest_sha256="c" * 64,
                analyzer_id="test-analyzer",
                analyzer_version="1",
                status="COMPLETED",
                source_fragment_count=1,
                source_char_count=1,
                failure_code=None,
            )
        )
        session.flush()
        session.add(
            DceRcRequirementObservationRecord(
                id=observation_id,
                tenant_id=tenant_id,
                analysis_id=analysis_id,
                dce_version_id=dce_version_id,
                requirement_kind="RC_DOCUMENT_CANDIDATURE",
                directive="REQUIRED_SIGNAL",
                rule_id="TEST_RULE_V1",
                rule_version="1",
                fragment_id=uuid4(),
                start_byte_offset=0,
                end_byte_offset=1,
                excerpt="X",
            )
        )
        session.flush()
        session.add(
            DceRequirementMaterializationRunRecord(
                id=run_id,
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                dce_rc_analysis_id=analysis_id,
                input_manifest_sha256="d" * 64,
                materializer_id="test-materializer",
                materializer_version="1",
                status="COMPLETED",
                source_observation_count=1,
                failure_code=None,
            )
        )
        session.flush()
        session.add(
            DceRequirementRecord(
                id=requirement_id,
                tenant_id=tenant_id,
                requirements_run_id=run_id,
                dce_version_id=dce_version_id,
                source_observation_id=observation_id,
                requirement_type="CANDIDATURE_DOCUMENT",
                directive_signal="REQUIRED_SIGNAL",
                confirmation_status="PENDING_HUMAN_CONFIRMATION",
                uncertainty_status="SOURCE_SIGNAL_ONLY",
            )
        )
        session.flush()
        session.add(
            CaseRecord(
                id=case_id,
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="e" * 64,
                title="Affaire test",
                object_description=None,
                business_origin="OPPORTUNITY",
                origin_reference_id=None,
                origin_rationale=None,
                consultation_id=consultation_id,
                scope_kind="CUSTOM",
                scope_json={},
                scope_fingerprint="f" * 64,
                applicable_dce_version_id=dce_version_id,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
                stopped_reason=None,
                stopped_at=None,
                archived_reason=None,
                archived_at=None,
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
    return requirement_id, case_id


def _assign_collaborator(
    session_factory: sessionmaker[Session],
    *,
    tenant_id: UUID,
    membership_id: UUID,
    case_id: UUID,
    scope_actions: list[str] | None = None,
) -> None:
    with session_factory.begin() as session:
        session.add(
            CaseAssignmentRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                membership_id=membership_id,
                case_id=case_id,
                state="ACTIVE",
                scope_actions_json=scope_actions or ["dce.requirement.confirm"],
                scope_classifications_json=["INTERNAL_OPERATIONAL"],
                granted_by_membership_id=membership_id,
                granted_at=NOW,
                starts_at=NOW,
                ends_at=None,
                ended_at=None,
            )
        )


def _client(
    session_factory: sessionmaker[Session],
) -> tuple[TestClient, JwtAccessTokenCodec]:
    clock = FixedClock()
    tokens = JwtAccessTokenCodec(
        signing_key="test-only-signing-key-at-least-32-bytes",
        issuer="smart-ao-test",
        audience="smart-ao-web",
        clock=clock,
    )
    auth_runtime = AuthenticationHttpRuntime.create(
        authentication_service=AuthenticationService(
            session_factory=session_factory,
            password_verifier=UnusedPasswordVerifier(),
            token_generator=UnusedTokenGenerator(),
            clock=clock,
        ),
        session_factory=session_factory,
        access_tokens=tokens,
        csrf_token_generator=UnusedTokenGenerator(),
        clock=clock,
    )
    return (
        TestClient(
            create_app(
                runtime=AppRuntime.create(session_factory=session_factory),
                authentication_runtime=auth_runtime,
            ),
            base_url="https://smart-ao.test",
        ),
        tokens,
    )


def _headers(
    tokens: JwtAccessTokenCodec,
    *,
    identity_id: UUID,
    session_id: UUID,
) -> dict[str, str]:
    return {
        "Authorization": (
            "Bearer "
            f"{tokens.issue(identity_id=identity_id, session_id=session_id, token_version=1)}"
        )
    }


def _request_payload(*, outcome: str = "CONFIRMED", reason_code: str = "SOURCE_REVIEWED") -> dict:
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "confirmation_id": str(uuid4()),
        "expected_confirmation_revision": 0,
        "outcome": outcome,
        "reason_code": reason_code,
    }


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_patron_confirms_requirement_with_real_bearer_and_transactional_success_audit(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    requirement_id, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    client, tokens = _client(session_factory)

    unauthenticated = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        json=_request_payload(),
    )
    assert unauthenticated.status_code == 401

    response = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
        json=_request_payload(),
    )
    assert response.status_code == 201
    assert response.json()["result_code"] == "DCE_REQUIREMENT_CONFIRMED"

    with session_factory() as session:
        audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.action == "dce.requirement.confirm",
                SecurityAuditEventRecord.event_type == "AUTHZ_SUCCEEDED",
            )
        )
    assert audit is not None
    assert audit.outcome == "SUCCEEDED"
    assert audit.resource_id == requirement_id
    assert audit.case_id == case_id


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_collaborator_without_case_assignment_is_denied_and_audited(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="COLLABORATEUR",
    )
    requirement_id, _ = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    client, tokens = _client(session_factory)

    response = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
        json=_request_payload(),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "FORBIDDEN"}
    with session_factory() as session:
        audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.event_type == "AUTHZ_DENIED"
            )
        )
    assert audit is not None
    assert audit.action == "dce.requirement.confirm"


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_collaborator_cannot_mark_requirement_not_applicable(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, session_id = _seed_principal(
        database_engine,
        role="COLLABORATEUR",
    )
    requirement_id, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    _assign_collaborator(
        session_factory,
        tenant_id=tenant_id,
        membership_id=membership_id,
        case_id=case_id,
    )
    client, tokens = _client(session_factory)

    response = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
        json=_request_payload(
            outcome="NOT_APPLICABLE",
            reason_code="PATRON_NOT_APPLICABLE",
        ),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "FORBIDDEN"}
    with session_factory() as session:
        confirmations = session.scalars(sa.select(DceRequirementConfirmationRecord)).all()
        denial_audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.event_type == "AUTHZ_DENIED",
                SecurityAuditEventRecord.reason_code == "DCE_REQUIREMENT_PATRON_REQUIRED",
            )
        )
    assert confirmations == []
    assert denial_audit is not None
    assert denial_audit.case_id == case_id


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_other_tenant_requirement_returns_neutral_not_found_and_is_audited(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    owner_tenant_id, _, _, _ = _seed_principal(database_engine, role="PATRON_ADMIN")
    requirement_id, _ = _seed_requirement_and_case(
        session_factory,
        tenant_id=owner_tenant_id,
    )
    requester_tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    client, tokens = _client(session_factory)

    response = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
        json=_request_payload(),
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    with session_factory() as session:
        audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.tenant_id == requester_tenant_id,
                SecurityAuditEventRecord.event_type == "AUTHZ_DENIED",
                SecurityAuditEventRecord.reason_code == "NOT_FOUND_OR_FORBIDDEN",
            )
        )
    assert audit is not None
    assert audit.resource_id == requirement_id
    assert audit.case_id is None


def _forbidden_response_keys(value: object) -> set[str]:
    forbidden = {
        "storage_key",
        "storage_object_id",
        "original_filename",
        "media_type",
        "byte_size",
        "sha256",
        "corpus_hash",
        "provenance_channel",
        "provenance_reference",
        "provenance_url",
        "excerpt",
        "text",
        "locator_json",
        "confirmed_by_actor_id",
        "price",
        "margin",
        "budget",
        "audit",
    }
    if isinstance(value, dict):
        return (set(value) & forbidden) | set().union(
            *(_forbidden_response_keys(item) for item in value.values())
        )
    if isinstance(value, list):
        return set().union(*(_forbidden_response_keys(item) for item in value)) if value else set()
    return set()


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_patron_requires_real_bearer_and_returns_closed_projection(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    client, tokens = _client(session_factory)

    unauthenticated = client.get(f"/api/v1/cases/{case_id}/dce-reading")
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {"detail": "UNAUTHENTICATED"}

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["case_id"] == str(case_id)
    assert payload["availability"] == "AVAILABLE"
    assert payload["dce"]["lifecycle"] == "ADMITTED"
    assert payload["counters"]["total"] == 1
    assert payload["requirements"][0]["confirmation_outcome"] == "PENDING_HUMAN_CONFIRMATION"
    assert not _forbidden_response_keys(payload)


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_http_projects_real_anchor_only_for_authorized_tenant(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    requirement_id, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    source_bytes = b"X"
    source_sha256 = sha256(source_bytes).hexdigest()
    fragment_text = "X"
    fragment_sha256 = sha256(fragment_text.encode("utf-8")).hexdigest()
    staged_object_id, document_id, extraction_id = uuid4(), uuid4(), uuid4()
    with session_factory.begin() as session:
        requirement = session.get(DceRequirementRecord, requirement_id)
        case = session.get(CaseRecord, case_id)
        assert requirement is not None and case is not None
        observation = session.get(
            DceRcRequirementObservationRecord, requirement.source_observation_id
        )
        assert observation is not None
        fragment_id = observation.fragment_id
        dce_version_id = requirement.dce_version_id
        consultation_id = case.consultation_id
        storage_key = f"dce-staging/{tenant_id}/{staged_object_id}"
        session.add(
            DceStagedObjectRecord(
                id=staged_object_id,
                tenant_id=tenant_id,
                consultation_id=consultation_id,
                storage_key=storage_key,
                original_filename="fixture.txt",
                expected_byte_size=len(source_bytes),
                actual_byte_size=len(source_bytes),
                sha256=source_sha256,
                media_type="text/plain",
                source_channel="MANUAL_UPLOAD",
                state="CONSUMED",
                scan_verdict="CLEAN",
                scanner_name="synthetic-clamd",
                scanner_signature_version="synthetic-signatures",
                scanned_at=NOW,
                rejection_code=None,
                expires_at=NOW + timedelta(days=1),
                consumed_by_dce_version_id=dce_version_id,
                consumed_at=NOW,
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
        session.add(
            DceDocumentRecord(
                id=document_id,
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                storage_object_id=staged_object_id,
                storage_key=storage_key,
                original_filename="fixture.txt",
                media_type="text/plain",
                byte_size=len(source_bytes),
                sha256=source_sha256,
                received_from="MANUAL_UPLOAD",
            )
        )
        session.flush()
        session.add(
            DceDocumentExtractionRecord(
                id=extraction_id,
                tenant_id=tenant_id,
                dce_version_id=dce_version_id,
                dce_document_id=document_id,
                input_sha256=source_sha256,
                extractor_id="smart-ao-native",
                extractor_version="2",
                status="COMPLETED",
                fragment_count=1,
                extracted_char_count=len(fragment_text),
                failure_code=None,
            )
        )
        session.flush()
        session.add(
            DceDocumentExtractionFragmentRecord(
                id=fragment_id,
                tenant_id=tenant_id,
                extraction_id=extraction_id,
                ordinal=1,
                locator_json={"kind": "text_line", "line": 1, "part": 1},
                text=fragment_text,
                text_sha256=fragment_sha256,
            )
        )
        session.add(
            DceRequirementSourceRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                requirement_id=requirement_id,
                source_observation_id=requirement.source_observation_id,
                fragment_id=fragment_id,
                start_byte_offset=0,
                end_byte_offset=1,
            )
        )

    client, tokens = _client(session_factory)
    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 200
    requirement_response = response.json()["requirements"][0]
    anchor = requirement_response["source_anchor"]
    assert anchor["source_anchor_id"] == str(fragment_id)
    assert anchor["dce_version_id"] == str(dce_version_id)
    assert anchor["dce_document_id"] == str(document_id)
    assert anchor["extraction_id"] == str(extraction_id)
    assert anchor["source_sha256"] == source_sha256
    assert anchor["fragment_sha256"] == fragment_sha256
    assert anchor["locator_state"] == "RESOLVED"
    assert anchor["locator"] == {"kind": "text_line", "coordinates": {"line": 1, "part": 1}}
    assert "source_text" not in anchor

    foreign_tenant_id, foreign_identity_id, _, foreign_session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    assert foreign_tenant_id != tenant_id
    foreign_response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=foreign_identity_id, session_id=foreign_session_id),
    )
    assert foreign_response.status_code == 404
    assert foreign_response.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}

    collaborator_id, collaborator_membership_id, collaborator_session_id = (
        uuid4(),
        uuid4(),
        uuid4(),
    )
    with database_engine.begin() as connection:
        connection.execute(
            sa.insert(IdentityRecord).values(
                id=collaborator_id,
                email_normalized=f"collaborator-{collaborator_id}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        connection.execute(
            sa.insert(TenantMembershipRecord).values(
                id=collaborator_membership_id,
                tenant_id=tenant_id,
                identity_id=collaborator_id,
                role="COLLABORATEUR",
                state="ACTIVE",
                activated_at=NOW,
                revoked_at=None,
            )
        )
        connection.execute(
            sa.insert(AuthSessionRecord).values(
                id=collaborator_session_id,
                tenant_id=tenant_id,
                membership_id=collaborator_membership_id,
                identity_id=collaborator_id,
                state="ACTIVE",
                auth_strength="MFA",
                token_version=1,
                issued_at=NOW,
                last_seen_at=NOW,
                expires_at=NOW + timedelta(hours=8),
                absolute_expires_at=NOW + timedelta(hours=12),
                mfa_verified_at=NOW,
                revoked_at=None,
                revoke_reason=None,
            )
        )
    collaborator_response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(
            tokens,
            identity_id=collaborator_id,
            session_id=collaborator_session_id,
        ),
    )
    assert collaborator_response.status_code == 403
    assert collaborator_response.json() == {"detail": "FORBIDDEN"}


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_collaborator_with_matching_scope_is_allowed(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, session_id = _seed_principal(
        database_engine,
        role="COLLABORATEUR",
    )
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    _assign_collaborator(
        session_factory,
        tenant_id=tenant_id,
        membership_id=membership_id,
        case_id=case_id,
        scope_actions=["case.dce.read"],
    )
    client, tokens = _client(session_factory)

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 200
    assert response.json()["availability"] == "AVAILABLE"


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_collaborator_with_scope_missing_read_action_is_denied(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, membership_id, session_id = _seed_principal(
        database_engine,
        role="COLLABORATEUR",
    )
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    _assign_collaborator(
        session_factory,
        tenant_id=tenant_id,
        membership_id=membership_id,
        case_id=case_id,
        scope_actions=["dce.requirement.confirm"],
    )
    client, tokens = _client(session_factory)

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "FORBIDDEN"}


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_collaborator_without_assignment_is_denied_and_audited(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="COLLABORATEUR",
    )
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    client, tokens = _client(session_factory)

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "FORBIDDEN"}
    with session_factory() as session:
        audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.event_type == "AUTHZ_DENIED",
                SecurityAuditEventRecord.action == "case.dce.read",
            )
        )
    assert audit is not None
    assert audit.resource_id == case_id
    assert audit.case_id == case_id


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_other_tenant_is_neutral_and_audited(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    owner_tenant_id, _, _, _ = _seed_principal(database_engine, role="PATRON_ADMIN")
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=owner_tenant_id)
    requester_tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    client, tokens = _client(session_factory)

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    with session_factory() as session:
        audit = session.scalar(
            sa.select(SecurityAuditEventRecord).where(
                SecurityAuditEventRecord.tenant_id == requester_tenant_id,
                SecurityAuditEventRecord.event_type == "AUTHZ_DENIED",
                SecurityAuditEventRecord.action == "case.dce.read",
                SecurityAuditEventRecord.reason_code == "NOT_FOUND_OR_FORBIDDEN",
            )
        )
    assert audit is not None
    assert audit.resource_id == case_id
    assert audit.case_id == case_id


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_case_dce_reading_case_without_applicable_dce_is_rejected(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    _, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    with session_factory.begin() as session:
        case = session.get(CaseRecord, case_id)
        assert case is not None
        case.applicable_dce_version_id = None
        case.dce_freshness = "NO_DCE"
    client, tokens = _client(session_factory)

    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "COMMAND_REJECTED"}


@pytest.mark.api
@pytest.mark.db
@pytest.mark.security
def test_multiple_active_cases_for_one_dce_are_rejected_without_confirmation(
    database_engine: sa.Engine,
    session_factory: sessionmaker[Session],
) -> None:
    tenant_id, identity_id, _, session_id = _seed_principal(
        database_engine,
        role="PATRON_ADMIN",
    )
    requirement_id, case_id = _seed_requirement_and_case(session_factory, tenant_id=tenant_id)
    with session_factory.begin() as session:
        requirement = session.get(DceRequirementRecord, requirement_id)
        case = session.get(CaseRecord, case_id)
        assert requirement is not None and case is not None
        session.add(
            CaseRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                aggregate_revision=1,
                functional_identity_hash="1" * 64,
                title="Affaire concurrente",
                object_description=None,
                business_origin="OPPORTUNITY",
                origin_reference_id=None,
                origin_rationale=None,
                consultation_id=case.consultation_id,
                scope_kind="CUSTOM",
                scope_json={},
                scope_fingerprint="2" * 64,
                applicable_dce_version_id=requirement.dce_version_id,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
                stopped_reason=None,
                stopped_at=None,
                archived_reason=None,
                archived_at=None,
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )
    client, tokens = _client(session_factory)

    response = client.post(
        f"/api/v1/dce-requirements/{requirement_id}/confirmations",
        headers=_headers(tokens, identity_id=identity_id, session_id=session_id),
        json=_request_payload(),
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "COMMAND_REJECTED"}
    with session_factory() as session:
        confirmations = session.scalars(sa.select(DceRequirementConfirmationRecord)).all()
    assert confirmations == []
