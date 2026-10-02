"""Read contracts for the tenant-scoped P7 handover projection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CaseHandoverSnapshotProjection:
    id: UUID
    outcome_id: UUID
    lot_reference: str
    submission_package_id: UUID
    package_version: int
    manifest_sha256: str
    revision: int
    created_at: datetime
    snapshot_json: dict[str, object]


@dataclass(frozen=True, slots=True)
class CaseHandoverOfferDocumentCandidate:
    manifest_json: dict[str, object]
    manifest_sha256: str
    snapshot_manifest_sha256: str
    snapshot_offer: dict[str, object]
    authorization_present: bool
    technical_source_kind: str | None
    technical_source_sha256: str | None
    technical_document_sha256: str | None
    technical_document_storage_key: str | None


class CaseHandoverReader(Protocol):
    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[CaseHandoverSnapshotProjection, ...]: ...

    def offer_document_candidate(
        self, *, tenant_id: UUID, case_id: UUID, snapshot_id: UUID
    ) -> CaseHandoverOfferDocumentCandidate | None: ...

    def list_offer_options(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[dict[str, object], ...]: ...


def technical_document_source(
    manifest: dict[str, object], *, document_id: UUID, version: int
) -> dict[str, str] | None:
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if (
            entry.get("document_id") == str(document_id)
            and entry.get("version") == version
            and isinstance(entry.get("sha256"), str)
        ):
            return {
                "document_id": str(document_id),
                "version": str(version),
                "kind": str(entry.get("kind", "")),
                "sha256": str(entry["sha256"]),
            }
    return None
