"""Read-only comparison of current safe DCE signals and one exact native response."""

from __future__ import annotations

import json
from types import SimpleNamespace

import sqlalchemy as sa

from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.preparation.application.document_content import build_response_coverage
from app.modules.preparation.infrastructure.buyer_docx_sources import validate_buyer_docx_sources
from app.modules.preparation.infrastructure.contribution_sources import (
    CONTRIBUTION_SOURCE_PREFIX,
    contribution_source_snapshots,
    validate_contribution_sources,
)
from app.modules.preparation.infrastructure.models import (
    PreparationPackageRecord,
    PreparationResponsePlanRecord,
    TechnicalResponseDraftRecord,
)
from app.modules.preparation.infrastructure.response_artifact import (
    read_response_artifact,
    source_contributions,
)
from app.modules.preparation.public.contracts import (
    ResponseCitedAnnex,
    ResponseCoverageProjection,
    SelectedResponseDraft,
)
from app.platform.events.dispatcher import CommandExecutionError


def read_response_coverage(session, *, tenant_id, package_id, selection, storage):
    selection = SelectedResponseDraft.model_validate(selection)
    package = session.scalar(
        sa.select(PreparationPackageRecord)
        .where(
            PreparationPackageRecord.tenant_id == tenant_id,
            PreparationPackageRecord.id == package_id,
        )
        .with_for_update(read=True, nowait=True)
    )
    if package is None:
        raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
    draft = session.scalar(
        sa.select(TechnicalResponseDraftRecord)
        .where(
            TechnicalResponseDraftRecord.tenant_id == tenant_id,
            TechnicalResponseDraftRecord.package_id == package_id,
            TechnicalResponseDraftRecord.draft_id == selection.draft_id,
        )
        .order_by(TechnicalResponseDraftRecord.version.desc())
        .limit(1)
    )
    if (
        draft is None
        or draft.version != selection.version
        or draft.content_sha256 != selection.content_sha256
    ):
        raise CommandExecutionError("RESPONSE_DRAFT_SELECTION_UNKNOWN")
    plan = session.scalar(
        sa.select(PreparationResponsePlanRecord)
        .where(
            PreparationResponsePlanRecord.tenant_id == tenant_id,
            PreparationResponsePlanRecord.package_id == package_id,
        )
        .order_by(PreparationResponsePlanRecord.version.desc())
        .limit(1)
    )
    if (
        plan is None
        or plan.state != "SOURCES_CURRENT"
        or plan.plan_id != draft.response_plan_id
        or plan.version != draft.response_plan_version
    ):
        raise CommandExecutionError("RESPONSE_PLAN_UNKNOWN")
    lookup = SqlAlchemyCaseDceReadingReader(session).get(
        tenant_id=tenant_id, case_id=package.case_id
    )
    if (
        lookup is None
        or lookup.reading is None
        or lookup.case_lifecycle != "ACTIVE"
        or lookup.dce_freshness != "CURRENT"
        or lookup.reading.dce_version_id != package.dce_version_id
        or lookup.reading.lifecycle != "ADMITTED"
        or lookup.reading.integrity != "VERIFIED"
    ):
        raise CommandExecutionError("CONTRIBUTION_SOURCE_UNKNOWN")
    try:
        raw, text = read_response_artifact(storage, draft)
        selected_byte_size = len(raw)
        regions = None
        if draft.content_format == "DOCX":
            regions = validate_buyer_docx_sources(
                session,
                tenant_id=tenant_id,
                package=package,
                draft=draft,
                storage=storage,
            )
            original = SelectedResponseDraft.model_validate(
                draft.content_provenance_json["source_response"]
            )
            source = session.scalar(
                sa.select(TechnicalResponseDraftRecord).where(
                    TechnicalResponseDraftRecord.tenant_id == tenant_id,
                    TechnicalResponseDraftRecord.package_id == package_id,
                    TechnicalResponseDraftRecord.draft_id == original.draft_id,
                    TechnicalResponseDraftRecord.version == original.version,
                )
            )
            raw, _ = read_response_artifact(storage, source)
        else:
            validate_contribution_sources(
                session,
                tenant_id=tenant_id,
                case_id=package.case_id,
                dce_version_id=package.dce_version_id,
                content=text,
            )
        contributions = source_contributions(raw)
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN") from error
    requirements = build_response_coverage(
        requirements=lookup.reading.requirements,
        contributions=contributions,
        regions=regions,
    )
    buyer_sources = contribution_source_snapshots(
        session,
        tenant_id=tenant_id,
        case_id=package.case_id,
        dce_version_id=package.dce_version_id,
        contributions=[
            SimpleNamespace(requirement_id=row["requirement_id"], content="")
            for row in requirements
        ],
    )
    for row in requirements:
        row["source_excerpt"] = buyer_sources[row["requirement_id"]].get("buyer_excerpt")
    selected_items = {
        (str(row["requirement_id"]), piece["section_code"])
        for row in requirements
        for piece in row["pieces"]
    }
    cited_annexes = []
    try:
        for line in raw.decode("utf-8").splitlines():
            if not line.startswith(CONTRIBUTION_SOURCE_PREFIX):
                continue
            source = json.loads(line[len(CONTRIBUTION_SOURCE_PREFIX) :])
            identity = source["buyer"]["requirement_id"], source["section_code"]
            if identity not in selected_items:
                continue
            for proof in source["enterprise"]["proofs"]:
                cited_annexes.append(
                    ResponseCitedAnnex(
                        requirement_id=identity[0],
                        section_code=identity[1],
                        document_id=proof["document_id"],
                        sha256=proof["sha256"],
                    )
                )
    except (KeyError, TypeError, ValueError) as error:
        raise CommandExecutionError("RESPONSE_DRAFT_UNKNOWN") from error
    return ResponseCoverageProjection(
        content_byte_size=selected_byte_size,
        package_id=package.id,
        dce_version_id=package.dce_version_id,
        selected_response=selection,
        content_format=draft.content_format,
        requirements=requirements,
        cited_annexes=cited_annexes,
    )
