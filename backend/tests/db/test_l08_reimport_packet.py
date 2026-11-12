"""One Case, real synthetic reimport, two exact packets with independent human acts."""

from __future__ import annotations

import asyncio
import io
import json
import shutil
from datetime import timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application import commands as cmds
from app.modules.dce.application import handlers as hs
from app.modules.dce.application.classification import DceDocumentClassificationService
from app.modules.dce.application.requirements import DceRequirementsService
from app.modules.dce.application.upload import DceUploadService, MalwareScanResult
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.dce.infrastructure.quarantine import (
    LocalQuarantineStorageAdapter,
    PythonMagicContentInspectionAdapter,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from docx import Document
from tests.application.test_dce_rc_analysis import _analysis_service, _extraction_service, _stream
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db import test_transversal_affaire_workflow as flow


class FixtureScanner:
    def __init__(self, storage, allowed, now):
        self.storage, self.allowed, self.now = storage, allowed, now

    async def scan(self, *, storage_key):
        raw = self.storage.read_verified_bytes(storage_key=storage_key, max_bytes=150_000_000)
        return MalwareScanResult(
            verdict="CLEAN" if sha256(raw).hexdigest() in self.allowed else "ERROR",
            scanner_name="SYNTHETIC_SHA_ALLOWLIST",
            scanner_signature_version="fixture-v1",
            scanned_at=self.now,
        )


def import_rectification(factory, w, root):
    from app.bootstrap.application import _ALLOWED_DCE_MEDIA_TYPES
    from app.modules.case.application.commands import LinkCaseDceVersionCommand
    from app.modules.case.application.link_dce_version_handler import LinkCaseDceVersionHandler

    with factory() as session:
        version = session.get(DceVersionRecord, w.seed[2])
        consultation = version.consultation_id
        sources = session.scalars(
            sa.select(DceDocumentRecord).where(
                DceDocumentRecord.tenant_id == w.seed[0],
                DceDocumentRecord.dce_version_id == version.id,
            )
        ).all()
    storage = LocalQuarantineStorageAdapter(root=root)
    payloads: dict[str, tuple[str, bytes]] = {}
    for document in sources:
        if document.original_filename.endswith(".txt"):
            source_text = storage.read_verified_bytes(
                storage_key=document.storage_key, max_bytes=150_000_000
            ).decode()
            native = Document()
            family_titles = {
                "rc.txt": "Règlement de la consultation",
                "reglement-consultation.txt": "Règlement de la consultation",
                "ccap.txt": "CCAP",
                "dpgf.txt": "DPGF",
                "bordereau.txt": "Règlement de la consultation",
            }
            native.add_paragraph(family_titles.get(document.original_filename, "CCTP"))
            native.add_paragraph("Version synthétique V2 — nouvelles sources à relire.")
            for line in source_text.splitlines():
                native.add_paragraph(line.replace("30 novembre 2026", "15 décembre 2026"))
            out = io.BytesIO()
            native.save(out)
            payloads[document.original_filename] = (
                document.original_filename[:-4] + ".docx",
                out.getvalue(),
            )
        elif document.original_filename == "cadre.docx":
            raw = storage.read_verified_bytes(
                storage_key=document.storage_key, max_bytes=150_000_000
            )
            native = Document(io.BytesIO(raw))
            native.paragraphs[0].text = "Annexe — cadre acheteur synthétique V2"
            out = io.BytesIO()
            native.save(out)
            payloads[document.original_filename] = (document.original_filename, out.getvalue())
            w.docx_template_bytes = out.getvalue()
        else:
            raise AssertionError("Only these explicit synthetic originals are qualified")
    dispatcher = CommandDispatcher(
        session_factory=factory,
        handlers={
            "PrepareDceStaging": hs.PrepareDceStagingHandler(),
            "ClaimDceStagedObjectUpload": hs.ClaimDceStagedObjectUploadHandler(),
            "RecordDceStagedObjectQuarantine": hs.RecordDceStagedObjectQuarantineHandler(),
            "RecordDceStagedObjectScan": hs.RecordDceStagedObjectScanHandler(),
            "RejectDceStagedObjectUpload": hs.RejectDceStagedObjectUploadHandler(),
            "RegisterDceVersion": hs.RegisterDceVersionHandler(),
            "RecordDceDocumentClassificationRun": hs.RecordDceDocumentClassificationRunHandler(),
            "RecordDceRequirementMaterializationRun": (
                hs.RecordDceRequirementMaterializationRunHandler()
            ),
            "LinkCaseDceVersion": LinkCaseDceVersionHandler(),
        },
    )
    context = CommandContext(
        tenant_id=w.actor.tenant_id,
        actor_id=w.actor.actor_id,
        actor_kind="PATRON_ADMIN",
        membership_id=w.actor.membership_id,
        received_at=w.now,
    )
    uploader = DceUploadService(
        dispatcher=dispatcher,
        storage=storage,
        inspector=PythonMagicContentInspectionAdapter(storage=storage),
        scanner=FixtureScanner(
            storage, {sha256(raw).hexdigest() for _, raw in payloads.values()}, w.now
        ),
        allowed_media_types=_ALLOWED_DCE_MEDIA_TYPES,
        max_bytes=150_000_000,
    )
    documents = []
    ids = {}
    for old_name, (filename, raw) in payloads.items():
        with factory() as session:
            revision = session.get(ConsultationRecord, consultation).aggregate_revision
        staged, document = uuid4(), uuid4()
        claim = cmds.PrepareDceStagingCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            storage_object_id=staged,
            consultation_id=consultation,
            consultation_revision=revision,
            original_filename=filename,
            expected_byte_size=len(raw),
            source_channel="RECTIFICATION",
            expires_at=w.now + timedelta(hours=1),
        )
        dispatcher.dispatch(command=claim, context=context)
        with factory() as session:
            key = session.get(DceStagedObjectRecord, staged).storage_key
        result = asyncio.run(
            uploader.upload(
                tenant_id=w.actor.tenant_id,
                actor_id=w.actor.actor_id,
                actor_kind="PATRON_ADMIN",
                storage_object_id=staged,
                storage_key=key,
                expected_byte_size=len(raw),
                idempotency_key=uuid4(),
                stream=_stream(raw),
                content_length=len(raw),
            )
        )
        assert result.state == "CLEAN"
        documents.append(dict(document_id=document, storage_object_id=staged))
        ids[old_name] = document
    with factory() as session:
        revision = session.get(ConsultationRecord, consultation).aggregate_revision
    new_version = uuid4()
    admit = cmds.RegisterDceVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        dce_version_id=new_version,
        consultation_id=consultation,
        consultation_revision=revision,
        corpus_hash=sha256(
            "\n".join(sorted(sha256(raw).hexdigest() for _, raw in payloads.values())).encode(
                "ascii"
            )
        ).hexdigest(),
        provenance_channel="RECTIFICATION",
        provenance_reference=f"synthetic-rectification:{w.seed[2]}",
        source_received_at=w.now,
        documents=documents,
    )
    dispatcher.dispatch(command=admit, context=context)
    assert dispatcher.dispatch(command=admit, context=context).replayed
    for document in ids.values():
        asyncio.run(
            _extraction_service(session_factory=factory, storage=storage).extract(
                tenant_id=w.seed[0], dce_document_id=document, now=w.now
            )
        )
    DceDocumentClassificationService(session_factory=factory, dispatcher=dispatcher).classify(
        tenant_id=w.seed[0], dce_version_id=new_version, now=w.now
    )
    analysis = _analysis_service(session_factory=factory).analyze(
        tenant_id=w.seed[0], dce_version_id=new_version, now=w.now
    )
    DceRequirementsService(session_factory=factory, dispatcher=dispatcher).materialize(
        tenant_id=w.seed[0],
        dce_version_id=new_version,
        dce_rc_analysis_id=UUID(str(analysis.aggregate_refs[0]["aggregate_id"])),
        now=w.now,
    )
    with factory() as session:
        revision = session.get(CaseRecord, w.case_id).aggregate_revision
    link = LinkCaseDceVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=w.case_id,
        dce_version_id=new_version,
        expected_case_revision=revision,
        reason="Réimport et adoption explicite du rectificatif synthétique V2.",
    )
    dispatcher.dispatch(command=link, context=context)
    assert dispatcher.dispatch(command=link, context=context).replayed
    return new_version, ids


@pytest.mark.parametrize("technical_docx", [False, True])
def test_rectification_reimport_rebuilds_an_exact_packet_without_transferring_agreements(
    session_factory, tmp_path, monkeypatch, technical_docx, configure_workflow=None
):
    import secrets

    from tests.support.final_control import qualify_final_control

    callback_secret = secrets.token_hex(32)
    monkeypatch.setenv("SMART_AO_SIGNATURE_PROVIDER", "TEST_PROVIDER")
    monkeypatch.setenv("SMART_AO_SIGNATURE_CALLBACK_SECRET", callback_secret)
    development = tmp_path / "development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    ccap = corpus / "ccap.txt"
    ccap.write_text(
        ccap.read_text() + "\nUne attestation d'assurance décennale est exigée pour le lot 1.\n"
    )
    manifest = json.loads((corpus / "manifest.json").read_text())
    next(d for d in manifest["documents"] if d["file"] == "ccap.txt")["sha256"] = sha256(
        ccap.read_bytes()
    ).hexdigest()
    if technical_docx:
        native = Document()
        native.add_heading("Cadre acheteur synthétique — assurances", 0)
        native.add_paragraph("Engagement synthétique lot 1, à relire.")
        native.add_paragraph("[[REPONSE:COUVERTURE]]")
        table = native.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Rubrique acheteur"
        table.cell(0, 1).text = "Réponse"
        table.cell(1, 0).text = "Pièces assurance lot 1"
        table.cell(1, 1).text = "[[REPONSE:ATTESTATION]]"
        native.add_paragraph("[[REPONSE:AUTRE]]")
        out = io.BytesIO()
        native.save(out)
        frame = out.getvalue()
        (corpus / "cadre.docx").write_bytes(frame)
        manifest["documents"].append(
            dict(
                file="cadre.docx",
                family="ANNEXE",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                sha256=sha256(frame).hexdigest(),
            )
        )
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    w = flow.affaire.__wrapped__(session_factory, tmp_path)
    if technical_docx:
        w.buyer_docx = True
        w.docx_template_bytes = frame
    w.source_annexes = True
    w.response_assembly = True
    w.capture_packets = True
    w.packet_runs = []
    if configure_workflow is not None:
        configure_workflow(w)
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, w, tmp_path, monkeypatch
    )
    first = w.packet_runs[0]
    first_control = qualify_final_control(
        session_factory,
        w.packet_http,
        first,
        callback_secret=callback_secret,
    )
    old_version = w.seed[2]
    duplicate = w.packet_http.client.post(
        f"/api/v1/patron/cases/{w.case_id}/decisions",
        headers=w.packet_http.patron_headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
    )
    assert duplicate.status_code == 409 and duplicate.json() == {
        "detail": "DECISION_ALREADY_ACTIVE"
    }
    new_version, ids = import_rectification(session_factory, w, tmp_path)
    stale = w.packet_http.client.get(
        f"/api/v1/patron/submission-packages/{first.candidate_id}/final-control",
        headers=w.packet_http.patron_headers,
    )
    assert stale.status_code == 200, stale.text
    assert stale.json()["state"] == stale.json()["source_state"] == "REVIEW_REQUIRED"
    assert stale.json()["requirements"] == []
    w.stale_final_control = stale.json()
    assert all(f["presence"] == "UNKNOWN" for f in stale.json()["files"])
    denied = w.packet_http.client.get(
        f"/api/v1/patron/submission-packages/{first.candidate_id}/export",
        headers=w.packet_http.patron_headers,
    )
    assert denied.status_code == 422
    w.stale_export_status = denied.status_code
    from concurrent.futures import ThreadPoolExecutor

    intents = [dict(command_id=str(uuid4()), idempotency_key=str(uuid4())) for _ in range(2)]

    def create_current_cycle(body):
        return w.packet_http.client.post(
            f"/api/v1/patron/cases/{w.case_id}/decisions",
            headers=w.packet_http.patron_headers,
            json=body,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(create_current_cycle, intents))
    assert sorted(r.status_code for r in responses) == [201, 409], [r.text for r in responses]
    winner = next(i for i, r in enumerate(responses) if r.status_code == 201)
    w.new_cycle_receipt = (intents[winner], responses[winner])
    w.seed = (w.seed[0], w.case_id, new_version, ids, w.seed[4])
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, w, tmp_path, monkeypatch
    )
    assert len(w.packet_runs) == 2, "A fresh exact packet must be rebuilt after reimport"
    second = w.packet_runs[1]
    second_control = qualify_final_control(
        session_factory,
        w.packet_http,
        second,
        callback_secret=callback_secret,
    )
    assert first_control["p5_authorization_id"] != second_control["p5_authorization_id"]
    assert first_control["signature_records"] == second_control["signature_records"] == []

    assert first.package_id != second.package_id and first.snapshot_id != second.snapshot_id
    assert first.content_sha256 != second.content_sha256 and first.review_id != second.review_id
    assert first.candidate_id != second.candidate_id and first.candidate_sha != second.candidate_sha
    assert first.manifest["dce_version_id"] == str(old_version) and second.manifest[
        "dce_version_id"
    ] == str(new_version)
    assert first.archive != second.archive
    from app.bootstrap.application import _build_preparation_storage
    from app.modules.preparation.infrastructure.annexes import frozen_annex_bytes
    from app.modules.preparation.infrastructure.models import (
        PreparationSnapshotRecord,
        TechnicalResponseDraftRecord,
    )
    from app.modules.submission.infrastructure.models import SubmissionPackageAuthorizationRecord

    with session_factory() as session:
        assert session.get(CaseRecord, w.case_id).applicable_dce_version_id == new_version
        assert (
            session.get(PreparationSnapshotRecord, first.snapshot_id).manifest_sha256
            == first.manifest["preparation_source"]["manifest_sha256"]
        )
        draft = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == w.actor.tenant_id,
                TechnicalResponseDraftRecord.package_id == first.package_id,
                TechnicalResponseDraftRecord.draft_id == first.draft_id,
            )
        )
        assert (
            sha256(_build_preparation_storage().read(storage_key=draft.storage_key)).hexdigest()
            == first.content_sha256
        )
        approvals = session.scalars(
            sa.select(SubmissionPackageAuthorizationRecord).where(
                SubmissionPackageAuthorizationRecord.tenant_id == w.actor.tenant_id,
                SubmissionPackageAuthorizationRecord.submission_package_id.in_(
                    [UUID(first.candidate_id), UUID(second.candidate_id)]
                ),
            )
        ).all()
        assert len(approvals) == 2 and len({a.id for a in approvals}) == 2
        assert {a.manifest_sha256 for a in approvals} == {first.candidate_sha, second.candidate_sha}
        old_documents = session.scalars(
            sa.select(DceDocumentRecord).where(
                DceDocumentRecord.tenant_id == w.actor.tenant_id,
                DceDocumentRecord.dce_version_id == old_version,
            )
        ).all()
        for doc in old_documents:
            assert (
                sha256(
                    LocalQuarantineStorageAdapter(root=tmp_path).read_verified_bytes(
                        storage_key=doc.storage_key, max_bytes=150_000_000
                    )
                ).hexdigest()
                == doc.sha256
            )
    import zipfile

    for run in w.packet_runs:
        with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
            assert json.loads(archive.read("manifest.json")) == run.manifest
            for item in run.manifest["preparation_source"]["annexes"]:
                assert archive.read(item["archive_path"]) == frozen_annex_bytes(
                    _build_preparation_storage(),
                    tenant_id=w.actor.tenant_id,
                    package_id=run.package_id,
                    snapshot_id=run.snapshot_id,
                    item=item,
                )
    assert {a["sha256"] for a in first.manifest["preparation_source"]["annexes"]} != {
        a["sha256"] for a in second.manifest["preparation_source"]["annexes"]
    }
    import os

    if proof_root := os.environ.get("SMART_AO_REIMPORT_PROOF_DIR"):
        from pathlib import Path

        destination = Path(proof_root) / ("docx" if technical_docx else "markdown")
        destination.mkdir(parents=True, exist_ok=True)
        for number, run in enumerate(w.packet_runs, 1):
            (destination / f"packet-v{number}.zip").write_bytes(run.archive)
            (destination / f"manifest-v{number}.json").write_text(
                json.dumps(run.manifest, ensure_ascii=False, indent=2)
            )
        (destination / "evidence.json").write_text(
            json.dumps(
                dict(
                    case_id=str(w.case_id),
                    old_dce_version_id=str(old_version),
                    new_dce_version_id=str(new_version),
                    packages=[str(r.package_id) for r in w.packet_runs],
                    snapshots=[str(r.snapshot_id) for r in w.packet_runs],
                    reviews=[r.review_id for r in w.packet_runs],
                    p5_hashes=[r.candidate_sha for r in w.packet_runs],
                ),
                indent=2,
            )
        )
    w.packet_http.client.close()
