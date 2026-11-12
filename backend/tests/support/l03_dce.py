"""Local synthetic originals through native staging, admission and extraction."""

import asyncio
from base64 import b64decode
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from io import BytesIO
from types import SimpleNamespace
from uuid import UUID, uuid4
from zipfile import ZipFile

import sqlalchemy as sa
from app.bootstrap.application import _ALLOWED_DCE_MEDIA_TYPES
from app.modules.dce.application.extraction import DceDocumentExtractionService
from app.modules.dce.application.handlers import RecordDceDocumentExtractionHandler
from app.modules.dce.application.upload import DceUploadService
from app.modules.dce.infrastructure.models.consultation import ConsultationLotRecord
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentRecord,
    DceMissingDocumentDeclarationRecord,
)
from app.modules.dce.infrastructure.quarantine import (
    LocalQuarantineStorageAdapter,
    PythonMagicContentInspectionAdapter,
)
from app.platform.events.dispatcher import CommandDispatcher

from tests.api.test_dce_authenticated_api import (
    UploadTestScanner,
    _client,
    _headers,
    _seed_consultation,
    _seed_principal,
)
from tests.db.test_l04_multiformat_rectification import originals
from tests.db.test_regulatory_profile_persistence import _case


def ids():
    return {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "correlation_id": str(uuid4()),
    }


def world(database_engine, session_factory, tmp_path, *, now=None):
    tenant, identity, auth_session = _seed_principal(
        database_engine, **({"now": now} if now else {})
    )
    consultation = _seed_consultation(database_engine, tenant_id=tenant)
    case_id, other_case_id = uuid4(), uuid4()
    storage = LocalQuarantineStorageAdapter(root=tmp_path / "storage")

    def upload_factory(dispatcher):
        return DceUploadService(
            dispatcher=dispatcher,
            storage=storage,
            inspector=PythonMagicContentInspectionAdapter(storage=storage),
            scanner=UploadTestScanner(),
            allowed_media_types=_ALLOWED_DCE_MEDIA_TYPES,
        )

    client, tokens = _client(
        session_factory,
        dce_upload_service_factory=upload_factory,
        clock=SimpleNamespace(now=lambda: now) if now else None,
    )
    headers = _headers(tokens, identity_id=identity, session_id=auth_session)
    with session_factory.begin() as s:
        for number in ("2", "7"):
            s.add(
                ConsultationLotRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    consultation_id=consultation,
                    lot_number=number,
                    label=f"Lot synthétique {number}",
                    source_reference="Déclaration synthétique locale",
                )
            )
        for target, marker in ((case_id, "f"), (other_case_id, "9")):
            case = _case(tenant_id=tenant, case_id=target, marker=marker)
            case.consultation_id = consultation
            case.scope_kind = "MULTI_LOT"
            case.scope_json = {"lot_numbers": ["2", "7"]}
            s.add(case)

    def sources(revision):
        folder = tmp_path / f"originals-v{revision}"
        originals(folder, revision)
        archive = BytesIO()
        with ZipFile(archive, "w") as z:
            z.writestr(
                f"annexe-lot-{revision}.txt",
                f"Annexe synthétique V{revision}, non admise séparément.",
            )
            z.writestr("../exclu.txt", "Entrée à exclure, pas une instruction.")
        raw = [
            (f"RC-v{revision}.pdf", (folder / "rc.pdf").read_bytes()),
            (f"annexes-v{revision}.zip", archive.getvalue()),
        ]
        if revision == 1:
            raw.append(
                (
                    "plan-non-lu.png",
                    b64decode(
                        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
                    ),
                )
            )
        return raw

    def admit(revision, predecessor=None):
        raw = sources(revision)
        documents = []
        hashes = []
        for name, content in raw:
            prepare = {
                **ids(),
                "consultation_id": str(consultation),
                "consultation_revision": 4,
                "original_filename": name,
                "expected_byte_size": len(content),
                "source_channel": "RECTIFICATION" if predecessor else "MANUAL_UPLOAD",
                "expires_at": (datetime.now(tz=UTC) + timedelta(hours=1)).isoformat(),
            }
            prepared = client.post("/api/v1/dce-staged-objects", headers=headers, json=prepare)
            assert prepared.status_code == 201, prepared.text
            stage = prepared.json()["staging"]["storage_object_id"]
            uploaded = client.put(
                f"/api/v1/dce-staged-objects/{stage}/content",
                headers={**headers, "Idempotency-Key": prepare["idempotency_key"]},
                content=content,
            )
            assert uploaded.status_code == 200, uploaded.text
            documents.append({"document_id": str(uuid4()), "storage_object_id": stage})
            hashes.append(sha256(content).hexdigest())
        payload = {
            **ids(),
            "dce_version_id": str(uuid4()),
            "consultation_id": str(consultation),
            "consultation_revision": 4,
            "corpus_hash": sha256("\n".join(sorted(hashes)).encode("ascii")).hexdigest(),
            "provenance_channel": "RECTIFICATION" if predecessor else "MANUAL_UPLOAD",
            "source_received_at": datetime.now(tz=UTC).isoformat(),
            "documents": documents,
        }
        if predecessor:
            metadata = client.get(
                f"/api/v1/dce-versions/{predecessor['dce_version_id']}", headers=headers
            )
            assert metadata.status_code == 200, metadata.text
            payload.update(
                predecessor_dce_version_id=predecessor["dce_version_id"],
                expected_predecessor_revision=metadata.json()["aggregate_revision"],
                replacement_reason=(
                    "Rectificatif synthétique reçu ; sources V2 exactes, aucun accord repris."
                ),
            )
        response = client.post("/api/v1/dce-versions", headers=headers, json=payload)
        assert response.status_code == 201, response.text
        replay = client.post("/api/v1/dce-versions", headers=headers, json=payload)
        assert replay.status_code == 200 and replay.json()["replayed"]
        with session_factory() as s:
            records = s.scalars(
                sa.select(DceDocumentRecord)
                .where(
                    DceDocumentRecord.tenant_id == tenant,
                    DceDocumentRecord.dce_version_id == UUID(payload["dce_version_id"]),
                )
                .order_by(DceDocumentRecord.original_filename)
            ).all()
            assert sorted(row.sha256 for row in records) == sorted(hashes)
        extract = DceDocumentExtractionService(
            session_factory=session_factory,
            storage=storage,
            dispatcher=CommandDispatcher(
                session_factory=session_factory,
                handlers={"RecordDceDocumentExtraction": RecordDceDocumentExtractionHandler()},
            ),
        )
        for doc in documents:
            asyncio.run(extract.extract(tenant_id=tenant, dce_document_id=UUID(doc["document_id"])))
        with session_factory.begin() as s:
            s.add(
                DceMissingDocumentDeclarationRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    dce_version_id=UUID(payload["dce_version_id"]),
                    expected_document_family="CCAP" if revision == 1 else "AE",
                    expectation_source_kind="HUMAN_SYNTHETIC_DECLARATION",
                    expectation_source_id=f"local-v{revision}",
                    reason="Pièce annoncée manquante, autorité non établie.",
                    created_by_actor_id=identity,
                )
            )
        return payload

    def link(version, target=case_id, expected=1):
        response = client.post(
            f"/api/v1/cases/{target}/dce-applicability",
            headers=headers,
            json={
                **ids(),
                "dce_version_id": version["dce_version_id"],
                "expected_case_revision": expected,
                "reason": "Rattachement humain synthétique de cette version exacte.",
            },
        )
        assert response.status_code == 201, response.text

    return SimpleNamespace(
        tenant=tenant,
        identity=identity,
        consultation=consultation,
        case_id=case_id,
        other_case_id=other_case_id,
        client=client,
        headers=headers,
        tokens=tokens,
        storage=storage,
        admit=admit,
        sources=sources,
        link=link,
    )
