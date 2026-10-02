"""SQLAlchemy adapter for B1 handover projections and verified document metadata."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.patron_action.application.handover_queries import (
    CaseHandoverOfferDocumentCandidate,
    CaseHandoverSnapshotProjection,
    technical_document_source,
)
from app.modules.patron_action.infrastructure.models.handover import CaseHandoverSnapshotRecord
from app.modules.patron_action.infrastructure.models.outcome import CaseOutcomeRecord
from app.modules.preparation.infrastructure.models import GeneratedTechnicalDocumentRecord
from app.modules.submission.infrastructure.models.submission import (
    SubmissionPackageAuthorizationRecord,
    SubmissionPackageRecord,
)


class SqlAlchemyCaseHandoverReader:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_case(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[CaseHandoverSnapshotProjection, ...]:
        with self._session_factory() as session:
            rows = session.scalars(
                sa.select(CaseHandoverSnapshotRecord)
                .where(
                    CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                    CaseHandoverSnapshotRecord.case_id == case_id,
                )
                .order_by(
                    CaseHandoverSnapshotRecord.created_at.desc(),
                    CaseHandoverSnapshotRecord.revision.desc(),
                )
            ).all()
            latest: dict[UUID, CaseHandoverSnapshotRecord] = {}
            for row in rows:
                latest.setdefault(row.outcome_id, row)
            selected = sorted(
                latest.values(), key=lambda item: (item.lot_reference, item.revision)
            )
            return tuple(
                CaseHandoverSnapshotProjection(
                    id=row.id,
                    outcome_id=row.outcome_id,
                    lot_reference=row.lot_reference,
                    submission_package_id=row.submission_package_id,
                    package_version=row.package_version,
                    manifest_sha256=row.manifest_sha256,
                    revision=row.revision,
                    created_at=row.created_at,
                    snapshot_json=row.snapshot_json,
                )
                for row in selected
            )

    def offer_document_candidate(
        self, *, tenant_id: UUID, case_id: UUID, snapshot_id: UUID
    ) -> CaseHandoverOfferDocumentCandidate | None:
        with self._session_factory() as session:
            handover = session.scalar(
                sa.select(CaseHandoverSnapshotRecord).where(
                    CaseHandoverSnapshotRecord.tenant_id == tenant_id,
                    CaseHandoverSnapshotRecord.case_id == case_id,
                    CaseHandoverSnapshotRecord.id == snapshot_id,
                )
            )
            if handover is None:
                return None
            package = session.scalar(
                sa.select(SubmissionPackageRecord).where(
                    SubmissionPackageRecord.tenant_id == tenant_id,
                    SubmissionPackageRecord.case_id == case_id,
                    SubmissionPackageRecord.id == handover.submission_package_id,
                    SubmissionPackageRecord.version == handover.package_version,
                )
            )
            if package is None:
                return None
            authorization = session.scalar(
                sa.select(SubmissionPackageAuthorizationRecord.id)
                .where(
                    SubmissionPackageAuthorizationRecord.tenant_id == tenant_id,
                    SubmissionPackageAuthorizationRecord.submission_package_id == package.id,
                    SubmissionPackageAuthorizationRecord.package_version == package.version,
                    SubmissionPackageAuthorizationRecord.manifest_sha256
                    == package.manifest_sha256,
                    SubmissionPackageAuthorizationRecord.state == "AUTHORIZED",
                )
                .limit(1)
            )
            source = technical_document_source(
                package.manifest_json,
                document_id=package.technical_document_id,
                version=package.technical_document_version,
            )
            document = session.scalar(
                sa.select(GeneratedTechnicalDocumentRecord).where(
                    GeneratedTechnicalDocumentRecord.tenant_id == tenant_id,
                    GeneratedTechnicalDocumentRecord.id == package.technical_document_id,
                    GeneratedTechnicalDocumentRecord.package_id == package.preparation_package_id,
                    GeneratedTechnicalDocumentRecord.version == package.technical_document_version,
                    GeneratedTechnicalDocumentRecord.state == "GENERATED",
                    GeneratedTechnicalDocumentRecord.document_kind == "TECHNICAL_RESPONSE",
                )
            )
            offer = handover.snapshot_json.get("offer", {})
            return CaseHandoverOfferDocumentCandidate(
                manifest_json=package.manifest_json,
                manifest_sha256=package.manifest_sha256,
                snapshot_manifest_sha256=handover.manifest_sha256,
                snapshot_offer=offer if isinstance(offer, dict) else {},
                authorization_present=authorization is not None,
                technical_source_kind=source["kind"] if source else None,
                technical_source_sha256=source["sha256"] if source else None,
                technical_document_sha256=document.content_sha256 if document else None,
                technical_document_storage_key=document.storage_key if document else None,
            )

    def list_offer_options(
        self, *, tenant_id: UUID, case_id: UUID
    ) -> tuple[dict[str, object], ...]:
        with self._session_factory() as session:
            outcomes = session.scalars(
                sa.select(CaseOutcomeRecord)
                .where(
                    CaseOutcomeRecord.tenant_id == tenant_id,
                    CaseOutcomeRecord.case_id == case_id,
                    CaseOutcomeRecord.outcome == "WON",
                )
                .order_by(CaseOutcomeRecord.created_at, CaseOutcomeRecord.id)
            ).all()
            packages = session.scalars(
                sa.select(SubmissionPackageRecord)
                .where(
                    SubmissionPackageRecord.tenant_id == tenant_id,
                    SubmissionPackageRecord.case_id == case_id,
                )
                .order_by(SubmissionPackageRecord.version, SubmissionPackageRecord.id)
            ).all()
            options: list[dict[str, object]] = []
            for outcome in outcomes:
                for package in packages:
                    manifest = package.manifest_json
                    scope = manifest.get("scope") if isinstance(manifest, dict) else None
                    lots = scope.get("lot_numbers", []) if isinstance(scope, dict) else []
                    if outcome.lot_reference not in {str(lot).strip() for lot in lots}:
                        continue
                    authorization = session.scalar(
                        sa.select(SubmissionPackageAuthorizationRecord.id)
                        .where(
                            SubmissionPackageAuthorizationRecord.tenant_id == tenant_id,
                            SubmissionPackageAuthorizationRecord.submission_package_id
                            == package.id,
                            SubmissionPackageAuthorizationRecord.package_version == package.version,
                            SubmissionPackageAuthorizationRecord.manifest_sha256
                            == package.manifest_sha256,
                            SubmissionPackageAuthorizationRecord.state == "AUTHORIZED",
                        )
                        .limit(1)
                    )
                    if authorization is None:
                        continue
                    raw = json.dumps(
                        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                    if hashlib.sha256(raw).hexdigest() != package.manifest_sha256:
                        continue
                    source = technical_document_source(
                        manifest,
                        document_id=package.technical_document_id,
                        version=package.technical_document_version,
                    )
                    if source is None:
                        continue
                    options.append(
                        {
                            "outcome_id": str(outcome.id),
                            "lot_reference": outcome.lot_reference,
                            "submission_package_id": str(package.id),
                            "package_version": package.version,
                            "manifest_sha256": package.manifest_sha256,
                            "dce_version_id": str(package.dce_version_id),
                            "technical_document_id": str(package.technical_document_id),
                            "technical_document_version": package.technical_document_version,
                            "technical_document_kind": source["kind"],
                            "technical_document_sha256": source["sha256"],
                        }
                    )
            return tuple(options)
