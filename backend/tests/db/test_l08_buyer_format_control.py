"""Sourced file/packaging observations never authorize a buyer submission."""

import io
import json
import shutil
from hashlib import sha256

import pytest
import sqlalchemy as sa
from app.modules.dce.infrastructure.quarantine import (
    LocalQuarantineStorageAdapter,
    PythonMagicContentInspectionAdapter,
)
from app.modules.enterprise.application.enterprise_upload import EnterprisePrivateUploadService
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord
from docx import Document
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db import test_transversal_affaire_workflow as flow
from tests.db.test_l08_reimport_packet import FixtureScanner
from tests.support.third_party import kbis_proposal


@pytest.mark.parametrize(
    "docx,requested,mode",
    [(False, "PDF", "NO_ZIP"), (True, "DOCX", "ZIP"), (False, "PDF", "INDIVIDUAL_FILES")],
)
def test_native_source_formats_compare_exact_files_without_an_act(
    session_factory, tmp_path, monkeypatch, docx, requested, mode
):
    from app.bootstrap import application as bootstrap

    development = tmp_path / "development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    rc = corpus / "rc.txt"
    mode_quote = {
        "NO_ZIP": "Format de fichier : Les archives ZIP sont interdites.",
        "ZIP": "Format de fichier : Le pli doit être remis sous forme d'une archive ZIP.",
        "INDIVIDUAL_FILES": (
            "Format de fichier : Les fichiers doivent être déposés individuellement, sans archive."
        ),
    }[mode]
    rc.write_text(
        rc.read_text()
        + (
            "\nLe dossier de candidature doit inclure un extrait KBIS pour le lot 1.\n"
            f"Le mémoire technique doit être remis au format {requested}.\n"
            "Le KBIS doit être fourni au format PDF.\n"
            "Format de fichier : Le KBIS doit être nommé «KBIS».\n"
            "Format de fichier : La taille du mémoire technique ne doit pas dépasser 1 octet.\n"
            "Format de fichier : La taille de chaque fichier ne doit pas dépasser 1048576 octets.\n"
            "Format de fichier : Les noms des fichiers ne doivent pas contenir d’espaces.\n"
        )
        + (
            "Format de fichier : Le mémoire technique doit être nommé «Memoire.pdf».\n"
            if docx
            else ""
        )
        + mode_quote
        + "\n"
    )
    manifest = json.loads((corpus / "manifest.json").read_text())
    next(d for d in manifest["documents"] if d["file"] == "rc.txt")["sha256"] = sha256(
        rc.read_bytes()
    ).hexdigest()
    if docx:
        frame = Document()
        frame.add_heading("Cadre synthétique - candidature", 0)
        frame.add_paragraph("Engagement de test à relire.")
        frame.add_paragraph("[[REPONSE:COUVERTURE]]")
        table = frame.add_table(rows=2, cols=2)
        table.cell(0, 0).text = "Rubrique acheteur"
        table.cell(0, 1).text = "Réponse"
        table.cell(1, 0).text = "Pièces de candidature"
        table.cell(1, 1).text = "[[REPONSE:ATTESTATION]]"
        frame.add_paragraph("[[REPONSE:AUTRE]]")
        buffer = io.BytesIO()
        frame.save(buffer)
        raw = buffer.getvalue()
        (corpus / "cadre.docx").write_bytes(raw)
        manifest["documents"].append(
            dict(
                file="cadre.docx",
                family="ANNEXE",
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                sha256=sha256(raw).hexdigest(),
            )
        )
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    w = flow.affaire.__wrapped__(session_factory, tmp_path)
    w.response_assembly = True
    w.source_annexes = True
    w.capture_packets = True
    w.packet_runs = []
    w.secondary_clause = "dossier de candidature doit inclure un extrait kbis"
    w.secondary_contribution = "Le KBIS synthétique est cité, validité officielle UNKNOWN."
    w.secondary_proof_factory = kbis_proposal
    w.kbis_format = "pdf"
    w.include_kbis = True
    w.scan_allowed = set()
    if docx:
        w.buyer_docx = True
        w.docx_template_bytes = raw

    def native_upload(*, session_factory, dispatcher, policy):
        storage = LocalQuarantineStorageAdapter(root=tmp_path)
        return EnterprisePrivateUploadService(
            session_factory=session_factory,
            dispatcher=dispatcher,
            policy=policy,
            storage=storage,
            inspector=PythonMagicContentInspectionAdapter(storage=storage),
            scanner=FixtureScanner(storage, w.scan_allowed, w.now),
            allowed_media_types=bootstrap._ALLOWED_DCE_MEDIA_TYPES,
        )

    monkeypatch.setattr(bootstrap, "_default_enterprise_private_upload_service", native_upload)
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, w, tmp_path, monkeypatch
    )
    run = w.packet_runs[0]
    with session_factory() as session:
        before = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(model))
            for model in [DomainEventRecord, OutboxMessageRecord]
        )
    response = w.packet_http.client.get(
        f"/api/v1/patron/submission-packages/{run.candidate_id}/final-control",
        headers=w.packet_http.patron_headers,
    )
    assert response.status_code == 200, response.text
    report = response.json()
    import os
    from pathlib import Path

    if diagnostic := os.environ.get("SMART_AO_BUYER_FORMAT_PROOF_DIR"):
        target = Path(diagnostic) / mode.lower()
        target.mkdir(parents=True, exist_ok=True)
        (target / "control-diagnostic.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2)
        )

    import zipfile

    with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
        for file in report["files"]:
            assert file["byte_size"] == len(archive.read(file["archive_path"]))
    name_sizes = report["name_size_comparisons"]
    assert name_sizes and report["buyer_names_sizes_state"] == "OBSERVATIONS_AVAILABLE"
    assert any(
        r["criterion"] == "EXACT_NAME"
        and r["state"] == "OBSERVED_MISMATCH"
        and r["requested_name"] == "KBIS"
        for r in name_sizes
    )
    if docx:
        assert any(
            r["state"] == "OBSERVED_MISMATCH"
            and r["requested_name"] == "Memoire.pdf"
            and r["source_excerpt"]
            == "Format de fichier : Le mémoire technique doit être nommé «Memoire.pdf»."
            for r in name_sizes
        ), "Complete literal names are compared without changing the export"
    assert any(
        r["criterion"] == "MAX_BYTES" and r["max_bytes"] == 1 and r["state"] == "OBSERVED_MISMATCH"
        for r in name_sizes
    )
    assert any(
        r["criterion"] == "MAX_BYTES"
        and r["max_bytes"] == 1048576
        and r["state"] == "OBSERVED_MATCH"
        for r in name_sizes
    )
    assert any(
        r["criterion"] == "NO_WHITESPACE" and r["state"] == "OBSERVED_MATCH" for r in name_sizes
    )
    assert all(r["conformity"] == r["applicability"] == "UNKNOWN" for r in name_sizes)
    assert all(r["source_anchor"]["dce_version_id"] == report["dce_version_id"] for r in name_sizes)
    comparisons = report["format_comparisons"]
    assert comparisons
    technical = [r for r in comparisons if r["scope"] == "TECHNICAL_RESPONSE"]
    assert technical and all(r["requested"] == requested for r in technical)
    assert all(r["state"] == ("OBSERVED_MATCH" if docx else "OBSERVED_MISMATCH") for r in technical)
    assert all(r["files"][0]["sha256"] == run.content_sha256 for r in technical)
    assert any(r["scope"] == "KBIS" and r["state"] == "OBSERVED_MATCH" for r in comparisons)
    assert any(
        r["scope"] == "DELIVERY"
        and r["requested"] == mode
        and r["state"] == ("OBSERVED_MATCH" if mode == "ZIP" else "OBSERVED_MISMATCH")
        for r in comparisons
    )
    assert all(r["conformity"] == r["applicability"] == "UNKNOWN" for r in comparisons)
    assert all(
        r["source_anchor"]["dce_version_id"] == report["dce_version_id"] for r in comparisons
    )
    assert (
        report["manifest_sha256"] == run.candidate_sha
        and report["external_submission"] == "NOT_PERFORMED"
    )
    assert report["conformity"] == "UNKNOWN" and report["local_delivery_mode"] == "LOCAL_ZIP"
    with session_factory() as session:
        after = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(model))
            for model in [DomainEventRecord, OutboxMessageRecord]
        )
    assert after == before, "Format comparison must not create an act/event/outbox"
    import os

    if root := os.environ.get("SMART_AO_BUYER_FORMAT_PROOF_DIR"):
        from pathlib import Path

        destination = Path(root) / mode.lower()
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "control.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        (destination / "manifest.json").write_text(
            json.dumps(run.manifest, ensure_ascii=False, indent=2)
        )
        (destination / "packet.zip").write_bytes(run.archive)
    w.packet_http.client.close()
