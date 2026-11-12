"""One Case across native DCE generations, exact documents and visible limitations."""

import io
import json
import os
import shutil
import zipfile
from hashlib import sha256
from pathlib import Path

import pytest
from app.modules.dce.infrastructure.quarantine import (
    LocalQuarantineStorageAdapter,
    PythonMagicContentInspectionAdapter,
)
from app.modules.enterprise.application.enterprise_upload import EnterprisePrivateUploadService
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db.test_l08_reimport_packet import (
    FixtureScanner,
)
from tests.db.test_l08_reimport_packet import (
    test_rectification_reimport_rebuilds_an_exact_packet_without_transferring_agreements as _run,
)
from tests.support import final_control
from tests.support.third_party import kbis_proposal


@pytest.mark.parametrize("technical_docx", [False, True])
def test_same_case_integrates_response_controls_and_native_rectification(
    session_factory,
    tmp_path,
    monkeypatch,
    technical_docx,
    handover_qualifier=None,
    buyer_requested_name="Memoire.pdf",
):
    from app.bootstrap import application as bootstrap

    # Development copy only: never change reference corpus or measured gold.
    development = tmp_path / "integrated-development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    rc = corpus / "rc.txt"
    requested = "DOCX" if technical_docx else "PDF"
    rc.write_text(
        rc.read_text()
        + "\nLe dossier de candidature doit inclure un extrait KBIS pour le lot 1.\n"
        + f"Le mémoire technique doit être remis au format {requested}.\n"
        + "Le KBIS doit être fourni au format PDF.\n"
        + "Format de fichier : Le pli doit être remis sous forme d'une archive ZIP.\n"
        + "Format de fichier : Le KBIS doit être nommé «KBIS».\n"
        + "Format de fichier : La taille du mémoire technique ne doit pas dépasser 1 octet.\n"
        + "Format de fichier : La taille de chaque fichier ne doit pas dépasser 1048576 octets.\n"
        + "Format de fichier : Les noms des fichiers ne doivent pas contenir d'espaces.\n"
        + f"Format de fichier : Le mémoire technique doit être nommé «{buyer_requested_name}».\n"
    )
    manifest_path = corpus / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    next(d for d in manifest["documents"] if d["file"] == "rc.txt")["sha256"] = sha256(
        rc.read_bytes()
    ).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    configured = []

    def configure(w):
        w.secondary_clause = "dossier de candidature doit inclure un extrait kbis"
        w.secondary_contribution = "KBIS synthétique cité; validité officielle UNKNOWN."
        w.secondary_proof_factory = kbis_proposal
        w.kbis_format = "pdf"
        w.include_kbis = True
        w.scan_allowed = set()
        configured.append(w)

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

    controls = []
    original_qualifier = final_control.qualify_final_control

    def integrated_control(factory, http, run, *, callback_secret):
        report = original_qualifier(factory, http, run, callback_secret=callback_secret)
        controls.append(report)
        generation = len(controls)
        if destination := os.environ.get("SMART_AO_L08_INTEGRATED_PROOF_DIR"):
            target = (
                Path(destination) / ("docx" if technical_docx else "markdown") / f"v{generation}"
            )
            target.mkdir(parents=True, exist_ok=True)
            (target / "control.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            (target / "manifest.json").write_text(
                json.dumps(run.manifest, ensure_ascii=False, indent=2)
            )
            (target / "packet.zip").write_bytes(run.archive)
        with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
            for file in report["files"]:
                raw = archive.read(file["archive_path"])
                assert file["byte_size"] == len(raw)
                assert file["sha256"] == sha256(raw).hexdigest()
        assert any(f["document_kind"] == "KBIS" for f in report["files"])
        assert (
            report["buyer_formats_state"]
            == report["buyer_names_sizes_state"]
            == "OBSERVATIONS_AVAILABLE"
        )
        formats = report["format_comparisons"]
        assert any(
            r["scope"] == "TECHNICAL_RESPONSE"
            and r["requested"] == requested
            and r["state"] == ("OBSERVED_MATCH" if technical_docx else "OBSERVED_MISMATCH")
            for r in formats
        )
        assert any(r["scope"] == "KBIS" and r["state"] == "OBSERVED_MATCH" for r in formats)
        assert any(r["scope"] == "DELIVERY" and r["state"] == "OBSERVED_MATCH" for r in formats)
        names_sizes = report["name_size_comparisons"]
        assert any(
            r["criterion"] == "EXACT_NAME" and r["state"] == "OBSERVED_MISMATCH"
            for r in names_sizes
        )
        assert any(
            r["criterion"] == "MAX_BYTES"
            and r["max_bytes"] == 1
            and r["state"] == "OBSERVED_MISMATCH"
            for r in names_sizes
        )
        assert any(
            r["criterion"] == "MAX_BYTES"
            and r["max_bytes"] == 1048576
            and r["state"] == "OBSERVED_MATCH"
            for r in names_sizes
        )
        name_row = next(r for r in names_sizes if r["requested_name"] == buyer_requested_name)
        assert name_row["criterion"] == "EXACT_NAME"
        assert name_row["source_excerpt"] == (
            f"Format de fichier : Le mémoire technique doit être nommé «{buyer_requested_name}»."
        )
        actual_name = "technical-response.docx" if technical_docx else "technical-response.md"
        assert name_row["state"] == (
            "OBSERVED_MATCH" if buyer_requested_name == actual_name else "OBSERVED_MISMATCH"
        )
        for row in formats + names_sizes:
            assert row["conformity"] == row["applicability"] == "UNKNOWN"
            assert row["source_anchor"]["dce_version_id"] == report["dce_version_id"]
            assert row["confirmation"] == "CONFIRMED"
        if handover_qualifier is not None:
            handover_qualifier(factory, http, run, report, generation, configured[0])
        return report

    # Wrap the assertion helper only; all application HTTP, policy, DB and storage stay native.
    monkeypatch.setattr(final_control, "qualify_final_control", integrated_control)
    _run(session_factory, tmp_path, monkeypatch, technical_docx, configure_workflow=configure)
    assert len(configured) == 1 and len(controls) == 2
    first, second = controls
    assert first["dce_version_id"] != second["dce_version_id"]
    assert first["p5_authorization_id"] != second["p5_authorization_id"]
    assert first["patron_review_ids"] != second["patron_review_ids"]
    assert {r["requirement_id"] for r in first["requirements"]}.isdisjoint(
        r["requirement_id"] for r in second["requirements"]
    )
    assert first["conformity"] == second["conformity"] == "UNKNOWN"

    w = configured[0]
    stale = w.stale_final_control
    assert stale["source_state"] == "REVIEW_REQUIRED" and w.stale_export_status == 422
    assert stale["format_comparisons"] == stale["name_size_comparisons"] == []
    assert stale["buyer_formats_state"] == stale["buyer_names_sizes_state"] == "UNKNOWN"
    assert all(f["presence"] == "UNKNOWN" for f in stale["files"])
    if destination := os.environ.get("SMART_AO_L08_INTEGRATED_PROOF_DIR"):
        target = Path(destination) / ("docx" if technical_docx else "markdown")
        (target / "stale-v1-after-rectificatif.json").write_text(
            json.dumps(stale, ensure_ascii=False, indent=2)
        )
        (target / "lineage.json").write_text(
            json.dumps(
                {
                    "case_id": str(w.case_id),
                    "old_dce_version_id": first["dce_version_id"],
                    "new_dce_version_id": second["dce_version_id"],
                    "package_ids": [str(r.package_id) for r in w.packet_runs],
                    "snapshots": [str(r.snapshot_id) for r in w.packet_runs],
                    "decisions": [str(r.decision_id) for r in w.packet_runs],
                    "reviews": [r.review_id for r in w.packet_runs],
                    "p5_authorizations": [r["p5_authorization_id"] for r in controls],
                    "manifest_hashes": [r["manifest_sha256"] for r in controls],
                    "old_export_after_rectification_status": w.stale_export_status,
                    "external_submission": "NOT_PERFORMED",
                    "conformity": "UNKNOWN",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
