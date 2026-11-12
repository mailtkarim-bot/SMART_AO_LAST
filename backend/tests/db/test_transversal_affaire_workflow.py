"""One synthetic Case shared across native business deliverables."""

import json
from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest
from app.modules.optimization.application.dated_commands import RecordDatedCapacityCommand
from app.modules.optimization.infrastructure.dated_service import (
    DatedCapacityService,
    RecordDatedCapacityHandler,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy
from tests.db.test_l04_multilot_pipeline import complete_dossier, read
from tests.db.test_regulatory_profile_persistence import _actor


@pytest.fixture
def affaire(session_factory, tmp_path):
    seed = complete_dossier.__wrapped__(
        session_factory, tmp_path, SimpleNamespace(param="dce_l04_multilot")
    )
    now = datetime.now(UTC)
    actor = replace(_actor(seed[0], seed[1]), authenticated_at=now, mfa_verified_at=now)
    capacity = DatedCapacityService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDatedCapacity": RecordDatedCapacityHandler()},
        ),
        policy=AuthorizationPolicy(),
    )
    return SimpleNamespace(seed=seed, actor=actor, case_id=seed[1], now=now, capacity=capacity)


def test_recorded_capacity_reaches_same_case_dossier_with_exact_provenance(
    session_factory, affaire
):
    w = affaire
    source = dict(
        reference="planning://synthetic/lot-1", revision="v1", locator="planning.txt:ligne1"
    )
    base = dict(resource_type="POSE", units=1, start="2027-05-03", end="2027-05-05", source=source)
    command = RecordDatedCapacityCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        case_id=w.case_id,
        expected_revision=0,
        context_sha256=w.capacity.read(actor=w.actor, case_id=w.case_id, now=w.now)[
            "context_sha256"
        ],
        demands=[dict(id=uuid4(), label="Pose lot 1", **base)],
        supplies=[dict(id=uuid4(), label="Équipe synthétique", **base)],
        justification="Hypothèse datée synthétique, aucune réservation.",
        human_confirmed=True,
    )
    w.capacity.record(actor=w.actor, command=command, now=w.now)
    assert w.capacity.record(actor=w.actor, command=command, now=w.now).replayed
    native = w.capacity.read(actor=w.actor, case_id=w.case_id, now=w.now)
    dossier = read(session_factory, w.seed)
    axis = next(a for a in dossier["axes"] if a["code"] == "CAPACITY")
    assert axis.get("capacity_plans"), "L07 run is silently omitted from the L04 dossier"
    plan = axis["capacity_plans"][0]
    assert plan["run_id"] == str(command.run_id)
    assert plan["revision"] == native["revision"]
    assert plan["input_sha256"] == native["current"]["input_sha256"]
    assert plan["details"]["reservation_state"] == "NOT_RESERVED"
    assert dossier["analysis_complete"] is False


def test_capacity_is_an_exact_card_reference_not_an_inferred_gate(session_factory, affaire):
    from app.modules.decision.infrastructure.commitment_service import CommitmentCardService
    from app.modules.decision.infrastructure.repositories import (
        SqlAlchemyDecisionLifecycleRepository,
    )

    w = affaire
    cmd = RecordDatedCapacityCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        case_id=w.case_id,
        expected_revision=0,
        context_sha256=w.capacity.read(actor=w.actor, case_id=w.case_id, now=w.now)[
            "context_sha256"
        ],
        demands=None,
        supplies=None,
        justification="Disponibilités encore inconnues.",
        human_confirmed=True,
    )
    w.capacity.record(actor=w.actor, command=cmd, now=w.now)
    service = CommitmentCardService(
        session_factory=session_factory, dispatcher=None, policy=AuthorizationPolicy()
    )
    card = service.read(actor=w.actor, case_id=w.case_id, now=w.now)
    refs = [r for r in card["references"] if r["aggregate_type"] == "CAPACITY_RUN"]
    assert len(refs) == 1, "L07 provenance disappears at the L04→L05 boundary"
    ref = refs[0]
    assert ref["aggregate_id"] == str(cmd.run_id) and ref["aggregate_revision"] == 1
    assert card["gate_effect"] == "NONE" and card["analysis_complete"] is False
    repository = SqlAlchemyDecisionLifecycleRepository()
    with session_factory() as s:
        assert repository.context_reference_is_valid(
            session=s,
            tenant_id=w.actor.tenant_id,
            case_id=w.case_id,
            **{
                k: ref[k]
                for k in ("aggregate_type", "aggregate_id", "aggregate_revision", "content_hash")
            },
        )
    replacement = cmd.model_copy(
        update={
            "command_id": uuid4(),
            "idempotency_key": uuid4(),
            "run_id": uuid4(),
            "expected_revision": 1,
        }
    )
    w.capacity.record(actor=w.actor, command=replacement, now=w.now)
    with session_factory() as s:
        assert not repository.context_reference_is_valid(
            session=s,
            tenant_id=w.actor.tenant_id,
            case_id=w.case_id,
            **{
                k: ref[k]
                for k in ("aggregate_type", "aggregate_id", "aggregate_revision", "content_hash")
            },
        )


def test_shared_native_http_preserves_case_sources_and_denies_financial_access(
    session_factory, affaire, tmp_path, monkeypatch
):
    from tests.support.transversal_affaire import shared_http

    w = affaire
    assembly = getattr(w, "response_assembly", False)
    buyer_docx = getattr(w, "buyer_docx", False)
    revision_offset = 1 if assembly else 0
    http = getattr(w, "packet_http", None) or shared_http(session_factory, w, tmp_path, monkeypatch)
    url = f"/api/v1/cases/{w.case_id}/analysis-summary"
    response = http.client.get(url, headers=http.patron_headers)
    assert response.status_code == 200, response.text
    assert response.json()["case_id"] == str(w.case_id)
    assert response.json()["dce_version_id"] == str(w.seed[2])
    assert http.client.get(url, headers=http.driver_headers).status_code == 403
    created = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/financial-reports/drafts",
        headers=http.patron_headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4()), currency_code="EUR"),
    )
    assert created.status_code == 201, created.text
    report = created.json()["aggregate_refs"][0]["aggregate_id"]
    from tests.application.test_pricing_workbook_completeness import HEADERS, workbook_payload

    payload = workbook_payload(
        [
            ("Lot 1", [HEADERS, ["A", "Pose de pompe", 2, 100]]),
            ("Lot 2", [HEADERS, ["B", "Contrôle", 1, 50]]),
        ]
    )
    from hashlib import sha256

    http.allowed_scans.add(sha256(payload).hexdigest())
    uploaded = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/pricing-import/preview",
        headers={
            **http.patron_headers,
            "X-Command-Id": str(uuid4()),
            "Idempotency-Key": str(uuid4()),
        },
        files={
            "upload": (
                "lots.xlsx",
                payload,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert uploaded.status_code == 201, uploaded.text
    batch = uploaded.json()["batch_id"]
    imported = http.client.get(
        f"/api/v1/patron/cases/{w.case_id}/pricing-import/{batch}", headers=http.patron_headers
    )
    assert imported.status_code == 200, imported.text
    assert {r["source_locator"]["sheet"] for r in imported.json()["rows"]} == {"Lot 1", "Lot 2"}
    assert (
        http.client.get(
            f"/api/v1/patron/cases/{w.case_id}/pricing-import/{batch}", headers=http.driver_headers
        ).status_code
        == 403
    )
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        report_id=report,
        expected_batch_revision=1,
        expected_report_revision=0,
    )
    committed = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/pricing-import/{batch}/commit",
        headers=http.patron_headers,
        json=body,
    )
    assert committed.status_code == 201, committed.text
    replay = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/pricing-import/{batch}/commit",
        headers=http.patron_headers,
        json=body,
    )
    assert replay.status_code == 200 and replay.json()["replayed"]
    positions = http.client.get(
        f"/api/v1/patron/cases/{w.case_id}/pricing-import/{batch}/positions",
        headers=http.patron_headers,
    )
    assert positions.status_code == 200, positions.text
    assert len(positions.json()["positions"]) == 2
    assert all(row["cost_state"] == "UNKNOWN" for row in positions.json()["positions"])
    import sqlalchemy as sa
    from app.modules.dce.application.commands import RecordDceRequirementConfirmationCommand
    from app.modules.dce.application.handlers import RecordDceRequirementConfirmationHandler
    from app.modules.dce.application.requirement_confirmation import (
        DceRequirementConfirmationService,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord

    confirm = DceRequirementConfirmationService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementConfirmation": RecordDceRequirementConfirmationHandler()
            },
        ),
        policy=AuthorizationPolicy(),
    )
    with session_factory() as s:
        requirement_ids = list(
            s.scalars(
                sa.select(DceRequirementRecord.id).where(
                    DceRequirementRecord.tenant_id == w.actor.tenant_id,
                    DceRequirementRecord.dce_version_id == w.seed[2],
                )
            )
        )
    for requirement_id in requirement_ids:
        confirm.confirm(
            actor=w.actor,
            now=w.now,
            command=RecordDceRequirementConfirmationCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                confirmation_id=uuid4(),
                requirement_id=requirement_id,
                expected_confirmation_revision=0,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
            ),
        )
    from app.platform.security.models import FinancialReportSnapshotRecord

    with session_factory() as s:
        revision = s.get(
            FinancialReportSnapshotRecord, __import__("uuid").UUID(report)
        ).aggregate_revision
    cost = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/financial-reports/{report}/lines",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=revision,
            category="DIRECT_COST",
            label="Coût déclaré pompe, périmètre partiel",
            quantity_decimal="1",
            unit="u",
            amount_minor=12000,
        ),
    )
    assert cost.status_code == 201, cost.text
    with session_factory() as s:
        revision = s.get(
            FinancialReportSnapshotRecord, __import__("uuid").UUID(report)
        ).aggregate_revision
    publication = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/financial-reports/{report}/publications",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()), idempotency_key=str(uuid4()), expected_revision=revision
        ),
    )
    assert publication.status_code == 201, publication.text
    cap = RecordDatedCapacityCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        run_id=uuid4(),
        case_id=w.case_id,
        expected_revision=w.capacity.read(actor=w.actor, case_id=w.case_id, now=w.now)["revision"],
        context_sha256=w.capacity.read(actor=w.actor, case_id=w.case_id, now=w.now)[
            "context_sha256"
        ],
        demands=None,
        supplies=None,
        justification="Hypothèses de ressources encore à compléter.",
        human_confirmed=True,
    )
    w.capacity.record(actor=w.actor, command=cap, now=w.now)
    full = http.client.get(url, headers=http.patron_headers).json()
    assert next(a for a in full["axes"] if a["code"] == "CAPACITY")["capacity_plans"][0][
        "run_id"
    ] == str(cap.run_id)
    from tests.application.test_analysis_assessment import fields

    for axis in full["axes"]:
        for point in axis["items"]:
            data = fields()
            if getattr(w, "packet_runs", []):
                from app.modules.case.infrastructure.models.analysis_assessment import (
                    AnalysisAssessmentRecord,
                )

                with session_factory() as revision_session:
                    data["expected_revision"] = revision_session.scalar(
                        sa.select(
                            sa.func.coalesce(sa.func.max(AnalysisAssessmentRecord.revision), 0)
                        ).where(
                            AnalysisAssessmentRecord.tenant_id == w.actor.tenant_id,
                            AnalysisAssessmentRecord.case_id == w.case_id,
                            AnalysisAssessmentRecord.point_kind == point["kind"],
                            AnalysisAssessmentRecord.point_id
                            == __import__("uuid").UUID(point["item_id"]),
                        )
                    )
            data.pop("case_id", None)
            data.update(
                point_kind=point["kind"],
                point_id=point["item_id"],
                source_context_sha256=point["source_context_sha256"],
                treatment=dict(
                    axis_code=axis["code"],
                    applicability="UNKNOWN",
                    applicability_reason="Portée relue sans conclusion automatique.",
                    consequences=dict(
                        technical=None, price=None, delay=None, cash=None, contract=None
                    ),
                    unknown_reason="Hypothèses et preuves à compléter.",
                    action="Obtenir la preuve du point exact.",
                    responsible="SELF",
                    due_at=None,
                ),
            )
            data = {
                k: str(v) if isinstance(v, __import__("uuid").UUID) else v for k, v in data.items()
            }
            treated = http.client.post(
                f"/api/v1/cases/{w.case_id}/analysis-assessments",
                headers=http.patron_headers,
                json=data,
            )
            assert treated.status_code == 201, treated.text
    review_base = 0
    if getattr(w, "packet_runs", []):
        from app.modules.case.infrastructure.models.analysis_dossier import (
            AnalysisDossierReviewRecord,
        )

        with session_factory() as revision_session:
            review_base = revision_session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(AnalysisDossierReviewRecord.revision), 0)
                ).where(
                    AnalysisDossierReviewRecord.tenant_id == w.actor.tenant_id,
                    AnalysisDossierReviewRecord.case_id == w.case_id,
                )
            )
    for revision, phase in ((review_base, "PREPARED"), (review_base + 1, "REVIEWED")):
        full = http.client.get(url, headers=http.patron_headers).json()
        reviewed = http.client.post(
            f"/api/v1/cases/{w.case_id}/analysis-dossier-reviews",
            headers=http.patron_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                review_id=str(uuid4()),
                expected_revision=revision,
                dossier_sha256=full["dossier_sha256"],
                phase=phase,
                axes=[
                    dict(
                        code=a["code"],
                        state="UNKNOWN",
                        note="Sources relues, couverture non déduite.",
                        follow_up="Compléter les preuves.",
                        responsible="SELF",
                    )
                    for a in full["axes"]
                ],
                justification="Revue synthétique complète du dossier courant.",
                human_confirmed=True,
            ),
        )
        assert reviewed.status_code == 201, reviewed.text
    full = http.client.get(url, headers=http.patron_headers).json()
    assert full["dossier_review"]["state"] == "CURRENT"
    card = http.client.get(
        f"/api/v1/patron/cases/{w.case_id}/commitment-card", headers=http.patron_headers
    )
    assert card.status_code == 200, card.text
    assert any(
        r["aggregate_type"] == "CAPACITY_RUN" and r["aggregate_id"] == str(cap.run_id)
        for r in card.json()["references"]
    )
    if getattr(w, "new_cycle_receipt", None):
        decision_intent, decision = w.new_cycle_receipt
        w.new_cycle_receipt = None
    else:
        decision_intent = dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))
        decision = http.client.post(
            f"/api/v1/patron/cases/{w.case_id}/decisions",
            headers=http.patron_headers,
            json=decision_intent,
        )
    assert decision.status_code == 201, decision.text
    if getattr(w, "capture_packets", False):
        replayed_decision = http.client.post(
            f"/api/v1/patron/cases/{w.case_id}/decisions",
            headers=http.patron_headers,
            json=decision_intent,
        )
        assert replayed_decision.status_code == 200 and replayed_decision.json()["replayed"]
        assert replayed_decision.json()["decision_id"] == decision.json()["decision_id"]
    if getattr(w, "packet_runs", []):
        from app.modules.decision.infrastructure.models.decision import (
            DecisionConditionRecord,
            DecisionContextRecord,
            DecisionRecord,
        )

        with session_factory() as agreement_session:
            new_root = agreement_session.get(
                DecisionRecord, __import__("uuid").UUID(decision.json()["decision_id"])
            )
            prior_root = agreement_session.get(
                DecisionRecord, __import__("uuid").UUID(w.packet_runs[-1].decision_id)
            )
            assert (
                new_root.lifecycle == "DRAFT"
                and new_root.outcome == "UNDECIDED"
                and new_root.selected_final_context_id is None
            )
            assert new_root.cycle_number == prior_root.cycle_number + 1
            assert (
                prior_root.final_justification and prior_root.selected_final_context_id is not None
            )
            assert new_root.final_justification is None and new_root.finalized_at is None
            assert prior_root.validity == "REVIEW_REQUIRED" and prior_root.context_status == "STALE"
            assert (
                agreement_session.scalar(
                    sa.select(sa.func.count())
                    .select_from(DecisionContextRecord)
                    .where(
                        DecisionContextRecord.tenant_id == w.actor.tenant_id,
                        DecisionContextRecord.decision_id == new_root.id,
                    )
                )
                == 0
            )
            assert (
                agreement_session.scalar(
                    sa.select(sa.func.count())
                    .select_from(DecisionConditionRecord)
                    .where(
                        DecisionConditionRecord.tenant_id == w.actor.tenant_id,
                        DecisionConditionRecord.decision_id == new_root.id,
                    )
                )
                == 0
            )
    frozen = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions/{decision.json()['decision_id']}/context",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            context_id=str(uuid4()),
            expected_revision=decision.json()["version"],
            rationale="Références exactes, ressources inconnues conservées.",
            unknowns=["Réservation et couverture de ressources inconnues."],
            references=card.json()["references"],
        ),
    )
    assert frozen.status_code == 200, frozen.text
    package = uuid4()
    ready = http.client.post(
        f"/api/v1/collaborator/cases/{w.case_id}/preparation/readiness",
        headers=http.driver_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            package_id=str(package),
            assignment_id=str(http.assignment_id),
            dce_version_id=str(w.seed[2]),
            expected_revision=0,
        ),
    )
    assert ready.status_code == 201, ready.text
    from app.modules.preparation.infrastructure.models import PreparationReadinessRecord

    with session_factory() as s:
        readiness = s.scalar(
            sa.select(PreparationReadinessRecord).where(
                PreparationReadinessRecord.tenant_id == w.actor.tenant_id,
                PreparationReadinessRecord.package_id == package,
            )
        )
        assert readiness.state == "READY", readiness.blocker_codes_json
    generated = http.client.post(
        f"/api/v1/collaborator/preparation/{package}/documents",
        headers=http.driver_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=1,
            readiness_revision=1,
            document_kind="TECHNICAL_RESPONSE",
        ),
    )
    assert generated.status_code == 201, generated.text
    from app.modules.preparation.infrastructure.models import (
        GeneratedTechnicalDocumentRecord,
        TechnicalResponseDraftRecord,
    )

    with session_factory() as s:
        original = s.scalar(
            sa.select(GeneratedTechnicalDocumentRecord).where(
                GeneratedTechnicalDocumentRecord.tenant_id == w.actor.tenant_id,
                GeneratedTechnicalDocumentRecord.package_id == package,
            )
        )
        original_id = original.id
    insurance = next(
        p
        for axis in full["axes"]
        for p in axis["items"]
        if "assurance" in (p.get("source_excerpt") or "").casefold()
        and "attestation" not in (p.get("source_excerpt") or "").casefold()
    )
    from tests.support.transversal_affaire import insurance_proposal

    proof = insurance_proposal(
        session_factory, w, http, tmp_path, __import__("uuid").UUID(insurance["item_id"])
    )
    extra_item = None
    extra_contribution = getattr(
        w,
        "secondary_contribution",
        "La pièce synthétique d’assurance du lot 1 est référencée pour la revue.",
    )
    if assembly:
        second = next(
            p
            for axis in full["axes"]
            for p in axis["items"]
            if getattr(w, "secondary_clause", "attestation d'assurance")
            in (p.get("source_excerpt") or "").casefold()
        )
        extra_proof = getattr(w, "secondary_proof_factory", insurance_proposal)(
            session_factory,
            w,
            http,
            tmp_path,
            __import__("uuid").UUID(second["item_id"]),
            label_suffix=" — attestation",
        )
        extra_item = dict(
            requirement_id=second["item_id"],
            section_code="SOURCES",
            source_proposal_id=str(extra_proof.proposal_id),
        )
    plan_id = uuid4()
    plan = http.client.post(
        f"/api/v1/preparation/{package}/response-plans",
        headers=http.driver_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            plan_id=str(plan_id),
            expected_package_revision=2,
            items=[
                dict(
                    requirement_id=insurance["item_id"],
                    section_code="RISKS",
                    source_proposal_id=str(proof.proposal_id),
                ),
                *([extra_item] if extra_item else []),
            ],
        ),
    )
    assert plan.status_code == 201, plan.text
    draft_id = uuid4()
    contribution = (
        "Pour le lot 1, la couverture décennale déclarée est référencée par son attestation "
        "synthétique. Elle sera relue avant toute intervention ; cet essai ne prouve aucune "
        "couverture réelle."
    )
    draft_body: dict[str, Any] = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        draft_id=str(draft_id),
        source_document_id=str(original_id),
        expected_package_revision=3,
        section_codes=["RISKS"],
        source_refs=[str(proof.proposal_id)],
        contributions=[
            dict(
                requirement_id=insurance["item_id"],
                section_code="RISKS",
                content=contribution,
                missing="Autres exigences et pièces à traiter séparément, sans complétude déduite.",
            )
        ],
    )
    if assembly:
        assert extra_item is not None
        draft_body["section_codes"].append("SOURCES")
        draft_body["source_refs"].append(str(extra_proof.proposal_id))
        draft_body["contributions"].append(
            dict(
                requirement_id=extra_item["requirement_id"],
                section_code="SOURCES",
                content=extra_contribution,
                missing="Validité réelle et autres pièces : UNKNOWN.",
            )
        )
    draft = http.client.post(
        f"/api/v1/preparation/{package}/response-drafts",
        headers=http.driver_headers,
        json=draft_body,
    )
    assert draft.status_code == 201, draft.text
    replay = http.client.post(
        f"/api/v1/preparation/{package}/response-drafts",
        headers=http.driver_headers,
        json=draft_body,
    )
    assert replay.status_code == 200 and replay.json()["replayed"]
    with session_factory() as s:
        native = s.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                TechnicalResponseDraftRecord.draft_id == draft_id,
            )
        )
        from app.modules.preparation.infrastructure.models import PreparationPackageRecord

        parent = s.get(PreparationPackageRecord, native.package_id)
        assert (
            native.package_id == package
            and parent.case_id == w.case_id
            and parent.dce_version_id == w.seed[2]
        )
        digest = native.content_sha256
    if assembly:
        alternate = dict(
            draft_body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            draft_id=str(uuid4()),
            expected_package_revision=4,
        )
        alternate["contributions"] = [
            dict(c, content="Alternative non sélectionnée à relire.")
            for c in draft_body["contributions"]
        ]
        alt_response = http.client.post(
            f"/api/v1/preparation/{package}/response-drafts",
            headers=http.driver_headers,
            json=alternate,
        )
        assert alt_response.status_code == 201, alt_response.text
    if getattr(w, "packet_runs", []):
        prior = w.packet_runs[-1]
        reused = http.client.post(
            f"/api/v1/preparation/{package}/reviews",
            headers=http.patron_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                review_id=str(uuid4()),
                expected_package_revision=4 + revision_offset,
                target_draft_id=str(prior.draft_id),
                target_draft_version=1,
                target_content_sha256=prior.content_sha256,
            ),
        )
        assert reused.status_code == 422, reused.text
    review_id = uuid4()
    requested = http.client.post(
        f"/api/v1/preparation/{package}/reviews",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            review_id=str(review_id),
            expected_package_revision=4 + revision_offset,
            target_draft_id=str(draft_id),
            target_draft_version=1,
            target_content_sha256=digest,
        ),
    )
    assert requested.status_code == 201, requested.text
    approved = http.client.post(
        f"/api/v1/preparation/{package}/reviews/{review_id}/decision",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_review_revision=1,
            target_draft_id=str(draft_id),
            target_draft_version=1,
            target_content_sha256=digest,
            review_id=str(review_id),
            decision_code="ACCEPTED",
            decision_note=(
                "Revue synthétique de la contribution assurance, "
                "autres points non couverts visibles."
            ),
        ),
    )
    assert approved.status_code == 201, approved.text
    if buyer_docx:
        import io

        from app.modules.preparation.infrastructure.buyer_docx import inspect_template

        assert extra_item is not None
        template = w.docx_template_bytes
        regions = inspect_template(template)
        lookup = {r.locator: r for r in regions}
        output_id = uuid4()
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            draft_id=str(output_id),
            expected_package_revision=7,
            source_response=dict(draft_id=str(draft_id), version=1, content_sha256=digest),
            template=dict(
                document_id=str(w.seed[3]["cadre.docx"]),
                dce_version_id=str(w.seed[2]),
                sha256=__import__("hashlib").sha256(template).hexdigest(),
            ),
            fields=[
                dict(
                    locator="p:3",
                    expected_xml_sha256=lookup["p:3"].xml_sha256,
                    requirement_id=insurance["item_id"],
                    section_code="RISKS",
                ),
                dict(
                    locator="t:1/r:2/c:2/p:1",
                    expected_xml_sha256=lookup["t:1/r:2/c:2/p:1"].xml_sha256,
                    requirement_id=extra_item["requirement_id"],
                    section_code="SOURCES",
                ),
            ],
        )
        import copy

        # Refusals must not consume the package revision or produce a DOCX draft.
        for target, patch, reason in [
            ("template", {"sha256": "0" * 64}, "BUYER_TEMPLATE_UNKNOWN"),
            ("template", {"document_id": str(uuid4())}, "BUYER_TEMPLATE_UNKNOWN"),
            ("template", {"dce_version_id": str(uuid4())}, "BUYER_TEMPLATE_UNKNOWN"),
            ("source_response", {"content_sha256": "0" * 64}, "RESPONSE_DRAFT_UNKNOWN"),
            ("field", {"expected_xml_sha256": "0" * 64}, "DOCX_REGION_CHANGED"),
            ("field", {"requirement_id": str(uuid4())}, "BUYER_CONTRIBUTION_UNKNOWN"),
        ]:
            bad = copy.deepcopy(body)
            bad["command_id"], bad["idempotency_key"] = str(uuid4()), str(uuid4())
            (bad["fields"][0] if target == "field" else bad[target]).update(patch)
            refused_docx = http.client.post(
                f"/api/v1/preparation/{package}/buyer-response-drafts",
                headers=http.driver_headers,
                json=bad,
            )
            assert refused_docx.status_code == 422, refused_docx.text
            assert refused_docx.json()["detail"] == reason, refused_docx.text
        inspect_docx = http.client.post(
            f"/api/v1/preparation/{package}/buyer-docx-inputs",
            headers=http.driver_headers,
            json={"source_response": body["source_response"]},
        )
        assert inspect_docx.status_code == 200, inspect_docx.text
        assert inspect_docx.json()["package_revision"] == 7
        assert any(t["template"] == body["template"] for t in inspect_docx.json()["templates"])
        created_docx = http.client.post(
            f"/api/v1/preparation/{package}/buyer-response-drafts",
            headers=http.driver_headers,
            json=body,
        )
        assert created_docx.status_code == 201, created_docx.text
        replay_docx = http.client.post(
            f"/api/v1/preparation/{package}/buyer-response-drafts",
            headers=http.driver_headers,
            json=body,
        )
        assert replay_docx.status_code == 200 and replay_docx.json()["replayed"]
        with session_factory() as s:
            native_docx = s.scalar(
                sa.select(TechnicalResponseDraftRecord).where(
                    TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                    TechnicalResponseDraftRecord.draft_id == output_id,
                )
            )
            assert native_docx.content_format == "DOCX"
            assert any(
                r["state"] == "UNKNOWN" for r in native_docx.content_provenance_json["regions"]
            )
            digest = native_docx.content_sha256
        # A Markdown approval does not authorize a different binary piece.
        before_review = http.client.post(
            f"/api/v1/collaborator/preparation/{package}/snapshots",
            headers=http.driver_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                package_id=str(package),
                snapshot_id=str(uuid4()),
                expected_package_revision=8,
                selected_response_draft=dict(
                    draft_id=str(output_id), version=1, content_sha256=digest
                ),
            ),
        )
        assert (
            before_review.status_code == 422
            and before_review.json()["detail"] == "RESPONSE_DRAFT_REVIEW_REQUIRED"
        )
        for headers, prefix in [(http.driver_headers, "collaborator/"), (http.patron_headers, "")]:
            binary = http.client.get(
                f"/api/v1/{prefix}preparation/{package}/response-drafts/{output_id}/versions/1/content",
                headers=headers,
            )
            assert binary.status_code == 200, binary.text
            assert binary.headers["content-type"].startswith("application/vnd.openxmlformats")
            assert __import__("hashlib").sha256(binary.content).hexdigest() == digest
        w.docx_provenance = native_docx.content_provenance_json
        draft_id = output_id
        review_docx = uuid4()
        requested_docx = http.client.post(
            f"/api/v1/preparation/{package}/reviews",
            headers=http.patron_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                review_id=str(review_docx),
                expected_package_revision=8,
                target_draft_id=str(draft_id),
                target_draft_version=1,
                target_content_sha256=digest,
            ),
        )
        assert requested_docx.status_code == 201, requested_docx.text
        accepted_docx = http.client.post(
            f"/api/v1/preparation/{package}/reviews/{review_docx}/decision",
            headers=http.patron_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                review_id=str(review_docx),
                expected_review_revision=1,
                target_draft_id=str(draft_id),
                target_draft_version=1,
                target_content_sha256=digest,
                decision_code="ACCEPTED",
                decision_note="Pièce DOCX synthétique relue, champs UNKNOWN conservés.",
            ),
        )
        assert accepted_docx.status_code == 201, accepted_docx.text
        revision_offset += 3
    if assembly:
        projection = http.client.get(
            f"/api/v1/collaborator/preparation/{package}", headers=http.driver_headers
        )
        assert projection.status_code == 200, projection.text
        selected_projection = next(
            d for d in projection.json()["response_drafts"] if d["draft_id"] == str(draft_id)
        )
        assert selected_projection["content_sha256"] == digest
        assert selected_projection["response_plan_id"] == str(plan_id)
        assert extra_contribution in selected_projection["content"]
    from app.modules.preparation.infrastructure.document_storage import (
        LocalGeneratedDocumentStorage,
    )
    from app.modules.preparation.infrastructure.models import PreparationSnapshotRecord
    from app.platform.events.dispatcher import CommandExecutionError

    snapshot_id = uuid4()
    snapshot_body: dict[str, Any] = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        package_id=str(package),
        snapshot_id=str(snapshot_id),
        expected_package_revision=6 + revision_offset,
    )
    if assembly:
        snapshot_body["selected_response_draft"] = dict(
            draft_id=str(draft_id), version=1, content_sha256=digest
        )
    if assembly:
        from app.modules.dce.infrastructure.case_dce_reading_reader import (
            SqlAlchemyCaseDceReadingReader,
        )

        with session_factory() as coverage_session:
            coverage_lookup = SqlAlchemyCaseDceReadingReader(coverage_session).get(
                tenant_id=w.actor.tenant_id, case_id=w.case_id
            )
            assert coverage_lookup is not None
            reading = coverage_lookup.reading
            assert reading is not None
            expected_requirements = {
                str(point.requirement_id)
                for point in reading.requirements
                if point.document_family not in {"DPGF", "BPU"}
            }
        coverage_selection = snapshot_body["selected_response_draft"]
        for coverage_headers, prefix in [
            (http.driver_headers, "collaborator/"),
            (http.patron_headers, ""),
        ]:
            coverage = http.client.post(
                f"/api/v1/{prefix}preparation/{package}/response-coverage",
                headers=coverage_headers,
                json=coverage_selection,
            )
            assert coverage.status_code == 200, coverage.text
            coverage_view = coverage.json()
            assert coverage_view["selected_response"] == coverage_selection
            assert {
                row["requirement_id"] for row in coverage_view["requirements"]
            } == expected_requirements
            assert any(row["response_state"] == "MISSING" for row in coverage_view["requirements"])
            assert coverage_view["signature"] == coverage_view["coverage"] == "UNKNOWN"
            assert coverage_view["cited_annexes"]
            assert all(a["inclusion"] == "UNKNOWN" for a in coverage_view["cited_annexes"])
            if buyer_docx:
                locators = {
                    piece["locator"]
                    for row in coverage_view["requirements"]
                    for piece in row["pieces"]
                }
                assert locators == {"p:3", "t:1/r:2/c:2/p:1"}
            w.coverage_report = coverage_view
            import os

            if coverage_root := os.environ.get("SMART_AO_RESPONSE_COVERAGE_PROOF_DIR"):
                import json as proof_json
                from pathlib import Path

                destination = Path(coverage_root)
                destination.mkdir(mode=0o700, parents=True, exist_ok=True)
                (
                    destination / ("docx-coverage.json" if buyer_docx else "markdown-coverage.json")
                ).write_text(proof_json.dumps(coverage_view, ensure_ascii=False, indent=2))
    snapshot_url = f"/api/v1/collaborator/preparation/{package}/snapshots"
    if getattr(w, "source_annexes", False):
        snapshot_body["selected_annexes"] = [
            {key: item[key] for key in ("requirement_id", "document_id", "sha256")}
            for item in w.coverage_report["cited_annexes"]
            if item["document_id"] not in getattr(w, "omitted_annex_ids", set())
        ]
        snapshot_body["annex_justification"] = (
            "Pièces administratives sélectionnées pour les seules exigences liées."
        )
        if not getattr(w, "packet_runs", []):
            denied_annexes = http.client.post(
                snapshot_url, headers=http.driver_headers, json=snapshot_body
            )
            assert denied_annexes.status_code == 403, denied_annexes.text
            from app.modules.membership.infrastructure.records import CaseAssignmentRecord

            with session_factory.begin() as annex_session:
                preparation = annex_session.get(PreparationPackageRecord, package)
                assignment = annex_session.get(CaseAssignmentRecord, preparation.assignment_id)
                assignment.scope_classifications_json = [
                    *assignment.scope_classifications_json,
                    "PERSONAL_OR_ADMINISTRATIVE",
                ]
    if getattr(w, "source_annexes", False):
        import copy as annex_copy

        for patch in [
            {"sha256": "0" * 64},
            {"document_id": str(uuid4())},
            {"requirement_id": str(uuid4())},
        ]:
            invalid_annex = annex_copy.deepcopy(snapshot_body)
            invalid_annex["command_id"], invalid_annex["idempotency_key"] = (
                str(uuid4()),
                str(uuid4()),
            )
            invalid_annex["selected_annexes"][0].update(patch)
            refusal = http.client.post(
                snapshot_url, headers=http.driver_headers, json=invalid_annex
            )
            assert refusal.status_code == 422, refusal.text
    if getattr(w, "packet_runs", []):
        import copy as old_agreement_copy

        for key in ("selected_response_draft", "selected_annexes"):
            reused = old_agreement_copy.deepcopy(snapshot_body)
            reused["command_id"], reused["idempotency_key"] = str(uuid4()), str(uuid4())
            reused[key] = w.packet_runs[-1].snapshot_body[key]
            refused_old_selection = http.client.post(
                snapshot_url, headers=http.driver_headers, json=reused
            )
            assert refused_old_selection.status_code == 422, refused_old_selection.text
    if assembly:
        import copy

        # Choosing another version/hash/identity never falls back to any available response.
        for selection_patch in [
            dict(version=2),
            dict(content_sha256="0" * 64),
            dict(draft_id=str(uuid4())),
        ]:
            invalid = copy.deepcopy(snapshot_body)
            invalid["command_id"], invalid["idempotency_key"] = str(uuid4()), str(uuid4())
            invalid["selected_response_draft"].update(selection_patch)
            denied = http.client.post(snapshot_url, headers=http.driver_headers, json=invalid)
            assert (
                denied.status_code == 422
                and denied.json()["detail"] == "RESPONSE_DRAFT_SELECTION_UNKNOWN"
            )
    if assembly:
        with session_factory() as s:
            alt_native = s.scalar(
                sa.select(TechnicalResponseDraftRecord).where(
                    TechnicalResponseDraftRecord.draft_id
                    == __import__("uuid").UUID(alternate["draft_id"]),
                    TechnicalResponseDraftRecord.package_id == package,
                )
            )
            unreviewed = dict(
                snapshot_body,
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                selected_response_draft=dict(
                    draft_id=str(alt_native.draft_id),
                    version=alt_native.version,
                    content_sha256=alt_native.content_sha256,
                ),
            )
        denied = http.client.post(snapshot_url, headers=http.driver_headers, json=unreviewed)
        assert (
            denied.status_code == 422
            and denied.json()["detail"] == "RESPONSE_DRAFT_REVIEW_REQUIRED"
        )
    if buyer_docx:
        from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
        from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord

        with session_factory() as s:
            source_native = s.scalar(
                sa.select(TechnicalResponseDraftRecord).where(
                    TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                    TechnicalResponseDraftRecord.draft_id
                    == __import__("uuid").UUID(body["source_response"]["draft_id"]),
                    TechnicalResponseDraftRecord.version == 1,
                )
            )
            template_key = s.scalar(
                sa.select(DceStagedObjectRecord.storage_key)
                .join(
                    DceDocumentRecord,
                    DceDocumentRecord.storage_object_id == DceStagedObjectRecord.id,
                )
                .where(DceDocumentRecord.id == w.seed[3]["cadre.docx"])
            )
            source_key = source_native.storage_key
        read = LocalGeneratedDocumentStorage.read
        for corrupt_key in (source_key, template_key):

            def altered_source(storage, *, storage_key, expected_key=corrupt_key):
                return (
                    b"changed after exact review"
                    if storage_key == expected_key
                    else read(storage, storage_key=storage_key)
                )

            with monkeypatch.context() as corrupt:
                corrupt.setattr(LocalGeneratedDocumentStorage, "read", altered_source)
                stale = http.client.post(
                    snapshot_url,
                    headers=http.driver_headers,
                    json=dict(snapshot_body, command_id=str(uuid4()), idempotency_key=str(uuid4())),
                )
                assert stale.status_code == 422, stale.text
                assert stale.json()["detail"] in {
                    "BUYER_DOCX_SOURCE_UNKNOWN",
                    "BUYER_TEMPLATE_UNKNOWN",
                    "RESPONSE_DRAFT_UNKNOWN",
                }, stale.text
    write = LocalGeneratedDocumentStorage.write
    interrupted = False
    stored: dict[str, Any] = {}

    def interrupted_write(storage, *, storage_key, content):
        nonlocal interrupted
        result = write(storage, storage_key=storage_key, content=content)
        if not interrupted:
            interrupted = True
            stored.update(path=storage._path(storage_key), content=content)
            raise CommandExecutionError("SYNTHETIC_INTERRUPTED_AFTER_STORAGE_WRITE")
        return result

    with monkeypatch.context() as failure:
        failure.setattr(LocalGeneratedDocumentStorage, "write", interrupted_write)
        lost = http.client.post(snapshot_url, headers=http.driver_headers, json=snapshot_body)
    assert lost.status_code == 422 and interrupted
    stored["path"].write_bytes(b"altered uncommitted publication")
    refused = http.client.post(snapshot_url, headers=http.driver_headers, json=snapshot_body)
    assert refused.status_code == 422
    stored["path"].write_bytes(stored["content"])
    snapshot = http.client.post(snapshot_url, headers=http.driver_headers, json=snapshot_body)
    assert snapshot.status_code == 201, snapshot.text
    sent = http.client.post(
        f"/api/v1/collaborator/preparation/{package}/transmissions",
        headers=http.driver_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            package_id=str(package),
            snapshot_id=str(snapshot_id),
            transmission_id=str(uuid4()),
            expected_package_revision=7 + revision_offset,
        ),
    )
    assert sent.status_code == 201, sent.text
    condition_id = uuid4()
    decision_id = decision.json()["decision_id"]
    final = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions/{decision_id}/go-no-go",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=frozen.json()["version"],
            displayed_fingerprint=frozen.json()["fingerprint"],
            outcome="CONDITIONAL_GO",
            justification=(
                "Décision d’acteur fictif pour la qualification, "
                "sans GO réel ni couverture globale déduite."
            ),
            conditions=[
                dict(
                    condition_id=str(condition_id),
                    label="Vérifier les octets de la preuve synthétique sélectionnée.",
                    owner_actor_id=str(w.actor.actor_id),
                    due_date_absence_reason="Aucun délai légal calculé.",
                    failure_consequence="Maintenir la revue avant préparation du paquet.",
                )
            ],
        ),
    )
    assert final.status_code == 200, final.text
    resolved = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions/{decision_id}/conditions/{condition_id}/resolve",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            transition_id=str(uuid4()),
            expected_revision=final.json()["version"],
            target_status="SATISFIED",
            evidence_reference=f"enterprise-document://{proof.document_id}#sha256={proof.sha256}",
        ),
    )
    assert resolved.status_code == 200, resolved.text
    with session_factory() as s:
        origin = s.get(PreparationSnapshotRecord, snapshot_id)
        if assembly:
            assert (
                origin.manifest_json["selected_response_draft"]
                == snapshot_body["selected_response_draft"]
            )
            assert [d["draft_id"] for d in origin.manifest_json["response_drafts"]] == [
                str(draft_id)
            ]
        source_ref = dict(
            snapshot_id=str(snapshot_id),
            snapshot_version=origin.version,
            manifest_sha256=origin.manifest_sha256,
        )
        parent = s.get(PreparationPackageRecord, package)
        package_revision = parent.aggregate_revision
    candidate = http.client.post(
        f"/api/v1/patron/preparation/{package}/submission-packages",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_preparation_revision=package_revision,
            submission_mode="FULL",
            preparation_snapshot_source=source_ref,
        ),
    )
    assert candidate.status_code == 201, candidate.text
    from app.modules.submission.infrastructure.models import SubmissionPackageRecord

    candidate_id = candidate.json()["aggregate_refs"][0]["aggregate_id"]
    with session_factory() as s:
        submitted = s.get(SubmissionPackageRecord, __import__("uuid").UUID(candidate_id))
        candidate_version = submitted.version
        candidate_sha = submitted.manifest_sha256
    if getattr(w, "packet_runs", []):
        prior = w.packet_runs[-1]
        old_p5 = http.client.post(
            f"/api/v1/patron/submission-packages/{candidate_id}/authorize",
            headers=http.patron_headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                expected_package_version=candidate_version,
                expected_manifest_sha256=prior.candidate_sha,
                authorization_id=str(uuid4()),
                rationale="Ancien hash présenté volontairement pour refus.",
            ),
        )
        assert old_p5.status_code == 422 and old_p5.json() == {
            "detail": "SUBMISSION_MANIFEST_HASH_MISMATCH"
        }, old_p5.text
        before_new_p5 = http.client.get(
            f"/api/v1/patron/submission-packages/{candidate_id}/export", headers=http.patron_headers
        )
        assert before_new_p5.status_code == 422, before_new_p5.text
    authorization = http.client.post(
        f"/api/v1/patron/submission-packages/{candidate_id}/authorize",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            authorization_id=str(uuid4()),
            expected_package_version=candidate_version,
            expected_manifest_sha256=candidate_sha,
            rationale=(
                "Acteur fictif, candidat exact et sources relues "
                "pour la qualification locale uniquement."
            ),
        ),
    )
    assert authorization.status_code == 201, authorization.text
    # CT31-40 qualifies this local export after exact P5; it is never a buyer receipt.
    exported = http.client.get(
        f"/api/v1/patron/submission-packages/{candidate_id}/export", headers=http.patron_headers
    )
    assert exported.status_code == 200, f"Unexpected ZIP status {exported.status_code}"
    import io
    import zipfile
    from hashlib import sha256

    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        packed = json.loads(archive.read("manifest.json"))
        technical = archive.read(
            "technical-response.docx" if buyer_docx else "technical-response.md"
        )
        if buyer_docx:
            from app.modules.preparation.infrastructure.response_artifact import docx_text

            text = docx_text(technical)
            assert contribution in text and extra_contribution in text and "UNKNOWN" in text
            assert "Alternative non sélectionnée" not in text
            assert __import__("hashlib").sha256(technical).hexdigest() == digest
        else:
            assert contribution.encode() in technical
            if assembly:
                assert extra_contribution.encode() in technical
                assert "Alternative non sélectionnée".encode() not in technical
        assert packed["schema_version"] == 3
        if getattr(w, "source_annexes", False):
            frozen = packed["preparation_source"]["annexes"]
            assert len(frozen) == len({r["document_id"] for r in snapshot_body["selected_annexes"]})
            assert set(archive.namelist()) == {
                "manifest.json",
                "technical-response.docx" if buyer_docx else "technical-response.md",
                *(item["archive_path"] for item in frozen),
            }
            from app.bootstrap.application import _build_preparation_storage
            from app.modules.enterprise.infrastructure.models import EnterpriseDocumentUploadRecord

            with session_factory() as annex_session:
                for item in frozen:
                    upload = annex_session.scalar(
                        sa.select(EnterpriseDocumentUploadRecord).where(
                            EnterpriseDocumentUploadRecord.tenant_id == w.actor.tenant_id,
                            EnterpriseDocumentUploadRecord.document_id
                            == __import__("uuid").UUID(item["document_id"]),
                        )
                    )
                    original = _build_preparation_storage().read(storage_key=upload.storage_key)
                    assert archive.read(item["archive_path"]) == original
                    assert sha256(original).hexdigest() == item["sha256"]
                    assert item["signature"] == "UNKNOWN"
    if buyer_docx:
        w.exported_docx = technical
    if getattr(w, "source_annexes", False):
        import os as annex_os

        if annex_root := annex_os.environ.get("SMART_AO_ANNEX_PROOF_DIR"):
            from pathlib import Path as AnnexPath

            annex_destination = AnnexPath(annex_root)
            annex_destination.mkdir(parents=True, exist_ok=True)
            format_name = "docx" if buyer_docx else "markdown"
            (annex_destination / f"{format_name}-packet.zip").write_bytes(exported.content)
            (annex_destination / f"{format_name}-manifest.json").write_text(
                json.dumps(packed, ensure_ascii=False, indent=2)
            )
            (annex_destination / f"{format_name}-coverage.json").write_text(
                json.dumps(w.coverage_report, ensure_ascii=False, indent=2)
            )
    if getattr(w, "source_annexes", False):
        from app.bootstrap.application import _build_preparation_storage
        from app.modules.case.infrastructure.models.case import CaseRecord
        from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
        from app.modules.preparation.infrastructure.annexes import (
            annex_storage_key,
            frozen_annex_bytes,
        )
        from tests.db.test_candidate_retrieval_sql import _clone

        storage = _build_preparation_storage()
        frozen = packed["preparation_source"]["annexes"]
        copied = {
            item["document_id"]: frozen_annex_bytes(
                storage,
                tenant_id=w.actor.tenant_id,
                package_id=package,
                snapshot_id=snapshot_id,
                item=item,
            )
            for item in frozen
        }
        copied_item = frozen[0]
        copied_path = tmp_path / annex_storage_key(
            w.actor.tenant_id, package, snapshot_id, copied_item
        )
        copied_path.write_bytes(b"SYNTHETIC CORRUPTED COPY")
        corrupt_export = http.client.get(
            f"/api/v1/patron/submission-packages/{candidate_id}/export", headers=http.patron_headers
        )
        assert corrupt_export.status_code == 422
        copied_path.write_bytes(copied[copied_item["document_id"]])
        repeated_export = http.client.get(
            f"/api/v1/patron/submission-packages/{candidate_id}/export", headers=http.patron_headers
        )
        assert repeated_export.status_code == 200 and repeated_export.content == exported.content
        with session_factory() as annex_session:
            historical = annex_session.get(PreparationSnapshotRecord, snapshot_id)
            assert len(historical.manifest_json["documents"]) == 1 + len(frozen)
            historical_sha = historical.manifest_sha256
    if getattr(w, "capture_packets", False):
        w.packet_http = http
        w.packet_runs.append(
            SimpleNamespace(
                package_id=package,
                snapshot_id=snapshot_id,
                draft_id=draft_id,
                content_sha256=digest,
                manifest=packed,
                archive=exported.content,
                candidate_id=candidate_id,
                candidate_sha=candidate_sha,
                candidate_version=candidate_version,
                decision_id=decision_id,
                review_id=packed["preparation_source"]["response_drafts"][0]["review_id"],
                snapshot_body=snapshot_body,
            )
        )
        return
    outcome_id = uuid4()
    won = http.client.post(
        "/api/v1/patron/case-outcomes",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            outcome_id=str(outcome_id),
            case_id=str(w.case_id),
            lot_reference="1",
            outcome="WON",
            source_locator="attribution://synthetic/lot1",
            reservations=["Résultat fictif, aucun effet juridique réel."],
        ),
    )
    assert won.status_code == 201, won.text
    instrument_id = uuid4()
    contract = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/contract-instrument-versions",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            contract_instrument_version_id=str(instrument_id),
            instrument_kind="SIGNED_CONTRACT",
            version_reference="Contrat synthétique lot 1 — v1",
            source_refs=["contrat://synthetic/lot1/assurance"],
            evidence_refs=["preuve://synthetic/contrat/1"],
        ),
    )
    assert contract.status_code == 201, contract.text
    options = http.client.get(
        f"/api/v1/patron/cases/{w.case_id}/p7-handover/contracts", headers=http.patron_headers
    )
    assert options.status_code == 200, options.text
    selected = next(
        c for c in options.json()["items"] if c["instrument_version_id"] == str(instrument_id)
    )
    handover_id, point_id = uuid4(), uuid4()
    transfer_body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        correlation_id=str(uuid4()),
        snapshot_id=str(handover_id),
        outcome_id=str(outcome_id),
        submission_package_id=candidate_id,
        operational_review=dict(
            expected_source_context_sha256=options.json()["source_context_sha256"],
            expected_handover_revision=0,
            expected_offer_manifest_sha256=candidate_sha,
            contract_instrument_version_id=str(instrument_id),
            expected_contract_record_sha256=selected["record_sha256"],
            justification="Rapprochement humain fictif de la réponse revue et du contrat déclaré.",
            human_confirmed=True,
            points=[
                dict(
                    point_id=str(point_id),
                    kind="ENGAGEMENT",
                    statement="Relire la couverture déclarée du lot 1 avant intervention.",
                    offer_excerpt=contribution,
                    offer_locator="Réponse revue §RISKS, assurance",
                    contract_locator="Contrat déclaré §assurance",
                    difference_state="UNKNOWN",
                    responsible="Conducteur synthétique",
                    action="Obtenir une attestation réelle avant usage.",
                    expected_evidence="Attestation à qualifier hors essai.",
                    criticality="CRITICAL",
                )
            ],
        ),
    )
    published = http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/p7-handover",
        headers=http.patron_headers,
        json=transfer_body,
    )
    assert published.status_code == 201, published.text
    operational = http.client.get(
        f"/api/v1/cases/{w.case_id}/p7-handover", headers=http.driver_headers
    )
    assert operational.status_code == 200, operational.text
    view = operational.json()["items"][0]
    assert view["source_state"] == "CURRENT"
    downloaded = http.client.get(
        f"/api/v1/cases/{w.case_id}/p7-handover/{handover_id}/offer-document",
        headers=http.driver_headers,
    )
    assert downloaded.status_code == 200, (
        f"Unexpected offer document status {downloaded.status_code}"
    )
    if buyer_docx:
        assert downloaded.headers["content-type"].startswith("application/vnd.openxmlformats")
        assert downloaded.headers["content-disposition"].endswith('offre-technique.docx"')
    assert downloaded.content == technical, (
        "Conducteur received an earlier template instead of the exact reviewed offer"
    )
    if getattr(w, "source_annexes", False):
        with session_factory.begin() as annex_session:
            case = annex_session.get(CaseRecord, w.case_id)
            old_version = annex_session.get(DceVersionRecord, case.applicable_dce_version_id)
            replacement = uuid4()
            annex_session.add(
                _clone(
                    old_version,
                    id=replacement,
                    predecessor_dce_version_id=old_version.id,
                    corpus_hash=sha256(str(replacement).encode()).hexdigest(),
                )
            )
            annex_session.flush()
            case.applicable_dce_version_id = replacement
            case.dce_freshness = "CURRENT"
        refused_old = http.client.get(
            f"/api/v1/patron/submission-packages/{candidate_id}/export", headers=http.patron_headers
        )
        assert refused_old.status_code in {409, 422}, refused_old.text
        refused_snapshot = dict(
            snapshot_body,
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            snapshot_id=str(uuid4()),
        )
        with session_factory() as annex_session:
            refused_snapshot["expected_package_revision"] = annex_session.get(
                PreparationPackageRecord, package
            ).aggregate_revision
        refused_reuse = http.client.post(
            snapshot_url, headers=http.driver_headers, json=refused_snapshot
        )
        assert refused_reuse.status_code == 422, refused_reuse.text
        with session_factory() as annex_session:
            assert (
                annex_session.get(PreparationSnapshotRecord, snapshot_id).manifest_sha256
                == historical_sha
            )
        for item in frozen:
            assert (
                frozen_annex_bytes(
                    storage,
                    tenant_id=w.actor.tenant_id,
                    package_id=package,
                    snapshot_id=snapshot_id,
                    item=item,
                )
                == copied[item["document_id"]]
            )
        w.exported_annex_zip = exported.content
        http.client.close()
        return
    from tests.support.transversal_affaire import finish_execution_and_reuse

    finish_execution_and_reuse(
        http, w, handover_id=handover_id, point_id=point_id, instrument_id=instrument_id, view=view
    )
    http.client.close()


def test_reclassification_is_a_new_analysis_input_not_a_changed_retry(session_factory, affaire):
    import sqlalchemy as sa
    from app.modules.dce.infrastructure.models.dce_version import DceDocumentClassificationRecord
    from tests.application.test_dce_rc_analysis import _analysis_service

    w = affaire
    document = w.seed[3]["rc.txt"]
    with session_factory.begin() as s:
        previous = s.scalar(
            sa.select(DceDocumentClassificationRecord).where(
                DceDocumentClassificationRecord.tenant_id == w.actor.tenant_id,
                DceDocumentClassificationRecord.dce_document_id == document,
                DceDocumentClassificationRecord.is_current.is_(True),
            )
        )
        previous.is_current = False
        s.flush()
        s.add(
            DceDocumentClassificationRecord(
                id=uuid4(),
                tenant_id=w.actor.tenant_id,
                dce_document_id=document,
                classification="CCTP",
                source="SYNTHETIC",
                rationale="Reclassification synthétique de contrôle.",
                previous_classification_id=previous.id,
                is_current=True,
                created_by_actor_id=None,
            )
        )
    result = _analysis_service(session_factory=session_factory).analyze(
        tenant_id=w.actor.tenant_id, dce_version_id=w.seed[2], now=w.now
    )
    assert not result.replayed, "Classification changed but the old analysis was silently replayed"
