import importlib.util
from pathlib import Path

import pytest
from tests.ops.test_rc_semantic_qualification import development

ROOT = Path(__file__).resolve().parents[3]


def load(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    path = ROOT / "scripts/qualify_context_e5_sql.py"
    assert path.exists(), "context E5 qualification harness missing"
    spec = importlib.util.spec_from_file_location("context_e5", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_clause_score_does_not_confuse_retrieved_text_with_projection(monkeypatch, tmp_path):
    m = load(monkeypatch)
    data = development(tmp_path)
    fact = {**data["queries"][0]["gold_regions"][0], "id": "c", "subject": "DC2", "lot": 17}
    data["clause_inventory"] = [fact]
    data["queries"][0].update(expected_clause_ids=["c"], family="DC2", expected_refusal=False)
    state = {"regions": data["queries"][0]["gold_regions"], "rc_projection": {}}
    scores = m.clause_metrics(data, {"dev": state})
    assert scores["source_recall"] == 1 and scores["projected_recall"] == 0
    assert scores["missing_projection"] == ["dev:c"]


@pytest.mark.parametrize("field", ["start_byte", "excerpt", "source_sha256"])
def test_corrupted_projection_provenance_is_not_scored_as_valid(monkeypatch, tmp_path, field):
    m = load(monkeypatch)
    data = development(tmp_path)
    fact = {**data["queries"][0]["gold_regions"][0], "id": "c", "subject": "DC2", "lot": 17}
    data["clause_inventory"] = [fact]
    data["queries"][0].update(expected_clause_ids=["c"], family="DC2", expected_refusal=False)
    bad = {**fact, field: -1 if field == "start_byte" else "corrupt"}
    state = {"regions": [], "rc_projection": {"clauses": [bad]}}
    with pytest.raises(ValueError, match="anchor"):
        m.clause_metrics(data, {"dev": state})


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://proof@localhost/smartao_e5_sql",
        "postgresql+psycopg://proof@/other?host=/socket",
        "postgresql+psycopg://proof@/smartao_e5_sql?host=/socket&hostaddr=127.0.0.1",
    ],
)
def test_sql_guard_refuses_other_database_and_tcp(monkeypatch, url):
    m = load(monkeypatch)
    monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", "1")
    monkeypatch.setenv("SMART_AO_TEST_DATABASE_URL", url)
    with pytest.raises(ValueError, match="disposable"):
        m.disposable_url()


def test_libpq_override_is_refused(monkeypatch):
    m = load(monkeypatch)
    monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", "1")
    monkeypatch.setenv(
        "SMART_AO_TEST_DATABASE_URL", "postgresql+psycopg://proof@/smartao_e5_sql?host=/socket"
    )
    monkeypatch.setenv("PGSERVICE", "foreign")
    with pytest.raises(ValueError, match="disposable"):
        m.disposable_url()


def test_complete_trial_preserves_recognition_and_raw_query(monkeypatch, tmp_path):
    import json

    from tests.db.test_candidate_retrieval_sql import SqlProbeEncoder

    m = load(monkeypatch)
    data = development(tmp_path)
    data["queries"][0].update(expected_contexts=[], expected_clause_ids=[], family="DC2")
    data["clause_inventory"] = []
    profile = m.CandidateRetrievalProfile(
        **json.loads(
            (ROOT / "ops/retrieval-candidate/profile-context-transport-v1.json").read_text()
        )
    )
    result = m.run_trial(data, profile, m.fixture_source(data), SqlProbeEncoder(profile))
    assert result["encoder_calls"]["query"] == 4
    assert all(result["fidelity"].values())
    assert not result["admitted"] and not result["production_engine_changed"]


def test_freeze_detects_changed_inputs(monkeypatch, tmp_path):
    import json
    from hashlib import sha256

    m = load(monkeypatch)
    (tmp_path / "input").write_text("original")
    freeze = tmp_path / "freeze.json"
    freeze.write_text(json.dumps({"input": sha256(b"original").hexdigest()}))
    m.verify_freeze(freeze, tmp_path)
    (tmp_path / "input").write_text("changed")
    with pytest.raises(ValueError, match="frozen"):
        m.verify_freeze(freeze, tmp_path)


def test_wrong_modality_is_not_a_successful_projection(monkeypatch, tmp_path):
    m = load(monkeypatch)
    data = development(tmp_path)
    doc = data["documents"][0]
    fact = {**data["queries"][0]["gold_regions"][0], "id": "c", "subject": "DC2", "lot": 17}
    data["clause_inventory"] = [fact]
    data["queries"][0].update(expected_clause_ids=["c"], family="DC2", expected_refusal=False)
    actual = {
        **fact,
        "value": "NOT_REQUIRED",
        "dce_version_id": doc["version_id"],
        "locator": {"page": doc["page"]},
    }
    scores = m.clause_metrics(
        data, {"dev": {"regions": [], "rc_projection": {"clauses": [actual]}}}
    )
    assert scores["projected_recall"] == 0 and scores["projected_precision"] == 0


def test_clause_and_linked_context_can_have_distinct_regions(monkeypatch, tmp_path):
    from hashlib import sha256

    m = load(monkeypatch)
    data = development(tmp_path)
    doc = data["documents"][0]
    prefix = "Si requis. "
    clause = doc["text"]
    doc["text"] = prefix + clause
    digest = sha256(doc["text"].encode()).hexdigest()
    doc["text_sha256"] = digest
    context = dict(
        source_fragment_id=doc["id"],
        start_byte=0,
        end_byte=len(prefix.encode()),
        excerpt=prefix,
        source_sha256=digest,
    )
    fact = dict(
        id="c",
        source_fragment_id=doc["id"],
        start_byte=len(prefix.encode()),
        end_byte=len(doc["text"].encode()),
        excerpt=clause,
        source_sha256=digest,
        subject="DC2",
        lot=17,
        value="REQUIRED",
        kind="ASSERTION",
        context_regions=[context],
    )
    data["clause_inventory"] = [fact]
    data["queries"][0].update(expected_clause_ids=["c"], family="DC2", expected_refusal=False)
    actual = dict(
        fact,
        dce_version_id=doc["version_id"],
        locator={"page": doc["page"]},
        condition_signals=[context],
    )
    state = {"regions": [], "rc_projection": {"clauses": [actual]}}
    assert m.clause_metrics(data, {"dev": state})["fully_proven_recall"] == 1
    actual["condition_signals"] = []
    scores = m.clause_metrics(data, {"dev": state})
    assert scores["projected_recall"] == 1 and scores["fully_proven_recall"] == 0
