"""Technical eligibility of current admitted inputs, never analysis completeness."""

import json
from collections import Counter
from hashlib import sha256
from uuid import UUID

import sqlalchemy as sa

from app.modules.dce.domain.rc_source_manifest import rc_source_manifest
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord as Fragment,
)
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionRecord as Extraction,
)
from app.modules.dce.infrastructure.models.dce_rc_analysis import DceRcAnalysisRunRecord as Analysis
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord as Materialization,
)
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord as Classification,
)
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord as Document


def _current_preparation_readiness(session, *, version, lock_documents=False):
    """Retain an explicit legacy declaration only until new pipeline evidence exists."""
    if (
        version.lifecycle != "ADMITTED"
        or version.integrity != "VERIFIED"
        or version.analysis_readiness == "REVIEW_REQUIRED"
    ):
        return "REVIEW_REQUIRED", None
    tenant, identity = version.tenant_id, version.id
    extractions = list(
        session.scalars(
            sa.select(Extraction)
            .where(Extraction.tenant_id == tenant, Extraction.dce_version_id == identity)
            .order_by(
                Extraction.created_at.desc(),
                (Extraction.status != "COMPLETED").desc(),
                Extraction.id.desc(),
            )
            .limit(100001)
        )
    )
    analysis = session.scalar(
        sa.select(Analysis)
        .where(Analysis.tenant_id == tenant, Analysis.dce_version_id == identity)
        .order_by(
            Analysis.created_at.desc(), (Analysis.status != "COMPLETED").desc(), Analysis.id.desc()
        )
        .limit(1)
    )
    if not extractions:
        return version.analysis_readiness, None
    if (
        len(extractions) > 100000
        or analysis is None
        or analysis.status != "COMPLETED"
        or analysis.analyzer_version not in {"10", "11"}
    ):
        return "NOT_READY", None
    if lock_documents:
        session.scalars(
            sa.select(Document)
            .where(Document.tenant_id == tenant, Document.dce_version_id == identity)
            .order_by(Document.id)
            .with_for_update(read=True, nowait=True)
        ).all()
    documents = list(
        session.scalars(
            sa.select(Document)
            .where(Document.tenant_id == tenant, Document.dce_version_id == identity)
            .order_by(Document.id)
            .limit(1001)
        )
    )
    if not documents or len(documents) > 1000:
        return "NOT_READY", None
    latest: dict[UUID, Extraction] = {}
    for extraction in extractions:
        latest.setdefault(extraction.dce_document_id, extraction)
    if any(
        d.id not in latest
        or latest[d.id].status != "COMPLETED"
        or latest[d.id].input_sha256 != d.sha256
        for d in documents
    ):
        return "REVIEW_REQUIRED", None
    classes = list(
        session.scalars(
            sa.select(Classification).where(
                Classification.tenant_id == tenant,
                Classification.dce_document_id.in_([d.id for d in documents]),
                Classification.is_current.is_(True),
            )
        )
    )
    by_document = {r.dce_document_id: (r.id, r.classification) for r in classes}
    if len(by_document) != len(documents) or any(
        not kind or kind in {"UNKNOWN", "UNCLASSIFIED"} for _, kind in by_document.values()
    ):
        return "NOT_READY", None
    fragments = list(
        session.scalars(
            sa.select(Fragment)
            .where(
                Fragment.tenant_id == tenant,
                Fragment.extraction_id.in_([latest[d.id].id for d in documents]),
            )
            .order_by(Fragment.extraction_id, Fragment.ordinal, Fragment.id)
            .limit(100001)
        )
    )
    if len(fragments) > 100000 or any(
        sha256(f.text.encode()).hexdigest() != f.text_sha256 for f in fragments
    ):
        return "REVIEW_REQUIRED", None
    extraction_documents = {e.id: e.dce_document_id for e in latest.values()}
    fragments.sort(
        key=lambda f: (
            str(extraction_documents[f.extraction_id]),
            str(f.extraction_id),
            f.ordinal,
            str(f.id),
        )
    )
    counts = Counter(f.extraction_id for f in fragments)
    if any(
        counts[latest[d.id].id] != latest[d.id].fragment_count or counts[latest[d.id].id] == 0
        for d in documents
    ):
        return "REVIEW_REQUIRED", None
    manifest = rc_source_manifest(
        [
            (extraction_documents[f.extraction_id], f.extraction_id, f.id, f.ordinal, f.text_sha256)
            for f in fragments
        ],
        classifications=by_document,
        format_version=2,
    )
    if manifest != analysis.input_manifest_sha256:
        return "REVIEW_REQUIRED", None
    materialization = session.scalar(
        sa.select(Materialization)
        .where(Materialization.tenant_id == tenant, Materialization.dce_version_id == identity)
        .order_by(
            Materialization.created_at.desc(),
            (Materialization.status != "COMPLETED").desc(),
            Materialization.id.desc(),
        )
        .limit(1)
    )
    if (
        materialization is None
        or materialization.status != "COMPLETED"
        or materialization.dce_rc_analysis_id != analysis.id
    ):
        return "NOT_READY", None
    proof = sha256(
        json.dumps(
            {
                "dce_version_id": str(identity),
                "analysis_id": str(analysis.id),
                "analysis_input_sha256": manifest,
                "requirements_run_id": str(materialization.id),
                "requirements_input_sha256": materialization.input_manifest_sha256,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return "READY_FOR_ANALYSIS", proof


def current_preparation_readiness(session, *, version, lock=False):
    if not lock:
        return _current_preparation_readiness(session, version=version)
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord

    try:
        with session.begin_nested():
            current = session.scalar(
                sa.select(DceVersionRecord)
                .where(
                    DceVersionRecord.tenant_id == version.tenant_id,
                    DceVersionRecord.id == version.id,
                )
                .execution_options(populate_existing=True)
                .with_for_update(read=True, nowait=True)
            )
            if current is None:
                return "REVIEW_REQUIRED", None
            return _current_preparation_readiness(session, version=current, lock_documents=True)
    except sa.exc.OperationalError:
        return "REVIEW_REQUIRED", None
