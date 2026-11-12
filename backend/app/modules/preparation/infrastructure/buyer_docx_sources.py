"""Exact buyer-frame/source reconstruction used at creation and every later act."""

from __future__ import annotations

import hashlib
from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.preparation.infrastructure.buyer_docx import DocxFill, fill_template
from app.modules.preparation.infrastructure.contribution_sources import (
    validate_contribution_sources,
)
from app.modules.preparation.infrastructure.models import (
    PreparationReviewRecord,
    TechnicalResponseDraftRecord,
)
from app.modules.preparation.infrastructure.response_artifact import (
    read_response_artifact,
    source_contributions,
)
from app.modules.preparation.public.contracts import (
    BuyerDocxFieldMapping,
    BuyerDocxTemplateReference,
    SelectedResponseDraft,
)
from app.platform.events.dispatcher import CommandExecutionError

DOCX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def load_buyer_template(session, *, tenant_id, package, reference, storage):
    try:
        reference = BuyerDocxTemplateReference.model_validate(reference)
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == package.case_id)
            .with_for_update(read=True, nowait=True)
        )
        version = session.scalar(
            sa.select(DceVersionRecord)
            .where(
                DceVersionRecord.tenant_id == tenant_id,
                DceVersionRecord.id == package.dce_version_id,
            )
            .with_for_update(read=True, nowait=True)
        )
        if (
            case is None
            or version is None
            or case.lifecycle != "ACTIVE"
            or case.dce_freshness != "CURRENT"
            or case.applicable_dce_version_id != package.dce_version_id
            or version.lifecycle != "ADMITTED"
            or version.integrity != "VERIFIED"
            or reference.dce_version_id != package.dce_version_id
        ):
            raise ValueError("template context")
        row = session.execute(
            sa.select(DceDocumentRecord, DceStagedObjectRecord)
            .join(
                DceStagedObjectRecord,
                sa.and_(
                    DceStagedObjectRecord.tenant_id == DceDocumentRecord.tenant_id,
                    DceStagedObjectRecord.id == DceDocumentRecord.storage_object_id,
                ),
            )
            .where(
                DceDocumentRecord.tenant_id == tenant_id,
                DceDocumentRecord.dce_version_id == package.dce_version_id,
                DceDocumentRecord.id == reference.document_id,
            )
            .with_for_update(read=True, nowait=True)
        ).one_or_none()
        if row is None:
            raise ValueError("template missing")
        document, staged = row
        if (
            document.media_type != DOCX_MEDIA_TYPE
            or document.sha256 != reference.sha256
            or staged.state != "CONSUMED"
            or staged.consumed_by_dce_version_id != package.dce_version_id
            or staged.sha256 != reference.sha256
        ):
            raise ValueError("template source")
        content = storage.read(storage_key=staged.storage_key)
        if hashlib.sha256(content).hexdigest() != reference.sha256:
            raise ValueError("template hash")
        return content
    except sa.exc.OperationalError as error:
        raise CommandExecutionError("VERSION_CONFLICT") from error
    except (ValueError, OSError) as error:
        raise CommandExecutionError("BUYER_TEMPLATE_UNKNOWN") from error


def render_buyer_response(template: bytes, source: bytes, fields):
    contributions = source_contributions(source)
    mappings = [BuyerDocxFieldMapping.model_validate(field) for field in fields]
    fills, provenance = [], {}
    for field in mappings:
        part = contributions.get((str(field.requirement_id), field.section_code))
        if part is None:
            raise ValueError("BUYER_CONTRIBUTION_UNKNOWN")
        fills.append(DocxFill(field.locator, field.expected_xml_sha256, part.text))
        provenance[field.locator] = {
            "requirement_id": part.requirement_id,
            "section_code": part.section_code,
            "start_byte": part.start_byte,
            "end_byte": part.end_byte,
            "raw_sha256": part.raw_sha256,
            "missing": part.missing,
        }
    result = fill_template(template, tuple(fills))
    regions = [
        {
            "locator": region.locator,
            "template_region_sha256": region.xml_sha256,
            "text_sha256": hashlib.sha256(region.text.encode()).hexdigest(),
            "state": region.state,
            "source": provenance.get(region.locator),
        }
        for region in result.regions
    ]
    return result.content, regions


def validate_buyer_docx_sources(session, *, tenant_id, package, draft, storage):
    try:
        provenance = draft.content_provenance_json
        if not isinstance(provenance, dict) or provenance.get("schema_version") != 1:
            raise ValueError("provenance")
        source = SelectedResponseDraft.model_validate(provenance["source_response"])
        original = session.scalar(
            sa.select(TechnicalResponseDraftRecord).where(
                TechnicalResponseDraftRecord.tenant_id == tenant_id,
                TechnicalResponseDraftRecord.package_id == package.id,
                TechnicalResponseDraftRecord.draft_id == source.draft_id,
                TechnicalResponseDraftRecord.version == source.version,
            )
        )
        latest = session.scalar(
            sa.select(sa.func.max(TechnicalResponseDraftRecord.version)).where(
                TechnicalResponseDraftRecord.tenant_id == tenant_id,
                TechnicalResponseDraftRecord.package_id == package.id,
                TechnicalResponseDraftRecord.draft_id == source.draft_id,
            )
        )
        if (
            original is None
            or original.content_format != "MARKDOWN"
            or latest != source.version
            or original.content_sha256 != source.content_sha256
            or original.response_plan_id != draft.response_plan_id
            or original.response_plan_version != draft.response_plan_version
        ):
            raise ValueError("source")
        source_bytes, text = read_response_artifact(storage, original)
        validate_contribution_sources(
            session,
            tenant_id=tenant_id,
            case_id=package.case_id,
            dce_version_id=package.dce_version_id,
            content=text,
        )
        accepted = provenance["source_review"]
        review = session.scalar(
            sa.select(PreparationReviewRecord)
            .where(
                PreparationReviewRecord.tenant_id == tenant_id,
                PreparationReviewRecord.package_id == package.id,
                PreparationReviewRecord.review_id == UUID(accepted["review_id"]),
            )
            .order_by(PreparationReviewRecord.revision.desc())
            .limit(1)
        )
        if (
            review is None
            or review.state != "ACCEPTED"
            or review.revision != accepted["review_revision"]
            or review.target_draft_id != source.draft_id
            or review.target_draft_version != source.version
            or review.target_content_sha256 != source.content_sha256
        ):
            raise ValueError("source review")
        template = load_buyer_template(
            session,
            tenant_id=tenant_id,
            package=package,
            reference=provenance["template"],
            storage=storage,
        )
        content, regions = render_buyer_response(template, source_bytes, provenance["fields"])
        if (
            regions != provenance["regions"]
            or hashlib.sha256(content).hexdigest() != draft.content_sha256
        ):
            raise ValueError("output provenance")
        return regions
    except CommandExecutionError:
        raise
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise CommandExecutionError("BUYER_DOCX_SOURCE_UNKNOWN") from error


def inspect_buyer_docx_inputs(session, *, tenant_id, package_id, source_response, storage):
    from app.modules.membership.public.text_safety import contains_forbidden_text
    from app.modules.preparation.application.transmission import PreparationTransmissionHandler
    from app.modules.preparation.infrastructure.buyer_docx import inspect_template
    from app.modules.preparation.infrastructure.models import PreparationPackageRecord
    from app.modules.preparation.infrastructure.response_artifact import docx_text

    package = session.scalar(
        sa.select(PreparationPackageRecord).where(
            PreparationPackageRecord.tenant_id == tenant_id,
            PreparationPackageRecord.id == package_id,
        )
    )
    if package is None:
        raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
    source = SelectedResponseDraft.model_validate(source_response)
    original = session.scalar(
        sa.select(TechnicalResponseDraftRecord).where(
            TechnicalResponseDraftRecord.tenant_id == tenant_id,
            TechnicalResponseDraftRecord.package_id == package_id,
            TechnicalResponseDraftRecord.draft_id == source.draft_id,
            TechnicalResponseDraftRecord.version == source.version,
        )
    )
    if original is None or original.content_format != "MARKDOWN":
        raise CommandExecutionError("BUYER_DOCX_MARKDOWN_SOURCE_REQUIRED")
    PreparationTransmissionHandler(storage=storage).current_c10_review_manifest(
        session=session, package=package, tenant_id=tenant_id, selected_response_draft=source
    )
    raw, _ = read_response_artifact(storage, original)
    contributions = source_contributions(raw)
    documents = list(
        session.scalars(
            sa.select(DceDocumentRecord)
            .where(
                DceDocumentRecord.tenant_id == tenant_id,
                DceDocumentRecord.dce_version_id == package.dce_version_id,
                DceDocumentRecord.media_type == DOCX_MEDIA_TYPE,
            )
            .order_by(DceDocumentRecord.id)
            .limit(65)
        )
    )
    templates = []
    for doc in documents[:64]:
        reference = {
            "document_id": str(doc.id),
            "dce_version_id": str(doc.dce_version_id),
            "sha256": doc.sha256,
        }
        item = {
            "template": reference,
            "filename": doc.original_filename,
            "state": "REVIEW_REQUIRED",
            "regions": [],
            "reason": None,
        }
        try:
            data = load_buyer_template(
                session, tenant_id=tenant_id, package=package, reference=reference, storage=storage
            )
            if contains_forbidden_text(docx_text(data)):
                raise ValueError("FINANCIAL_DATA_FORBIDDEN")
            regions = inspect_template(data)
            item.update(
                state="CANDIDATE",
                regions=[
                    {"locator": r.locator, "xml_sha256": r.xml_sha256, "text": r.text}
                    for r in regions
                ],
            )
        except (ValueError, CommandExecutionError) as error:
            item["reason"] = str(error)
        templates.append(item)
    return {
        "package_id": str(package.id),
        "package_revision": package.aggregate_revision,
        "source_response": source.model_dump(mode="json"),
        "contributions": [
            {
                "requirement_id": c.requirement_id,
                "section_code": c.section_code,
                "text": c.text,
                "missing": c.missing,
                "start_byte": c.start_byte,
                "end_byte": c.end_byte,
                "raw_sha256": c.raw_sha256,
            }
            for c in contributions.values()
        ],
        "templates": templates,
        "truncated": len(documents) > 64,
    }
