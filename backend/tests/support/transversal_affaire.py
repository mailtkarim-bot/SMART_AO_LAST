"""Shared identities and native HTTP composition; no mocked authorization or gates."""

from dataclasses import replace
from types import SimpleNamespace
from uuid import UUID, uuid4

from app.modules.case.application.handlers import _scope_json, _sha256_json
from app.modules.case.domain.case import CaseScope
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.enterprise.infrastructure.models import EnterpriseCompanyRecord
from app.modules.membership.infrastructure.records import CaseAssignmentRecord
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import (
    ActorKind,
    AssignmentScope,
    DataClassification,
    OperationalProfile,
)
from app.platform.security.models import IdentityRecord, TenantMembershipRecord


def shared_http(session_factory, w, tmp_path, monkeypatch):
    from app.bootstrap import application as bootstrap

    from tests.api import test_collaborator_capability_api as auth_fixture

    driver_id, driver_member, assignment, company = uuid4(), uuid4(), uuid4(), uuid4()
    actions = sorted(capabilities_for(ActorKind.COLLABORATEUR))
    with session_factory.begin() as s:
        for identity, member, role, profile in (
            (w.actor.identity_id, w.actor.membership_id, "PATRON_ADMIN", None),
            (driver_id, driver_member, "COLLABORATEUR", "RESPONSABLE"),
        ):
            s.add(
                IdentityRecord(
                    id=identity,
                    email_normalized=f"{identity}@example.test",
                    lifecycle="ACTIVE",
                    email_verified_at=w.now,
                )
            )
            s.flush()
            s.add(
                TenantMembershipRecord(
                    id=member,
                    tenant_id=w.actor.tenant_id,
                    identity_id=identity,
                    role=role,
                    operational_profile=profile,
                    state="ACTIVE",
                    activated_at=w.now,
                    revoked_at=None,
                )
            )
        s.flush()
        scope = CaseScope.multi_lot(
            tuple(str(lot) for lot in w.seed[4]["lots"]),
            "Deux lots du manifeste synthétique relus.",
        )
        scope.validate()
        row = s.get(CaseRecord, w.case_id)
        row.scope_json = _scope_json(scope)
        row.scope_fingerprint = _sha256_json(row.scope_json)
        s.add(
            CaseAssignmentRecord(
                id=assignment,
                tenant_id=w.actor.tenant_id,
                membership_id=driver_member,
                case_id=w.case_id,
                aggregate_revision=0,
                state="ACTIVE",
                scope_actions_json=actions,
                scope_classifications_json=["INTERNAL_OPERATIONAL"],
                granted_by_membership_id=w.actor.membership_id,
                granted_at=w.now,
                starts_at=w.now,
                ends_at=None,
                ended_at=None,
            )
        )
        s.add(
            EnterpriseCompanyRecord(
                id=company,
                tenant_id=w.actor.tenant_id,
                aggregate_revision=0,
                legal_name="Entreprise synthétique Atelier BTP",
                trade_name=None,
                siren="123456789",
                siret="12345678900011",
                vat_number="FR12123456789",
                address_line1="1 rue de la fixture",
                postal_code="75001",
                city="Paris",
                country_code="FR",
            )
        )
    driver = replace(
        w.actor,
        actor_id=driver_id,
        identity_id=driver_id,
        membership_id=driver_member,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        session_id=uuid4(),
        assigned_case_ids=frozenset({w.case_id}),
        operational_profile=OperationalProfile.RESPONSABLE,
        assignment_scopes=(
            AssignmentScope(
                case_id=w.case_id,
                allowed_actions=frozenset(actions),
                allowed_classifications=frozenset({DataClassification.INTERNAL_OPERATIONAL}),
            ),
        ),
    )
    monkeypatch.setattr(auth_fixture, "NOW", w.now)
    monkeypatch.setenv("SMART_AO_OBJECT_STORAGE_ENABLED", "0")
    monkeypatch.setenv("SMART_AO_DCE_QUARANTINE_ROOT", str(tmp_path))
    for provider in (
        "_build_company_registry",
        "_build_submission_export_notifier",
        "_build_submission_deadline_calendar",
        "_build_public_notice_search",
    ):
        monkeypatch.setattr(bootstrap, provider, lambda: None)
    auth_fixture._auth_session(session_factory, w.actor)
    auth_fixture._auth_session(session_factory, driver)
    from hashlib import sha256

    from app.modules.pricing.application.file_security import LibmagicClamdPricingFileSecurity

    allowed_scans: set[str] = set()

    async def scan_fixture_only(self, payload):
        return (
            ("CLEAN", "synthetic-sha256-allowlist-v1")
            if sha256(payload).hexdigest() in allowed_scans
            else ("ERROR", "synthetic-unqualified")
        )

    monkeypatch.setattr(LibmagicClamdPricingFileSecurity, "_scan", scan_fixture_only)
    client, tokens = auth_fixture._client(session_factory)
    return SimpleNamespace(
        client=client,
        allowed_scans=allowed_scans,
        driver=driver,
        assignment_id=assignment,
        company_id=company,
        patron_headers=auth_fixture._headers(tokens, w.actor),
        driver_headers=auth_fixture._headers(tokens, driver),
    )


def insurance_proposal(session_factory, w, http, root, requirement_id, *, label_suffix=""):
    """One explicitly fictitious insurance proof, relevant only to its selected clause."""
    import io
    from datetime import timedelta
    from hashlib import sha256

    from app.modules.enterprise.infrastructure.models import (
        EnterpriseCapabilityProofLinkRecord,
        EnterpriseCapabilityRecord,
        EnterpriseCapabilityVersionRecord,
        EnterpriseDocumentRecord,
        EnterpriseDocumentUploadRecord,
    )
    from app.modules.membership.application.collab_capability_commands import (
        ProposeCapabilityForCaseCommand,
    )
    from pypdf import PdfReader, PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    from tests.application.test_collab_capability import _service

    if getattr(w, "capture_packets", False):
        label_suffix += f" — source synthétique V{len(w.packet_runs) + 1}"
    capability, version, document, upload = uuid4(), uuid4(), uuid4(), uuid4()
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )
    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 50 720 Td (SYNTHETIC INSURANCE - lot 1 - no real legal validity.) Tj ET"
        + (
            f"\n% SYNTHETIC GENERATION {len(w.packet_runs) + 1}".encode("ascii")
            if getattr(w, "capture_packets", False)
            else b""
        )
    )
    page[NameObject("/Contents")] = writer._add_object(stream)
    output = io.BytesIO()
    writer.write(output)
    data = output.getvalue()
    assert "SYNTHETIC INSURANCE" in PdfReader(io.BytesIO(data)).pages[0].extract_text()
    digest = sha256(data).hexdigest()
    key = f"{w.actor.tenant_id}/{document}/{upload}.bin"
    path = root / key
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(data)
    path.chmod(0o600)
    with session_factory.begin() as s:
        s.add(
            EnterpriseCapabilityRecord(
                id=capability,
                tenant_id=w.actor.tenant_id,
                company_id=http.company_id,
                aggregate_revision=1,
                capability_kind="QUALIFICATION",
                name="Assurance décennale synthétique déclarée" + label_suffix,
                summary="Fixture de couverture déclarée pour le lot 1, sans validité réelle.",
                state="ACTIVE",
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        s.flush()
        s.add(
            EnterpriseCapabilityVersionRecord(
                id=version,
                tenant_id=w.actor.tenant_id,
                capability_id=capability,
                version_number=1,
                title="Couverture de test lot 1",
                description="Source synthétique pour le seul essai de reprise de clause.",
                valid_from=w.now - timedelta(days=1),
                valid_until=w.now + timedelta(days=365),
                usage_scope="Assurance déclarée synthétique lot 1",
                created_by_membership_id=w.actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        s.add(
            EnterpriseDocumentUploadRecord(
                id=upload,
                tenant_id=w.actor.tenant_id,
                company_id=http.company_id,
                document_id=document,
                document_kind="INSURANCE",
                document_label="SYNTHETIC ONLY - assurance lot 1",
                original_filename="insurance-fixture.pdf",
                storage_key=key,
                expected_byte_size=len(data),
                actual_byte_size=len(data),
                sha256=digest,
                media_type="application/pdf",
                state="CLEAN",
                scan_verdict="CLEAN",
                scanner_name="synthetic-known-input",
                scanner_signature_version="fixture-only",
                scanned_at=w.now,
                expires_at=w.now + timedelta(hours=1),
                created_by_membership_id=w.actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        s.flush()
        s.add(
            EnterpriseDocumentRecord(
                id=document,
                tenant_id=w.actor.tenant_id,
                company_id=http.company_id,
                document_kind="INSURANCE",
                document_label="SYNTHETIC ONLY - assurance lot 1",
                storage_object_id=upload,
                original_filename="insurance-fixture.pdf",
                issued_at=w.now - timedelta(days=1),
                expires_at=w.now + timedelta(days=365),
                sha256=digest,
                verification_status="VALIDATED",
                registered_by_membership_id=w.actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=None,
            )
        )
        s.flush()
        s.add(
            EnterpriseCapabilityProofLinkRecord(
                id=uuid4(),
                tenant_id=w.actor.tenant_id,
                capability_version_id=version,
                document_id=document,
                relation_label="SUPPORTS_CAPABILITY",
            )
        )
    command = ProposeCapabilityForCaseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        proposal_id=uuid4(),
        case_id=w.case_id,
        assignment_id=http.assignment_id,
        capability_id=capability,
        capability_version_id=version,
        requirement_id=requirement_id,
        justification="Source de test limitée à la clause assurance lot 1.",
        source_locator=f"enterprise-document://{document}",
    )
    recorded = _service(session_factory).propose_capability(
        actor=http.driver, command=command, now=w.now
    )
    return SimpleNamespace(
        proposal_id=UUID(str(recorded.aggregate_refs[0]["aggregate_id"])),
        document_id=document,
        sha256=digest,
    )


def finish_execution_and_reuse(http, w, *, handover_id, point_id, instrument_id, view):
    """Continue the original HTTP Affaire; never seed a replacement source Case."""

    def identity(correlation=False):
        values = dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))
        if correlation:
            values["correlation_id"] = str(uuid4())
        return values

    def post(url, payload, *, replay=False):
        response = http.client.post(url, headers=http.patron_headers, json=payload)
        assert response.status_code == 201, response.text
        if replay:
            repeated = http.client.post(url, headers=http.patron_headers, json=payload)
            assert repeated.status_code == 200 and repeated.json()["replayed"], repeated.text
        return response.json()

    case_root = f"/api/v1/patron/cases/{w.case_id}"
    changes = case_root + "/contract-change-events"
    event, review_id, action = map(str, (uuid4(), uuid4(), uuid4()))
    context = dict(
        expected_view_sha256=view["view_sha256"],
        point_ids=[str(point_id)],
        justification="Rapprochement fictif de l’instruction et de l’engagement transmis.",
        human_confirmed=True,
        publish=True,
    )
    post(
        changes,
        dict(
            **identity(True),
            event_id=event,
            handover_snapshot_id=str(handover_id),
            change_kind="ORDER_OF_SERVICE",
            contract_instrument_version_id=str(instrument_id),
            issuer="MOA synthétique",
            summary="Demande déclarée de contrôle supplémentaire de finition.",
            scope_note="Lot 1 seulement.",
            source_refs=["os://synthetic/lot1/v1"],
            evidence_refs=["courrier://synthetic/os/1"],
            declared_received_at=w.now.isoformat(),
            operational_context=context,
        ),
        replay=True,
    )
    post(
        changes + f"/{event}/applicability",
        dict(
            **identity(True),
            review_id=review_id,
            handover_snapshot_id=str(handover_id),
            contract_instrument_version_id=str(instrument_id),
            expected_revision=0,
            decision="APPLICABLE_TO_HANDOVER",
            delta_state="DECLARED",
            delta_note="Un contrôle de finition additionnel est déclaré.",
            rationale="Instruction rapprochée du point transmis.",
            evidence_refs=["os://synthetic/lot1/v1"],
            operational_review=context,
        ),
    )
    post(
        changes + f"/{event}/actions",
        dict(
            **identity(True),
            action_id=action,
            applicability_review_id=review_id,
            expected_revision=0,
            action_summary="Organiser le contrôle de finition.",
            evidence_refs=["os://synthetic/lot1/v1"],
            due_date_absence_reason="Date non déterminée dans cet essai.",
            operational_details=dict(
                responsible="Conducteur synthétique",
                expected_evidence="PV du contrôle déclaré",
                human_confirmed=True,
                publish=True,
                justification="Action à suivre humainement.",
            ),
        ),
    )
    operational = http.client.get(
        f"/api/v1/cases/{w.case_id}/contract-change-events", headers=http.driver_headers
    )
    assert operational.status_code == 200, operational.text
    row = operational.json()["events"][0]
    assert row["source_state"] == "CURRENT" and row["legal_effect_state"] == "UNKNOWN"
    assert row["actions"][0]["operational_details"]["responsible"] == "Conducteur synthétique"

    closure = case_root + "/closure"

    def read(url=closure):
        response = http.client.get(url, headers=http.patron_headers)
        assert response.status_code == 200, response.text
        return response.json()

    assert http.client.get(closure, headers=http.driver_headers).status_code == 403

    def act_review():
        return dict(
            expected_dossier_sha256=read()["dossier_sha256"],
            human_confirmed=True,
            justification="Pièces et suivi de la même Affaire relus en essai.",
            responsible="Conducteur synthétique",
            expected_evidence="PV synthétique référencé",
            acknowledged_open_obligation_ids=[],
            comparisons=[],
        )

    reception, obligation, exit_id = map(str, (uuid4(), uuid4(), uuid4()))
    post(
        closure + "/acts",
        dict(
            **identity(),
            act_id=reception,
            act_kind="WORK_RECEPTION",
            reception_outcome="WITH_RESERVATIONS",
            summary="Réception déclarée avec réserve de finition.",
            source_refs=["pv://synthetic/reception/lot1"],
            evidence_refs=["preuve://synthetic/pv"],
            contract_instrument_version_id=str(instrument_id),
            closure_review=act_review(),
        ),
        replay=True,
    )
    post(
        closure + "/obligations",
        dict(
            **identity(),
            obligation_id=obligation,
            obligation_type="RESERVES_LIFTING",
            origin_reception_act_id=reception,
            summary="Reprendre la finition contrôlée.",
            source_refs=["pv://synthetic/reception/lot1"],
            closure_review=act_review(),
        ),
    )
    post(
        closure + "/obligation-transitions",
        dict(
            **identity(),
            obligation_id=obligation,
            transition_id=str(uuid4()),
            expected_revision=0,
            resulting_status="COMPLETED",
            rationale="Levée déclarée avec référence de preuve.",
            evidence_refs=["pv://synthetic/levee"],
        ),
    )
    cycle = str(uuid4())
    post(
        closure + "/cycles",
        dict(
            **identity(),
            cycle_id=cycle,
            source_refs=["ccap://synthetic/paiement"],
            trigger_event="INVOICE",
            status="REVIEW_REQUIRED",
        ),
    )
    parent = None
    for kind, amount in [
        ("INVOICE_DECLARED", 100000),
        ("PAYMENT_EXPECTED", 100000),
        ("COLLECTION_RECORDED", 60000),
    ]:
        fact = str(uuid4())
        payload = dict(
            **identity(),
            fact_id=fact,
            cycle_id=cycle,
            kind=kind,
            amount_minor=amount,
            currency_code="EUR",
            declared_date=w.now.date().isoformat(),
            source_refs=["compta://synthetic/lot1"],
            evidence_refs=["preuve://synthetic/compta"],
            human_confirmed=True,
            justification="Déclaration fictive, aucune connexion bancaire.",
            expected_dossier_sha256=read()["dossier_sha256"],
            compared_to_fact_id=parent,
        )
        post(closure + "/payment-facts", payload, replay=True)
        parent = fact
    observed = read()
    assert observed["financial_observations"]["settlement_state"] == "UNKNOWN"
    assert any(
        c["difference_minor"] == -40000 for c in observed["financial_observations"]["comparisons"]
    )
    post(
        closure + "/acts",
        dict(
            **identity(),
            act_id=exit_id,
            act_kind="CONTRACT_EXIT",
            summary="Sortie déclarée sans effet juridique déduit.",
            source_refs=["sortie://synthetic/lot1"],
            evidence_refs=["preuve://synthetic/sortie"],
            contract_instrument_version_id=str(instrument_id),
            closure_review=act_review(),
        ),
    )
    rex, interview = str(uuid4()), str(uuid4())
    post(
        closure + "/rex",
        dict(
            **identity(),
            rex_id=rex,
            exit_act_id=exit_id,
            publish_to_rex=True,
            lot_reference="1",
            scope="LOT_PATTERN",
            validation="APPROVED",
            observation="La finition a nécessité un contrôle additionnel déclaré.",
            consequence="Une reprise a été déclarée avant sortie.",
            follow_up="Prévoir un contrôle de finition dans une prochaine Affaire.",
            source_locator="pv://synthetic/reception/lot1",
            human_confirmed=True,
            justification="Enseignement fictif relu, sans généralisation automatique.",
            expected_dossier_sha256=read()["dossier_sha256"],
        ),
        replay=True,
    )
    from datetime import timedelta

    post(
        closure + "/interviews",
        dict(
            **identity(),
            interview_id=interview,
            held_on=w.now.date().isoformat(),
            expires_on=(w.now.date() + timedelta(days=90)).isoformat(),
            source_locator="interview://synthetic/lot1",
            rationale="REX de la chaîne complète relu.",
        ),
    )
    created = post(
        "/api/v1/cases",
        dict(
            **identity(),
            title="Seconde Affaire synthétique — finition",
            object_description="Cible distincte du réemploi humain de l’enseignement.",
            scope_kind="SINGLE_LOT",
            lot_numbers=["1"],
            origin_kind="MANUAL",
            origin_rationale="Qualification transversale locale, aucun marché réel.",
        ),
    )
    target = created["case_id"]
    assert target != str(w.case_id)
    target_url = f"/api/v1/patron/cases/{target}/closure"
    post(
        target_url + "/teaching-reuse",
        dict(
            **identity(),
            applicability_id=str(uuid4()),
            target_case_id=target,
            source_case_id=str(w.case_id),
            source_interview_id=interview,
            source_rex_id=rex,
            decision="APPLICABLE",
            rationale="Contrôle repris par décision fictive explicite.",
            target_source_locator="programme://synthetic/target/finition",
            human_confirmed=True,
            expected_target_dossier_sha256=read(target_url)["dossier_sha256"],
        ),
        replay=True,
    )
    reused = read(target_url)
    assert len(reused["reuse_history"]) == 1
    # The manually created target has no DCE: applicability never proves source completeness.
    assert reused["reuse_history"][0]["context_state"] == "UNKNOWN"
    assert http.client.get(target_url, headers=http.driver_headers).status_code == 403
    replacement = str(uuid4())
    post(
        case_root + "/contract-instrument-versions",
        dict(
            **identity(),
            contract_instrument_version_id=replacement,
            instrument_kind="AMENDMENT",
            version_reference="Contrat synthétique lot 1 — v2",
            source_refs=["contrat://synthetic/lot1/v2"],
            evidence_refs=["preuve://synthetic/contrat/2"],
        ),
    )
    post(
        case_root + "/contract-instrument-supersessions",
        dict(
            **identity(),
            supersession_id=str(uuid4()),
            replacing_contract_instrument_version_id=replacement,
            replaced_contract_instrument_version_id=str(instrument_id),
            rationale="Remplacement synthétique explicite, relecture des actes requise.",
        ),
    )
    stale = http.client.get(f"/api/v1/cases/{w.case_id}/p7-handover", headers=http.driver_headers)
    assert stale.status_code == 200, stale.text
    assert stale.json()["items"][0]["source_state"] == "REVIEW_REQUIRED"
    retained = read()
    assert retained["acts"] and all(
        a["context_state"] == "REVIEW_REQUIRED" for a in retained["acts"]
    )
    assert read(target_url)["reuse_history"][0]["context_state"] == "REVIEW_REQUIRED"
    return dict(
        source_case_id=str(w.case_id),
        target_case_id=target,
        rex_id=rex,
        interview_id=interview,
        handover_id=str(handover_id),
    )
