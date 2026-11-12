from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from uuid import UUID

import pytest
from app.modules.knowledge.domain.retrieval import RetrievalScope

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "qualify_btp_retrieval.py"


@pytest.fixture
def trial():
    spec = importlib.util.spec_from_file_location("btp_retrieval_trial", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def scope():
    return RetrievalScope(tenant_id=UUID(int=1), case_id=UUID(int=2), dce_version_id=UUID(int=3))


def document(**changes):
    return {
        "id": str(UUID(int=4)),
        "tenant_id": str(UUID(int=1)),
        "case_id": str(UUID(int=2)),
        "version_id": str(UUID(int=3)),
        "classification": "INTERNAL_OPERATIONAL",
        "current": True,
        "extraction_status": "COMPLETED",
        "page": 12,
        "text": "Prévoir une visite obligatoire pour le lot 2. " * 12,
        **changes,
    }


def test_segmentation_preserves_every_byte_and_exact_hash(trial):
    from hashlib import sha256

    doc = document()
    chunks, trace = trial.prepare_chunks([doc], scope(), segment_chars=80)
    assert "".join(c.text for c in chunks) == doc["text"]
    assert len(chunks) > 1 and len({c.chunk_id for c in chunks}) == len(chunks)
    for chunk, region in zip(chunks, trace["segments"], strict=True):
        assert (
            doc["text"].encode()[region["start_byte"] : region["end_byte"]].decode() == chunk.text
        )
        assert region["source_sha256"] == sha256(doc["text"].encode()).hexdigest()
        assert region["segment_sha256"] == sha256(chunk.text.encode()).hexdigest()
        assert chunk.source_fragment_id == UUID(doc["id"])


@pytest.mark.parametrize(
    "change",
    [
        {"tenant_id": str(UUID(int=99))},
        {"case_id": str(UUID(int=99))},
        {"version_id": str(UUID(int=99))},
        {"current": False},
        {"extraction_status": "REVIEW_REQUIRED"},
        {"classification": "FINANCIAL_PRIVATE"},
        {"classification": "PERSONAL_DATA"},
    ],
)
def test_forbidden_sources_never_reach_segmentation_or_encoding(trial, change):
    chunks, trace = trial.prepare_chunks([document(**change)], scope())
    assert chunks == [] and trace["segments"] == [] and len(trace["excluded"]) == 1


def test_duplicate_source_id_is_refused_instead_of_overwriting(trial):
    with pytest.raises(ValueError):
        trial.prepare_chunks([document(), document()], scope())


def test_e5_prefixes_are_role_specific_and_bge_has_none(trial):
    assert (
        trial.model_texts("e5", "query", ["visite obligatoire"])[0] == "query: visite obligatoire"
    )
    assert (
        trial.model_texts("e5", "passage", ["visite obligatoire"])[0]
        == "passage: visite obligatoire"
    )
    assert trial.model_texts("bge", "query", ["visite obligatoire"])[0] == "visite obligatoire"


def test_scoring_accounts_for_every_query_and_unknown_answers(trial):
    gold = [
        {"id": "q1", "expected": ["a", "b"], "critical": True},
        {"id": "q2", "expected": [], "critical": False},
    ]
    score = trial.score_queries(gold, {"q1": ["a"], "q2": ["noise"]})
    assert score["recall_at_5"] == 0.5 and score["critical_missing_at_5"] == ["q1"]
    assert score["no_answer_with_candidates"] == ["q2"]
    with pytest.raises(ValueError):
        trial.score_queries(gold, {"q1": ["a"]})


def test_bm25_retains_negation_and_does_not_return_no_overlap(trial):
    assert "pas" in trial.tokens("La visite ne sera pas obligatoire")
    assert trial.lexical_rank("zèbre", ["visite obligatoire", "visite non obligatoire"]) == []
    assert (
        trial.lexical_rank("visite obligatoire", ["réception finale", "visite obligatoire"])[0][0]
        == 1
    )


def test_multiple_segments_cannot_artificially_improve_top_k_recall(trial):
    gold = [{"id": "q", "expected": ["target"], "critical": True}]
    score = trial.score_queries(gold, {"q": ["noise"] * 5 + ["target"]})
    assert score["recall_at_5"] == 0 and score["recall_at_10"] == 1
    assert score["critical_missing_at_5"] == ["q"]
    assert score["mrr"] == pytest.approx(1 / 6)


def test_same_parent_without_required_tail_region_is_still_an_omission(trial):
    gold = [
        {
            "id": "q",
            "expected": ["source"],
            "critical": True,
            "expected_regions": [
                {"source_fragment_id": "source", "start_byte": 900, "end_byte": 950}
            ],
        }
    ]
    score = trial.score_queries(
        gold,
        {"q": ["source"]},
        retrieved_regions={
            "q": [{"source_fragment_id": "source", "start_byte": 0, "end_byte": 100}]
        },
    )
    assert score["recall_at_5"] == 1
    assert score["evidence_recall_at_5"] == 0 and score["critical_evidence_missing_at_5"] == ["q"]


@pytest.mark.parametrize("second_start,expected", [(925, 1), (930, 0)])
def test_evidence_can_span_contiguous_regions_but_never_a_gap(trial, second_start, expected):
    gold = [
        {
            "id": "q",
            "expected": ["source"],
            "critical": True,
            "expected_regions": [
                {"source_fragment_id": "source", "start_byte": 900, "end_byte": 950}
            ],
        }
    ]
    score = trial.score_queries(
        gold,
        {"q": ["source", "source"]},
        retrieved_regions={
            "q": [
                {"source_fragment_id": "source", "start_byte": 850, "end_byte": 925},
                {"source_fragment_id": "source", "start_byte": second_start, "end_byte": 975},
            ]
        },
    )
    assert score["evidence_recall_at_5"] == expected
