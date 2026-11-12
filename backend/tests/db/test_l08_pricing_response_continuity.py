"""Native revised workbook -> fresh C10 review/snapshot -> independently authorized ZIP."""

import json
import shutil
from copy import deepcopy
from hashlib import sha256
from io import BytesIO
from uuid import UUID, uuid4
from zipfile import ZipFile

import sqlalchemy as sa
from app.modules.preparation.infrastructure.models import (
    PreparationPackageRecord,
    PreparationResponsePlanRecord,
    PreparationSnapshotRecord,
    TechnicalResponseDraftRecord,
)
from app.modules.pricing.infrastructure.models import FinancialReportSnapshotRecord
from app.modules.submission.infrastructure.models import SubmissionPackageRecord
from tests.application.test_pricing_workbook_completeness import workbook_payload
from tests.db import test_transversal_affaire_workflow as flow


def test_revised_prices_rebuild_a_sourced_response_packet_with_new_human_acts(
    session_factory, tmp_path, monkeypatch, handover_qualifier=None, pricing_qualifier=None
):
    from tests.db import test_l04_multilot_pipeline as pipeline

    development = tmp_path / "development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    ccap = corpus / "ccap.txt"
    ccap.write_text(
        ccap.read_text() + "\nUne attestation d'assurance décennale est exigée pour le lot 1.\n"
    )
    manifest = json.loads((corpus / "manifest.json").read_text())
    next(row for row in manifest["documents"] if row["file"] == "ccap.txt")["sha256"] = sha256(
        ccap.read_bytes()
    ).hexdigest()
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    w = flow.affaire.__wrapped__(session_factory, tmp_path)
    w.source_annexes = w.response_assembly = w.capture_packets = True
    w.packet_runs = []
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, w, tmp_path, monkeypatch
    )
    first = w.packet_runs[0]
    http = w.packet_http
    case_root = f"/api/v1/patron/cases/{w.case_id}"
    package = UUID(str(first.package_id))

    def post(path, body, *, headers=None, status=201):
        response = http.client.post(path, json=body, headers=headers or http.patron_headers)
        assert response.status_code == status, response.text
        return response.json()

    def get(path):
        response = http.client.get(path, headers=http.patron_headers)
        assert response.status_code == 200, response.text
        assert response.headers.get("cache-control") == "no-store"
        return response.json()

    def ids():
        return dict(command_id=str(uuid4()), idempotency_key=str(uuid4()))

    def revision(model, identifier):
        with session_factory() as session:
            return session.get(model, UUID(str(identifier))).aggregate_revision

    control_url = f"/api/v1/patron/submission-packages/{first.candidate_id}/final-control"
    before = get(control_url)
    assert before["pricing_reference"]["state"] == "CURRENT"
    assert before["p5_authorization_status"] == "RECORDED"
    assert "OFFICIAL_PRICING_VERSION" in before["entries_without_exported_file"]
    if handover_qualifier is not None:
        handover_qualifier(session_factory, http, first, before, 1, w)
    created = post(case_root + "/financial-reports/drafts", dict(ids(), currency_code="EUR"))
    report = created["aggregate_refs"][0]["aggregate_id"]
    original = workbook_payload(
        [
            (
                "Prix révisés",
                [
                    ["Code", "Désignation", "Unité", "Quantité", "Prix unitaire"],
                    ["A", "Pompe révisée", "u", 2, 300],
                ],
            )
        ]
    )
    http.allowed_scans.add(sha256(original).hexdigest())
    preview = http.client.post(
        case_root + "/pricing-import/preview",
        headers={
            **http.patron_headers,
            "X-Command-Id": str(uuid4()),
            "Idempotency-Key": str(uuid4()),
        },
        files={
            "upload": (
                "prix-revises.xlsx",
                original,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert preview.status_code == 201, preview.text
    batch = preview.json()["batch_id"]
    assert preview.json()["rows"][0]["source_locator"]["sheet"] == "Prix révisés"
    commit = dict(ids(), report_id=report, expected_batch_revision=1, expected_report_revision=0)
    post(case_root + f"/pricing-import/{batch}/commit", commit)
    assert post(case_root + f"/pricing-import/{batch}/commit", commit, status=200)["replayed"]
    post(
        case_root + f"/financial-reports/{report}/lines",
        dict(
            ids(),
            expected_revision=revision(FinancialReportSnapshotRecord, report),
            category="DIRECT_COST",
            label="Hypothèse de coût révisée, transport non couvert",
            quantity_decimal="1",
            unit="u",
            amount_minor=17000,
        ),
    )
    post(
        case_root + f"/financial-reports/{report}/publications",
        dict(
            ids(),
            expected_revision=revision(FinancialReportSnapshotRecord, report),
        ),
    )
    revised = get(control_url)
    assert revised["pricing_reference"]["state"] == "REVIEW_REQUIRED"
    assert revised["pricing_reference"]["referenced"] == before["pricing_reference"]["referenced"]
    assert revised["pricing_reference"]["latest_published"]["report_id"] == report
    assert revised["manifest_sha256"] == first.candidate_sha
    assert revised["p5_authorization_id"] == before["p5_authorization_id"]
    if pricing_qualifier is not None:
        pricing_qualifier(session_factory, http, w, report)

    # A prior review cannot be reissued for the same immutable draft.
    post(
        f"/api/v1/preparation/{package}/reviews",
        dict(
            ids(),
            review_id=str(uuid4()),
            expected_package_revision=revision(PreparationPackageRecord, package),
            target_draft_id=str(first.draft_id),
            target_draft_version=1,
            target_content_sha256=first.content_sha256,
        ),
        status=422,
    )
    with session_factory() as session:
        old_draft = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                TechnicalResponseDraftRecord.draft_id == UUID(str(first.draft_id)),
                TechnicalResponseDraftRecord.version == 1,
            )
        )
        source_document = str(old_draft.source_document_id)
        sections, source_refs = old_draft.section_codes_json, old_draft.source_refs_json
        plan = session.scalar(
            sa.select(PreparationResponsePlanRecord).where(
                PreparationResponsePlanRecord.tenant_id == w.actor.tenant_id,
                PreparationResponsePlanRecord.package_id == package,
                PreparationResponsePlanRecord.plan_id == old_draft.response_plan_id,
                PreparationResponsePlanRecord.version == old_draft.response_plan_version,
            )
        )
        plan_items = plan.content_json["items"]
    new_draft = str(uuid4())
    post(
        f"/api/v1/preparation/{package}/response-drafts",
        dict(
            ids(),
            draft_id=new_draft,
            source_document_id=source_document,
            expected_package_revision=revision(PreparationPackageRecord, package),
            section_codes=sections,
            source_refs=source_refs,
            contributions=[
                dict(
                    requirement_id=item["requirement_id"],
                    section_code=item["section_code"],
                    content="Pièce synthétique référencée et relue pour cette nouvelle réponse.",
                    missing="Validité réelle et autres pièces : UNKNOWN.",
                )
                for item in plan_items
            ],
        ),
        headers=http.driver_headers,
    )
    with session_factory() as session:
        fresh_draft = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                TechnicalResponseDraftRecord.draft_id == UUID(new_draft),
                TechnicalResponseDraftRecord.version == 1,
            )
        )
        new_content_sha = fresh_draft.content_sha256
    review = str(uuid4())
    target = dict(
        target_draft_id=new_draft, target_draft_version=1, target_content_sha256=new_content_sha
    )
    review_root = f"/api/v1/preparation/{package}/reviews"
    post(
        review_root,
        dict(
            ids(),
            review_id=review,
            expected_package_revision=revision(PreparationPackageRecord, package),
            **target,
        ),
    )
    post(
        review_root + f"/{review}/decision",
        dict(
            ids(),
            review_id=review,
            expected_review_revision=1,
            **target,
            decision_code="ACCEPTED",
            decision_note="Prix 17000 EUR à recopier.",
        ),
        status=422,
    )
    post(
        review_root + f"/{review}/decision",
        dict(
            ids(),
            review_id=review,
            expected_review_revision=1,
            **target,
            decision_code="ACCEPTED",
            decision_note="Nouvelle revue du brouillon et des pièces sourcées ; manques conservés.",
        ),
    )
    snapshot_body = deepcopy(first.snapshot_body)
    snapshot = str(uuid4())
    snapshot_body["selected_response_draft"] = dict(
        draft_id=new_draft, version=1, content_sha256=new_content_sha
    )
    snapshot_body.update(
        ids(),
        snapshot_id=snapshot,
        expected_package_revision=revision(PreparationPackageRecord, package),
    )
    post(
        f"/api/v1/collaborator/preparation/{package}/snapshots",
        snapshot_body,
        headers=http.driver_headers,
    )
    post(
        f"/api/v1/collaborator/preparation/{package}/transmissions",
        dict(
            ids(),
            package_id=str(package),
            snapshot_id=snapshot,
            transmission_id=str(uuid4()),
            expected_package_revision=revision(PreparationPackageRecord, package),
        ),
        headers=http.driver_headers,
    )
    with session_factory() as session:
        frozen = session.get(PreparationSnapshotRecord, UUID(snapshot))
        source = dict(
            snapshot_id=snapshot,
            snapshot_version=frozen.version,
            manifest_sha256=frozen.manifest_sha256,
        )
    candidate = post(
        f"/api/v1/patron/preparation/{package}/submission-packages",
        dict(
            ids(),
            expected_preparation_revision=revision(PreparationPackageRecord, package),
            submission_mode="FULL",
            preparation_snapshot_source=source,
        ),
    )
    candidate_id = candidate["aggregate_refs"][0]["aggregate_id"]
    with session_factory() as session:
        record = session.get(SubmissionPackageRecord, UUID(candidate_id))
        package_version, digest = record.version, record.manifest_sha256
    fresh_url = f"/api/v1/patron/submission-packages/{candidate_id}"
    fresh = get(fresh_url + "/final-control")
    assert fresh["pricing_reference"]["state"] == "CURRENT"
    assert fresh["pricing_reference"]["referenced"]["report_id"] == report
    assert fresh["p5_authorization_status"] == "NOT_RECORDED"
    assert fresh["patron_review_ids"] == [review] and review != first.review_id
    assert digest != first.candidate_sha and snapshot != str(first.snapshot_id)
    assert http.client.get(fresh_url + "/export", headers=http.patron_headers).status_code == 422
    post(
        fresh_url + "/authorize",
        dict(
            ids(),
            authorization_id=str(uuid4()),
            expected_package_version=package_version,
            expected_manifest_sha256=first.candidate_sha,
            rationale="Ancien accord présenté pour refus.",
        ),
        status=422,
    )
    authorization = str(uuid4())
    p5 = dict(
        ids(),
        authorization_id=authorization,
        expected_package_version=package_version,
        expected_manifest_sha256=digest,
        rationale="Pli et référence du chiffrage révisé relus ; manques toujours explicites.",
    )
    post(fresh_url + "/authorize", p5)
    assert post(fresh_url + "/authorize", p5, status=200)["replayed"]
    archive = http.client.get(fresh_url + "/export", headers=http.patron_headers)
    assert archive.status_code == 200, archive.text
    with ZipFile(BytesIO(archive.content)) as bundle:
        manifest = bundle.read("manifest.json")
        assert sha256(manifest).hexdigest() == digest
        parsed = json.loads(manifest)
        price = next(e for e in parsed["entries"] if e["kind"] == "OFFICIAL_PRICING_VERSION")
        assert price["snapshot_id"] == report
        assert "financial_amounts" in parsed["exclusions"]
        assert not any("prix-revises" in name for name in bundle.namelist())
    final = get(fresh_url + "/final-control")
    assert final["p5_authorization_id"] == authorization != before["p5_authorization_id"]
    assert "OFFICIAL_PRICING_VERSION" in final["entries_without_exported_file"]
    assert final["conformity"] == final["signature_verification"] == "UNKNOWN"
    assert any(r["response_state"] == "MISSING" for r in final["requirements"])
    assert (
        http.client.get(fresh_url + "/final-control", headers=http.driver_headers).status_code
        == 403
    )
    assert "sales_total_minor" not in json.dumps(final) and "storage_key" not in json.dumps(final)
    (tmp_path / "l08-pricing-controls.json").write_text(
        json.dumps(
            dict(
                first=before,
                revised=revised,
                fresh=final,
            )
        )
    )
    (tmp_path / "revised-packet.zip").write_bytes(archive.content)
    if handover_qualifier is not None:
        from types import SimpleNamespace

        rebuilt = SimpleNamespace(
            candidate_id=candidate_id,
            candidate_sha=digest,
            candidate_version=package_version,
            package_id=package,
            snapshot_id=snapshot,
            draft_id=new_draft,
            content_sha256=new_content_sha,
            review_id=review,
            archive=archive.content,
            decision_id=first.decision_id,
        )
        handover_qualifier(session_factory, http, rebuilt, final, 2, w)
    http.client.close()
