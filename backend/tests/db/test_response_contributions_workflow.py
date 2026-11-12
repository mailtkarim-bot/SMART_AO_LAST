"""L08 native response content, exact provenance and human review on synthetic SQL."""

from __future__ import annotations

import hashlib
import os
from dataclasses import replace
from datetime import timedelta
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.enterprise.infrastructure.models import (
    CaseCapabilityProposalRecord,
    EnterpriseCapabilityProofLinkRecord,
    EnterpriseCapabilityRecord,
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationReadinessRecord,
    TechnicalResponseDraftRecord,
)
from app.platform.events.dispatcher import CommandExecutionError
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import ActorKind
from app.platform.security.models import TenantMembershipRecord
from tests.api.test_collaborator_capability_api import (
    NOW,
    _auth_session,
    _client,
    _headers,
)
from tests.application.test_collab_capability import _seed
from tests.application.test_preparation_completeness import _confirm_requirement


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


def real_requirement(session_factory, tmp_path, actor, case_id):
    import asyncio

    from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
    from app.modules.dce.application.requirements import DceRequirementsService
    from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
    from app.modules.dce.infrastructure.models.dce_version import (
        DceDocumentClassificationRecord,
        DceDocumentRecord,
    )
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
    from app.platform.events.dispatcher import CommandDispatcher
    from tests.application.test_dce_rc_analysis import _extract_then_analyze, _stream

    storage = LocalQuarantineStorageAdapter(root=tmp_path / "buyer-source")
    content = b"Lot 6 : le DC1 est obligatoire."
    digest = hashlib.sha256(content).hexdigest()
    document_id, object_id = uuid4(), uuid4()
    key = f"dce-staging/{actor.tenant_id}/{object_id}"
    asyncio.run(storage.write(storage_key=key, stream=_stream(content), max_bytes=100000))
    with session_factory.begin() as session:
        case = session.get(CaseRecord, case_id)
        version = case.applicable_dce_version_id
        session.add(
            DceStagedObjectRecord(
                id=object_id,
                tenant_id=actor.tenant_id,
                consultation_id=case.consultation_id,
                storage_key=key,
                original_filename="RC-synthetique.txt",
                expected_byte_size=len(content),
                actual_byte_size=len(content),
                sha256=digest,
                media_type="text/plain",
                source_channel="MANUAL_UPLOAD",
                state="CONSUMED",
                scan_verdict="CLEAN",
                scanner_name="synthetic",
                scanner_signature_version="1",
                scanned_at=NOW,
                expires_at=NOW + timedelta(days=1),
                consumed_by_dce_version_id=version,
                consumed_at=NOW,
            )
        )
        session.flush()
        session.add(
            DceDocumentRecord(
                id=document_id,
                tenant_id=actor.tenant_id,
                dce_version_id=version,
                storage_object_id=object_id,
                storage_key=key,
                original_filename="RC-synthetique.txt",
                media_type="text/plain",
                byte_size=len(content),
                sha256=digest,
                received_from="MANUAL_UPLOAD",
            )
        )
        session.flush()
        session.add(
            DceDocumentClassificationRecord(
                id=uuid4(),
                tenant_id=actor.tenant_id,
                dce_document_id=document_id,
                classification="RC",
                rationale=None,
                source="SYNTHETIC",
                previous_classification_id=None,
                is_current=True,
                created_by_actor_id=None,
            )
        )
    analysis = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=actor.tenant_id,
        document_id=document_id,
        dce_version_id=version,
    )
    DceRequirementsService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementMaterializationRun": (
                    RecordDceRequirementMaterializationRunHandler()
                )
            },
        ),
    ).materialize(
        tenant_id=actor.tenant_id,
        dce_version_id=version,
        dce_rc_analysis_id=UUID(analysis.aggregate_refs[0]["aggregate_id"]),
        now=NOW,
    )
    with session_factory() as session:
        requirement = session.scalar(
            sa.select(DceRequirementRecord.id)
            .where(
                DceRequirementRecord.tenant_id == actor.tenant_id,
                DceRequirementRecord.dce_version_id == version,
            )
            .order_by(DceRequirementRecord.created_at.desc())
        )
    _confirm_requirement(session_factory, actor=actor, requirement_id=requirement)
    return requirement


@pytest.fixture
def response_case(database_engine, session_factory, tmp_path, monkeypatch):
    with database_engine.begin() as connection:
        connection.execute(sa.text("TRUNCATE TABLE tenants, identities CASCADE"))
    actor, assignment_id, case_id, requirement_id, capability_id, version_id = _seed(
        session_factory
    )
    requirement_id = real_requirement(session_factory, tmp_path, actor, case_id)
    package_id, plan_id = uuid4(), uuid4()
    source_bytes = b"synthetic authorized evidence used only for C10 hash verification\n"
    source_sha256 = hashlib.sha256(source_bytes).hexdigest()
    generated_document_bytes = b"# Synthetic C10 technical response\n"
    generated_document_sha256 = hashlib.sha256(generated_document_bytes).hexdigest()
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
                Capability.PREPARATION_TRANSMIT.value,
                Capability.WORK_TASK_READ.value,
                Capability.CASE_DCE_READ.value,
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
                content_sha256=generated_document_sha256,
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
    from app.bootstrap.application import _build_preparation_storage

    _build_preparation_storage().write(
        storage_key=(
            f"generated-documents/{actor.tenant_id}/{package_id}/{generated_document_id}.md"
        ),
        content=generated_document_bytes,
    )

    _auth_session(session_factory, actor)
    client, tokens = _client(session_factory)
    headers = _headers(tokens, actor)
    return SimpleNamespace(
        actor=actor,
        requirement_id=requirement_id,
        case_id=case_id,
        source=source,
        package_id=package_id,
        plan_id=plan_id,
        generated_document_id=generated_document_id,
        client=client,
        headers=headers,
        tokens=tokens,
    )


def test_human_contribution_native_draft_review_and_source_invalidation(
    session_factory, response_case, monkeypatch
):
    w = response_case
    plan = w.client.post(
        f"/api/v1/preparation/{w.package_id}/response-plans",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_package_revision=0,
            plan_id=str(w.plan_id),
            items=[
                dict(
                    requirement_id=str(w.requirement_id),
                    section_code="METHOD",
                    source_proposal_id=str(w.source.id),
                )
            ],
        ),
    )
    assert plan.status_code == 201, plan.text
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        expected_package_revision=1,
        draft_id=str(uuid4()),
        source_document_id=str(w.generated_document_id),
        section_codes=["METHOD"],
        source_refs=[str(w.source.id)],
        contributions=[
            dict(
                requirement_id=str(w.requirement_id),
                section_code="METHOD",
                content="Nous joignons le DC1 relu. Aucune signature ne sera inventée.",
                missing="Signature du représentant à obtenir.",
            )
        ],
    )
    from app.modules.preparation.infrastructure import contribution_sources

    with monkeypatch.context() as isolated:

        def forbidden_reader(*args, **kwargs):
            pytest.fail("An out-of-plan contribution must not touch source records")

        isolated.setattr(contribution_sources, "contribution_source_snapshots", forbidden_reader)
        outside = dict(
            body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            contributions=[dict(body["contributions"][0], requirement_id=str(uuid4()))],
        )
        refused = w.client.post(
            f"/api/v1/preparation/{w.package_id}/response-drafts", headers=w.headers, json=outside
        )
        assert refused.status_code == 422, refused.text
        assert refused.json() == {"detail": "RESPONSE_PLAN_MISMATCH"}
    draft = w.client.post(
        f"/api/v1/preparation/{w.package_id}/response-drafts", headers=w.headers, json=body
    )
    assert draft.status_code == 201, draft.text
    replay = w.client.post(
        f"/api/v1/preparation/{w.package_id}/response-drafts", headers=w.headers, json=body
    )
    assert replay.status_code == 200, replay.text
    with session_factory() as session:
        rows = session.scalars(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id
            )
        ).all()
        assert len(rows) == 1
        native = rows[0]
        from app.bootstrap.application import _build_preparation_storage

        content = _build_preparation_storage().read(storage_key=native.storage_key)
    text = content.decode()
    assert (
        body["contributions"][0]["content"] in text and body["contributions"][0]["missing"] in text
    )
    assert "Lot 6 : le DC1 est obligatoire." in text
    assert str(w.requirement_id) in text and "fragment_sha256" in text and "UNKNOWN" in text
    assert hashlib.sha256(content).hexdigest() == native.content_sha256
    with session_factory.begin() as session:
        session.get(TenantMembershipRecord, w.actor.membership_id).role = "PATRON_ADMIN"
    patron = replace(
        w.actor,
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
    )
    headers = _headers(w.tokens, patron)
    request = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        review_id=str(uuid4()),
        expected_package_revision=2,
        target_draft_id=str(native.draft_id),
        target_draft_version=native.version,
        target_content_sha256=native.content_sha256,
    )
    reviewed = w.client.post(
        f"/api/v1/preparation/{w.package_id}/reviews", headers=headers, json=request
    )
    assert reviewed.status_code == 201, reviewed.text
    accepted = w.client.post(
        f"/api/v1/preparation/{w.package_id}/reviews/{request['review_id']}/decision",
        headers=headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            review_id=request["review_id"],
            expected_review_revision=1,
            target_draft_id=str(native.draft_id),
            target_draft_version=native.version,
            target_content_sha256=native.content_sha256,
            decision_code="ACCEPTED",
            decision_note="Rédaction relue; signature reste explicitement à obtenir.",
        ),
    )
    assert accepted.status_code == 201, accepted.text
    with session_factory.begin() as session:
        session.get(TenantMembershipRecord, w.actor.membership_id).role = "COLLABORATEUR"
    snapshot_id = uuid4()
    snapshot = w.client.post(
        f"/api/v1/collaborator/preparation/{w.package_id}/snapshots",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_package_revision=4,
            package_id=str(w.package_id),
            snapshot_id=str(snapshot_id),
        ),
    )
    assert snapshot.status_code == 201, snapshot.text
    from app.modules.submission.infrastructure.models import SubmissionPackageAuthorizationRecord
    from app.platform.security.models import PreparationSnapshotRecord

    with session_factory() as session:
        manifest = session.get(PreparationSnapshotRecord, snapshot_id).manifest_json
        assert manifest["response_drafts"][0]["content_sha256"] == native.content_sha256
        assert manifest["response_drafts"][0]["review_state"] == "ACCEPTED"
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(SubmissionPackageAuthorizationRecord)
            )
            == 0
        )
    with session_factory.begin() as session:
        case = session.get(CaseRecord, w.case_id)
        case.dce_freshness = "REVIEW_REQUIRED"
    from app.modules.preparation.application.transmission import PreparationTransmissionHandler

    with (
        session_factory() as session,
        pytest.raises(CommandExecutionError, match="CONTRIBUTION_SOURCE_UNKNOWN"),
    ):
        PreparationTransmissionHandler(
            storage=_build_preparation_storage()
        ).current_c10_review_manifest(
            session=session,
            tenant_id=w.actor.tenant_id,
            package=session.get(PreparationPackageRecord, w.package_id),
        )


def test_contribution_source_blocks_a_concurrent_requirement_confirmation(
    session_factory, response_case
):
    from app.modules.preparation.infrastructure.contribution_sources import (
        contribution_source_snapshots,
    )
    from app.modules.preparation.public.contracts import ResponseContribution

    w = response_case
    with session_factory.begin() as blocker:
        blocker.scalar(
            sa.select(DceRequirementRecord)
            .where(
                DceRequirementRecord.tenant_id == w.actor.tenant_id,
                DceRequirementRecord.id == w.requirement_id,
            )
            .with_for_update()
        )
        version = blocker.get(CaseRecord, w.case_id).applicable_dce_version_id
        with session_factory() as reader, pytest.raises(sa.exc.OperationalError) as refused:
            contribution_source_snapshots(
                reader,
                tenant_id=w.actor.tenant_id,
                case_id=w.case_id,
                dce_version_id=version,
                contributions=[
                    ResponseContribution(
                        requirement_id=w.requirement_id,
                        section_code="METHOD",
                        content="DC1 joint",
                        missing="Signature attendue",
                    )
                ],
            )
        assert refused.value.orig.sqlstate == "55P03"


def test_selected_response_coverage_is_read_only_exact_and_invalidated(
    session_factory, response_case
):
    w = response_case
    plan = w.client.post(
        f"/api/v1/preparation/{w.package_id}/response-plans",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_package_revision=0,
            plan_id=str(w.plan_id),
            items=[
                dict(
                    requirement_id=str(w.requirement_id),
                    section_code="METHOD",
                    source_proposal_id=str(w.source.id),
                )
            ],
        ),
    )
    assert plan.status_code == 201, plan.text
    draft_id = uuid4()
    created = w.client.post(
        f"/api/v1/preparation/{w.package_id}/response-drafts",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_package_revision=1,
            draft_id=str(draft_id),
            source_document_id=str(w.generated_document_id),
            section_codes=["METHOD"],
            source_refs=[str(w.source.id)],
            contributions=[
                dict(
                    requirement_id=str(w.requirement_id),
                    section_code="METHOD",
                    content="Le DC1 sera joint après revue.",
                    missing="Signature à obtenir.",
                )
            ],
        ),
    )
    assert created.status_code == 201, created.text
    with session_factory() as session:
        native = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                TechnicalResponseDraftRecord.draft_id == draft_id,
            )
        )
    selection = dict(draft_id=str(draft_id), version=1, content_sha256=native.content_sha256)
    url = f"/api/v1/preparation/{w.package_id}/response-coverage"
    response = w.client.post(url, headers=w.headers, json=selection)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["selected_response"] == selection
    assert result["coverage"] == result["signature"] == "UNKNOWN"
    assert result["annexes"] == "UNKNOWN"
    assert result["cited_annexes"]
    assert all(item["inclusion"] == "UNKNOWN" for item in result["cited_annexes"])
    assert all(item["requirement_id"] == str(w.requirement_id) for item in result["cited_annexes"])
    point = next(
        row for row in result["requirements"] if row["requirement_id"] == str(w.requirement_id)
    )
    assert point["response_state"] == "TEXT_WITH_GAPS"
    assert point["pieces"][0]["missing"] == "Signature à obtenir."
    assert point["source_anchor"]["source_sha256"]
    assert point["source_excerpt"] == "Lot 6 : le DC1 est obligatoire."
    assert result == w.client.post(url, headers=w.headers, json=selection).json()
    assert response.headers["cache-control"] == "no-store"
    stranger, *_ = _seed(session_factory)
    _auth_session(session_factory, stranger)
    foreign_headers = _headers(w.tokens, stranger)
    foreign = w.client.post(url, headers=foreign_headers, json=selection)
    assert foreign.status_code == 404
    assert foreign.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    assert (
        w.client.post(
            f"/api/v1/collaborator/preparation/{w.package_id}/response-coverage",
            headers=foreign_headers,
            json=selection,
        ).status_code
        == 404
    )
    assert w.client.post(url, json=selection).status_code == 401
    wrong = w.client.post(url, headers=w.headers, json=dict(selection, content_sha256="0" * 64))
    assert wrong.status_code == 422
    assert (
        w.client.post(
            url.replace(str(w.package_id), str(uuid4())), headers=w.headers, json=selection
        ).status_code
        == 404
    )
    with session_factory() as session:
        assert session.get(PreparationPackageRecord, w.package_id).aggregate_revision == 2
    with session_factory.begin() as session:
        session.get(CaseRecord, w.case_id).dce_freshness = "REVIEW_REQUIRED"
    stale = w.client.post(url, headers=w.headers, json=selection)
    assert stale.status_code == 422

    # A replacement source cannot inherit the old exact response's coverage read.
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from tests.db.test_candidate_retrieval_sql import _clone

    with session_factory.begin() as session:
        case = session.get(CaseRecord, w.case_id)
        old_version = session.get(DceVersionRecord, case.applicable_dce_version_id)
        replacement_id = uuid4()
        session.add(
            _clone(
                old_version,
                id=replacement_id,
                predecessor_dce_version_id=old_version.id,
                corpus_hash="d" * 64,
            )
        )
        session.flush()
        case.applicable_dce_version_id = replacement_id
        case.dce_freshness = "CURRENT"
    rectified = w.client.post(url, headers=w.headers, json=selection)
    assert rectified.status_code == 422
    assert rectified.json() == {"detail": "CONTRIBUTION_SOURCE_UNKNOWN"}
    with session_factory() as session:
        assert session.get(PreparationPackageRecord, w.package_id).aggregate_revision == 2
        assert (
            session.scalar(
                sa.select(TechnicalResponseDraftRecord.content_sha256).where(
                    TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                    TechnicalResponseDraftRecord.draft_id == draft_id,
                )
            )
            == native.content_sha256
        )
