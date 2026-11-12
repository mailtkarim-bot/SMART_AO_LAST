from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha256
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, aliased, sessionmaker
from sqlalchemy.sql.elements import ColumnElement

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord
from app.modules.knowledge.domain.retrieval import DataClassification, RetrievalChunk


def current_completed_extraction() -> ColumnElement[bool]:
    """Use the RC analyser's conservative ordering, including equal-time refusals."""
    extraction = DceDocumentExtractionRecord
    newer = aliased(DceDocumentExtractionRecord)
    superseded = (
        sa.select(newer.id)
        .where(
            newer.tenant_id == extraction.tenant_id,
            newer.dce_document_id == extraction.dce_document_id,
            sa.or_(
                newer.created_at > extraction.created_at,
                sa.and_(
                    newer.created_at == extraction.created_at,
                    sa.or_(newer.status != "COMPLETED", newer.id > extraction.id),
                ),
            ),
        )
        .correlate(extraction)
        .exists()
    )
    return sa.and_(extraction.status == "COMPLETED", ~superseded)


class SqlAlchemyDceRetrievalSource:
    """Reads only completed fragments for the case's current DCE version."""

    def __init__(self, *, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def read_chunks(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        dce_version_id: UUID,
    ) -> Sequence[RetrievalChunk]:
        with self._session_factory() as session:
            rows = session.execute(
                sa.select(
                    DceDocumentExtractionFragmentRecord,
                    DceDocumentExtractionRecord,
                )
                .join(
                    DceDocumentExtractionRecord,
                    sa.and_(
                        DceDocumentExtractionRecord.tenant_id
                        == DceDocumentExtractionFragmentRecord.tenant_id,
                        DceDocumentExtractionRecord.id
                        == DceDocumentExtractionFragmentRecord.extraction_id,
                    ),
                )
                .join(
                    DceDocumentRecord,
                    sa.and_(
                        DceDocumentRecord.tenant_id == DceDocumentExtractionRecord.tenant_id,
                        DceDocumentRecord.id == DceDocumentExtractionRecord.dce_document_id,
                        DceDocumentRecord.dce_version_id
                        == DceDocumentExtractionRecord.dce_version_id,
                        DceDocumentRecord.sha256 == DceDocumentExtractionRecord.input_sha256,
                    ),
                )
                .join(
                    CaseRecord,
                    sa.and_(
                        CaseRecord.tenant_id == DceDocumentExtractionRecord.tenant_id,
                        CaseRecord.id == case_id,
                        CaseRecord.applicable_dce_version_id
                        == DceDocumentExtractionRecord.dce_version_id,
                    ),
                )
                .where(
                    DceDocumentExtractionFragmentRecord.tenant_id == tenant_id,
                    DceDocumentExtractionRecord.dce_version_id == dce_version_id,
                    current_completed_extraction(),
                )
                .order_by(
                    DceDocumentExtractionFragmentRecord.ordinal,
                    DceDocumentExtractionFragmentRecord.id,
                )
            ).all()

        if any(
            sha256(fragment.text.encode()).hexdigest() != fragment.text_sha256
            for fragment, _ in rows
        ):
            raise ValueError("DCE_FRAGMENT_INTEGRITY_MISMATCH")

        return tuple(
            RetrievalChunk(
                chunk_id=fragment.id,
                tenant_id=fragment.tenant_id,
                case_id=case_id,
                dce_version_id=extraction.dce_version_id,
                source_fragment_id=fragment.id,
                ordinal=fragment.ordinal,
                text=fragment.text,
                locator=fragment.locator_json,
                classification=DataClassification.INTERNAL_OPERATIONAL,
            )
            for fragment, extraction in rows
            # Cross-cell conditions remain unqualified outside the human L04 review.
            if fragment.locator_json.get("kind") != "docx_table_cell"
        )
