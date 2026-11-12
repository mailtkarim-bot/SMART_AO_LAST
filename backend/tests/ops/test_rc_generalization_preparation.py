"""Semantic preparation gold stays separate from measured finite-parser expectations."""

import json
from hashlib import sha256

import pytest
from tests.ops.test_candidate_qualification_cli import ROOT, args, load

FIXTURE = "rc_generalization_preparation_v1.json"


def test_semantic_preparation_has_scoped_exact_sources_and_declared_budgets():
    data = json.loads((ROOT / "backend/tests/fixtures/knowledge" / FIXTURE).read_text())
    documents = {d["id"]: d for d in data["documents"]}
    assert len(documents) == len(data["documents"]) == 16
    assert len({q["id"] for q in data["queries"]}) == len(data["queries"]) == 18
    assert data["preparation_only"] is True and data["held_out"] is False
    for doc in documents.values():
        assert doc["text_sha256"] == sha256(doc["text"].encode()).hexdigest()
    facts = {f["id"]: f for f in data["source_facts"]}
    assert len(facts) == len(data["source_facts"]) == 4
    for fact in facts.values():
        doc = documents[fact["source_fragment_id"]]
        assert fact["source_sha256"] == doc["text_sha256"]
        assert 0 <= fact["start_byte"] < fact["end_byte"] <= len(doc["text"].encode())
        assert (
            doc["text"].encode()[fact["start_byte"] : fact["end_byte"]] == fact["excerpt"].encode()
        )
        assert fact["normalized_value"] is None
    for query in data["queries"]:
        assert set(query["fact_ids"]) == {
            key
            for key, fact in facts.items()
            if fact["source_fragment_id"] in query["gold_sources"]
        }
        assert query["runtime_expectations"] is None
        assert query["query_sha256"] == sha256(query["text"].encode()).hexdigest()
        assert len(query["gold_sources"]) == len(set(query["gold_sources"]))
        assert set(query["gold_sources"]) == {
            region["source_fragment_id"] for region in query["gold_regions"]
        }
        for region in query["gold_regions"]:
            doc = documents[region["source_fragment_id"]]
            assert all(doc[key] == data[key] for key in ("tenant_id", "case_id", "version_id"))
            assert doc["current"] and doc["extraction_status"] == "COMPLETED"
            assert doc["classification"] == "INTERNAL_OPERATIONAL"
            assert region["source_sha256"] == doc["text_sha256"]
            assert 0 <= region["start_byte"] < region["end_byte"] <= len(doc["text"].encode())
            assert doc["text"].encode()[region["start_byte"] : region["end_byte"]] == (
                region["excerpt"].encode()
            )
            assert region["applicability"] == "UNKNOWN"
    protocol = data["qualification_protocol"]
    assert protocol["status"] == "PREPARED_NOT_RUN" and protocol["engine_invoked"] is False
    assert protocol["top_k"] == 10 and protocol["report_at"] == [1, 5, 10]
    assert protocol["max_relevant_sources"] == max(len(q["gold_sources"]) for q in data["queries"])
    assert protocol["semantic_positive_queries"] == sum(
        bool(q["gold_sources"]) for q in data["queries"]
    )
    assert protocol["model_tuning_allowed"] is protocol["production_activation_allowed"] is False
    # SQL seed requires one current version per tenant/case, including foreign distractors.
    for tenant, case in {(d["tenant_id"], d["case_id"]) for d in documents.values()}:
        assert (
            len(
                {
                    d["version_id"]
                    for d in documents.values()
                    if d["tenant_id"] == tenant and d["case_id"] == case and d["current"]
                }
            )
            == 1
        )


def test_preparation_fixture_cannot_accidentally_start_candidate_measurement(tmp_path, monkeypatch):
    module = load(monkeypatch)
    monkeypatch.setattr(module, "CpuCandidateEncoder", lambda **kw: pytest.fail("encoder invoked"))
    cli = args(tmp_path, FIXTURE)
    cli[cli.index("--profile") + 1] = str(ROOT / "ops/retrieval-candidate/profile-v10.json")
    with pytest.raises(ValueError, match="only synthetic held-out"):
        module.main(cli)
    assert not (tmp_path / "report.json").exists()
