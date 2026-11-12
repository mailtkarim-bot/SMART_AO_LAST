"""Adversarial SQL rows for the existing index, no model runtime or live data."""

from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    EmbeddingVector,
    RetrievalScope,
)
from app.modules.knowledge.infrastructure.models import DceFragmentEmbeddingRecord
from tests.db.test_candidate_retrieval_sql import TEXT, _append, _clone, _successor
from tests.db.test_knowledge_source_freshness import MODEL_ID, seed_indexed_source
from tests.db.test_knowledge_source_freshness import indexed_source as indexed_source

VECTOR = EmbeddingVector(values=(1.0, 0.0))


def _scope(seed):
    return RetrievalScope(tenant_id=seed[0], case_id=seed[1], dce_version_id=seed[2])


def _search(seed, **kwargs):
    return seed[8].search(
        query=VECTOR,
        scope=_scope(seed),
        top_k=5,
        embedding_model=kwargs.pop("embedding_model", MODEL_ID),
        **kwargs,
    )


def _stored(session_factory, seed, **changes):
    _, fragment = _append(session_factory, seed)
    values = dict(
        id=uuid4(),
        tenant_id=seed[0],
        case_id=seed[1],
        dce_version_id=seed[2],
        fragment_id=fragment,
        model_id=MODEL_ID,
        ordinal=1,
        text=TEXT,
        locator_json={"kind": "pdf_region", "page": 7, "region": [12, 30, 400, 90]},
        classification="INTERNAL_OPERATIONAL",
        text_sha256=sha256(TEXT.encode()).hexdigest(),
        embedding=[1.0, 0.0],
        embedding_dimension=2,
    )
    values.update(changes)
    with session_factory.begin() as session:
        session.add(DceFragmentEmbeddingRecord(**values))
    return values


@pytest.mark.parametrize(
    "changes",
    [
        {"text": "Clause inventée."},
        {"text_sha256": "0" * 64},
        {"ordinal": 2},
        {"locator_json": {"page": 99}},
        {"classification": "PUBLIC"},
        {"embedding": [True, 0.0]},
        {"embedding": ["1", 0.0]},
        {"embedding": [None, 0.0]},
        {"embedding": [{}, 0.0]},
        {"embedding": [0.0, 0.0]},
        {"embedding": [1e308, 1e308]},
        {"embedding": [1.0], "embedding_dimension": 1},
    ],
)
def test_sql_index_refuses_discordant_persisted_copy(session_factory, indexed_source, changes):
    values = _stored(session_factory, indexed_source, **changes)
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_INTEGRITY_MISMATCH$"):
        _search(indexed_source)
    # Refusal is read-only; historical evidence is not repaired/deleted.
    with session_factory() as session:
        row = session.get(DceFragmentEmbeddingRecord, values["id"])
        assert row is not None and row.text == values["text"]


@pytest.mark.parametrize("change", ["input_hash", "document_version", "fragment_hash"])
def test_sql_index_revalidates_source_chain(session_factory, indexed_source, change):
    seed = indexed_source
    if change == "document_version":
        successor, _ = _successor(session_factory, seed)
        wrong = list(successor)
        wrong[2] = seed[2]
        seed = tuple(wrong)
    _, fragment = _append(
        session_factory,
        seed,
        input_hash="0" * 64 if change == "input_hash" else None,
        fragment_hash="0" * 64 if change == "fragment_hash" else None,
    )
    with session_factory.begin() as session:
        session.add(
            DceFragmentEmbeddingRecord(
                id=uuid4(),
                tenant_id=seed[0],
                case_id=seed[1],
                dce_version_id=seed[2],
                fragment_id=fragment,
                model_id=MODEL_ID,
                ordinal=1,
                text=TEXT,
                locator_json={"kind": "pdf_region", "page": 7, "region": [12, 30, 400, 90]},
                classification="INTERNAL_OPERATIONAL",
                text_sha256=sha256(TEXT.encode()).hexdigest(),
                embedding=[1.0, 0.0],
                embedding_dimension=2,
            )
        )
    if change == "fragment_hash":
        with pytest.raises(ValueError, match="^DCE_FRAGMENT_INTEGRITY_MISMATCH$"):
            _search(indexed_source)
    else:
        assert fragment not in {r.chunk.source_fragment_id for r in _search(indexed_source)}


@pytest.mark.parametrize(
    "change",
    [
        {"text": "Clause inventée."},
        {"ordinal": 2},
        {"locator": {"page": 99}},
        {"classification": DataClassification.PUBLIC},
        {"dce_version_id": uuid4()},
        {"case_id": uuid4()},
    ],
)
def test_sql_index_upsert_rejects_unproved_chunk_without_write(
    session_factory, indexed_source, change
):
    source = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )[0]
    with session_factory() as session:
        before = session.scalar(sa.select(sa.func.count()).select_from(DceFragmentEmbeddingRecord))
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_SOURCE_MISMATCH$"):
        indexed_source[8].upsert(chunks=[replace(source, **change)], embeddings=[VECTOR])
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(DceFragmentEmbeddingRecord))
            == before
        )


def test_sql_index_rejects_query_model_different_from_instance(indexed_source):
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_MODEL_MISMATCH$"):
        _search(indexed_source, embedding_model="other-model")


def test_sql_index_nominal_retry_preserves_exact_source_and_vector(session_factory, indexed_source):
    first = _search(indexed_source)
    assert len(first) == 1
    chunks = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    for _ in range(2):
        indexed_source[8].upsert(chunks=chunks, embeddings=[VECTOR])
    assert _search(indexed_source) == first
    assert first[0].chunk.text == chunks[0].text and first[0].chunk.locator == chunks[0].locator


def test_sql_index_foreign_populated_scopes_do_not_expose_counts_or_text(
    session_factory, indexed_source
):
    other = seed_indexed_source(session_factory)
    for field in ("tenant_id", "case_id", "dce_version_id"):
        wrong_scope = replace(_scope(indexed_source), **{field: getattr(_scope(other), field)})
        assert (
            indexed_source[8].search(
                query=VECTOR, scope=wrong_scope, top_k=5, embedding_model=MODEL_ID
            )
            == []
        )


def test_sql_index_same_tenant_case_cannot_borrow_version(session_factory, indexed_source):
    new_seed, _ = _successor(session_factory, indexed_source)
    other_case = uuid4()
    with session_factory.begin() as session:
        session.add(
            _clone(
                session.get(CaseRecord, indexed_source[1]),
                id=other_case,
                applicable_dce_version_id=new_seed[2],
                functional_identity_hash=sha256(str(other_case).encode()).hexdigest(),
                scope_fingerprint=sha256(str(other_case).encode()).hexdigest(),
            )
        )
    assert (
        indexed_source[8].search(
            query=VECTOR,
            scope=replace(_scope(indexed_source), case_id=other_case),
            top_k=5,
            embedding_model=MODEL_ID,
        )
        == []
    )


def test_sql_index_huge_json_integer_is_a_controlled_refusal(session_factory, indexed_source):
    _stored(session_factory, indexed_source, embedding=[10**400, 0])
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_INTEGRITY_MISMATCH$"):
        _search(indexed_source)


def test_sql_index_retry_does_not_accept_stored_boolean_as_float(session_factory, indexed_source):
    _stored(session_factory, indexed_source, embedding=[True, 0.0])
    chunks = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_INTEGRITY_MISMATCH$"):
        indexed_source[8].upsert(chunks=chunks, embeddings=[VECTOR])


def test_sql_index_batch_refusal_rolls_back_first_insert(session_factory, indexed_source):
    _append(session_factory, indexed_source)
    chunks = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    with session_factory() as session:
        before = session.scalar(sa.select(sa.func.count()).select_from(DceFragmentEmbeddingRecord))
    with pytest.raises(ValueError, match="^DCE_EMBEDDING_SOURCE_MISMATCH$"):
        indexed_source[8].upsert(
            chunks=[chunks[0], replace(chunks[0], text="Fausse clause.")],
            embeddings=[VECTOR, VECTOR],
        )
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(DceFragmentEmbeddingRecord))
            == before
        )


def test_sql_index_same_fragment_other_case_does_not_reuse_receipt(session_factory, indexed_source):
    other_case = uuid4()
    with session_factory.begin() as session:
        session.add(
            _clone(
                session.get(CaseRecord, indexed_source[1]),
                id=other_case,
                functional_identity_hash=sha256(str(other_case).encode()).hexdigest(),
                scope_fingerprint=sha256(str(other_case).encode()).hexdigest(),
            )
        )
    chunks = indexed_source[7].read_chunks(
        tenant_id=indexed_source[0], case_id=other_case, dce_version_id=indexed_source[2]
    )
    assert chunks
    with pytest.raises(
        ValueError, match="embedding identity already exists with different content"
    ):
        indexed_source[8].upsert(chunks=chunks, embeddings=[VECTOR])
    assert _search(indexed_source)[0].chunk.case_id == indexed_source[1]
