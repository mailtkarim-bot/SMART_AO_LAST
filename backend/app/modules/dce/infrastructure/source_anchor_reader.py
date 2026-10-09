"""Read-only SourceAnchor projections over immutable DCE extraction fragments."""

from __future__ import annotations

import re
from collections.abc import Iterable
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.dce.application.source_anchor_projection import (
    DceSourceAnchorProjection,
    resolve_dce_source_locator,
)
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentRecord,
    DceVersionRecord,
)

_SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")


class SqlAlchemyDceSourceAnchorReader:
    def get(
        self, *, session: Session, tenant_id: UUID, fragment_id: UUID
    ) -> DceSourceAnchorProjection | None:
        return self.get_many(
            session=session,
            tenant_id=tenant_id,
            fragment_ids=(fragment_id,),
        ).get(fragment_id)

    def get_many(
        self,
        *,
        session: Session,
        tenant_id: UUID | str,
        fragment_ids: Iterable[UUID],
        dce_version_id: UUID | None = None,
    ) -> dict[UUID, DceSourceAnchorProjection]:
        selected_ids = tuple(dict.fromkeys(fragment_ids))
        if not selected_ids:
            return {}
        fragment = DceDocumentExtractionFragmentRecord
        extraction = DceDocumentExtractionRecord
        document = DceDocumentRecord
        version = DceVersionRecord
        statement = (
            sa.select(fragment, extraction, document, version)
            .join(
                extraction,
                sa.and_(
                    extraction.tenant_id == fragment.tenant_id,
                    extraction.id == fragment.extraction_id,
                ),
            )
            .join(
                document,
                sa.and_(
                    document.tenant_id == extraction.tenant_id,
                    document.id == extraction.dce_document_id,
                ),
            )
            .join(
                version,
                sa.and_(
                    version.tenant_id == extraction.tenant_id,
                    version.id == extraction.dce_version_id,
                    version.id == document.dce_version_id,
                ),
            )
            .where(
                fragment.tenant_id == tenant_id,
                fragment.id.in_(selected_ids),
                extraction.status == "COMPLETED",
            )
        )
        if dce_version_id is not None:
            statement = statement.where(extraction.dce_version_id == dce_version_id)
        rows = session.execute(statement).all()

        projections = {}
        for fragment_record, extraction_record, document_record, _version_record in rows:
            document_sha256 = _canonical_sha256(document_record.sha256)
            extraction_sha256 = _canonical_sha256(extraction_record.input_sha256)
            fragment_sha256 = _canonical_sha256(fragment_record.text_sha256)
            if document_sha256 != extraction_sha256:
                raise ValueError("DCE_SOURCE_ANCHOR_SOURCE_HASH_MISMATCH")

            projections[fragment_record.id] = DceSourceAnchorProjection(
                source_anchor_id=fragment_record.id,
                dce_version_id=extraction_record.dce_version_id,
                dce_document_id=document_record.id,
                extraction_id=extraction_record.id,
                fragment_ordinal=fragment_record.ordinal,
                source_sha256=document_sha256,
                extractor_id=extraction_record.extractor_id,
                extractor_version=extraction_record.extractor_version,
                fragment_sha256=fragment_sha256,
                locator=resolve_dce_source_locator(fragment_record.locator_json),
            )
        return projections


def _canonical_sha256(value: object) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError("DCE_SOURCE_ANCHOR_HASH_INVALID")
    return value.lower()
