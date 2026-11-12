"""One native, append-only DOCX draft derived from exact reviewed contributions."""

from __future__ import annotations

import hashlib
import json

import sqlalchemy as sa

from app.modules.membership.public.text_safety import contains_forbidden_text
from app.modules.preparation.infrastructure.buyer_docx_sources import (
    load_buyer_template,
    render_buyer_response,
)
from app.modules.preparation.infrastructure.models import TechnicalResponseDraftRecord
from app.modules.preparation.infrastructure.response_artifact import (
    docx_text,
    read_response_artifact,
)
from app.platform.events.dispatcher import CommandExecutionError
from app.platform.security.context import ActorKind


class BuyerDocxResponseDraftHandler:
    def __init__(self, review):
        self.review = review

    def execute(self, *, session, command, context):
        if context.actor_kind != ActorKind.COLLABORATEUR.value:
            raise CommandExecutionError("COLLABORATOR_REQUIRED")
        package = self.review._package(
            session=session, context=context, package_id=command.package_id
        )
        if package.aggregate_revision != command.expected_package_revision:
            raise CommandExecutionError("VERSION_CONFLICT")
        source = command.source_response
        original = self.review._exact_response_draft(
            session=session,
            context=context,
            package=package,
            draft_id=source.draft_id,
            version=source.version,
            expected_sha256=source.content_sha256,
        )
        if original.content_format != "MARKDOWN" or command.draft_id == source.draft_id:
            raise CommandExecutionError("BUYER_DOCX_MARKDOWN_SOURCE_REQUIRED")
        from app.modules.preparation.application.transmission import PreparationTransmissionHandler

        source_review = PreparationTransmissionHandler(
            storage=self.review._storage
        ).current_c10_review_manifest(
            session=session,
            package=package,
            tenant_id=context.tenant_id,
            selected_response_draft=source,
        )
        if not source_review or len(source_review) != 1:
            raise CommandExecutionError("RESPONSE_DRAFT_REVIEW_REQUIRED")
        source_bytes, _ = read_response_artifact(self.review._storage, original)
        template = load_buyer_template(
            session,
            tenant_id=context.tenant_id,
            package=package,
            reference=command.template,
            storage=self.review._storage,
        )
        try:
            content, regions = render_buyer_response(template, source_bytes, command.fields)
            if contains_forbidden_text(docx_text(content)):
                raise ValueError("FINANCIAL_DATA_FORBIDDEN")
        except ValueError as error:
            raise CommandExecutionError(str(error)) from error
        version = (
            session.scalar(
                sa.select(
                    sa.func.coalesce(sa.func.max(TechnicalResponseDraftRecord.version), 0)
                ).where(
                    TechnicalResponseDraftRecord.tenant_id == context.tenant_id,
                    TechnicalResponseDraftRecord.draft_id == command.draft_id,
                )
            )
            + 1
        )
        provenance = {
            "schema_version": 1,
            "source_response": source.model_dump(mode="json"),
            "source_review": {
                "review_id": source_review[0]["review_id"],
                "review_revision": source_review[0]["review_revision"],
            },
            "template": command.template.model_dump(mode="json"),
            "fields": [f.model_dump(mode="json") for f in command.fields],
            "regions": regions,
        }
        digest = hashlib.sha256(content).hexdigest()
        key = (
            f"technical-response-drafts/{context.tenant_id}/{package.id}/"
            f"{command.draft_id}/{version}.docx"
        )
        try:
            written = self.review._storage.write(storage_key=key, content=content)
        except FileExistsError:
            written = hashlib.sha256(self.review._storage.read(storage_key=key)).hexdigest()
        if written != digest:
            raise CommandExecutionError("BUYER_DOCX_WRITE_UNKNOWN")
        session.add(
            TechnicalResponseDraftRecord(
                id=command.command_id,
                tenant_id=context.tenant_id,
                draft_id=command.draft_id,
                package_id=package.id,
                source_document_id=original.source_document_id,
                response_plan_id=original.response_plan_id,
                response_plan_version=original.response_plan_version,
                version=version,
                state="DRAFT",
                section_codes_json=original.section_codes_json,
                source_refs_json=original.source_refs_json,
                responsible_role="COLLABORATEUR",
                content_sha256=digest,
                storage_key=key,
                content_format="DOCX",
                content_provenance_json=provenance,
                actor_id=context.actor_id,
                membership_id=context.membership_id,
                command_id=command.command_id,
                idempotency_key=command.idempotency_key,
                correlation_id=context.correlation_id,
            )
        )
        package.aggregate_revision += 1
        package.state = "IN_PREPARATION"
        return self.review._outcome(
            aggregate_type="TechnicalResponseDraft",
            aggregate_id=command.draft_id,
            revision=version,
            event_type="BuyerDocxResponseDraftCreated",
            payload={
                "package_id": str(package.id),
                "draft_id": str(command.draft_id),
                "version": version,
                "content_sha256": digest,
                "content_provenance_sha256": hashlib.sha256(
                    json.dumps(provenance, sort_keys=True, separators=(",", ":")).encode()
                ).hexdigest(),
            },
            result_code="BUYER_DOCX_RESPONSE_DRAFT_CREATED",
        )
