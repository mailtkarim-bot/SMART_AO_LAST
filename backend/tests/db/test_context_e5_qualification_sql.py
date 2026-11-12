import json

from tests.db.test_candidate_retrieval_sql import SqlProbeEncoder
from tests.ops.test_context_e5_qualification import ROOT, load
from tests.ops.test_rc_semantic_qualification import development


def test_measurement_sql_runtime_checks_without_real_model(session_factory, monkeypatch, tmp_path):
    module = load(monkeypatch)
    data = development(tmp_path)
    data["documents"][0]["page"] = 15
    data["qualification_protocol"]["control_query"] = data["queries"][0]["text"]
    profile = module.CandidateRetrievalProfile(
        **json.loads(
            (ROOT / "ops/retrieval-candidate/profile-context-transport-v1.json").read_text()
        )
    )
    module.seed_fixture(data, session_factory)
    result = module.sql_runtime(data, session_factory, profile, SqlProbeEncoder(profile))
    assert all(result["checks"].values()), result["checks"]
    assert len(result["fragment_manifest"]) == len(data["documents"])
