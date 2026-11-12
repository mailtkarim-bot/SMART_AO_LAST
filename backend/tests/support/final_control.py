"""Assertions on the native final-control read and synthetic signature acts."""

import io
import json
import zipfile
from uuid import uuid4

import sqlalchemy as sa
from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord


def qualify_final_control(factory, http, run, *, callback_secret):
    path = f"/api/v1/patron/submission-packages/{run.candidate_id}/final-control"
    with factory() as session:
        before = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(m))
            for m in (DomainEventRecord, OutboxMessageRecord)
        )
    result = http.client.get(path, headers=http.patron_headers)
    assert result.status_code == 200, result.text
    assert result.headers["cache-control"] == "no-store"
    report = result.json()
    assert report["manifest_sha256"] == run.candidate_sha
    assert report["package_version"] == run.candidate_version
    assert report["state"] == "PARTIAL" and report["source_state"] == "CURRENT"
    assert report["conformity"] == report["signature_verification"] == "UNKNOWN"
    assert report["signer_authority"] == report["signature_requirement"] == "UNKNOWN"
    assert report["external_submission"] == "NOT_PERFORMED"
    assert report["p5_authorization_status"] == "RECORDED"
    assert report["patron_review_ids"] == [run.review_id]
    assert report["signature_records"] == []
    assert report["requirements"] and any(
        r["response_state"] == "MISSING" for r in report["requirements"]
    )
    assert any(p["missing"] for r in report["requirements"] for p in r["pieces"])
    assert all(r["signature"] == r["coverage"] == "UNKNOWN" for r in report["requirements"])
    assert "storage_key" not in json.dumps(report) and "sales_total_minor" not in json.dumps(report)
    with zipfile.ZipFile(io.BytesIO(run.archive)) as archive:
        assert {f["archive_path"] for f in report["files"]} == set(archive.namelist()) - {
            "manifest.json"
        }
        for f in report["files"]:
            assert f["presence"] == "VERIFIED_SOURCE" and f["signature"] == "UNKNOWN"
            from hashlib import sha256

            assert sha256(archive.read(f["archive_path"])).hexdigest() == f["sha256"]
    assert http.client.get(path, headers=http.driver_headers).status_code == 403
    assert http.client.get(path).status_code == 401
    assert (
        http.client.get(
            f"/api/v1/patron/submission-packages/{uuid4()}/final-control",
            headers=http.patron_headers,
        ).status_code
        == 404
    )
    with factory() as session:
        after = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(m))
            for m in (DomainEventRecord, OutboxMessageRecord)
        )
    assert before == after, "A control read cannot grant a gate or create an event/outbox"
    intent = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        signature_id=str(uuid4()),
        expected_package_version=run.candidate_version,
    )
    request_path = f"/api/v1/patron/submission-packages/{run.candidate_id}/signatures"
    response = http.client.post(request_path, headers=http.patron_headers, json=intent)
    # The native policy deliberately denies SECURITY_RESTRICTED until a dedicated flow exists.
    assert response.status_code == 403, response.text
    retry = http.client.post(request_path, headers=http.patron_headers, json=intent)
    assert retry.status_code == 403
    after_refusal = http.client.get(path, headers=http.patron_headers).json()
    assert after_refusal["signature_records"] == []
    assert after_refusal["conformity"] == after_refusal["signature_verification"] == "UNKNOWN"
    with factory() as session:
        unchanged = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(m))
            for m in (DomainEventRecord, OutboxMessageRecord)
        )
    assert unchanged == before
    import os

    if proof_root := os.environ.get("SMART_AO_FINAL_CONTROL_PROOF_DIR"):
        from pathlib import Path

        destination = Path(proof_root) / str(run.candidate_id)
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "control.json").write_text(
            json.dumps(after_refusal, ensure_ascii=False, indent=2)
        )
        (destination / "packet.zip").write_bytes(run.archive)
        (destination / "manifest.json").write_text(
            json.dumps(run.manifest, ensure_ascii=False, indent=2)
        )
    return after_refusal
