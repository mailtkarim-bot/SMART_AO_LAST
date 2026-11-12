from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker
from tests.db.test_knowledge_source_freshness import indexed_source as indexed_source

ROOT = Path(__file__).resolve().parents[3]


def test_sql_measurement_seed_fidelity_and_invalidations(database_engine, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "sql_trial", ROOT / "scripts/qualify_candidate_sql.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = json.loads(
        (ROOT / "backend/tests/fixtures/knowledge/btp_e5_sql_heldout_v8.json").read_text()
    )
    next(q for q in data["queries"] if q["id"] == "j8-site524")["id"] = (
        "independent-validation-query"
    )
    factory = sessionmaker(bind=database_engine, expire_on_commit=False)
    module.seed_fixture(data, factory)
    source = module.SqlAlchemyDceRetrievalSource(session_factory=factory)
    chunks = source.read_chunks(
        tenant_id=module.UUID(data["tenant_id"]),
        case_id=module.UUID(data["case_id"]),
        dce_version_id=module.UUID(data["version_id"]),
    )
    assert len(chunks) == 14
    documents = {d["id"]: d for d in data["documents"]}
    assert all(c.text == documents[str(c.source_fragment_id)]["text"] for c in chunks)
    profile = module.CandidateRetrievalProfile(
        **json.loads((ROOT / "ops/retrieval-candidate/profile-v6.json").read_text())
    )

    class Encoder:
        profile_id = profile.profile_id

        def encode_passages(self, texts):
            return [(1.0,) + (0.0,) * 383 for _ in texts]

        def encode_query(self, text):
            return (1.0,) + (0.0,) * 383

    report = module.validate_runtime(data, factory, profile, Encoder())
    assert all(report.values())


@pytest.mark.parametrize(
    "version,query",
    [
        (7, "Le DC2 est-il requis pour le lot 17 ?"),
        (8, "Faut-il joindre le DC2 pour le lot 17 ?"),
        (9, "Pour le lot 17, le formulaire DC2 doit-il être fourni ?"),
    ],
)
def test_candidate_sql_typed_scope_financial_guard_and_invalidation(
    session_factory, indexed_source, monkeypatch, version, query
):
    import pytest
    import sqlalchemy as sa
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService
    from app.modules.knowledge.application.retrieval import FinancialRetrievalQueryRejected
    from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
    from app.modules.knowledge.domain.retrieval import RetrievalScope
    from app.modules.knowledge.infrastructure.dce_source import SqlAlchemyDceRetrievalSource
    from tests.db.test_candidate_retrieval_sql import SqlProbeEncoder, _append

    _append(
        session_factory,
        indexed_source,
        text="Lot 17 : le DC2 est requis. Lot 17 : la DPGF est requise.",
    )
    profile = CandidateRetrievalProfile(
        **json.loads((ROOT / f"ops/retrieval-candidate/profile-v{version}.json").read_text())
    )
    source = SqlAlchemyDceRetrievalSource(session_factory=session_factory)
    encoder = SqlProbeEncoder(profile)
    service = CandidateRetrievalService(profile=profile, source=source, encoder=encoder)
    scope = RetrievalScope(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    result = service.retrieve(query=query, scope=scope)
    assert len(result.hits) == 1 and result.score_trace[0].decision == "RC_TYPED_RESCUE"
    if version in {8, 9}:
        assert result.query_intent.coverage == "COVERED" and result.query_intent.scope.lot == 17
    assert {c.subject for c in result.rc_projection.clauses} == {"DC2"}
    assert {c.subject for c in result.rc_unscoped_evidence} == {"DPGF"}
    with monkeypatch.context() as m:
        m.setattr(source, "read_chunks", lambda **kwargs: pytest.fail("financial source read"))
        with pytest.raises(FinancialRetrievalQueryRejected):
            service.retrieve(query="Quel montant DPGF pour le lot 17 ?", scope=scope)

    def invalidate():
        with session_factory.begin() as s:
            s.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == scope.case_id)
                .values(applicable_dce_version_id=None)
            )

    encoder.after_query = invalidate
    changed = service.retrieve(query=query, scope=scope)
    assert changed.reason == "SOURCE_CHANGED" and not changed.hits and not changed.score_trace
    assert changed.answer_state == "UNKNOWN"


def test_v10_sql_condition_unknown_retry_and_source_change(session_factory, indexed_source):
    from hashlib import sha256

    import sqlalchemy as sa
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.knowledge.application.candidate_retrieval import CandidateRetrievalService
    from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile
    from app.modules.knowledge.domain.retrieval import RetrievalScope
    from app.modules.knowledge.infrastructure.dce_source import SqlAlchemyDceRetrievalSource
    from tests.db.test_candidate_retrieval_sql import SqlProbeEncoder, _append

    text = "Lot n° 17 : joindre le DC2 si le candidat n'est pas dispensé."
    _append(session_factory, indexed_source, text=text)
    profile = CandidateRetrievalProfile(
        **json.loads((ROOT / "ops/retrieval-candidate/profile-v10.json").read_text())
    )
    source = SqlAlchemyDceRetrievalSource(session_factory=session_factory)
    encoder = SqlProbeEncoder(profile)
    service = CandidateRetrievalService(profile=profile, source=source, encoder=encoder)
    scope = RetrievalScope(
        tenant_id=indexed_source[0], case_id=indexed_source[1], dce_version_id=indexed_source[2]
    )
    query = "Pour le lot 17, faut-il joindre le DC2 ?"
    result = service.retrieve(query=query, scope=scope)
    assert result.state == "REVIEW_REQUIRED" and result.answer_state == "UNKNOWN"
    condition = result.rc_projection.unknown_regions[0]
    assert condition.value == condition.kind == "UNKNOWN"
    assert condition.source_sha256 == sha256(text.encode()).hexdigest()
    assert condition.condition_signals[0].excerpt == "si le candidat n'est pas dispensé"
    assert service.retrieve(query=query, scope=scope) == result

    def change():
        with session_factory.begin() as s:
            s.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == scope.case_id)
                .values(applicable_dce_version_id=None)
            )

    encoder.after_query = change
    changed = service.retrieve(query=query, scope=scope)
    assert changed.reason == "SOURCE_CHANGED" and not changed.hits
