from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha256
from math import isfinite
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.knowledge.application.retrieval import (
    InMemoryVectorIndex,
    VectorIndex,
)
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    EmbeddingVector,
    RetrievalChunk,
    RetrievalResult,
    RetrievalScope,
)
from app.modules.knowledge.infrastructure.dce_source import (
    SqlAlchemyDceRetrievalSource,
    current_completed_extraction,
)
from app.modules.knowledge.infrastructure.models import DceFragmentEmbeddingRecord


class SqlAlchemyVectorIndex(VectorIndex):
    """Persistent index bridge until a measured pgvector migration is justified."""

    def __init__(self, *, session_factory: sessionmaker[Session], model_id: str) -> None:
        if not model_id.strip():
            raise ValueError("model_id must not be empty")
        self._session_factory = session_factory
        self._model_id = model_id
        self._source = SqlAlchemyDceRetrievalSource(session_factory=session_factory)

    def upsert(
        self,
        *,
        chunks: Sequence[RetrievalChunk],
        embeddings: Sequence[EmbeddingVector],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        with self._session_factory.begin() as session:
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                if chunk.classification is DataClassification.FINANCIAL_PRIVATE:
                    continue
                current = {
                    item.source_fragment_id: item
                    for item in self._source.read_chunks(
                        tenant_id=chunk.tenant_id,
                        case_id=chunk.case_id,
                        dce_version_id=chunk.dce_version_id,
                    )
                }.get(chunk.source_fragment_id)
                if current is None or (
                    chunk.text != current.text
                    or chunk.ordinal != current.ordinal
                    or chunk.locator != current.locator
                    or chunk.classification != current.classification
                ):
                    raise ValueError("DCE_EMBEDDING_SOURCE_MISMATCH")
                _validate_vector(embedding.values, embedding.dimension)
                source_hash = sha256(chunk.text.encode("utf-8")).hexdigest()
                existing = session.scalar(
                    sa.select(DceFragmentEmbeddingRecord).where(
                        DceFragmentEmbeddingRecord.tenant_id == chunk.tenant_id,
                        DceFragmentEmbeddingRecord.fragment_id == chunk.source_fragment_id,
                        DceFragmentEmbeddingRecord.model_id == self._model_id,
                    )
                )
                if existing is not None:
                    _validate_vector(existing.embedding, existing.embedding_dimension)
                    embedding_values = list(embedding.values)
                    if (
                        existing.text_sha256 != source_hash
                        or existing.embedding != embedding_values
                        or existing.embedding_dimension != embedding.dimension
                        or existing.case_id != chunk.case_id
                        or existing.dce_version_id != chunk.dce_version_id
                        or existing.ordinal != chunk.ordinal
                        or existing.text != chunk.text
                        or existing.locator_json != chunk.locator
                        or existing.classification != chunk.classification.value
                    ):
                        raise ValueError("embedding identity already exists with different content")
                    continue
                session.add(
                    DceFragmentEmbeddingRecord(
                        id=uuid4(),
                        tenant_id=chunk.tenant_id,
                        dce_version_id=chunk.dce_version_id,
                        case_id=chunk.case_id,
                        fragment_id=chunk.source_fragment_id,
                        model_id=self._model_id,
                        ordinal=chunk.ordinal,
                        text=chunk.text,
                        locator_json=chunk.locator,
                        classification=chunk.classification.value,
                        text_sha256=source_hash,
                        embedding=list(embedding.values),
                        embedding_dimension=embedding.dimension,
                    )
                )

    def search(
        self,
        *,
        query: EmbeddingVector,
        scope: RetrievalScope,
        top_k: int,
        embedding_model: str,
    ) -> list[RetrievalResult]:
        if embedding_model != self._model_id:
            raise ValueError("DCE_EMBEDDING_MODEL_MISMATCH")
        with self._session_factory() as session:
            rows = session.scalars(
                sa.select(DceFragmentEmbeddingRecord)
                .join(
                    DceDocumentExtractionFragmentRecord,
                    sa.and_(
                        DceDocumentExtractionFragmentRecord.tenant_id
                        == DceFragmentEmbeddingRecord.tenant_id,
                        DceDocumentExtractionFragmentRecord.id
                        == DceFragmentEmbeddingRecord.fragment_id,
                    ),
                )
                .join(
                    DceDocumentExtractionRecord,
                    sa.and_(
                        DceDocumentExtractionRecord.tenant_id
                        == DceFragmentEmbeddingRecord.tenant_id,
                        DceDocumentExtractionRecord.id
                        == DceDocumentExtractionFragmentRecord.extraction_id,
                        DceDocumentExtractionRecord.dce_version_id
                        == DceFragmentEmbeddingRecord.dce_version_id,
                    ),
                )
                .join(
                    CaseRecord,
                    sa.and_(
                        CaseRecord.tenant_id == DceFragmentEmbeddingRecord.tenant_id,
                        CaseRecord.id == DceFragmentEmbeddingRecord.case_id,
                        CaseRecord.applicable_dce_version_id
                        == DceFragmentEmbeddingRecord.dce_version_id,
                    ),
                )
                .where(
                    current_completed_extraction(),
                    DceFragmentEmbeddingRecord.tenant_id == scope.tenant_id,
                    DceFragmentEmbeddingRecord.case_id == scope.case_id,
                    DceFragmentEmbeddingRecord.dce_version_id == scope.dce_version_id,
                    DceFragmentEmbeddingRecord.model_id == embedding_model,
                    DceFragmentEmbeddingRecord.classification.in_(
                        classification.value for classification in scope.allowed_classifications
                    ),
                )
                .order_by(
                    DceFragmentEmbeddingRecord.ordinal,
                    DceFragmentEmbeddingRecord.id,
                )
            ).all()
        if not rows:
            return []
        current = {
            item.source_fragment_id: item
            for item in self._source.read_chunks(
                tenant_id=scope.tenant_id,
                case_id=scope.case_id,
                dce_version_id=scope.dce_version_id,
            )
        }
        rows = [row for row in rows if row.fragment_id in current]
        for row in rows:
            source = current[row.fragment_id]
            if (
                row.text != source.text
                or row.text_sha256 != sha256(source.text.encode()).hexdigest()
                or row.ordinal != source.ordinal
                or row.locator_json != source.locator
                or row.classification != source.classification.value
            ):
                raise ValueError("DCE_EMBEDDING_INTEGRITY_MISMATCH")
            _validate_vector(row.embedding, row.embedding_dimension)
            if row.embedding_dimension != query.dimension:
                raise ValueError("DCE_EMBEDDING_INTEGRITY_MISMATCH")
        chunks = [
            RetrievalChunk(
                chunk_id=row.id,
                tenant_id=row.tenant_id,
                case_id=row.case_id,
                dce_version_id=row.dce_version_id,
                source_fragment_id=row.fragment_id,
                ordinal=row.ordinal,
                text=row.text,
                locator=row.locator_json,
                classification=DataClassification(row.classification),
            )
            for row in rows
        ]
        embeddings = [EmbeddingVector(values=tuple(row.embedding)) for row in rows]
        index = InMemoryVectorIndex()
        index.upsert(chunks=chunks, embeddings=embeddings)
        return index.search(
            query=query,
            scope=scope,
            top_k=top_k,
            embedding_model=embedding_model,
        )


def _validate_vector(values: Sequence[float], dimension: int) -> None:
    try:
        if (
            len(values) != dimension
            or not values
            or any(
                isinstance(v, bool) or not isinstance(v, (int, float)) or not isfinite(v)
                for v in values
            )
        ):
            raise ValueError("DCE_EMBEDDING_INTEGRITY_MISMATCH")
        squared_norm = sum(v * v for v in values)
        if not isfinite(squared_norm) or squared_norm <= 0:
            raise ValueError("DCE_EMBEDDING_INTEGRITY_MISMATCH")
    except (OverflowError, TypeError):
        raise ValueError("DCE_EMBEDDING_INTEGRITY_MISMATCH") from None
