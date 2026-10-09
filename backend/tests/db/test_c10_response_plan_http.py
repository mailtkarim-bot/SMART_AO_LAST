"""C10 response-plan API persists exact DCE and reusable-source lineage locally."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
    DceRequirementConfirmationRecord,
)
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.enterprise.infrastructure.models import (
    CaseCapabilityProposalRecord,
    EnterpriseCapabilityProofLinkRecord,
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationReadinessRecord,
    PreparationResponsePlanRecord,
    TechnicalResponseDraftRecord,
)
from app.platform.persistence.models import DomainEventRecord
from app.platform.security.capabilities import Capability
from app.platform.security.models import PreparationSnapshotRecord, TenantMembershipRecord
from sqlalchemy.exc import IntegrityError, ProgrammingError
from tests.api.test_collaborator_capability_api import (
    NOW,
    _auth_session,
    _client,
    _headers,
)
from tests.application.test_collab_capability import _seed


def _proposal(
    *,
    tenant_id,
    case_id,
    assignment_id,
    membership_id,
    requirement_id,
    capability_id,
    capability_version_id,
    validity_state="CURRENT",
):
    proposal_id = uuid4()
    return CaseCapabilityProposalRecord(
        id=proposal_id,
        tenant_id=tenant_id,
        case_id=case_id,
        assignment_id=assignment_id,
        capability_id=capability_id,
        capability_version_id=capability_version_id,
        requirement_id=requirement_id,
        task_id=None,
        state="PROPOSED",
        validity_state=validity_state,
        justification="Fixture synthétique de qualification.",
        source_locator=None,
        functional_key=f"{case_id}:{capability_version_id}:{requirement_id}:",
        proposed_by_membership_id=membership_id,
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=None,
    )


def test_response_plan_is_versioned_scope_checked_and_preserves_unknown(
    database_engine,
    session_factory,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    package_id, plan_id = uuid4(), uuid4()
    source_bytes = b"synthetic authorized evidence used only for C10 hash verification\n"
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    quarantine_root = tmp_path / "private-quarantine"
    monkeypatch.setenv("SMART_AO_DCE_QUARANTINE_ROOT", str(quarantine_root))
    source = _proposal(
        tenant_id=actor.tenant_id,
        case_id=case_id,
        assignment_id=assignment_id,
        membership_id=actor.membership_id,
        requirement_id=requirement_id,
        capability_id=capability_id,
        capability_version_id=version_id,
    )
    with session_factory.begin() as session:
        assignment = session.get(CaseAssignmentRecord, assignment_id)
        assignment.scope_actions_json = sorted(
            {
                *assignment.scope_actions_json,
                Capability.WORK_TASK_WRITE.value,
                Capability.PREPARATION_DOCUMENT_WRITE.value,
            }
        )
        session.add(
            PreparationPackageRecord(
                id=package_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                assignment_id=assignment_id,
                dce_version_id=session.scalar(
                    sa.select(CaseRecord.applicable_dce_version_id).where(
                        CaseRecord.tenant_id == actor.tenant_id,
                        CaseRecord.id == case_id,
                    )
                ),
                state="IN_PREPARATION",
                aggregate_revision=0,
                created_by_actor_id=actor.actor_id,
                membership_id=actor.membership_id,
            )
        )
        session.add(source)
        company_id = session.scalar(
            sa.select(EnterpriseCapabilityRecord.company_id).where(
                EnterpriseCapabilityRecord.tenant_id == actor.tenant_id,
                EnterpriseCapabilityRecord.id == capability_id,
            )
        )
        storage_object_id, document_id = uuid4(), uuid4()
        session.add(
            EnterpriseDocumentUploadRecord(
                id=storage_object_id,
                tenant_id=actor.tenant_id,
                company_id=company_id,
                document_id=document_id,
                document_kind="INSURANCE",
                document_label="Synthetic clean proof",
                original_filename="synthetic.pdf",
                storage_key=f"{actor.tenant_id}/{document_id}/{storage_object_id}.bin",
                expected_byte_size=len(source_bytes),
                actual_byte_size=len(source_bytes),
                sha256=source_sha256,
                media_type="application/pdf",
                state="CLEAN",
                scan_verdict="CLEAN",
                scanner_name="test-scanner",
                scanner_signature_version="test-1",
                scanned_at=NOW,
                expires_at=NOW + timedelta(hours=1),
                created_by_membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.add(
            EnterpriseDocumentRecord(
                id=document_id,
                tenant_id=actor.tenant_id,
                company_id=company_id,
                document_kind="INSURANCE",
                document_label="Synthetic clean proof",
                storage_object_id=storage_object_id,
                original_filename="synthetic.pdf",
                issued_at=NOW - timedelta(days=1),
                expires_at=NOW + timedelta(days=365),
                sha256=source_sha256,
                verification_status="VALIDATED",
                registered_by_membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.add(
            EnterpriseCapabilityProofLinkRecord(
                id=uuid4(),
                tenant_id=actor.tenant_id,
                capability_version_id=version_id,
                document_id=document_id,
                relation_label="SUPPORTS_CAPABILITY",
            )
        )
        readiness_id, generated_document_id = uuid4(), uuid4()
        session.add(
            PreparationReadinessRecord(
                id=readiness_id,
                tenant_id=actor.tenant_id,
                package_id=package_id,
                revision=1,
                state="READY",
                blocker_codes_json=[],
                warning_codes_json=[],
                checked_requirement_count=1,
                checked_task_count=0,
                input_manifest_sha256="c" * 64,
                evaluator_id="c10-synthetic",
                evaluator_version="1",
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.add(
            GeneratedTechnicalDocumentRecord(
                id=generated_document_id,
                tenant_id=actor.tenant_id,
                package_id=package_id,
                readiness_id=readiness_id,
                version=1,
                document_kind="TECHNICAL_RESPONSE",
                state="GENERATED",
                content_sha256="d" * 64,
                storage_key=f"generated-documents/{actor.tenant_id}/{package_id}/{generated_document_id}.md",
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                correlation_id=None,
            )
        )

    source_path = quarantine_root / f"{actor.tenant_id}/{document_id}/{storage_object_id}.bin"
    source_path.parent.mkdir(parents=True, mode=0o700)
    os.chmod(source_path.parent, 0o700)
    source_path.write_bytes(source_bytes)
    os.chmod(source_path, 0o600)

    _auth_session(session_factory, actor)
    client, tokens = _client(session_factory)
    headers = _headers(tokens, actor)
    path = f"/api/v1/preparation/{package_id}/response-plans"
    first_body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "expected_package_revision": 0,
        "plan_id": str(plan_id),
        "items": [
            {
                "requirement_id": str(requirement_id),
                "section_code": "RESOURCES",
                "source_proposal_id": str(source.id),
            }
        ],
    }

    created = client.post(path, json=first_body, headers=headers)
    replayed = client.post(path, json=first_body, headers=headers)
    assert created.status_code == 201, created.text
    assert replayed.status_code == 200, replayed.text
    assert replayed.json()["replayed"] is True
    assert created.json()["result_code"] == "PREPARATION_RESPONSE_PLAN_CREATED"
    first_projection = client.get(path, headers=headers)
    assert first_projection.status_code == 200, first_projection.text
    first_plan = first_projection.json()["plans"][0]
    assert first_plan["version"] == 1
    assert first_plan["dce_version_id"]
    assert first_plan["state"] == "UNKNOWN"
    assert first_plan["content"]["items"][0]["source_evidence_state"] == "CURRENT"
    assert first_plan["content"]["items"][0]["source_validity_state"] == "CURRENT"
    assert first_plan["content"]["items"][0]["requirement_state"] == "UNKNOWN"
    assert first_projection.headers["Cache-Control"] == "no-store"
    assert "document_id" not in first_projection.text
    assert "storage_key" not in first_projection.text
    assert "a" * 64 not in first_projection.text
    assert "sha256" not in created.text

    confirmation_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            DceRequirementConfirmationRecord(
                id=confirmation_id,
                tenant_id=actor.tenant_id,
                requirement_id=requirement_id,
                revision=1,
                previous_confirmation_id=None,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
                confirmed_by_actor_id=actor.actor_id,
            )
        )
        session.flush()
        session.add(
            DceRequirementConfirmationCurrentRecord(
                requirement_id=requirement_id,
                tenant_id=actor.tenant_id,
                confirmation_id=confirmation_id,
                revision=1,
                outcome="CONFIRMED",
            )
        )

    second_body = {
        **first_body,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "expected_package_revision": 1,
        "items": [
            {
                "requirement_id": str(requirement_id),
                "section_code": "RESOURCES",
                "source_proposal_id": str(source.id),
            }
        ],
    }
    second = client.post(path, json=second_body, headers=headers)
    assert second.status_code == 201, second.text
    second_projection = client.get(path, headers=headers)
    assert second_projection.status_code == 200, second_projection.text
    second_plan = second_projection.json()["plans"][1]
    assert second_plan["version"] == 2
    assert second_plan["state"] == "SOURCES_CURRENT"
    assert second_plan["content"]["items"][0]["requirement_state"] == "CONFIRMED"
    assert second_plan["content"]["items"][0]["source_evidence_state"] == "CURRENT"

    draft_path = f"/api/v1/preparation/{package_id}/response-drafts"
    draft_body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
        "draft_id": str(uuid4()),
        "expected_package_revision": 2,
        "source_document_id": str(generated_document_id),
        "section_codes": ["RESOURCES"],
        "source_refs": [str(source.id)],
    }
    draft_created = client.post(draft_path, json=draft_body, headers=headers)
    assert draft_created.status_code == 201, draft_created.text
    assert draft_created.json()["result_code"] == "TECHNICAL_RESPONSE_DRAFT_CREATED"
    with session_factory() as session:
        draft = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == actor.tenant_id
            )
        )
        assert draft is not None
        assert (draft.response_plan_id, draft.response_plan_version) == (plan_id, 2)
        draft_storage_key = draft.storage_key
        draft_hash = draft.content_sha256
    generated_draft = (quarantine_root / draft_storage_key).read_bytes()
    assert hashlib.sha256(generated_draft).hexdigest() == draft_hash
    assert b"Plan de r\xc3\xa9ponse \xe2\x80\x94 r\xc3\xa9vision 2" in generated_draft
    assert b"Brouillon \xe2\x80\x94 version 1" in generated_draft
    assert b"Qualification test" in generated_draft
    assert b"Version actuelle" in generated_draft
    assert b"1 pi\xc3\xa8ce(s) relue(s)" in generated_draft
    assert str(requirement_id).encode() not in generated_draft
    assert str(source.id).encode() not in generated_draft
    assert source_sha256.encode() not in generated_draft

    with session_factory.begin() as session:
        assignment = session.get(CaseAssignmentRecord, assignment_id)
        assignment.scope_actions_json = sorted(
            {
                *assignment.scope_actions_json,
                Capability.PREPARATION_TRANSMIT.value,
            }
        )
    snapshot_path = f"/api/v1/collaborator/preparation/{package_id}/snapshots"
    blocked_snapshot = client.post(
        snapshot_path,
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 3,
            "package_id": str(package_id),
            "snapshot_id": str(uuid4()),
        },
        headers=headers,
    )
    assert blocked_snapshot.status_code == 422, blocked_snapshot.text
    assert blocked_snapshot.json() == {"detail": "RESPONSE_DRAFT_REVIEW_REQUIRED"}
    with session_factory() as session:
        snapshot_count = session.scalar(
            sa.select(sa.func.count()).select_from(PreparationSnapshotRecord)
        )
        assert snapshot_count == 0

    with session_factory.begin() as session:
        membership = session.get(TenantMembershipRecord, actor.membership_id)
        membership.role = "PATRON_ADMIN"
    drafts_path = f"/api/v1/preparation/{package_id}/response-drafts"
    review_path = f"/api/v1/preparation/{package_id}/reviews"
    draft_object = quarantine_root / draft_storage_key
    draft_object.write_bytes(generated_draft + b"tampered")
    tampered_read = client.get(drafts_path, headers=headers)
    assert tampered_read.status_code == 422
    assert tampered_read.json() == {"detail": "RESPONSE_DRAFT_UNKNOWN"}
    draft_object.write_bytes(generated_draft)
    patron_drafts = client.get(drafts_path, headers=headers)
    assert patron_drafts.status_code == 200, patron_drafts.text
    patron_draft = patron_drafts.json()["drafts"][0]
    assert patron_draft["content_sha256"] == draft_hash
    assert hashlib.sha256(patron_draft["content"].encode("utf-8")).hexdigest() == draft_hash
    assert patron_drafts.headers["Cache-Control"] == "no-store"
    review_id = uuid4()
    requested = client.post(
        review_path,
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 3,
            "review_id": str(review_id),
            "target_draft_id": str(patron_draft["draft_id"]),
            "target_draft_version": patron_draft["version"],
            "target_content_sha256": draft_hash,
        },
        headers=headers,
    )
    duplicate_review = client.post(
        review_path,
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 4,
            "review_id": str(uuid4()),
            "target_draft_id": patron_draft["draft_id"],
            "target_draft_version": patron_draft["version"],
            "target_content_sha256": draft_hash,
        },
        headers=headers,
    )
    assert duplicate_review.status_code == 422
    assert duplicate_review.json() == {"detail": "REVIEW_ALREADY_EXISTS"}
    wrong_hash = client.post(
        review_path,
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 4,
            "review_id": str(uuid4()),
            "target_draft_id": patron_draft["draft_id"],
            "target_draft_version": patron_draft["version"],
            "target_content_sha256": "f" * 64,
        },
        headers=headers,
    )
    assert wrong_hash.status_code == 422
    assert wrong_hash.json() == {"detail": "RESPONSE_DRAFT_UNKNOWN"}
    assert requested.status_code == 201, requested.text
    returned = client.post(
        f"{review_path}/{review_id}/decision",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "review_id": str(review_id),
            "expected_review_revision": 1,
            "target_document_id": str(generated_document_id),
            "target_draft_id": patron_draft["draft_id"],
            "target_draft_version": patron_draft["version"],
            "target_content_sha256": draft_hash,
            "decision_code": "CORRECTIONS_REQUIRED",
            "decision_note": "Préciser la séquence de méthode.",
        },
        headers=headers,
    )
    assert returned.status_code == 201, returned.text
    corrected_content = (
        "# Méthode révisée\n\nLa séquence et les contrôles sont décrits explicitement."
    )
    correction = client.post(
        f"{review_path}/{review_id}/corrections",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "review_id": str(review_id),
            "target_document_id": str(generated_document_id),
            "target_draft_id": patron_draft["draft_id"],
            "target_draft_version": patron_draft["version"],
            "target_content_sha256": draft_hash,
            "correction_code": "SECTION_INCOMPLETE",
            "instruction": "Compléter la description de méthode.",
            "corrected_content": corrected_content,
        },
        headers=headers,
    )
    assert correction.status_code == 201, correction.text
    with session_factory() as session:
        emitted_events = set(
            session.scalars(
                sa.select(DomainEventRecord.event_type).where(
                    DomainEventRecord.tenant_id == actor.tenant_id
                )
            ).all()
        )
    assert {
        "TechnicalResponseDraftCorrected",
        "PreparationReviewRequested",
        "PreparationCorrectionAdded",
    } <= emitted_events
    patron_drafts = client.get(drafts_path, headers=headers)
    assert patron_drafts.status_code == 200, patron_drafts.text
    versions = patron_drafts.json()["drafts"]
    corrected_draft = next(item for item in versions if item["version"] == 2)
    assert corrected_draft["content"] == corrected_content
    assert (
        corrected_draft["content_sha256"]
        == hashlib.sha256(corrected_content.encode("utf-8")).hexdigest()
    )
    projected_reviews = client.get(review_path, headers=headers)
    assert projected_reviews.status_code == 200, projected_reviews.text
    current_review = projected_reviews.json()["reviews"][0]
    assert current_review["target_draft_version"] == 2
    assert current_review["target_content_sha256"] == corrected_draft["content_sha256"]
    assert current_review["state"] == "REQUESTED"
    assert current_review["corrections"][0]["target_draft_version"] == 1
    accepted = client.post(
        f"{review_path}/{review_id}/decision",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "review_id": str(review_id),
            "expected_review_revision": 3,
            "target_document_id": str(generated_document_id),
            "target_draft_id": patron_draft["draft_id"],
            "target_draft_version": 2,
            "target_content_sha256": corrected_draft["content_sha256"],
            "decision_code": "ACCEPTED",
        },
        headers=headers,
    )
    assert accepted.status_code == 201, accepted.text
    with session_factory.begin() as session:
        membership = session.get(TenantMembershipRecord, actor.membership_id)
        membership.role = "COLLABORATEUR"
    snapshot_id = uuid4()
    created_snapshot = client.post(
        snapshot_path,
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 7,
            "package_id": str(package_id),
            "snapshot_id": str(snapshot_id),
        },
        headers=headers,
    )
    assert created_snapshot.status_code == 201, created_snapshot.text
    with session_factory() as session:
        snapshot = session.get(PreparationSnapshotRecord, snapshot_id)
        assert snapshot is not None
        assert snapshot.manifest_json["response_drafts"] == [
            {
                "draft_id": str(patron_draft["draft_id"]),
                "version": 2,
                "content_sha256": corrected_draft["content_sha256"],
                "response_plan_id": str(plan_id),
                "response_plan_version": 2,
                "review_id": str(review_id),
                "review_revision": 4,
                "review_state": "ACCEPTED",
            }
        ]
    transmission_id = uuid4()
    transmitted = client.post(
        f"/api/v1/collaborator/preparation/{package_id}/transmissions",
        json={
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "correlation_id": str(uuid4()),
            "expected_package_revision": 8,
            "package_id": str(package_id),
            "snapshot_id": str(snapshot_id),
            "transmission_id": str(transmission_id),
        },
        headers=headers,
    )
    assert transmitted.status_code == 201, transmitted.text
    with session_factory.begin() as session:
        membership = session.get(TenantMembershipRecord, actor.membership_id)
        membership.role = "PATRON_ADMIN"
    receipt_client, receipt_tokens = _client(session_factory)
    receipt_headers = _headers(receipt_tokens, actor)
    deliveries = receipt_client.get(
        f"/api/v1/preparation/{package_id}/transmissions", headers=receipt_headers
    )
    assert deliveries.status_code == 200, deliveries.text
    delivery = deliveries.json()["deliveries"][0]
    assert delivery["snapshot_id"] == str(snapshot_id)
    assert delivery["snapshot_version"] == 1
    assert delivery["snapshot_manifest_sha256"]
    assert (
        delivery["snapshot_manifest"]["response_drafts"][0]["content_sha256"]
        == (corrected_draft["content_sha256"])
    )
    assert delivery["transmission_id"] == str(transmission_id)
    assert delivery["snapshot_receipt"]["aggregate_refs"][0] == {
        "aggregate_type": "PreparationSnapshot",
        "aggregate_id": str(snapshot_id),
        "aggregate_revision": 1,
    }
    assert delivery["transmission_receipt"]["aggregate_refs"][0]["aggregate_revision"] == 9
    assert delivery["transmission_receipt"]["result_code"] == ("PREPARATION_TRANSMITTED_TO_PATRON")
    assert deliveries.headers["Cache-Control"] == "no-store"
    assert "external_submission" not in deliveries.text
    with session_factory.begin() as session:
        membership = session.get(TenantMembershipRecord, actor.membership_id)
        membership.role = "COLLABORATEUR"
    collaborator_receipt_read = receipt_client.get(
        f"/api/v1/preparation/{package_id}/transmissions", headers=receipt_headers
    )
    assert collaborator_receipt_read.status_code == 403

    source_path.write_bytes(b"altered after CLEAN admission")
    changed_source = client.post(
        draft_path,
        json={
            **draft_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "draft_id": str(uuid4()),
            "expected_package_revision": 9,
        },
        headers=headers,
    )
    assert changed_source.status_code == 422, changed_source.text
    assert changed_source.json() == {"detail": "RESPONSE_PLAN_UNKNOWN"}
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(TechnicalResponseDraftRecord))
            == 2
        )
        package = session.scalar(
            sa.select(PreparationPackageRecord).where(
                PreparationPackageRecord.tenant_id == actor.tenant_id,
                PreparationPackageRecord.id == package_id,
            )
        )
        assert package.aggregate_revision == 9
    source_path.write_bytes(source_bytes)
    source_path.unlink()
    unavailable_source = client.post(
        draft_path,
        json={
            **draft_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "draft_id": str(uuid4()),
            "expected_package_revision": 9,
        },
        headers=headers,
    )
    assert unavailable_source.status_code == 422, unavailable_source.text
    assert unavailable_source.json() == {"detail": "RESPONSE_PLAN_UNKNOWN"}
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(TechnicalResponseDraftRecord))
            == 2
        )
    source_path.write_bytes(source_bytes)
    monkeypatch.setattr(
        "app.modules.preparation.application.review.contains_forbidden_text",
        lambda content: True,
    )
    financial_content = client.post(
        draft_path,
        json={
            **draft_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "draft_id": str(uuid4()),
            "expected_package_revision": 9,
        },
        headers=headers,
    )
    assert financial_content.status_code == 422, financial_content.text
    assert financial_content.json() == {"detail": "FINANCIAL_DATA_FORBIDDEN"}
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(TechnicalResponseDraftRecord))
            == 2
        )

    third_body = {
        **second_body,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "expected_package_revision": 9,
        "items": [
            {
                "requirement_id": str(requirement_id),
                "section_code": "RESOURCES",
                "source_proposal_id": None,
            }
        ],
    }
    third = client.post(path, json=third_body, headers=headers)
    assert third.status_code == 201, third.text
    third_projection = client.get(path, headers=headers)
    assert third_projection.status_code == 200, third_projection.text
    third_plan = third_projection.json()["plans"][2]
    assert third_plan["version"] == 3
    assert third_plan["state"] == "UNKNOWN"
    assert third_plan["content"]["items"][0]["source_evidence_state"] == "UNKNOWN"

    duplicate_item = {
        "requirement_id": str(requirement_id),
        "section_code": "RESOURCES",
        "source_proposal_id": None,
    }
    duplicate = client.post(
        path,
        json={
            **third_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_package_revision": 10,
            "items": [duplicate_item, duplicate_item],
        },
        headers=headers,
    )
    assert duplicate.status_code == 422

    absent = client.post(
        path,
        json={
            **third_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_package_revision": 10,
            "items": [
                {
                    "requirement_id": str(requirement_id),
                    "section_code": "RESOURCES",
                    "source_proposal_id": str(uuid4()),
                }
            ],
        },
        headers=headers,
    )
    assert absent.status_code == 404
    assert absent.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}

    expired_version_id = uuid4()
    expired_proposal = _proposal(
        tenant_id=actor.tenant_id,
        case_id=case_id,
        assignment_id=assignment_id,
        membership_id=actor.membership_id,
        requirement_id=requirement_id,
        capability_id=capability_id,
        capability_version_id=expired_version_id,
        validity_state="EXPIRED",
    )
    with session_factory.begin() as session:
        session.add(
            EnterpriseCapabilityVersionRecord(
                id=expired_version_id,
                tenant_id=actor.tenant_id,
                capability_id=capability_id,
                version_number=2,
                title="Version expirée",
                description="Fixture synthétique expirée.",
                valid_from=NOW - timedelta(days=30),
                valid_until=NOW - timedelta(days=1),
                usage_scope="Réponse synthétique",
                created_by_membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        session.flush()
        session.add(expired_proposal)
    expired = client.post(
        path,
        json={
            **third_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_package_revision": 10,
            "items": [
                {
                    "requirement_id": str(requirement_id),
                    "section_code": "RESOURCES",
                    "source_proposal_id": str(expired_proposal.id),
                }
            ],
        },
        headers=headers,
    )
    assert expired.status_code == 422
    assert expired.json() == {"detail": "REUSABLE_FACT_EXPIRED"}

    plans = client.get(path, headers=headers)
    assert plans.status_code == 200, plans.text
    assert [item["version"] for item in plans.json()["plans"]] == [1, 2, 3]
    plan = plans.json()["plans"][0]
    canonical = json.dumps(
        plan["content"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert plan["plan_sha256"] == hashlib.sha256(canonical).hexdigest()
    with session_factory() as session:
        expected_dce_version_id = session.scalar(
            sa.select(PreparationPackageRecord.dce_version_id).where(
                PreparationPackageRecord.tenant_id == actor.tenant_id,
                PreparationPackageRecord.id == package_id,
            )
        )
    assert plan["dce_version_id"] == str(expected_dce_version_id)
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(PreparationResponsePlanRecord))
            == 3
        )
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(TechnicalResponseDraftRecord))
            == 2
        )
        stored_plan = session.scalar(
            sa.select(PreparationResponsePlanRecord).where(
                PreparationResponsePlanRecord.tenant_id == actor.tenant_id,
                PreparationResponsePlanRecord.plan_id == plan_id,
                PreparationResponsePlanRecord.version == 1,
            )
        )
        assert stored_plan.source_evidence_json == [
            {
                "source_proposal_id": str(source.id),
                "source_capability_version_id": str(version_id),
                "source_evidence_state": "CURRENT",
                "proofs": [{"document_id": str(document_id), "sha256": source_sha256}],
            }
        ]
        evidence_bytes = json.dumps(
            stored_plan.source_evidence_json,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        assert stored_plan.source_evidence_sha256 == hashlib.sha256(evidence_bytes).hexdigest()

    (
        foreign_actor,
        foreign_assignment,
        foreign_case,
        foreign_requirement,
        foreign_capability,
        foreign_version,
    ) = _seed(session_factory)
    foreign_proposal = _proposal(
        tenant_id=foreign_actor.tenant_id,
        case_id=foreign_case,
        assignment_id=foreign_assignment,
        membership_id=foreign_actor.membership_id,
        requirement_id=foreign_requirement,
        capability_id=foreign_capability,
        capability_version_id=foreign_version,
    )
    with session_factory.begin() as session:
        session.add(foreign_proposal)
    _auth_session(session_factory, foreign_actor)
    foreign_client, foreign_tokens = _client(session_factory)
    foreign_headers = _headers(foreign_tokens, foreign_actor)
    with session_factory.begin() as session:
        session.get(TenantMembershipRecord, foreign_actor.membership_id).role = "PATRON_ADMIN"
    assert (
        foreign_client.get(
            f"/api/v1/preparation/{package_id}/transmissions", headers=foreign_headers
        ).status_code
        == 404
    )
    with session_factory.begin() as session:
        session.get(TenantMembershipRecord, foreign_actor.membership_id).role = "COLLABORATEUR"
    assert foreign_client.get(path, headers=foreign_headers).status_code == 404
    foreign = client.post(
        path,
        json={
            **third_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_package_revision": 10,
            "items": [
                {
                    "requirement_id": str(requirement_id),
                    "section_code": "RESOURCES",
                    "source_proposal_id": str(foreign_proposal.id),
                }
            ],
        },
        headers=headers,
    )
    assert foreign.status_code == absent.status_code
    assert foreign.json() == absent.json()

    with session_factory.begin() as session:
        case = session.get(CaseRecord, case_id)
        current_dce = session.get(DceVersionRecord, case.applicable_dce_version_id)
        replacement_id = uuid4()
        session.add(
            DceVersionRecord(
                id=replacement_id,
                tenant_id=actor.tenant_id,
                aggregate_revision=0,
                consultation_id=current_dce.consultation_id,
                corpus_hash="f" * 64,
                predecessor_dce_version_id=current_dce.id,
                provenance_channel="TEST",
                provenance_reference="replacement-test",
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
                created_by_actor_id=actor.actor_id,
                updated_by_actor_id=actor.actor_id,
            )
        )
        session.flush()
        case.applicable_dce_version_id = replacement_id
    stale_dce = client.post(
        path,
        json={
            **third_body,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "expected_package_revision": 10,
        },
        headers=headers,
    )
    assert stale_dce.status_code == 409
    assert stale_dce.json() == {"detail": "VERSION_CONFLICT"}

    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(PreparationResponsePlanRecord))
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(PreparationPackageRecord)
                .where(PreparationPackageRecord.id == package_id)
            )
            == 1
        )
    with pytest.raises((IntegrityError, ProgrammingError)), session_factory.begin() as session:
        session.execute(
            sa.update(PreparationResponsePlanRecord)
            .where(PreparationResponsePlanRecord.tenant_id == actor.tenant_id)
            .values(state="UNKNOWN")
        )
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))
