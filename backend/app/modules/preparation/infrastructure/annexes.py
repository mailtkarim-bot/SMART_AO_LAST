"""Exact native enterprise proof copies; citations never imply inclusion or signature."""

from __future__ import annotations

from hashlib import sha256
from typing import Any
from uuid import UUID

import sqlalchemy as sa

from app.modules.enterprise.infrastructure.document_verification import (
    current_document_verification_status,
)
from app.modules.enterprise.infrastructure.models import (
    EnterpriseDocumentRecord,
    EnterpriseDocumentUploadRecord,
)
from app.modules.preparation.infrastructure.response_coverage import read_response_coverage
from app.modules.preparation.public.contracts import SelectedResponseAnnex
from app.platform.events.dispatcher import CommandExecutionError
from app.platform.storage.ports import BoundedPrivateStorage

MAX_ANNEX_BYTES = 150_000_000
EXTENSIONS = {
    "application/pdf": "pdf",
    "image/png": "png",
    "image/jpeg": "jpg",
    "text/plain": "txt",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}


def annex_storage_key(tenant_id, package_id, snapshot_id, item):
    return (
        f"generated-annexes/{tenant_id}/{package_id}/{snapshot_id}/"
        f"{item['document_id']}-{item['sha256']}.bin"
    )


def frozen_annex_bytes(storage, *, tenant_id, package_id, snapshot_id, item):
    try:
        identity = UUID(item["document_id"])
        expected_path = f"annexes/{identity}.{EXTENSIONS[item['media_type']]}"
        if item["archive_path"] != expected_path or item["signature"] != "UNKNOWN":
            raise ValueError("annex identity")
        limit = item["byte_size"]
        if (
            not isinstance(limit, int)
            or not 0 < limit <= MAX_ANNEX_BYTES
            or not isinstance(storage, BoundedPrivateStorage)
        ):
            raise ValueError("annex byte limit")
        content = storage.read_bounded(
            storage_key=annex_storage_key(tenant_id, package_id, snapshot_id, item), max_bytes=limit
        )
        if len(content) != item["byte_size"] or sha256(content).hexdigest() != item["sha256"]:
            raise ValueError("annex bytes")
        return content
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN") from error


def selected_annex_manifest(session, *, package, selections, response, context, storage, review):
    if not selections:
        return [], []
    if review is None or storage is None or response is None:
        raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN")
    coverage = read_response_coverage(
        session,
        tenant_id=package.tenant_id,
        package_id=package.id,
        selection=response,
        storage=storage,
    )
    allowed = {(r.requirement_id, r.document_id, r.sha256) for r in coverage.cited_annexes}
    chosen = [SelectedResponseAnnex.model_validate(r) for r in selections]
    if any((r.requirement_id, r.document_id, r.sha256) not in allowed for r in chosen):
        raise CommandExecutionError("ANNEX_SELECTION_UNKNOWN")
    plan, facts = review.current_response_plan(
        session=session, package=package, command=None, context=context
    )
    review.reread_response_plan_sources(
        session=session, plan=plan, source_facts=facts, tenant_id=package.tenant_id
    )
    documents: dict[UUID, dict[str, Any]] = {}
    for r in chosen:
        if r.document_id in documents and documents[r.document_id]["sha256"] != r.sha256:
            raise CommandExecutionError("ANNEX_SELECTION_UNKNOWN")
        documents.setdefault(
            r.document_id, dict(document_id=str(r.document_id), sha256=r.sha256, requirement_ids=[])
        )["requirement_ids"].append(str(r.requirement_id))
    entries, contents = [], []
    total = 0
    for identity, entry in sorted(documents.items(), key=lambda pair: str(pair[0])):
        row = session.execute(
            sa.select(EnterpriseDocumentRecord, EnterpriseDocumentUploadRecord)
            .join(
                EnterpriseDocumentUploadRecord,
                sa.and_(
                    EnterpriseDocumentUploadRecord.tenant_id == EnterpriseDocumentRecord.tenant_id,
                    EnterpriseDocumentUploadRecord.id == EnterpriseDocumentRecord.storage_object_id,
                    EnterpriseDocumentUploadRecord.document_id == EnterpriseDocumentRecord.id,
                    EnterpriseDocumentUploadRecord.company_id
                    == EnterpriseDocumentRecord.company_id,
                    EnterpriseDocumentUploadRecord.document_kind
                    == EnterpriseDocumentRecord.document_kind,
                ),
            )
            .where(
                EnterpriseDocumentRecord.tenant_id == package.tenant_id,
                EnterpriseDocumentRecord.id == identity,
            )
            .with_for_update(read=True, nowait=True)
        ).one_or_none()
        if row is None:
            raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN")
        document, upload = row
        if (
            document.document_kind not in {"INSURANCE", "KBIS"}
            or current_document_verification_status(
                session, tenant_id=package.tenant_id, document_id=document.id
            )
            != "VALIDATED"
            or upload.state != "CLEAN"
            or upload.scan_verdict != "CLEAN"
            or upload.media_type not in EXTENSIONS
            or document.sha256 != entry["sha256"]
            or upload.sha256 != entry["sha256"]
            or (document.expires_at is not None and document.expires_at <= context.received_at)
        ):
            raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN")
        content = review.read_source_document_bytes(
            storage_key=upload.storage_key, max_bytes=MAX_ANNEX_BYTES - total
        )
        if (
            len(content) != upload.actual_byte_size
            or not content
            or sha256(content).hexdigest() != entry["sha256"]
        ):
            raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN")
        total += len(content)
        entry.update(
            requirement_ids=sorted(set(entry["requirement_ids"])),
            document_kind=document.document_kind,
            media_type=upload.media_type,
            byte_size=len(content),
            archive_path=f"annexes/{identity}.{EXTENSIONS[upload.media_type]}",
            signature="UNKNOWN",
        )
        entries.append(entry)
        contents.append(content)
    return entries, contents


def freeze_annexes(
    session, *, package, selections, response, context, storage, review, snapshot_id
):
    entries, contents = selected_annex_manifest(
        session,
        package=package,
        selections=selections,
        response=response,
        context=context,
        storage=storage,
        review=review,
    )
    for entry, content in zip(entries, contents, strict=True):
        key = annex_storage_key(package.tenant_id, package.id, snapshot_id, entry)
        try:
            written = storage.write(storage_key=key, content=content)
        except FileExistsError:
            written = sha256(
                frozen_annex_bytes(
                    storage,
                    tenant_id=package.tenant_id,
                    package_id=package.id,
                    snapshot_id=snapshot_id,
                    item=entry,
                )
            ).hexdigest()
        if written != entry["sha256"]:
            raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN")
    return entries


def validate_frozen_annexes(session, *, package, manifest, context, storage, review):
    stored = manifest.get("annexes", [])
    if not stored:
        return []
    try:
        if (
            not isinstance(manifest.get("annex_selection_note"), str)
            or not manifest["annex_selection_note"].strip()
        ):
            raise ValueError("annex justification")
        chosen = [
            dict(requirement_id=requirement, document_id=item["document_id"], sha256=item["sha256"])
            for item in stored
            for requirement in item["requirement_ids"]
        ]
        current, _ = selected_annex_manifest(
            session,
            package=package,
            selections=chosen,
            response=manifest.get("selected_response_draft"),
            context=context,
            storage=storage,
            review=review,
        )
        if current != stored:
            raise ValueError("annex manifest")
        for item in stored:
            frozen_annex_bytes(
                storage,
                tenant_id=package.tenant_id,
                package_id=package.id,
                snapshot_id=manifest["snapshot_id"],
                item=item,
            )
        return stored
    except (KeyError, TypeError, ValueError) as error:
        raise CommandExecutionError("ANNEX_SOURCE_UNKNOWN") from error
