"""Run an unwired candidate on an explicitly synthetic held-out fixture."""

from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from dataclasses import asdict
from hashlib import sha256
from math import ceil
from pathlib import Path
from statistics import fmean
from typing import Any
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.modules.knowledge.application.candidate_retrieval import (
    CandidateRetrievalService,  # noqa: E402
)
from app.modules.knowledge.application.rc_recall import obligation_rc_subject  # noqa: E402
from app.modules.knowledge.application.retrieval import (
    FinancialRetrievalQueryRejected,  # noqa: E402
)
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile  # noqa: E402
from app.modules.knowledge.domain.retrieval import (
    DataClassification,
    RetrievalChunk,
    RetrievalScope,
)  # noqa: E402
from app.modules.knowledge.infrastructure.candidate_embeddings import (
    CpuCandidateEncoder,  # noqa: E402
)
from qualify_btp_retrieval import score_queries  # noqa: E402


def score_rc_pairs(
    expected: list[dict[str, Any]], actual: list[dict[str, Any]]
) -> dict[str, list[str]]:
    def keys(items: list[dict[str, Any]]) -> set[str]:
        return {
            json.dumps({**item, "sources": sorted(item["sources"])}, sort_keys=True)
            for item in items
        }

    wanted, found = keys(expected), keys(actual)
    return {"missing": sorted(wanted - found), "unexpected": sorted(found - wanted)}


def score_query_intents(
    queries: list[dict[str, Any]],
    states: dict[str, dict[str, Any]],
    regions: dict[str, list[dict[str, Any]]],
) -> dict[str, bool]:
    valid = exact = True
    subjects = {
        "VISIT",
        "VISIT_MEDICAL",
        "VISIT_SITE",
        "DC1",
        "DC2",
        "MEMOIRE_TECHNIQUE",
        "VARIANTS",
        "UNKNOWN",
    }
    for q in queries:
        state = states[q["id"]]
        qi = state.get("query_intent")
        expected = q.get("expected_intent")
        if q.get("expected_refusal") == "FINANCIAL_SCOPE_REFUSED":
            valid = (
                valid
                and qi is None
                and not regions[q["id"]]
                and state["reason"] == "FINANCIAL_SCOPE_REFUSED"
            )
            exact = exact and expected is None
            continue
        if not isinstance(qi, dict) or not isinstance(qi.get("anchors"), list):
            valid = exact = False
            continue
        exact = exact and {k: qi.get(k) for k in ("subject", "demand", "coverage")} == expected
        valid = valid and (
            isinstance(qi.get("subject"), str)
            and qi["subject"] in subjects
            and qi.get("demand") in {"OBLIGATION", "DATE_TIME", "LOCATION", "UNKNOWN"}
            and qi.get("coverage") in {"COVERED", "UNSUPPORTED", "AMBIGUOUS", "UNKNOWN"}
            and qi.get("query_sha256") == sha256(q["text"].encode()).hexdigest()
            and qi.get("scope") == state.get("query_lot")
        )
        expected_anchors = q.get("expected_query_anchors")
        valid = (
            valid
            and isinstance(expected_anchors, list)
            and all(a in expected_anchors for a in qi["anchors"])
        )
        if qi.get("coverage") == "COVERED":
            valid = valid and qi["anchors"] == expected_anchors
        signals = []
        for a in qi["anchors"]:
            if not isinstance(a, dict):
                valid = False
                continue
            start, end = a.get("start_byte"), a.get("end_byte")
            signals.append(a.get("signal"))
            valid = valid and (
                a.get("signal") in {"SUBJECT", "DEMAND", "LOT"}
                and isinstance(start, int)
                and not isinstance(start, bool)
                and isinstance(end, int)
                and not isinstance(end, bool)
                and 0 <= start < end <= len(q["text"].encode())
                and isinstance(a.get("excerpt"), str)
                and q["text"].encode()[start:end] == a["excerpt"].encode()
            )
        scope = qi.get("scope") or {}
        lot_anchors = [a for a in qi["anchors"] if isinstance(a, dict) and a.get("signal") == "LOT"]
        if scope.get("state") == "CANDIDATE":
            valid = (
                valid
                and len(lot_anchors) == 1
                and lot_anchors[0].get("start_byte") == scope.get("start_byte")
                and lot_anchors[0].get("end_byte") == scope.get("end_byte")
            )
        else:
            valid = valid and not lot_anchors
        if qi.get("coverage") == "COVERED":
            valid = (
                valid
                and qi["demand"] == "OBLIGATION"
                and qi["subject"] != "UNKNOWN"
                and signals.count("SUBJECT") == signals.count("DEMAND") == 1
            )
        else:
            projection = state.get("rc_projection", {})
            valid = valid and not (
                regions[q["id"]]
                or state.get("score_trace")
                or state.get("visit_type_evidence")
                or projection.get("clauses")
                or projection.get("unknown_regions")
                or projection.get("links")
                or state.get("rc_unscoped_evidence")
            )
    return {"rc_query_intent_valid": bool(valid), "rc_query_intent_exact": bool(exact)}


def score_imperative_anchors(data: dict[str, Any], states: dict[str, Any]) -> bool:
    """Compare emitted imperative anchors with independent source-region gold."""
    documents = {d["id"]: d for d in data["documents"]}
    gold = data["imperative_anchors"]
    for state in states.values():
        projection = state.get("rc_projection") or {}
        evidence = [
            *projection.get("clauses", []),
            *projection.get("unknown_regions", []),
            *state.get("rc_unscoped_evidence", []),
            *state.get("visit_type_evidence", []),
        ]
        for e in evidence:
            anchors = e.get("directive_anchors", [])
            expected_region = [
                g
                for g in gold
                if all(
                    g[k] == e[k]
                    for k in ("source_fragment_id", "source_sha256", "start_byte", "end_byte")
                )
            ]
            if not anchors:
                if expected_region and e.get("directive_signal") == "CANDIDATE":
                    return False
                continue
            doc = documents.get(e["source_fragment_id"])
            if doc is None or e["source_sha256"] != sha256(doc["text"].encode()).hexdigest():
                return False
            expected = [
                g
                for g in gold
                if all(
                    g[k] == e[k]
                    for k in ("source_fragment_id", "source_sha256", "start_byte", "end_byte")
                )
            ]
            ordered = sorted(anchors, key=lambda a: (a["start_byte"], a["end_byte"], a["signal"]))
            if len(expected) != 1 or ordered != expected[0]["anchors"]:
                return False
            conditions = e.get("condition_signals", [])
            expected_conditions = expected[0].get("condition_signals", [])
            if conditions != expected_conditions:
                return False
            expected_value = expected[0].get("value", "REQUIRED")
            expected_kind = expected[0].get("kind", "ASSERTION")
            if conditions and (
                len(conditions) != 1
                or conditions[0].get("signal") != "CONDITION"
                or (expected_value, expected_kind) != ("UNKNOWN", "UNKNOWN")
            ):
                return False
            if (
                len(anchors) != 3
                or {a["signal"] for a in anchors} != {"SUBJECT", "DIRECTIVE", "LOT"}
                or e["value"] != expected_value
                or e["kind"] != expected_kind
                or e["directive_signal"] != "CANDIDATE"
            ):
                return False
            for a in [*anchors, *conditions]:
                start, end = a["start_byte"], a["end_byte"]
                if (
                    not isinstance(start, int)
                    or isinstance(start, bool)
                    or not isinstance(end, int)
                    or isinstance(end, bool)
                    or not e["start_byte"] <= start < end <= e["end_byte"]
                    or doc["text"].encode()[start:end] != a["excerpt"].encode()
                ):
                    return False
    return True


def main(argv=None, *, source_override=None, encoder_override=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["fixture", "profile", "model-dir", "runtime-manifest", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    data = json.loads(args.fixture.read_text())
    if (
        data.get("synthetic") is not True
        or data.get("held_out") is not True
        or data.get("schema_version") != 1
    ):
        raise ValueError("only synthetic held-out v1 fixtures")
    profile = CandidateRetrievalProfile(**json.loads(args.profile.read_text()))
    if profile.review_policy in {"rc-imperative-v9", "rc-conditional-v10"} and not isinstance(
        data.get("imperative_anchors"), list
    ):
        raise ValueError("RC v9 requires independent imperative gold")
    if profile.review_policy in {"rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"} and any(
        "expected_intent" not in q
        or (not q.get("expected_refusal") and "expected_query_anchors" not in q)
        for q in data["queries"]
    ):
        raise ValueError("RC v8 requires independent intent gold")
    if profile.review_policy in {
        "rc-opposition-v2",
        "rc-query-lot-v3",
        "rc-recall-v4",
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    } and any(
        "expected_conflicts" not in q or "expected_unknown" not in q for q in data["queries"]
    ):
        raise ValueError("RC v2 requires independent pair and unknown gold")
    if profile.review_policy in {
        "rc-query-lot-v3",
        "rc-recall-v4",
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    } and any(
        any(k not in q for k in ("expected_query_lot", "expected_query_anchor", "expected_refusal"))
        for q in data["queries"]
    ):
        raise ValueError("RC v3 requires independent query scope and refusal gold")
    if profile.review_policy in {
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    } and any(
        "expected_visit_subject" not in q or "expected_visit_anchor" not in q
        for q in data["queries"]
    ):
        raise ValueError("RC v5 requires independent visit intent gold")
    if profile.review_policy == "rc-conditional-v10" and any(
        "expected_legacy_intent" not in q
        or (q["expected_refusal"] is None and not isinstance(q["expected_legacy_intent"], dict))
        for q in data["queries"]
    ):
        raise ValueError("RC v10 requires independent legacy intent gold")
    scope = RetrievalScope(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )

    class Source:
        def read_chunks(self, **kwargs):
            return [
                RetrievalChunk(
                    chunk_id=UUID(d["id"]),
                    source_fragment_id=UUID(d["id"]),
                    tenant_id=UUID(d["tenant_id"]),
                    case_id=UUID(d["case_id"]),
                    dce_version_id=UUID(d["version_id"]),
                    ordinal=i + 1,
                    text=d["text"],
                    locator={"kind": "synthetic_page", "page": d["page"]},
                    classification=DataClassification(d["classification"]),
                )
                for i, d in enumerate(data["documents"])
                if d["current"] is True and d["extraction_status"] == "COMPLETED"
            ]

    encoder = encoder_override or CpuCandidateEncoder(
        profile=profile, model_dir=args.model_dir, runtime_manifest=args.runtime_manifest
    )
    service = CandidateRetrievalService(
        profile=profile,
        source=source_override if source_override is not None else Source(),
        encoder=encoder,
    )
    runs: dict[str, list[str]] = {}
    regions: dict[str, list[dict[str, Any]]] = {}
    states: dict[str, dict[str, Any]] = {}
    first: list[float] = []
    warm: list[float] = []
    for repetition in range(4):
        for query in data["queries"]:
            start = time.perf_counter()
            try:
                reading = service.retrieve(query=query["text"], scope=scope, top_k=10)
                ids = [str(h.result.chunk.source_fragment_id) for h in reading.hits]
                ranked = [
                    {
                        "chunk_id": str(h.result.chunk.chunk_id),
                        "source_fragment_id": str(h.result.chunk.source_fragment_id),
                        "start_byte": h.start_byte,
                        "end_byte": h.end_byte,
                        "source_sha256": h.source_sha256,
                        "segment_sha256": h.segment_sha256,
                        "score": h.result.score,
                        "locator": h.result.chunk.locator,
                    }
                    for h in reading.hits
                ]
                state: dict[str, Any] = {
                    "state": reading.state,
                    "reason": reading.reason,
                    "answer_state": reading.answer_state,
                    "review_source_ids": [str(s) for s in reading.review_source_ids],
                }
                if profile.review_policy in {
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["query_intent"] = (
                        json.loads(json.dumps(asdict(reading.query_intent)))
                        if reading.query_intent
                        else None
                    )
                if profile.review_policy in {
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["specific_intent"] = (
                        asdict(reading.specific_intent) if reading.specific_intent else None
                    )
                if profile.review_policy in {
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["visit_type_evidence"] = json.loads(
                        json.dumps([asdict(e) for e in reading.visit_type_evidence], default=str)
                    )
                if profile.review_policy in {
                    "rc-opposition-v2",
                    "rc-query-lot-v3",
                    "rc-recall-v4",
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["rc_projection"] = json.loads(
                        json.dumps(asdict(reading.rc_projection), default=str)
                    )
                if profile.review_policy in {
                    "rc-recall-v4",
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["score_trace"] = json.loads(
                        json.dumps([asdict(t) for t in reading.score_trace], default=str)
                    )
                if profile.review_policy in {
                    "rc-query-lot-v3",
                    "rc-recall-v4",
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["query_lot"] = asdict(reading.query_lot) if reading.query_lot else None
                    state["rc_unscoped_evidence"] = json.loads(
                        json.dumps([asdict(e) for e in reading.rc_unscoped_evidence], default=str)
                    )
            except FinancialRetrievalQueryRejected as exc:
                ids, ranked = [], []
                state = {
                    "state": "ABSTAIN",
                    "reason": "FINANCIAL_SCOPE_REFUSED",
                    "answer_state": "UNKNOWN",
                }
                if profile.review_policy in {
                    "rc-query-lot-v3",
                    "rc-recall-v4",
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }:
                    state["policy_refusal"] = {
                        "code": str(exc),
                        "stage": "BEFORE_SOURCE_AND_ENCODER",
                    }
            (first if repetition == 0 else warm).append((time.perf_counter() - start) * 1000)
            qid = query["id"]
            if qid in runs and (runs[qid] != ids or regions[qid] != ranked or states[qid] != state):
                raise ValueError("nondeterministic candidate reading")
            runs[qid], regions[qid], states[qid] = ids, ranked, state
    metrics = score_queries(data["queries"], runs, retrieved_regions=regions)
    reviews_missing = [
        q["id"]
        for q in data["queries"]
        if q.get("review_required")
        and (
            states[q["id"]]["state"] != "REVIEW_REQUIRED"
            or not (
                set(states[q["id"]].get("review_source_ids", [])) & set(q["expected"])
                or profile.review_policy
                in {
                    "rc-query-lot-v3",
                    "rc-recall-v4",
                    "rc-specific-v5",
                    "rc-type-proof-v6",
                    "rc-subject-proof-v7",
                    "rc-intent-v8",
                    "rc-imperative-v9",
                    "rc-conditional-v10",
                }
                and q["expected_query_lot"] is None
                and states[q["id"]].get("query_lot", {}).get("state") == "UNKNOWN"
                and states[q["id"]]["reason"] == "RC_QUERY_LOT_UNKNOWN"
            )
        )
    ]
    unexpected_reviews = [
        q["id"]
        for q in data["queries"]
        if not q.get("review_required") and states[q["id"]]["state"] == "REVIEW_REQUIRED"
    ]
    allowed = {
        str(c.source_fragment_id)
        for c in Source().read_chunks()
        if c.is_visible_in(scope)
        and c.classification in {DataClassification.PUBLIC, DataClassification.INTERNAL_OPERATIONAL}
    }
    source_gate = all(set(ids) <= allowed for ids in runs.values())
    p95 = sorted(warm)[ceil(len(warm) * 0.95) - 1]
    gates = {
        "source_scope": source_gate,
        "interactive_latency": p95 <= 2000,
        "unknown_answer": all(s["answer_state"] == "UNKNOWN" for s in states.values()),
        "evidence_recall_at_5": metrics["evidence_recall_at_5"] is not None
        and metrics["evidence_recall_at_5"] >= 0.90,
        "critical_complete": not metrics["critical_evidence_missing_at_5"],
        "review_signals": not reviews_missing,
        "unexpected_review_signals": not unexpected_reviews,
        "abstention": not metrics["no_answer_with_candidates"],
    }
    pair_scores = {}
    unknown_missing = []
    anchors_valid = True
    if profile.review_policy in {
        "rc-opposition-v2",
        "rc-query-lot-v3",
        "rc-recall-v4",
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    }:
        source_by_id = {
            str(c.source_fragment_id): c for c in Source().read_chunks() if c.is_visible_in(scope)
        }
        for query in data["queries"]:
            projection = states[query["id"]].get("rc_projection", {})
            actual = [
                {
                    "sources": [
                        link["left"]["source_fragment_id"],
                        link["right"]["source_fragment_id"],
                    ],
                    "subject": link["left"]["subject"],
                    "lot": link["left"]["lot"],
                    "version": link["left"]["dce_version_id"],
                    "kind": link["kind"],
                }
                for link in projection.get("links", [])
            ]
            pair_scores[query["id"]] = score_rc_pairs(query["expected_conflicts"], actual)
            unknown = projection.get("unknown_regions", [])
            if query["expected_unknown"] and not any(
                e["source_fragment_id"] in query["expected"] for e in unknown
            ):
                unknown_missing.append(query["id"])
            for e in (
                projection.get("clauses", [])
                + unknown
                + states[query["id"]].get("rc_unscoped_evidence", [])
                + states[query["id"]].get("visit_type_evidence", [])
            ):
                src = source_by_id.get(e["source_fragment_id"])
                anchors_valid = (
                    anchors_valid
                    and src is not None
                    and (
                        src.tenant_id == scope.tenant_id
                        and src.case_id == scope.case_id
                        and e["tenant_id"] == str(src.tenant_id)
                        and e["case_id"] == str(src.case_id)
                        and e["dce_version_id"] == str(src.dce_version_id)
                        and e["source_sha256"] == sha256(src.text.encode()).hexdigest()
                        and 0 <= e["start_byte"] < e["end_byte"] <= len(src.text.encode())
                        and src.text.encode()[e["start_byte"] : e["end_byte"]]
                        == e["excerpt"].encode()
                    )
                )
        gates.update(
            {
                "rc_pairs_recall": all(not x["missing"] for x in pair_scores.values()),
                "rc_pairs_precision": all(not x["unexpected"] for x in pair_scores.values()),
                "rc_unknown_refusals": not unknown_missing,
                "rc_anchor_integrity": bool(anchors_valid),
            }
        )
    non_evaluable = []
    if profile.review_policy in {
        "rc-query-lot-v3",
        "rc-recall-v4",
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    }:
        refusal_exact, query_scope_exact, projection_scoped = True, True, True
        for q in data["queries"]:
            state = states[q["id"]]
            refused = "policy_refusal" in state
            observed_refusal = state["reason"] if refused else None
            refusal_exact = refusal_exact and observed_refusal == q["expected_refusal"]
            if refused:
                non_evaluable.append(q["id"])
                continue  # Refusal is not evidence that a document or its query lot was evaluated.
            lot = state.get("query_lot") or {}
            expected = q["expected_query_lot"]
            query_scope_exact = query_scope_exact and (
                lot.get("lot") == expected
                and lot.get("state") == ("UNKNOWN" if expected is None else "CANDIDATE")
            )
            if expected is not None:
                query_start, query_end = lot.get("start_byte"), lot.get("end_byte")
                query_scope_exact = query_scope_exact and (
                    isinstance(query_start, int)
                    and isinstance(query_end, int)
                    and 0 <= query_start < query_end <= len(q["text"].encode())
                    and q["text"].encode()[query_start:query_end].decode()
                    == q["expected_query_anchor"]
                )
            projection = state.get("rc_projection", {})
            projection_scoped = (
                projection_scoped
                and all(
                    c["lot"] == expected and expected is not None
                    for c in projection.get("clauses", [])
                )
                and all(
                    link["left"]["lot"] == link["right"]["lot"] == expected and expected is not None
                    for link in projection.get("links", [])
                )
            )
        gates.update(
            {
                "policy_refusals_exact": bool(refusal_exact),
                "query_scope_exact": bool(query_scope_exact),
                "query_lot_projection": bool(projection_scoped),
            }
        )
    if profile.review_policy in {
        "rc-recall-v4",
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    }:
        trace_valid = True
        for q in data["queries"]:
            trace = states[q["id"]].get("score_trace", [])
            selected = {h["chunk_id"] for h in regions[q["id"]]}
            traced_selection = set()
            for rank, t in enumerate(trace, 1):
                src = source_by_id.get(t["source_fragment_id"])
                chosen = t["decision"] in {"DENSE_FLOOR", "RC_SUBJECT_RESCUE", "RC_TYPED_RESCUE"}
                if chosen:
                    traced_selection.add(t["chunk_id"])
                trace_valid = (
                    trace_valid
                    and src is not None
                    and (
                        t["rank"] == rank
                        and rank <= 50
                        and t["threshold"] == profile.minimum_score
                        and 0 <= t["score"] <= 1
                        and t["decision"]
                        in {
                            "DENSE_FLOOR",
                            "RC_SUBJECT_RESCUE",
                            "RC_TYPED_RESCUE",
                            "TOP_K_LIMIT",
                            "BELOW_FLOOR",
                            "SPECIFIC_MISMATCH",
                            "SPECIFIC_UNPROVEN",
                            "SPECIFIC_QUERY_UNKNOWN",
                        }
                        and (t["decision"] != "DENSE_FLOOR" or t["score"] >= t["threshold"])
                        and (
                            t["decision"] not in {"RC_SUBJECT_RESCUE", "RC_TYPED_RESCUE"}
                            or t["score"] < t["threshold"]
                        )
                        and t["source_sha256"] == sha256(src.text.encode()).hexdigest()
                        and 0 <= t["start_byte"] < t["end_byte"] <= len(src.text.encode())
                        and t["segment_sha256"]
                        == sha256(src.text.encode()[t["start_byte"] : t["end_byte"]]).hexdigest()
                    )
                )
            trace_valid = trace_valid and traced_selection == selected
        gates["score_trace_valid"] = bool(trace_valid)
    if profile.review_policy in {
        "rc-specific-v5",
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    }:
        intent_exact, typed_projection = True, True
        for q in data["queries"]:
            state = states[q["id"]]
            if "policy_refusal" in state:
                continue
            intent_data = state.get("specific_intent") or {}
            wanted = q["expected_visit_subject"]
            expected_state = (
                "NONE" if wanted is None else "UNKNOWN" if wanted == "UNKNOWN" else "CANDIDATE"
            )
            intent_exact = intent_exact and intent_data.get("state") == expected_state
            if expected_state == "CANDIDATE":
                intent_start, intent_end = (
                    intent_data.get("start_byte"),
                    intent_data.get("end_byte"),
                )
                intent_exact = intent_exact and (
                    intent_data.get("subject") == wanted
                    and isinstance(intent_start, int)
                    and isinstance(intent_end, int)
                    and 0 <= intent_start < intent_end <= len(q["text"].encode())
                    and q["text"].encode()[intent_start:intent_end].decode()
                    == q["expected_visit_anchor"]
                )
                projection = state.get("rc_projection", {})
                typed_projection = (
                    typed_projection
                    and all(c["subject"] == wanted for c in projection.get("clauses", []))
                    and all(
                        link["left"]["subject"] == link["right"]["subject"] == wanted
                        for link in projection.get("links", [])
                    )
                )
            if expected_state == "UNKNOWN":
                typed_projection = typed_projection and not regions[q["id"]]
        gates.update(
            {
                "specific_intent_exact": bool(intent_exact),
                "specific_projection_typed": bool(typed_projection),
            }
        )
    if profile.review_policy in {
        "rc-type-proof-v6",
        "rc-subject-proof-v7",
        "rc-intent-v8",
        "rc-imperative-v9",
        "rc-conditional-v10",
    }:
        proof_valid, typed_selected = True, True
        for q in data["queries"]:
            state = states[q["id"]]
            projection = state.get("rc_projection", {})
            evidence = (
                projection.get("clauses", [])
                + projection.get("unknown_regions", [])
                + state.get("rc_unscoped_evidence", [])
                + state.get("visit_type_evidence", [])
            )
            for e in evidence:
                proof = e.get("visit_type_proof")
                src = source_by_id.get(e["source_fragment_id"])
                if proof:
                    proof_valid = (
                        proof_valid
                        and src is not None
                        and (
                            proof["signal"] == e["subject"]
                            and proof["signal"] in {"VISIT_MEDICAL", "VISIT_SITE"}
                            and e["start_byte"]
                            <= proof["start_byte"]
                            < proof["end_byte"]
                            <= e["end_byte"]
                            and src.text.encode()[proof["start_byte"] : proof["end_byte"]].decode()
                            == proof["excerpt"]
                        )
                    )
                if e.get("directive_signal") == "CANDIDATE":
                    proof_valid = proof_valid and (
                        bool(proof)
                        or profile.review_policy
                        in {
                            "rc-subject-proof-v7",
                            "rc-intent-v8",
                            "rc-imperative-v9",
                            "rc-conditional-v10",
                        }
                        and e["subject"] in {"VISIT", "DC1", "DC2", "MEMOIRE_TECHNIQUE", "VARIANTS"}
                    )
                for c in e.get("condition_signals", []):
                    proof_valid = (
                        proof_valid
                        and src is not None
                        and (
                            c["signal"] == "CONDITION"
                            and 0 <= c["start_byte"] < c["end_byte"] <= len(src.text.encode())
                            and src.text.encode()[c["start_byte"] : c["end_byte"]].decode()
                            == c["excerpt"]
                            and e["value"] == "UNKNOWN"
                            and e["kind"] == "UNKNOWN"
                        )
                    )
            intent = state.get("specific_intent") or {}
            lot = (state.get("query_lot") or {}).get("lot")
            requested = intent.get("subject") or (
                obligation_rc_subject(q["text"])
                if profile.review_policy
                in {"rc-subject-proof-v7", "rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}
                else None
            )
            if profile.review_policy in {"rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}:
                qi = state.get("query_intent") or {}
                requested = qi.get("subject") if qi.get("coverage") == "COVERED" else None
            allowed_subjects = (
                {"VISIT", "VISIT_MEDICAL", "VISIT_SITE"} if requested == "VISIT" else {requested}
            )
            for trace in state.get("score_trace", []):
                if trace["decision"] == "RC_TYPED_RESCUE" or (
                    trace["decision"] == "DENSE_FLOOR"
                    and (
                        intent.get("state") == "CANDIDATE"
                        or profile.review_policy
                        in {
                            "rc-subject-proof-v7",
                            "rc-intent-v8",
                            "rc-imperative-v9",
                            "rc-conditional-v10",
                        }
                        and requested is not None
                    )
                ):
                    typed_selected = typed_selected and any(
                        e["source_fragment_id"] == trace["source_fragment_id"]
                        and e["source_sha256"] == trace["source_sha256"]
                        and trace["start_byte"]
                        <= e["start_byte"]
                        < e["end_byte"]
                        <= trace["end_byte"]
                        and (
                            e["subject"] in allowed_subjects
                            if profile.review_policy
                            in {
                                "rc-subject-proof-v7",
                                "rc-intent-v8",
                                "rc-imperative-v9",
                                "rc-conditional-v10",
                            }
                            else e.get("visit_type_proof") is not None
                            and e["visit_type_proof"]["signal"] == intent.get("subject")
                        )
                        and e["directive_signal"] == "CANDIDATE"
                        and (lot is None or e["lot"] == lot)
                        for e in evidence
                    )
        gates.update(
            {
                "visit_type_proof_valid": bool(proof_valid),
                "typed_selection_proven": bool(typed_selected),
            }
        )
    if profile.review_policy in {"rc-intent-v8", "rc-imperative-v9", "rc-conditional-v10"}:
        gates.update(score_query_intents(data["queries"], states, regions))
    if profile.review_policy == "rc-conditional-v10":
        gates["legacy_intent_exact"] = all(
            states[q["id"]].get("specific_intent") == q["expected_legacy_intent"]
            for q in data["queries"]
        )
    if profile.review_policy in {"rc-imperative-v9", "rc-conditional-v10"}:
        gates["imperative_anchors_valid"] = score_imperative_anchors(data, states)
    report = {
        "status": "MEASURED",
        "synthetic_only": True,
        "held_out": True,
        "profile_id": profile.profile_id,
        "profile": asdict(profile),
        "fixture_sha256": sha256(args.fixture.read_bytes()).hexdigest(),
        "metrics": metrics,
        "states": states,
        "review_signals_missing": reviews_missing,
        "unexpected_review_signals": unexpected_reviews,
        "gates": gates,
        "rc_pair_scores": pair_scores,
        "rc_unknown_missing": unknown_missing,
        "non_evaluable_queries": non_evaluable,
        "admitted": False,
        "production_engine_changed": False,
        "first_cycle_mean_ms": fmean(first),
        "first_query_ms": first[0],
        "warm_query_p95_ms": p95,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "peak_cgroup_bytes": int(Path("/sys/fs/cgroup/memory.peak").read_text())
        if Path("/sys/fs/cgroup/memory.peak").is_file()
        else None,
    }
    args.output.write_text(json.dumps(report, sort_keys=True, indent=2))
    print(
        json.dumps(
            {
                "status": "MEASURED",
                "profile_id": profile.profile_id,
                "gates": gates,
                "admitted": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
