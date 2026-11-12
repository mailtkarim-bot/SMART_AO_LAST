"""KBIS candidates reuse native upload/review/selection/P5; no official validity."""

import json
import shutil
from hashlib import sha256

import pytest
from app.modules.dce.infrastructure.quarantine import (
    LocalQuarantineStorageAdapter,
    PythonMagicContentInspectionAdapter,
)
from app.modules.enterprise.application.enterprise_upload import EnterprisePrivateUploadService
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db import test_transversal_affaire_workflow as flow
from tests.db.test_l08_reimport_packet import FixtureScanner
from tests.support.third_party import kbis_proposal


@pytest.mark.parametrize(
    "format,include", [("pdf", True), ("png", True), ("docx", True), ("pdf", False)]
)
def test_kbis_candidate_reaches_an_exact_packet_without_validity_presumed(
    session_factory, tmp_path, monkeypatch, format, include
):
    from app.bootstrap import application as bootstrap

    development = tmp_path / "development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    rc = corpus / "rc.txt"
    rc.write_text(
        rc.read_text() + "\nLe dossier de candidature doit inclure un extrait KBIS pour le lot 1.\n"
    )
    manifest = json.loads((corpus / "manifest.json").read_text())
    next(d for d in manifest["documents"] if d["file"] == "rc.txt")["sha256"] = sha256(
        rc.read_bytes()
    ).hexdigest()
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    w = flow.affaire.__wrapped__(session_factory, tmp_path)
    w.response_assembly = True
    w.source_annexes = True
    w.capture_packets = True
    w.packet_runs = []
    w.secondary_clause = "kbis"
    w.secondary_contribution = (
        "L’extrait KBIS synthétique est cité pour la candidature, sans validité présumée."
    )
    w.secondary_proof_factory = kbis_proposal
    w.kbis_format = format
    w.include_kbis = include
    w.scan_allowed = set()

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
    selected = [
        a
        for a in run.manifest["preparation_source"]["annexes"]
        if a["document_id"] == str(w.kbis.document_id)
    ]
    assert bool(selected) is include
    import io
    import zipfile

    with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
        if include:
            assert (
                selected[0]["document_kind"] == "KBIS" and selected[0]["media_type"] == w.kbis.mime
            )
            assert archive.read(selected[0]["archive_path"]) == w.kbis.data
        else:
            assert all(
                sha256(archive.read(name)).hexdigest() != w.kbis.sha256
                for name in archive.namelist()
            )
    path = f"/api/v1/patron/submission-packages/{run.candidate_id}/final-control"
    client = w.packet_http.client
    headers = w.packet_http.patron_headers
    result = client.get(path, headers=headers)
    assert result.status_code == 200, result.text
    control = result.json()
    files = [f for f in control["files"] if f["document_id"] == str(w.kbis.document_id)]
    assert bool(files) is include
    if include:
        assert files[0]["document_kind"] == "KBIS" and files[0]["media_type"] == w.kbis.mime
        assert (
            files[0]["presence"] == "VERIFIED_SOURCE"
            and files[0]["validity"] == files[0]["signature"] == "UNKNOWN"
        )
    else:
        assert any(
            a["document_id"] == str(w.kbis.document_id) for a in control["missing_cited_annexes"]
        )
    assert control["conformity"] == "UNKNOWN"
    import sqlalchemy as sa
    from app.modules.enterprise.infrastructure.models import (
        EnterpriseDocumentRecord,
        EnterpriseDocumentVerificationRecord,
    )

    with session_factory() as session:
        document = session.get(EnterpriseDocumentRecord, w.kbis.document_id)
        assert document.verification_status == "PENDING", (
            "The immutable initial register must not be rewritten"
        )
        reviews = session.scalars(
            sa.select(EnterpriseDocumentVerificationRecord).where(
                EnterpriseDocumentVerificationRecord.tenant_id == w.actor.tenant_id,
                EnterpriseDocumentVerificationRecord.document_id == w.kbis.document_id,
            )
        ).all()
        assert len(reviews) == 1 and reviews[0].outcome == "VALIDATED"
    from datetime import timedelta

    from app.interfaces.http.routes import patron_submission as routes

    class Future:
        @staticmethod
        def now(tz=None):
            return w.now + timedelta(hours=2)

    with monkeypatch.context() as clock:
        clock.setattr(routes, "datetime", Future)
        expired = client.get(path, headers=headers)
    assert expired.status_code == 200 and expired.json()["source_state"] == "REVIEW_REQUIRED", (
        expired.text
    )
    assert all(f["presence"] == "UNKNOWN" for f in expired.json()["files"])
    assert client.get(path, headers=headers).json()["source_state"] == "CURRENT"
    rejection = dict(
        command_id=str(__import__("uuid").uuid4()),
        idempotency_key=str(__import__("uuid").uuid4()),
        expected_verification_revision=0,
        outcome="REJECTED",
        reason_code="DOCUMENT_MISMATCH",
    )
    verify_path = w.kbis.prefix + f"/documents/{w.kbis.document_id}/verification"
    if format == "pdf" and include:
        from tests.support.third_party_concurrency import reject_after_control_read

        reject_after_control_read(
            session_factory, client, path, verify_path, headers, rejection, monkeypatch
        )
    else:
        rejected = client.post(verify_path, headers=headers, json=rejection)
        assert rejected.status_code == 200, rejected.text
    refused = client.get(
        f"/api/v1/patron/submission-packages/{run.candidate_id}/export", headers=headers
    )
    assert refused.status_code == 422, refused.text
    after = client.get(path, headers=headers)
    assert after.status_code == 200 and after.json()["source_state"] == "REVIEW_REQUIRED", (
        after.text
    )
    assert all(f["presence"] == "UNKNOWN" for f in after.json()["files"])
    from app.bootstrap.application import _build_preparation_storage
    from app.modules.preparation.infrastructure.annexes import frozen_annex_bytes

    for item in run.manifest["preparation_source"]["annexes"]:
        raw = frozen_annex_bytes(
            _build_preparation_storage(),
            tenant_id=w.actor.tenant_id,
            package_id=run.package_id,
            snapshot_id=run.snapshot_id,
            item=item,
        )
        assert sha256(raw).hexdigest() == item["sha256"]
    import os

    if proof_root := os.environ.get("SMART_AO_THIRD_PARTY_PROOF_DIR"):
        from pathlib import Path

        destination = Path(proof_root) / (format + ("-included" if include else "-omitted"))
        destination.mkdir(parents=True, exist_ok=True)
        for name, payload in [
            ("control-current", control),
            ("control-rejected", after.json()),
            ("manifest", run.manifest),
            (
                "history",
                dict(
                    initial_register="PENDING",
                    current_internal_outcome="REJECTED",
                    legal_validity="UNKNOWN",
                    expired_source_state=expired.json()["source_state"],
                ),
            ),
        ]:
            (destination / (name + ".json")).write_text(
                json.dumps(payload, ensure_ascii=False, indent=2)
            )
        (destination / "packet.zip").write_bytes(run.archive)
    w.packet_http.client.close()
