"""Synthetic local document metadata -> exact capability version -> assigned proposal.

CLEAN and human validation are fixtures, never real antivirus or external confirmation.
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
from threading import Barrier
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.enterprise.application.enterprise_capability_commands import (
    AddEnterpriseCapabilityVersionCommand,
    CreateEnterpriseCapabilityCommand,
)
from app.modules.enterprise.infrastructure.models import (
    CaseCapabilityGapRecord,
    CaseCapabilityProposalRecord,
    EnterpriseCapabilityProofLinkRecord,
    EnterpriseCapabilityRecord,
    EnterpriseCapabilityVersionRecord,
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorKind
from app.platform.security.models import (
    CaseAssignmentRecord,
    IdentityRecord,
    TenantMembershipRecord,
)
from tests.api.test_collaborator_capability_api import _auth_session, _client, _headers
from tests.application.test_collab_capability import (
    NOW,
    _clone_requirement_on_same_dce,
    _seed,
)
from tests.application.test_enterprise_capability_foundation import (
    _document_command,
    _seed_clean_upload,
    _services,
)


def _patron(session_factory, collaborator):
    identity_id, membership_id = uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(
            IdentityRecord(
                id=identity_id,
                email_normalized=f"synthetic-{identity_id}@example.test",
                lifecycle="ACTIVE",
                email_verified_at=NOW,
            )
        )
        session.add(
            TenantMembershipRecord(
                id=membership_id,
                tenant_id=collaborator.tenant_id,
                identity_id=identity_id,
                role="PATRON_ADMIN",
                state="ACTIVE",
                activated_at=NOW,
            )
        )
    return replace(
        collaborator,
        actor_id=identity_id,
        identity_id=identity_id,
        membership_id=membership_id,
        session_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assignment_scopes=(),
        assigned_case_ids=frozenset(),
    )


@pytest.mark.parametrize(
    "proof_kind,expected",
    [
        ("valid", "CURRENT"),
        ("expired", "EXPIRED"),
        ("absent", "UNKNOWN"),
        ("pending", "UNKNOWN"),
        ("hash_mismatch", "UNKNOWN"),
        ("missing_upload", "UNKNOWN"),
        ("quarantined", "UNKNOWN"),
        ("future_document", "UNKNOWN"),
        ("version_expired", "EXPIRED"),
        ("future_version", "UNKNOWN"),
        ("inactive", "UNKNOWN"),
        ("mixed_pending", "UNKNOWN"),
        ("mixed_expired", "EXPIRED"),
        ("unsupported_relation", "UNKNOWN"),
    ],
)
def test_exp05_document_version_proposal_chain_is_read_only_scoped_and_unknown_without_proof(
    session_factory,
    proof_kind,
    expected,
    monkeypatch,
):
    from app.interfaces.http.routes import collaborator_capabilities as route

    class RecipeClock:
        @staticmethod
        def now(tz=None):
            return NOW

    monkeypatch.setattr(route, "datetime", RecipeClock)
    collaborator, assignment_id, case_id, requirement_id, initial_capability, _ = _seed(
        session_factory
    )
    patron = _patron(session_factory, collaborator)
    library, capabilities = _services(session_factory)
    with session_factory() as session:
        company_id = session.get(EnterpriseCapabilityRecord, initial_capability).company_id
    content = b"%PDF-1.4\nX"
    digest = sha256(content).hexdigest()
    proof_ids: tuple[UUID, ...] = ()
    if proof_kind != "absent":
        document = _document_command(company_id=company_id, document_id=uuid4()).model_copy(
            update={
                "document_label": "SYNTHETIC LOCAL ONLY",
                "sha256": digest,
                "verification_status": "PENDING" if proof_kind == "pending" else "VALIDATED",
                "issued_at": NOW + timedelta(days=1)
                if proof_kind == "future_document"
                else NOW - timedelta(days=2),
                "expires_at": NOW + timedelta(days=-1 if proof_kind == "expired" else 365),
            }
        )
        _seed_clean_upload(session_factory, patron, document)
        # The registered identity must keep the digest owned by the CLEAN upload, not the caller.
        library.register_document(
            actor=patron, command=document.model_copy(update={"sha256": "f" * 64}), now=NOW
        )
        proof_ids = (document.document_id,)
    if proof_kind in {"mixed_pending", "mixed_expired"}:
        second = _document_command(company_id=company_id, document_id=uuid4()).model_copy(
            update={
                "expected_revision": 1,
                "sha256": sha256(b"%PDF-1.4\nY").hexdigest(),
                "document_label": "SECOND SYNTHETIC LOCAL ONLY",
                "issued_at": NOW - timedelta(days=2),
                "expires_at": NOW + timedelta(days=-1 if proof_kind == "mixed_expired" else 365),
                "verification_status": "PENDING" if proof_kind == "mixed_pending" else "VALIDATED",
            }
        )
        _seed_clean_upload(session_factory, patron, second)
        library.register_document(actor=patron, command=second.model_copy(deep=True), now=NOW)
        proof_ids += (second.document_id,)
    capability_id, version_id = uuid4(), uuid4()
    capabilities.create_capability(
        actor=patron,
        command=CreateEnterpriseCapabilityCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            capability_id=capability_id,
            company_id=company_id,
            capability_kind="EQUIPMENT",
            name="Moyen synthétique",
            summary="Capacité documentaire locale uniquement",
        ),
        now=NOW,
    )
    version = AddEnterpriseCapabilityVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        capability_id=capability_id,
        version_id=version_id,
        expected_revision=0,
        title="Version synthétique exacte",
        description="Aucune réservation ni engagement",
        valid_from=NOW + timedelta(days=1)
        if proof_kind == "future_version"
        else NOW - timedelta(days=2),
        valid_until=NOW + timedelta(days=-1 if proof_kind == "version_expired" else 365),
        usage_scope="Affaire synthétique",
        proof_document_ids=() if proof_kind == "unsupported_relation" else proof_ids,
    )
    capabilities.add_version(actor=patron, command=version, now=NOW)
    with session_factory.begin() as session:
        if proof_kind == "unsupported_relation":
            session.add(
                EnterpriseCapabilityProofLinkRecord(
                    id=uuid4(),
                    tenant_id=collaborator.tenant_id,
                    capability_version_id=version_id,
                    document_id=proof_ids[0],
                    relation_label="REFERENCE_ONLY",
                )
            )
        if proof_kind == "inactive":
            session.get(EnterpriseCapabilityRecord, capability_id).state = "SUSPENDED"
        if proof_kind in {"hash_mismatch", "missing_upload", "quarantined"}:
            upload = session.get(EnterpriseDocumentUploadRecord, document.storage_object_id)
            if proof_kind == "hash_mismatch":
                upload.sha256 = "f" * 64
            elif proof_kind == "missing_upload":
                session.delete(upload)
            else:
                upload.state = "QUARANTINED"
    _auth_session(session_factory, collaborator)
    client, tokens = _client(session_factory)
    headers = _headers(tokens, collaborator)
    path = f"/api/v1/collaborator/cases/{case_id}"
    candidates = client.get(path + "/capability-candidates", headers=headers)
    assert candidates.status_code == 200, candidates.text
    assert candidates.headers["Cache-Control"] == "no-store"
    matching_candidates = [
        item
        for item in candidates.json()
        if item["capability_id"] == str(capability_id) and item["version_id"] == str(version_id)
    ]
    assert len(matching_candidates) == 1
    candidate = matching_candidates[0]
    assert set(candidate) == {
        "capability_id",
        "capability_kind",
        "name",
        "version_id",
        "version_number",
        "title",
        "valid_from",
        "valid_until",
        "validity_state",
        "source_evidence_state",
        "evaluated_at",
    }
    assert candidate["source_evidence_state"] == expected
    assert candidate["evaluated_at"] == NOW.isoformat().replace("+00:00", "Z")
    assert "proof_document_ids" not in candidates.text and "sha256" not in candidates.text
    assert "original_filename" not in candidates.text and "storage_key" not in candidates.text

    payload = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "capability_id": str(capability_id),
        "capability_version_id": str(version_id),
        "requirement_id": str(requirement_id),
        "justification": "Proposition de moyen synthétique sans engagement",
    }
    empty = client.get(
        path + "/capability-assessments",
        headers=headers,
        params={"assignment_id": str(assignment_id)},
    )
    assert empty.status_code == 200 and empty.json() == {"proposals": [], "gaps": []}
    assert empty.headers["Cache-Control"] == "no-store"
    assert client.get(path + "/capability-assessments", headers=headers).json() == empty.json()
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(
                    CaseCapabilityProposalRecord.tenant_id == collaborator.tenant_id,
                    CaseCapabilityProposalRecord.case_id == case_id,
                )
            )
            == 0
        )
    created = client.post(path + "/capability-proposals", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    replay = client.post(path + "/capability-proposals", headers=headers, json=payload)
    assert replay.status_code == 200 and replay.json()["replayed"] is True
    read = client.get(
        path + "/capability-assessments",
        headers=headers,
        params={"assignment_id": str(assignment_id)},
    )
    assert read.status_code == 200, read.text
    case_only = client.get(path + "/capability-assessments", headers=headers)
    assert case_only.status_code == 200
    assert case_only.json() == read.json()
    proposal = read.json()["proposals"][0]
    assert proposal["capability_id"] == str(capability_id)
    assert proposal["capability_version_id"] == str(version_id)
    assert proposal["source_locator"] is None
    historical_state = (
        "EXPIRED" if proof_kind in {"version_expired", "future_version", "inactive"} else "CURRENT"
    )
    assert (
        proposal["validity_state"] == historical_state
    )  # Frozen declaration, not live proof qualification.
    assert proposal["source_evidence_state"] == expected
    assert proposal["source_evidence_evaluated_at"] == NOW.isoformat().replace("+00:00", "Z")
    assert read.headers["Cache-Control"] == "no-store"
    assert (
        digest not in read.text
        and "storage_key" not in read.text
        and "original_filename" not in read.text
    )
    with session_factory() as session:
        stored = session.scalar(
            sa.select(CaseCapabilityProposalRecord).where(
                CaseCapabilityProposalRecord.capability_version_id == version_id
            )
        )
        assert stored.validity_state == historical_state and stored.state == "PROPOSED"
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(CaseCapabilityProposalRecord.tenant_id == collaborator.tenant_id)
            )
            == 1
        )
        assert session.get(EnterpriseCapabilityVersionRecord, version_id).version_number == 1
        links = session.scalars(
            sa.select(EnterpriseCapabilityProofLinkRecord).where(
                EnterpriseCapabilityProofLinkRecord.capability_version_id == version_id
            )
        ).all()
        assert {link.document_id for link in links} == set(proof_ids)
        assert len(links) == len(proof_ids)
        if proof_ids:
            assert (
                session.get(EnterpriseDocumentRecord, proof_ids[0]).sha256
                == sha256(content).hexdigest()
            )
        assert session.scalar(sa.text("SELECT count(*) FROM decisions")) == 0
        assert (
            session.scalar(
                sa.text("SELECT decision_readiness FROM cases WHERE id=:id"), {"id": case_id}
            )
            == "NOT_ASSESSED"
        )

    # An assignment or tenant mismatch must never disclose eligibility or proof metadata.
    other, foreign_assignment, foreign_case, _, foreign_capability, foreign_version = _seed(
        session_factory
    )
    _auth_session(session_factory, other)
    foreign_headers = _headers(tokens, other)
    for candidate in [case_id, uuid4()]:
        refused = client.get(
            f"/api/v1/collaborator/cases/{candidate}/capability-assessments",
            headers=foreign_headers,
            params={"assignment_id": str(assignment_id)},
        )
        assert refused.status_code == 403 and refused.json() == {"detail": "FORBIDDEN"}
        case_only_refusal = client.get(path + "/capability-assessments", headers=foreign_headers)
        assert case_only_refusal.status_code == 403
        assert case_only_refusal.json() == {"detail": "FORBIDDEN"}
        foreign_candidates = client.get(path + "/capability-candidates", headers=foreign_headers)
        assert foreign_candidates.status_code == 403
        assert foreign_candidates.json() == {"detail": "FORBIDDEN"}
    for candidate in [foreign_assignment, uuid4()]:
        refused = client.get(
            path + "/capability-assessments",
            headers=headers,
            params={"assignment_id": str(candidate)},
        )
        assert refused.status_code == 404 and refused.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    for capability, source_version in [
        (foreign_capability, foreign_version),
        (initial_capability, version_id),
        (capability_id, uuid4()),
    ]:
        forged = {
            **payload,
            "command_id": str(uuid4()),
            "idempotency_key": str(uuid4()),
            "capability_id": str(capability),
            "capability_version_id": str(source_version),
        }
        refused = client.post(path + "/capability-proposals", headers=headers, json=forged)
        assert refused.status_code == 404 and refused.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    _auth_session(session_factory, patron)
    denied_patron = client.get(
        path + "/capability-assessments",
        headers=_headers(tokens, patron),
        params={"assignment_id": str(assignment_id)},
    )
    assert denied_patron.status_code == 403 and denied_patron.json() == {"detail": "FORBIDDEN"}
    denied_patron_candidates = client.get(
        path + "/capability-candidates", headers=_headers(tokens, patron)
    )
    assert denied_patron_candidates.status_code == 403
    assert denied_patron_candidates.json() == {"detail": "FORBIDDEN"}
    assert (
        client.get(path + "/capability-assessments", headers=_headers(tokens, patron)).status_code
        == 403
    )

    if proof_kind == "valid":
        # A newer expired version must not replace the exact version proposed for this Case.
        newest = version.model_copy(
            update={
                "command_id": uuid4(),
                "idempotency_key": uuid4(),
                "version_id": uuid4(),
                "expected_revision": 1,
                "valid_until": NOW - timedelta(days=1),
            }
        )
        capabilities.add_version(actor=patron, command=newest, now=NOW)
        same = client.get(
            path + "/capability-assessments",
            headers=headers,
            params={"assignment_id": str(assignment_id)},
        ).json()["proposals"][0]
        assert (
            same["capability_version_id"] == str(version_id)
            and same["source_evidence_state"] == "CURRENT"
        )
        from tests.application.test_collab_capability import _service

        boundary = (
            _service(session_factory)
            .read_assessments(
                actor=collaborator,
                case_id=case_id,
                assignment_id=assignment_id,
                now=NOW + timedelta(days=365),
            )
            .proposals[0]
        )
        assert boundary.source_evidence_state == "EXPIRED" and boundary.validity_state == "CURRENT"
        with session_factory() as session:
            # A ledger cannot retain CLEAN while declaring an ERROR scan verdict.
            with (
                pytest.raises(sa.exc.DatabaseError, match="clean_metadata_required"),
                session.begin_nested(),
            ):
                session.execute(
                    sa.update(EnterpriseDocumentUploadRecord)
                    .where(EnterpriseDocumentUploadRecord.id == document.storage_object_id)
                    .values(scan_verdict="ERROR")
                )
            for model, ident, field in [
                (CaseCapabilityProposalRecord, stored.id, "justification"),
                (EnterpriseCapabilityVersionRecord, version_id, "title"),
                (EnterpriseCapabilityProofLinkRecord, links[0].id, "relation_label"),
                (EnterpriseDocumentRecord, proof_ids[0], "document_label"),
            ]:
                with pytest.raises(sa.exc.DatabaseError), session.begin_nested():
                    session.execute(
                        sa.update(model)
                        .where(sa.inspect(model).c.id == ident)
                        .values(**{field: "synthetic mutation refused"})
                    )
        with session_factory.begin() as session:
            legacy_id = uuid4()
            session.add(
                CaseCapabilityProposalRecord(
                    id=legacy_id,
                    tenant_id=collaborator.tenant_id,
                    case_id=case_id,
                    assignment_id=assignment_id,
                    capability_id=initial_capability,
                    capability_version_id=version_id,
                    requirement_id=requirement_id,
                    state="PROPOSED",
                    validity_state="CURRENT",
                    justification="Synthetic inconsistent historical relation",
                    source_locator="fixture://exp05/history",
                    functional_key=str(uuid4()),
                    proposed_by_membership_id=collaborator.membership_id,
                    command_id=uuid4(),
                    idempotency_key=uuid4(),
                )
            )
        historical = client.get(
            path + "/capability-assessments",
            headers=headers,
            params={"assignment_id": str(assignment_id)},
        ).json()["proposals"]
        assert (
            next(item for item in historical if item["proposal_id"] == str(legacy_id))[
                "source_evidence_state"
            ]
            == "UNKNOWN"
        )
        with session_factory.begin() as session:
            assignment = session.get(CaseAssignmentRecord, assignment_id)
            assignment.starts_at = NOW - timedelta(days=1)
            assignment.ends_at = NOW
        closed = client.get(
            path + "/capability-assessments",
            headers=headers,
            params={"assignment_id": str(assignment_id)},
        )
        assert closed.status_code in {403, 404}
        assert "source_evidence_state" not in closed.text


def test_capability_reader_rejects_missing_assignment_action(session_factory):
    from app.modules.membership.infrastructure.collab_capability_reader import (
        SqlAlchemyCollaboratorCapabilityReader,
    )
    from app.platform.events.dispatcher import CommandExecutionError
    from app.platform.security.capabilities import Capability

    actor, assignment_id, case_id, _, _, _ = _seed(session_factory)
    with pytest.raises(CommandExecutionError, match="SCOPE_DENIED"):
        SqlAlchemyCollaboratorCapabilityReader(session_factory).require_active_assignment(
            tenant_id=actor.tenant_id,
            membership_id=actor.membership_id,
            case_id=case_id,
            assignment_id=assignment_id,
            required_action=Capability.WORK_TASK_READ.value,
            received_at=NOW,
        )


def test_case_only_read_refuses_session_without_mfa(session_factory):
    from app.platform.security.models import AuthSessionRecord

    collaborator, _, case_id, *_ = _seed(session_factory)
    _auth_session(session_factory, collaborator)
    with session_factory.begin() as session:
        auth = session.get(AuthSessionRecord, collaborator.session_id)
        auth.auth_strength = "PASSWORD"
        auth.mfa_verified_at = None
    client, tokens = _client(session_factory)
    response = client.get(
        f"/api/v1/collaborator/cases/{case_id}/capability-assessments",
        headers=_headers(tokens, collaborator),
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "STEP_UP_REQUIRED"}
    candidate_response = client.get(
        f"/api/v1/collaborator/cases/{case_id}/capability-candidates",
        headers=_headers(tokens, collaborator),
    )
    assert candidate_response.status_code == 403
    assert candidate_response.json() == {"detail": "STEP_UP_REQUIRED"}


@pytest.mark.parametrize("source_state", ["foreign", "absent", "obsolete", "task_mismatch"])
def test_collaborator_capability_posts_refuse_unbound_or_obsolete_dce_sources(
    session_factory, source_state
):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.platform.security.models import CollaboratorTaskRecord
    from tests.application.test_collab_capability import (
        _clone_requirement_for_another_consultation,
        _clone_requirement_on_same_dce,
    )

    collaborator, assignment_id, case_id, requirement_id, _, _ = _seed(session_factory)
    task_id = None
    if source_state == "foreign":
        requirement_id = _clone_requirement_for_another_consultation(
            session_factory, requirement_id
        )
    elif source_state == "task_mismatch":
        task_id = uuid4()
        different_requirement = _clone_requirement_on_same_dce(session_factory, requirement_id)
        with session_factory.begin() as session:
            session.add(
                CollaboratorTaskRecord(
                    id=task_id,
                    tenant_id=collaborator.tenant_id,
                    case_id=case_id,
                    assignment_id=assignment_id,
                    requirement_id=requirement_id,
                    task_kind="SYNTHETIC_REQUIREMENT",
                    title="Fixture task",
                    objective="Source consistency test",
                    priority="NORMAL",
                    state="READY",
                    functional_key=str(uuid4()),
                    aggregate_revision=0,
                )
            )
        requirement_id = different_requirement
    else:
        with session_factory.begin() as session:
            case = session.get(CaseRecord, case_id)
            if source_state == "absent":
                case.applicable_dce_version_id = None
                case.dce_freshness = "NO_DCE"
            else:
                case.dce_freshness = "REVIEW_REQUIRED"
    _auth_session(session_factory, collaborator)
    client, tokens = _client(session_factory)
    headers = _headers(tokens, collaborator)
    path = f"/api/v1/collaborator/cases/{case_id}"
    proposal = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "assignment_id": str(assignment_id),
        "capability_id": str(uuid4()),
        "capability_version_id": str(uuid4()),
        "requirement_id": str(requirement_id),
        "task_id": str(task_id) if task_id else None,
        "justification": "Proposition synthétique locale",
    }
    gap = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "assignment_id": str(assignment_id),
        "requirement_id": str(requirement_id),
        "task_id": str(task_id) if task_id else None,
        "gap_kind": "MISSING",
        "severity": "IMPORTANT",
        "reason": "Exigence synthétique à examiner",
        "recommended_action": "Réexaminer la source DCE",
    }
    for endpoint, payload in [
        ("capability-proposals", proposal),
        ("capability-gaps", gap),
    ]:
        refused = client.post(path + "/" + endpoint, headers=headers, json=payload)
        assert refused.status_code == 404
        assert refused.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(
                    CaseCapabilityProposalRecord.tenant_id == collaborator.tenant_id,
                    CaseCapabilityProposalRecord.case_id == case_id,
                )
            )
            == 0
        )
        from app.modules.enterprise.infrastructure.models import CaseCapabilityGapRecord

        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityGapRecord)
                .where(
                    CaseCapabilityGapRecord.tenant_id == collaborator.tenant_id,
                    CaseCapabilityGapRecord.case_id == case_id,
                )
            )
            == 0
        )


def _create_empty_enterprise_capability(session_factory, patron, initial_capability, label):
    library, service = _services(session_factory)
    with session_factory() as session:
        company_id = session.get(EnterpriseCapabilityRecord, initial_capability).company_id
    capability_id, version_id = uuid4(), uuid4()
    service.create_capability(
        actor=patron,
        command=CreateEnterpriseCapabilityCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            capability_id=capability_id,
            company_id=company_id,
            capability_kind="EQUIPMENT",
            name=label,
            summary="Synthetic local capability without documentary proof",
        ),
        now=NOW,
    )
    service.add_version(
        actor=patron,
        command=AddEnterpriseCapabilityVersionCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            capability_id=capability_id,
            version_id=version_id,
            expected_revision=0,
            title=f"{label} version",
            description="Synthetic local version",
            valid_from=NOW - timedelta(days=1),
            valid_until=NOW + timedelta(days=365),
            usage_scope="Fixture only",
            proof_document_ids=(),
        ),
        now=NOW,
    )
    return capability_id, version_id


@pytest.mark.db
@pytest.mark.security
def test_command_uuids_are_tenant_scoped_and_retries_are_stable(session_factory, monkeypatch):
    from app.interfaces.http.routes import collaborator_capabilities as route

    class RecipeClock:
        @staticmethod
        def now(tz=None):
            return NOW

    monkeypatch.setattr(route, "datetime", RecipeClock)
    first, first_assignment, first_case, first_req, first_initial_cap, _ = _seed(session_factory)
    second, second_assignment, second_case, second_req, second_initial_cap, _ = _seed(
        session_factory
    )
    _auth_session(session_factory, first)
    _auth_session(session_factory, second)
    first_patron, second_patron = _patron(session_factory, first), _patron(session_factory, second)
    first_cap, first_version = _create_empty_enterprise_capability(
        session_factory, first_patron, first_initial_cap, "Tenant one fixture"
    )
    second_cap, second_version = _create_empty_enterprise_capability(
        session_factory, second_patron, second_initial_cap, "Tenant two fixture"
    )
    client, tokens = _client(session_factory)
    first_headers, second_headers = _headers(tokens, first), _headers(tokens, second)
    command_id = str(uuid4())

    def proposal_payload(assignment_id, capability_id, version_id, requirement_id, idem):
        return {
            "command_id": command_id,
            "idempotency_key": str(idem),
            "assignment_id": str(assignment_id),
            "capability_id": str(capability_id),
            "capability_version_id": str(version_id),
            "requirement_id": str(requirement_id),
            "justification": "A human proposes this synthetic means",
        }

    first_path = f"/api/v1/collaborator/cases/{first_case}"
    second_path = f"/api/v1/collaborator/cases/{second_case}"
    # A foreign, known requirement remains a neutral refusal and does not reserve the ID.
    absent = client.post(
        second_path + "/capability-proposals",
        headers=second_headers,
        json=proposal_payload(second_assignment, second_cap, second_version, first_req, uuid4()),
    )
    assert absent.status_code == 404
    assert absent.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}

    first_body = proposal_payload(first_assignment, first_cap, first_version, first_req, uuid4())
    first_created = client.post(
        first_path + "/capability-proposals", headers=first_headers, json=first_body
    )
    assert first_created.status_code == 201, first_created.text
    first_replay = client.post(
        first_path + "/capability-proposals", headers=first_headers, json=first_body
    )
    assert first_replay.status_code == 200
    assert first_replay.json()["replayed"] is True
    assert first_replay.json()["aggregate_refs"] == first_created.json()["aggregate_refs"]
    other_key_same_command = {**first_body, "idempotency_key": str(uuid4())}
    command_conflict = client.post(
        first_path + "/capability-proposals", headers=first_headers, json=other_key_same_command
    )
    assert command_conflict.status_code == 409
    # The same command UUID with another tenant's absent source is always a neutral 404.
    absent_after_creation = client.post(
        second_path + "/capability-proposals",
        headers=second_headers,
        json=proposal_payload(second_assignment, second_cap, second_version, first_req, uuid4()),
    )
    assert absent_after_creation.status_code == 404
    altered = {**first_body, "justification": "Different human declaration"}
    key_conflict = client.post(
        first_path + "/capability-proposals", headers=first_headers, json=altered
    )
    assert key_conflict.status_code == 409

    second_body = proposal_payload(
        second_assignment, second_cap, second_version, second_req, uuid4()
    )
    second_created = client.post(
        second_path + "/capability-proposals", headers=second_headers, json=second_body
    )
    assert second_created.status_code == 201, second_created.text
    first_id = first_created.json()["aggregate_refs"][0]["aggregate_id"]
    second_id = second_created.json()["aggregate_refs"][0]["aggregate_id"]
    assert first_id != second_id

    gap_id = str(uuid4())

    def gap_payload(assignment_id, requirement_id, idem):
        return {
            "command_id": gap_id,
            "idempotency_key": str(idem),
            "assignment_id": str(assignment_id),
            "requirement_id": str(requirement_id),
            "gap_kind": "MISSING",
            "severity": "IMPORTANT",
            "reason": "Synthetic missing proof",
            "recommended_action": "Review manually",
        }

    first_gap_body = gap_payload(first_assignment, first_req, uuid4())
    first_gap = client.post(
        first_path + "/capability-gaps", headers=first_headers, json=first_gap_body
    )
    assert first_gap.status_code == 201, first_gap.text
    first_gap_replay = client.post(
        first_path + "/capability-gaps", headers=first_headers, json=first_gap_body
    )
    assert first_gap_replay.status_code == 200
    assert first_gap_replay.json()["aggregate_refs"] == first_gap.json()["aggregate_refs"]
    second_gap_absent = client.post(
        second_path + "/capability-gaps",
        headers=second_headers,
        json=gap_payload(second_assignment, first_req, uuid4()),
    )
    assert second_gap_absent.status_code == 404
    second_gap = client.post(
        second_path + "/capability-gaps",
        headers=second_headers,
        json=gap_payload(second_assignment, second_req, uuid4()),
    )
    assert second_gap.status_code == 201, second_gap.text
    assert (
        first_gap.json()["aggregate_refs"][0]["aggregate_id"]
        != second_gap.json()["aggregate_refs"][0]["aggregate_id"]
    )

    concurrent_requirement = _clone_requirement_on_same_dce(session_factory, first_req)
    concurrent_body = {
        **proposal_payload(
            first_assignment, first_cap, first_version, concurrent_requirement, uuid4()
        ),
        "command_id": str(uuid4()),
    }
    concurrent_id = concurrent_body["command_id"]
    barrier = Barrier(2)
    clients = [_client(session_factory)[0], _client(session_factory)[0]]

    def submit(index):
        barrier.wait(timeout=10)
        return clients[index].post(
            first_path + "/capability-proposals", headers=first_headers, json=concurrent_body
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(submit, (0, 1)))
    assert sorted(response.status_code for response in responses) == [200, 201]
    assert all(response.json()["command_id"] == concurrent_id for response in responses)
    assert responses[0].json()["aggregate_refs"] == responses[1].json()["aggregate_refs"]
    # Concurrent reuse of one command UUID with distinct intent keys is a conflict.
    conflicting_id = str(uuid4())
    conflicting_requirement = _clone_requirement_on_same_dce(session_factory, first_req)
    conflicting_bodies = [
        {
            **proposal_payload(
                first_assignment, first_cap, first_version, conflicting_requirement, uuid4()
            ),
            "command_id": conflicting_id,
        },
        {
            **proposal_payload(
                first_assignment, first_cap, first_version, conflicting_requirement, uuid4()
            ),
            "command_id": conflicting_id,
        },
    ]
    barrier = Barrier(2)

    def submit_conflict(index):
        barrier.wait(timeout=10)
        return clients[index].post(
            first_path + "/capability-proposals",
            headers=first_headers,
            json=conflicting_bodies[index],
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        conflict_responses = list(pool.map(submit_conflict, (0, 1)))
    assert sorted(response.status_code for response in conflict_responses) == [201, 409]
    assert all(
        response.json()["detail"] == "IDEMPOTENCY_CONFLICT"
        for response in conflict_responses
        if response.status_code == 409
    )

    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(
                    CaseCapabilityProposalRecord.tenant_id == first.tenant_id,
                    CaseCapabilityProposalRecord.case_id == first_case,
                )
            )
            == 3
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityProposalRecord)
                .where(
                    CaseCapabilityProposalRecord.tenant_id == second.tenant_id,
                    CaseCapabilityProposalRecord.case_id == second_case,
                )
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityGapRecord)
                .where(CaseCapabilityGapRecord.tenant_id == first.tenant_id)
            )
            == 1
        )
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CaseCapabilityGapRecord)
                .where(CaseCapabilityGapRecord.tenant_id == second.tenant_id)
            )
            == 1
        )
