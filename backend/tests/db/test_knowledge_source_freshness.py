from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.knowledge.domain.retrieval import (
    EmbeddingVector,
    RetrievalScope,
)
from app.modules.knowledge.infrastructure.dce_source import SqlAlchemyDceRetrievalSource
from app.modules.knowledge.infrastructure.models import DceFragmentEmbeddingRecord
from app.modules.knowledge.infrastructure.vector_index import SqlAlchemyVectorIndex
from app.platform.persistence.models import TenantRecord
from sqlalchemy.orm import Session, sessionmaker

NOW = datetime(2026, 10, 14, 12, tzinfo=UTC)
MODEL_ID = "synthetic-freshness"


def seed_indexed_source(session_factory: sessionmaker[Session]):
    tenant, consultation, version, document, staged, case, extraction, fragment = (
        uuid4() for _ in range(8)
    )
    text = "La visite est obligatoire."
    digest = sha256(text.encode()).hexdigest()
    with session_factory.begin() as session:
        session.add(TenantRecord(id=tenant, slug=f"r1-{tenant.hex}", lifecycle="ACTIVE"))
        session.flush()
        session.add(
            ConsultationRecord(
                id=consultation,
                tenant_id=tenant,
                functional_identity_hash="a" * 64,
                buyer_legal_name="Acheteur synthétique",
                object_label="Essai R1",
                source_channel="MANUAL_UPLOAD",
                source_received_at=NOW,
                lifecycle="OPEN",
                freshness="CURRENT",
            )
        )
        session.flush()
        session.add(
            DceVersionRecord(
                id=version,
                tenant_id=tenant,
                consultation_id=consultation,
                corpus_hash="b" * 64,
                provenance_channel="MANUAL_UPLOAD",
                source_received_at=NOW,
                lifecycle="ADMITTED",
                integrity="VERIFIED",
                classification_readiness="UNCLASSIFIED",
                analysis_readiness="NOT_READY",
            )
        )
        session.flush()
        session.add(
            DceStagedObjectRecord(
                id=staged,
                tenant_id=tenant,
                consultation_id=consultation,
                storage_key=f"synthetic/{staged}",
                original_filename="r1.txt",
                expected_byte_size=len(text.encode()),
                actual_byte_size=len(text.encode()),
                sha256=digest,
                media_type="text/plain",
                source_channel="MANUAL_UPLOAD",
                state="CONSUMED",
                scan_verdict="CLEAN",
                expires_at=NOW + timedelta(days=1),
                consumed_by_dce_version_id=version,
                consumed_at=NOW,
            )
        )
        session.flush()
        session.add(
            DceDocumentRecord(
                id=document,
                tenant_id=tenant,
                dce_version_id=version,
                storage_object_id=staged,
                storage_key=f"synthetic/{staged}",
                original_filename="r1.txt",
                media_type="text/plain",
                byte_size=len(text.encode()),
                sha256=digest,
                received_from="MANUAL_UPLOAD",
            )
        )
        session.add(
            CaseRecord(
                id=case,
                tenant_id=tenant,
                consultation_id=consultation,
                applicable_dce_version_id=version,
                functional_identity_hash="c" * 64,
                title="Affaire synthétique",
                business_origin="MANUAL",
                origin_rationale="Essai R1",
                scope_kind="SINGLE_LOT",
                scope_json={"lot": "1"},
                scope_fingerprint="d" * 64,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_READY",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
            )
        )
        session.flush()
        session.add(
            DceDocumentExtractionRecord(
                id=extraction,
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                input_sha256=digest,
                extractor_id="synthetic-initial",
                extractor_version="1",
                status="COMPLETED",
                fragment_count=1,
                extracted_char_count=len(text),
                created_at=NOW,
            )
        )
        session.flush()
        session.add(
            DceDocumentExtractionFragmentRecord(
                id=fragment,
                tenant_id=tenant,
                extraction_id=extraction,
                ordinal=1,
                locator_json={"page": 1},
                text=text,
                text_sha256=digest,
            )
        )
    source = SqlAlchemyDceRetrievalSource(session_factory=session_factory)
    index = SqlAlchemyVectorIndex(session_factory=session_factory, model_id=MODEL_ID)
    chunks = source.read_chunks(tenant_id=tenant, case_id=case, dce_version_id=version)
    assert [chunk.source_fragment_id for chunk in chunks] == [fragment]
    index.upsert(chunks=chunks, embeddings=[EmbeddingVector(values=(1.0, 0.0))])
    return tenant, case, version, document, extraction, fragment, digest, source, index


@pytest.fixture
def indexed_source(session_factory: sessionmaker[Session]):
    return seed_indexed_source(session_factory)


def _results(seed):
    tenant, case, version, _, _, _, _, _, index = seed
    return index.search(
        query=EmbeddingVector(values=(1.0, 0.0)),
        scope=RetrievalScope(tenant_id=tenant, case_id=case, dce_version_id=version),
        top_k=5,
        embedding_model=MODEL_ID,
    )


@pytest.mark.parametrize(
    "status", ["REVIEW_REQUIRED", "FAILED_SAFE", "UNSUPPORTED", "REJECTED_LIMIT"]
)
@pytest.mark.parametrize("same_time", [False, True])
@pytest.mark.parametrize("target", ["source", "index"])
def test_new_ineligible_extraction_excludes_previously_indexed_source(
    session_factory: sessionmaker[Session],
    indexed_source,
    status: str,
    same_time: bool,
    target: str,
) -> None:
    tenant, case, version, document, _, fragment, digest, source, _ = indexed_source
    assert [r.chunk.source_fragment_id for r in _results(indexed_source)] == [fragment]
    with session_factory.begin() as session:
        session.add(
            DceDocumentExtractionRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                input_sha256=digest,
                extractor_id="synthetic-refusal",
                extractor_version="1",
                status=status,
                fragment_count=0,
                extracted_char_count=0,
                failure_code="SYNTHETIC_REFUSAL",
                created_at=NOW if same_time else NOW + timedelta(seconds=1),
            )
        )
    if target == "source":
        assert source.read_chunks(tenant_id=tenant, case_id=case, dce_version_id=version) == ()
    else:
        assert _results(indexed_source) == []
    # Excluding a source must preserve its immutable historical proof and vector.
    with session_factory() as session:
        assert session.get(DceDocumentExtractionFragmentRecord, fragment) is not None
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(DceFragmentEmbeddingRecord)) >= 1
        )


@pytest.mark.parametrize("same_time", [False, True])
def test_new_completed_extraction_replaces_the_old_source_even_without_reindexing(
    session_factory: sessionmaker[Session],
    indexed_source,
    same_time: bool,
) -> None:
    tenant, case, version, document, old_extraction, old_fragment, digest, source, index = (
        indexed_source
    )
    extraction, fragment = UUID(int=old_extraction.int + 1), uuid4()
    text = "La visite est facultative."
    with session_factory.begin() as session:
        session.add(
            DceDocumentExtractionRecord(
                id=extraction,
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                input_sha256=digest,
                extractor_id="synthetic-new",
                extractor_version="1",
                status="COMPLETED",
                fragment_count=1,
                extracted_char_count=len(text),
                created_at=NOW if same_time else NOW + timedelta(seconds=1),
            )
        )
        session.flush()
        session.add(
            DceDocumentExtractionFragmentRecord(
                id=fragment,
                tenant_id=tenant,
                extraction_id=extraction,
                ordinal=1,
                locator_json={"page": 1},
                text=text,
                text_sha256=sha256(text.encode()).hexdigest(),
            )
        )
    chunks = source.read_chunks(tenant_id=tenant, case_id=case, dce_version_id=version)
    assert [c.source_fragment_id for c in chunks] == [fragment]
    assert _results(indexed_source) == []
    index.upsert(chunks=chunks, embeddings=[EmbeddingVector(values=(1.0, 0.0))])
    assert [r.chunk.source_fragment_id for r in _results(indexed_source)] == [fragment]
    assert fragment != old_fragment


def test_search_revalidates_case_current_version_and_tenant(
    session_factory: sessionmaker[Session],
    indexed_source,
) -> None:
    tenant, case, version, _, _, _, _, source, index = indexed_source
    assert source.read_chunks(tenant_id=uuid4(), case_id=case, dce_version_id=version) == ()
    assert (
        index.search(
            query=EmbeddingVector(values=(1.0, 0.0)),
            scope=RetrievalScope(tenant_id=uuid4(), case_id=case, dce_version_id=version),
            top_k=5,
            embedding_model=MODEL_ID,
        )
        == []
    )
    with session_factory.begin() as session:
        session.execute(
            sa.update(CaseRecord)
            .where(CaseRecord.id == case)
            .values(applicable_dce_version_id=None)
        )
    assert source.read_chunks(tenant_id=tenant, case_id=case, dce_version_id=version) == ()
    assert _results(indexed_source) == []
