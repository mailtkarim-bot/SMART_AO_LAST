"""Native, synthetic-only third-party documents; no registry or antivirus network."""

import io
from datetime import timedelta
from hashlib import sha256
from types import SimpleNamespace
from uuid import UUID, uuid4


def payload_for(format):
    if format == "pdf":
        from pypdf import PdfWriter

        writer = PdfWriter()
        writer.add_blank_page(width=600, height=200)
        writer.add_metadata({"/Title": "SYNTHETIC KBIS - NOT AN OFFICIAL DOCUMENT"})
        output = io.BytesIO()
        writer.write(output)
        return output.getvalue(), "application/pdf"
    if format == "png":
        from PIL import Image, ImageDraw

        image = Image.new("RGB", (640, 120), "white")
        ImageDraw.Draw(image).text(
            (20, 40), "SYNTHETIC KBIS - NOT AN OFFICIAL DOCUMENT", fill="black"
        )
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue(), "image/png"
    from docx import Document

    document = Document()
    document.add_heading("KBIS SYNTHETIQUE - AUCUNE VALIDITE OFFICIELLE", 0)
    document.add_paragraph("Fixture de candidature. Aucun titulaire reel, aucun effet juridique.")
    output = io.BytesIO()
    document.save(output)
    return (
        output.getvalue(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def kbis_proposal(factory, w, http, root, requirement_id, *, label_suffix=""):
    from app.modules.enterprise.infrastructure.models import EnterpriseDocumentUploadRecord
    from app.modules.membership.application.collab_capability_commands import (
        ProposeCapabilityForCaseCommand,
    )

    from tests.application.test_collab_capability import _service

    data, mime = payload_for(w.kbis_format)
    w.scan_allowed.add(sha256(data).hexdigest())
    prefix = f"/api/v1/patron/enterprise/companies/{http.company_id}"
    if getattr(w, "packet_runs", []):
        label_suffix += f" — source synthétique V{len(w.packet_runs) + 1}"
    intent = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        document_kind="KBIS",
        document_label="KBIS SYNTHETIQUE SANS VALIDITE OFFICIELLE",
        original_filename="synthetic-kbis." + w.kbis_format,
        expected_byte_size=len(data),
        expires_at=(w.now + timedelta(hours=1)).isoformat(),
    )
    invalid_body = {
        **intent,
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "original_filename": "synthetic-kbis.pdf",
        "expected_byte_size": 19,
    }
    invalid = http.client.post(
        prefix + "/documents/upload", headers=http.patron_headers, json=invalid_body
    )
    assert invalid.status_code == 201, invalid.text
    invalid_id = invalid.json()["aggregate_refs"][0]["aggregate_id"]
    invalid_content = http.client.put(
        prefix + f"/documents/uploads/{invalid_id}/content",
        headers={**http.patron_headers, "Idempotency-Key": str(uuid4())},
        content=b"not a real document",
    )
    assert invalid_content.status_code == 422, invalid_content.text
    prepared = http.client.post(
        prefix + "/documents/upload", headers=http.patron_headers, json=intent
    )
    assert prepared.status_code == 201, prepared.text
    replay = http.client.post(
        prefix + "/documents/upload", headers=http.patron_headers, json=intent
    )
    assert replay.status_code == 200 and replay.json()["replayed"]
    upload_id = UUID(prepared.json()["aggregate_refs"][0]["aggregate_id"])
    denied = http.client.put(
        f"/api/v1/patron/enterprise/companies/{uuid4()}/documents/uploads/{upload_id}/content",
        headers={**http.patron_headers, "Idempotency-Key": str(uuid4())},
        content=data,
    )
    assert denied.status_code == 404, denied.text
    uploaded = http.client.put(
        prefix + f"/documents/uploads/{upload_id}/content",
        headers={**http.patron_headers, "Idempotency-Key": str(uuid4())},
        content=data,
    )
    assert uploaded.status_code == 200 and uploaded.json()["state"] == "CLEAN", uploaded.text
    with factory() as session:
        row = session.get(EnterpriseDocumentUploadRecord, upload_id)
        assert row.media_type == mime and row.sha256 == sha256(data).hexdigest()
        document_id = row.document_id
    review = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        expected_verification_revision=0,
        outcome="VALIDATED",
        reason_code="DOCUMENT_ACCEPTED",
    )
    checked = http.client.post(
        prefix + f"/documents/{document_id}/verification", headers=http.patron_headers, json=review
    )
    assert checked.status_code == 200, checked.text
    checked_again = http.client.post(
        prefix + f"/documents/{document_id}/verification", headers=http.patron_headers, json=review
    )
    assert checked_again.status_code == 200 and checked_again.json()["replayed"]
    cap = http.client.post(
        prefix + "/capabilities",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            capability_kind="QUALIFICATION",
            name="Identification de candidature KBIS synthetique " + w.kbis_format + label_suffix,
            summary="Declaration de test sans validite officielle.",
        ),
    )
    assert cap.status_code == 201, cap.text
    capability_id = cap.json()["aggregate_refs"][0]["aggregate_id"]
    version = http.client.post(
        f"/api/v1/patron/enterprise/capabilities/{capability_id}/versions",
        headers=http.patron_headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=cap.json()["aggregate_refs"][0]["aggregate_revision"],
            title="Source KBIS de candidature",
            description="Source synthetique a relire.",
            valid_from=(w.now - timedelta(days=1)).isoformat(),
            valid_until=(w.now + timedelta(days=1)).isoformat(),
            usage_scope="Pour la seule exigence de candidature citee.",
            proof_document_ids=[str(document_id)],
        ),
    )
    assert version.status_code == 201, version.text
    version_id = version.json()["aggregate_refs"][0]["version_id"]
    command = ProposeCapabilityForCaseCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        proposal_id=uuid4(),
        case_id=w.case_id,
        assignment_id=http.assignment_id,
        capability_id=capability_id,
        capability_version_id=version_id,
        requirement_id=requirement_id,
        justification="Piece KBIS synthetique limitee a la candidature.",
        source_locator=f"enterprise-document://{document_id}",
    )
    result = _service(factory).propose_capability(actor=http.driver, command=command, now=w.now)
    w.omitted_annex_ids = set() if w.include_kbis else {str(document_id)}
    w.kbis = SimpleNamespace(
        document_id=document_id,
        data=data,
        sha256=sha256(data).hexdigest(),
        mime=mime,
        review=review,
        upload_id=upload_id,
        prefix=prefix,
    )
    return SimpleNamespace(
        proposal_id=UUID(str(result.aggregate_refs[0]["aggregate_id"])),
        document_id=document_id,
        sha256=w.kbis.sha256,
    )
