"""Read-only C10 source verification inside the candidate transaction."""

from __future__ import annotations

import hashlib
import json
from typing import cast
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.preparation.application.review import PreparationReviewHandler
from app.modules.preparation.application.transmission import (
    PreparationTransmissionHandler,
    PreparationTransmissionService,
)
from app.modules.preparation.application.transmission_commands import (
    CreatePreparationSnapshotCommand,
    TransmitPreparationSnapshotCommand,
)
from app.modules.preparation.infrastructure.models import (
    GeneratedTechnicalDocumentRecord,
    PreparationPackageRecord,
    PreparationResponsePlanRecord,
    PreparationSnapshotRecord,
    PreparationTransmissionRecord,
)
from app.platform.events.dispatcher import CommandContext, CommandExecutionError


class PreparationSubmissionSourceReader:
    def __init__(
        self,
        *,
        review_handler: PreparationReviewHandler,
        transmission_handler: PreparationTransmissionHandler,
    ) -> None:
        self._review = review_handler
        self._transmission = transmission_handler

    def read(
        self,
        *,
        session: object,
        preparation_package_id: UUID,
        source: dict[str, object] | None,
        context: CommandContext,
    ) -> dict[str, object] | None:
        db = cast(Session, session)
        package = db.scalar(
            sa.select(PreparationPackageRecord).where(
                PreparationPackageRecord.tenant_id == context.tenant_id,
                PreparationPackageRecord.id == preparation_package_id,
            )
        )
        if package is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        has_plan = db.scalar(
            sa.select(PreparationResponsePlanRecord.id)
            .where(
                PreparationResponsePlanRecord.tenant_id == context.tenant_id,
                PreparationResponsePlanRecord.package_id == package.id,
            )
            .limit(1)
        )
        if has_plan is None and source is None:
            return None
        if has_plan is None or source is None:
            raise CommandExecutionError("PREPARATION_SOURCE_UNKNOWN")
        snapshot_id = UUID(str(source["snapshot_id"]))
        row = db.execute(
            sa.select(PreparationSnapshotRecord, PreparationTransmissionRecord)
            .join(
                PreparationTransmissionRecord,
                sa.and_(
                    PreparationTransmissionRecord.tenant_id == PreparationSnapshotRecord.tenant_id,
                    PreparationTransmissionRecord.package_id
                    == PreparationSnapshotRecord.package_id,
                    PreparationTransmissionRecord.snapshot_id == PreparationSnapshotRecord.id,
                ),
            )
            .where(
                PreparationSnapshotRecord.tenant_id == context.tenant_id,
                PreparationSnapshotRecord.package_id == package.id,
                PreparationSnapshotRecord.id == snapshot_id,
                PreparationTransmissionRecord.state == "TRANSMITTED_TO_PATRON",
            )
        ).one_or_none()
        if row is None:
            raise CommandExecutionError("PREPARATION_SOURCE_UNKNOWN")
        snapshot, transmission = row
        latest_version = db.scalar(
            sa.select(sa.func.max(PreparationSnapshotRecord.version)).where(
                PreparationSnapshotRecord.tenant_id == context.tenant_id,
                PreparationSnapshotRecord.package_id == package.id,
            )
        )
        manifest = snapshot.manifest_json
        manifest_bytes = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if (
            snapshot.version != source["snapshot_version"]
            or snapshot.version != latest_version
            or snapshot.manifest_sha256 != source["manifest_sha256"]
            or hashlib.sha256(manifest_bytes).hexdigest() != snapshot.manifest_sha256
            or snapshot.case_id != package.case_id
            or snapshot.dce_version_id != package.dce_version_id
            or snapshot.state != "READY_FOR_PATRON_REVIEW"
            or manifest.get("package_id") != str(package.id)
            or manifest.get("case_id") != str(package.case_id)
            or manifest.get("dce_version_id") != str(package.dce_version_id)
        ):
            raise CommandExecutionError("PREPARATION_SOURCE_UNKNOWN")
        document = db.scalar(
            sa.select(GeneratedTechnicalDocumentRecord).where(
                GeneratedTechnicalDocumentRecord.tenant_id == context.tenant_id,
                GeneratedTechnicalDocumentRecord.package_id == package.id,
                GeneratedTechnicalDocumentRecord.id == snapshot.technical_document_id,
                GeneratedTechnicalDocumentRecord.version == snapshot.technical_document_version,
                GeneratedTechnicalDocumentRecord.state == "GENERATED",
            )
        )
        if document is None or manifest.get("documents") != [
            {
                "document_id": str(document.id),
                "version": document.version,
                "kind": document.document_kind,
                "sha256": document.content_sha256,
            }
        ]:
            raise CommandExecutionError("PREPARATION_SOURCE_UNKNOWN")
        plan, facts = self._review.current_response_plan(
            session=db,
            package=package,
            command=None,
            context=context,
        )
        self._review.reread_response_plan_sources(
            session=db,
            plan=plan,
            source_facts=facts,
            tenant_id=package.tenant_id,
        )
        drafts = self._transmission.current_c10_review_manifest(
            session=db,
            package=package,
            tenant_id=package.tenant_id,
        )
        if not drafts or manifest.get("response_drafts") != drafts:
            raise CommandExecutionError("PREPARATION_SOURCE_UNKNOWN")
        for record, command_type, result_code, aggregate_type, revision in (
            (
                snapshot,
                CreatePreparationSnapshotCommand.command_type,
                "PREPARATION_SNAPSHOT_CREATED",
                "PreparationSnapshot",
                snapshot.version,
            ),
            (
                transmission,
                TransmitPreparationSnapshotCommand.command_type,
                "PREPARATION_TRANSMITTED_TO_PATRON",
                "PreparationTransmission",
                None,
            ),
        ):
            PreparationTransmissionService.read_command_receipt(
                session=db,
                tenant_id=package.tenant_id,
                command_id=record.command_id,
                expected_command_type=command_type,
                expected_result_code=result_code,
                expected_aggregate_type=aggregate_type,
                expected_aggregate_id=record.id,
                expected_aggregate_revision=revision,
            )
        return {
            "snapshot_id": str(snapshot.id),
            "snapshot_version": snapshot.version,
            "manifest_sha256": snapshot.manifest_sha256,
            "transmission_id": str(transmission.id),
            "technical_document_id": str(snapshot.technical_document_id),
            "technical_document_version": snapshot.technical_document_version,
            "readiness": manifest["readiness"],
            "response_drafts": drafts,
        }
