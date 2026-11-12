import json
from hashlib import sha256
from uuid import UUID

import sqlalchemy as sa
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionFragmentRecord
from sqlalchemy.orm import sessionmaker
from tests.ops.test_candidate_qualification_cli import ROOT


def test_semantic_gold_sql_seed_has_exact_source_text_and_current_scope(
    database_engine, monkeypatch
):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    from qualify_candidate_sql import SqlAlchemyDceRetrievalSource, seed_fixture
    from qualify_rc_semantic import eligible_documents, validate_gold

    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/rc_semantic_measurement_v1.json").read_text()
    )
    validate_gold(data)
    factory = sessionmaker(bind=database_engine, expire_on_commit=False)
    seed_fixture(data, factory)
    documents = {UUID(d["id"]): d for d in data["documents"]}
    with factory() as s:
        fragments = s.scalars(sa.select(DceDocumentExtractionFragmentRecord)).all()
        assert {f.id for f in fragments} == set(documents)
        for fragment in fragments:
            doc = documents[fragment.id]
            assert fragment.text == doc["text"]
            assert fragment.text_sha256 == sha256(doc["text"].encode()).hexdigest()
            assert fragment.locator_json == dict(kind="synthetic_page", page=doc["page"])
    source = SqlAlchemyDceRetrievalSource(session_factory=factory)
    chunks = source.read_chunks(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )
    assert {str(c.source_fragment_id) for c in chunks} == set(eligible_documents(data))
    assert len(chunks) == 12
    # Preflight only: no parser, service, encoder or model receives the semantic queries.
