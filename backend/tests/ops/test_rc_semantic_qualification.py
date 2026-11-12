import importlib.util
from copy import deepcopy
from hashlib import sha256
from uuid import UUID

import pytest
from tests.ops.test_candidate_qualification_cli import ROOT, intent_dev_fixture


def load(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    path = ROOT / "scripts/qualify_rc_semantic.py"
    assert path.exists(), "semantic qualification adapter missing"
    spec = importlib.util.spec_from_file_location("semantic_qualifier", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def development(tmp_path):
    _, old = intent_dev_fixture(tmp_path)
    doc = old["documents"][0]
    query = old["queries"][0]
    old.update(kind="rc_semantic_measurement", preparation_only=False, source_facts=[])
    old["queries"] = [
        dict(
            id="dev",
            text=query["text"],
            query_sha256=sha256(query["text"].encode()).hexdigest(),
            semantic_request=dict(subject="DC2", demand="OBLIGATION", lot=17),
            gold_sources=[doc["id"]],
            gold_regions=[
                dict(
                    source_fragment_id=doc["id"],
                    start_byte=0,
                    end_byte=len(doc["text"].encode()),
                    source_sha256=sha256(doc["text"].encode()).hexdigest(),
                    excerpt=doc["text"],
                    value="REQUIRED",
                    kind="ASSERTION",
                    applicability="UNKNOWN",
                )
            ],
            runtime_expectations=None,
            fact_ids=[],
        )
    ]
    doc["text_sha256"] = sha256(doc["text"].encode()).hexdigest()
    old["qualification_protocol"] = dict(
        status="FROZEN_FOR_MEASUREMENT",
        top_k=10,
        report_at=[1, 5, 10],
        latency_budget_ms=1500,
        restricted_source_ids=[],
    )
    return old


def abstain():
    return dict(
        answer_state="UNKNOWN",
        reason="RC_QUERY_NOT_COVERED",
        regions=[],
        query_intent=dict(
            subject="UNKNOWN",
            demand="UNKNOWN",
            coverage="UNKNOWN",
            scope=dict(state="UNKNOWN", lot=None),
        ),
        rc_projection={},
        rc_unscoped_evidence=[],
        visit_type_evidence=[],
    )


def test_missing_semantic_evidence_is_not_hidden_by_safe_abstention(tmp_path, monkeypatch):
    module = load(monkeypatch)
    data = development(tmp_path)
    score = module.score_semantics(data, {"dev": abstain()})
    assert score["documentary"]["recall_at_5"] == 0
    assert score["documentary"]["critical_missing_at_5"] == ["dev"]
    assert score["safety"]["unknown_answer"] and score["safety"]["source_scope"]
    assert score["parser"]["dev"]["semantic_match"] is False


@pytest.mark.parametrize("change", ["preparation", "hash", "foreign", "gold_from_output"])
def test_invalid_or_unfrozen_semantic_gold_is_refused(tmp_path, monkeypatch, change):
    module = load(monkeypatch)
    data = development(tmp_path)
    if change == "preparation":
        data["held_out"], data["preparation_only"] = False, True
    elif change == "hash":
        data["documents"][0]["text_sha256"] = "0" * 64
    elif change == "foreign":
        data["documents"][0]["tenant_id"] = str(UUID(int=99))
    else:
        data["queries"][0]["runtime_expectations"] = dict(coverage="UNKNOWN")
    with pytest.raises(ValueError):
        module.validate_gold(data)


def test_financial_query_is_separate_from_recall_denominator(tmp_path, monkeypatch):
    module = load(monkeypatch)
    data = development(tmp_path)
    q = deepcopy(data["queries"][0])
    q.update(
        id="money",
        gold_sources=[],
        gold_regions=[],
        semantic_request=dict(subject="DPGF", demand="FINANCIAL", lot=17),
    )
    data["queries"].append(q)
    states = dict(
        dev=abstain(),
        money={**abstain(), "reason": "FINANCIAL_SCOPE_REFUSED", "query_intent": None},
    )
    score = module.score_semantics(data, states)
    assert [x["query_id"] for x in score["documentary"]["queries"]] == ["dev"]
    assert score["financial_non_evaluable"] == ["money"]
    assert score["safety"]["financial_refusal"]
    source = data["documents"][0]["id"]
    for field, payload in [
        ("score_trace", [dict(source_fragment_id=source)]),
        ("review_source_ids", [source]),
    ]:
        leaked = deepcopy(states)
        leaked["money"][field] = payload
        assert not module.score_semantics(data, leaked)["safety"]["financial_refusal"]


@pytest.mark.parametrize("corruption", ["foreign_hit", "foreign_evidence", "certainty"])
def test_safety_checks_projection_as_well_as_ranked_hits(tmp_path, monkeypatch, corruption):
    module = load(monkeypatch)
    data = development(tmp_path)
    source = data["documents"][0]["id"]
    data["qualification_protocol"]["restricted_source_ids"] = [source]
    state = abstain()
    if corruption == "foreign_hit":
        state["regions"] = [dict(source_fragment_id=str(UUID(int=99)), start_byte=0, end_byte=5)]
    else:
        state["rc_projection"] = dict(
            clauses=[
                dict(
                    source_fragment_id=source if corruption == "certainty" else str(UUID(int=99)),
                    value="REQUIRED",
                    kind="ASSERTION",
                )
            ]
        )
    safety = module.score_semantics(data, {"dev": state})["safety"]
    assert not safety["source_scope" if corruption != "certainty" else "protected_unknown"]


def test_adapter_runs_existing_service_on_development_without_gold_injection(tmp_path, monkeypatch):
    from tests.application.test_candidate_retrieval import Encoder, profile

    module = load(monkeypatch)
    data = development(tmp_path)
    p = profile(review_policy="rc-conditional-v10")
    encoder = Encoder(p)
    report = module.run_trial(data, p, module.fixture_source(data), encoder)
    assert report["scores"]["documentary"]["recall_at_5"] == 1
    assert all(report["scores"]["safety"].values())
    assert report["encoder_calls"]["query"] == 4
    assert not report["admitted"] and not report["production_engine_changed"]


@pytest.mark.parametrize("surface", ["score_trace", "review_source_ids", "links"])
def test_foreign_sources_cannot_hide_in_report_metadata(tmp_path, monkeypatch, surface):
    module = load(monkeypatch)
    data = development(tmp_path)
    state = abstain()
    foreign = str(UUID(int=99))
    if surface == "review_source_ids":
        state[surface] = [foreign]
    elif surface == "links":
        state["rc_projection"] = dict(
            links=[
                dict(left=dict(source_fragment_id=foreign), right=dict(source_fragment_id=foreign))
            ]
        )
    else:
        state[surface] = [dict(source_fragment_id=foreign)]
    assert not module.score_semantics(data, {"dev": state})["safety"]["source_scope"]


def test_source_recall_respects_segment_budget_before_deduplication(tmp_path, monkeypatch):
    module = load(monkeypatch)
    data = development(tmp_path)
    first = data["documents"][0]["id"]
    second = str(UUID(int=5))
    data["queries"][0]["gold_sources"].append(second)
    state = abstain()
    state["regions"] = [
        dict(source_fragment_id=x, start_byte=0, end_byte=5)
        for x in [first, first, first, first, first, second]
    ]
    scores = module.score_semantics(data, {"dev": state})["documentary"]
    assert scores["recall_at_5"] == 0.5
    assert scores["recall_at_10"] == 1


@pytest.mark.parametrize("surface", ["regions", "score_trace"])
def test_segment_hash_corruption_is_rejected(tmp_path, monkeypatch, surface):
    from tests.application.test_candidate_retrieval import Encoder, profile

    module = load(monkeypatch)
    data = development(tmp_path)
    p = profile(review_policy="rc-conditional-v10")
    report = module.run_trial(data, p, module.fixture_source(data), Encoder(p))
    assert report["scores"]["safety"]["anchor_integrity"]
    report["states"]["dev"][surface][0]["segment_sha256"] = "0" * 64
    assert not module.score_semantics(data, report["states"])["safety"]["anchor_integrity"]


def test_main_rejects_modified_v10_profile_before_encoding(tmp_path, monkeypatch):
    import json

    from tests.ops.test_candidate_qualification_cli import args

    module = load(monkeypatch)
    data = development(tmp_path)
    canonical = ROOT / "ops/retrieval-candidate/profile-v10.json"
    data["qualification_protocol"]["profile_sha256"] = sha256(canonical.read_bytes()).hexdigest()
    fixture = tmp_path / "dev-semantic.json"
    fixture.write_text(json.dumps(data))
    p = json.loads(canonical.read_text())
    p["minimum_score"] = 0.5
    changed = tmp_path / "changed-profile.json"
    changed.write_text(json.dumps(p))
    cli = args(tmp_path, "unused")
    cli[cli.index("--fixture") + 1] = str(fixture)
    cli[cli.index("--profile") + 1] = str(changed)
    monkeypatch.setattr(module, "CpuCandidateEncoder", lambda **kw: pytest.fail("encoder invoked"))
    with pytest.raises(ValueError, match="profile"):
        module.main(cli)


def test_uncovered_development_question_reports_no_source_or_encoder_work(tmp_path, monkeypatch):
    from tests.application.test_candidate_retrieval import Encoder, profile

    module = load(monkeypatch)
    data = development(tmp_path)
    q = data["queries"][0]
    q["text"] = "Racontez le rôle du DC2 pour le lot 17."
    q["query_sha256"] = sha256(q["text"].encode()).hexdigest()
    p = profile(review_policy="rc-conditional-v10")
    report = module.run_trial(data, p, module.fixture_source(data), Encoder(p))
    assert report["encoder_calls"]["source_reads"] == 0
    assert report["encoder_calls"]["query"] == report["encoder_calls"]["passages"] == 0
    assert report["scores"]["documentary"]["recall_at_5"] == 0
