"""Offline synthetic trial; no production composition, external inference or model choice."""

from __future__ import annotations

import argparse
import json
import re
import resource
import sys
import time
import unicodedata
from collections import Counter
from hashlib import sha256
from math import ceil, log
from pathlib import Path
from statistics import fmean
from typing import Any
from uuid import UUID, uuid5

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.modules.knowledge.application.retrieval import (  # noqa: E402
    FinancialRetrievalQueryRejected,
    InMemoryVectorIndex,
    RagRetrievalService,
)
from app.modules.knowledge.domain.retrieval import (  # noqa: E402
    DataClassification,
    RetrievalChunk,
    RetrievalScope,
)


def prepare_chunks(documents, scope, segment_chars=1000):
    if not 32 <= segment_chars <= 1000:
        raise ValueError("segment_chars outside qualification range")
    chunks: list[RetrievalChunk] = []
    segments: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    seen: set[UUID] = set()
    for doc in documents:
        identifier = UUID(doc["id"])
        if identifier in seen:
            raise ValueError("duplicate source fragment")
        seen.add(identifier)
        source = RetrievalChunk(
            chunk_id=identifier,
            source_fragment_id=identifier,
            tenant_id=UUID(doc["tenant_id"]),
            case_id=UUID(doc["case_id"]),
            dce_version_id=UUID(doc["version_id"]),
            ordinal=1,
            text=doc["text"],
            locator={"kind": "pdf_page", "page": doc["page"]},
            classification=DataClassification(doc["classification"]),
        )
        if (
            not source.is_visible_in(scope)
            or doc["current"] is not True
            or doc["extraction_status"] != "COMPLETED"
        ):
            excluded.append(
                {"source_fragment_id": str(identifier), "reason": "SCOPE_OR_SOURCE_REFUSED"}
            )
            continue
        start = 0
        while start < len(source.text):
            end = min(start + segment_chars, len(source.text))
            if end < len(source.text):
                boundary = source.text.rfind(" ", start + segment_chars // 2, end)
                if boundary >= 0:
                    end = boundary + 1
            text = source.text[start:end]
            lower, upper = len(source.text[:start].encode()), len(source.text[:end].encode())
            if text.strip():
                locator = {**source.locator, "start_byte": lower, "end_byte": upper}
                chunk = RetrievalChunk(
                    chunk_id=uuid5(identifier, f"{lower}:{upper}"),
                    source_fragment_id=identifier,
                    tenant_id=source.tenant_id,
                    case_id=source.case_id,
                    dce_version_id=source.dce_version_id,
                    ordinal=len(chunks) + 1,
                    text=text,
                    locator=locator,
                    classification=source.classification,
                )
                chunks.append(chunk)
                segments.append(
                    {
                        "chunk_id": str(chunk.chunk_id),
                        "source_fragment_id": str(identifier),
                        "version_id": str(source.dce_version_id),
                        "page": doc["page"],
                        "start_byte": lower,
                        "end_byte": upper,
                        "source_sha256": sha256(source.text.encode()).hexdigest(),
                        "segment_sha256": sha256(text.encode()).hexdigest(),
                    }
                )
            start = end
    return chunks, {"segments": segments, "excluded": excluded}


def model_texts(engine, role, texts):
    if engine not in {"bge", "e5"} or role not in {"query", "passage"}:
        raise ValueError("invalid encoder/role")
    prefix = role + ": " if engine == "e5" else ""
    return [prefix + text for text in texts]


_STOP = frozenset(
    [
        "le",
        "la",
        "les",
        "de",
        "du",
        "des",
        "un",
        "une",
        "et",
        "a",
        "au",
        "aux",
        "pour",
        "sur",
        "dans",
        "que",
        "qui",
        "quel",
        "quelle",
        "quels",
        "quelles",
        "est",
        "sont",
        "doit",
        "il",
        "elle",
        "en",
        "ce",
        "cette",
        "ces",
        "l",
        "d",
    ]
)


def tokens(text):
    folded = "".join(
        c for c in unicodedata.normalize("NFKD", text.casefold()) if unicodedata.category(c) != "Mn"
    )
    return [token for token in re.findall(r"\w+", folded) if token not in _STOP]


def lexical_rank(query, documents):
    terms = set(tokens(query))
    bags = [Counter(tokens(doc)) for doc in documents]
    avg = sum(sum(b.values()) for b in bags) / max(1, len(bags))
    scores = []
    for i, bag in enumerate(bags):
        score = 0.0
        for term in terms:
            frequency = bag[term]
            if frequency:
                df = sum(term in other for other in bags)
                idf = log(1 + (len(bags) - df + 0.5) / (df + 0.5))
                score += (
                    idf
                    * frequency
                    * 2.5
                    / (frequency + 1.5 * (0.25 + 0.75 * sum(bag.values()) / avg))
                )
        if score > 0:
            scores.append((i, score))
    return sorted(scores, key=lambda pair: (-pair[1], pair[0]))


def region_is_covered(gold, regions):
    cursor = gold["start_byte"]
    for region in sorted(regions, key=lambda r: r["start_byte"]):
        if region["source_fragment_id"] != gold["source_fragment_id"]:
            continue
        if region["end_byte"] <= cursor:
            continue
        if region["start_byte"] > cursor:
            return False
        cursor = max(cursor, region["end_byte"])
        if cursor >= gold["end_byte"]:
            return True
    return False


def score_queries(queries, results, retrieved_regions=None):
    if len({q["id"] for q in queries}) != len(queries) or set(results) != {
        q["id"] for q in queries
    }:
        raise ValueError("every query must be scored exactly once")
    positive = [q for q in queries if q["expected"]]
    recalls = {}
    for k in [1, 5, 10]:
        recalls[f"recall_at_{k}"] = (
            fmean(
                len(set(results[q["id"]][:k]) & set(q["expected"])) / len(set(q["expected"]))
                for q in positive
            )
            if positive
            else None
        )
    evidence_recalls = {}
    evidence_missing = []
    for k in [1, 5, 10]:
        values = []
        for q in positive:
            expected_regions = q.get("expected_regions")
            if expected_regions:
                if retrieved_regions is None or q["id"] not in retrieved_regions:
                    raise ValueError("ranked regions required for evidence qrels")
                hits = sum(
                    region_is_covered(gold, retrieved_regions[q["id"]][:k])
                    for gold in expected_regions
                )
                recall = hits / len(expected_regions)
            else:
                recall = len(set(results[q["id"]][:k]) & set(q["expected"])) / len(
                    set(q["expected"])
                )
            values.append(recall)
            if k == 5 and q["critical"] and recall < 1:
                evidence_missing.append(q["id"])
        evidence_recalls[f"evidence_recall_at_{k}"] = fmean(values) if values else None
    rows = []
    for q in queries:
        actual = results[q["id"]]
        expected = set(q["expected"])
        rank = next((i for i, identifier in enumerate(actual, 1) if identifier in expected), None)
        rows.append(
            {
                "query_id": q["id"],
                "expected": sorted(expected),
                "retrieved": actual,
                "ranked_regions": (retrieved_regions or {}).get(q["id"], []),
                "expected_regions": q.get("expected_regions", []),
                "missing_at_5": sorted(expected - set(actual[:5])),
                "first_relevant_rank": rank,
                "answer_state": "UNKNOWN",
            }
        )
    return {
        **recalls,
        **evidence_recalls,
        "critical_evidence_missing_at_5": evidence_missing,
        "mrr": fmean(
            1 / r["first_relevant_rank"] if r["first_relevant_rank"] else 0
            for r, q in zip(rows, queries, strict=True)
            if q["expected"]
        )
        if positive
        else None,
        "precision_at_5": fmean(
            len(set(results[q["id"]][:5]) & set(q["expected"])) / 5 for q in queries
        ),
        "critical_missing_at_5": [
            q["id"]
            for q in queries
            if q["critical"] and set(q["expected"]) - set(results[q["id"]][:5])
        ],
        "no_answer_with_candidates": [
            q["id"] for q in queries if not q["expected"] and results[q["id"]]
        ],
        "queries": rows,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--engine", choices=["lexical", "bge", "e5"], required=True)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = json.loads(args.fixture.read_text())
    if payload.get("synthetic") is not True or payload.get("schema_version") != 1:
        raise ValueError("only explicitly synthetic qualification fixture v1")
    scope = RetrievalScope(
        tenant_id=UUID(payload["tenant_id"]),
        case_id=UUID(payload["case_id"]),
        dce_version_id=UUID(payload["version_id"]),
    )
    chunks, trace = prepare_chunks(payload["documents"], scope)
    queries = payload["queries"]
    known_ids = {str(c.source_fragment_id) for c in chunks}
    if any(not set(q["expected"]).issubset(known_ids) for q in queries):
        raise ValueError("gold references a refused/missing source")
    start = time.perf_counter()
    service = None
    trace["token_lengths"] = []
    if args.engine != "lexical":
        if args.model_dir is None:
            raise ValueError("pinned local model directory required")
        import torch
        from sentence_transformers import SentenceTransformer

        torch.set_num_threads(2)
        model = SentenceTransformer(
            str(args.model_dir), device="cpu", local_files_only=True, trust_remote_code=False
        )
        model.max_seq_length = 512 if args.engine == "e5" else 8192
        expected_dimension = 384 if args.engine == "e5" else 1024
        if model.get_sentence_embedding_dimension() != expected_dimension:
            raise ValueError("MODEL_DIMENSION_MISMATCH")
        if next(model.parameters()).dtype != torch.float32:
            raise ValueError("UNQUALIFIED_PRECISION")

        class Encoder:
            role = "passage"
            model_id = args.engine

            def embed(self, texts):
                encoded = model_texts(args.engine, self.role, texts)
                lengths = [len(model.tokenizer(t, truncation=False)["input_ids"]) for t in encoded]
                if any(n > model.max_seq_length for n in lengths):
                    raise ValueError("TOKEN_TRUNCATION_REFUSED")
                trace["token_lengths"].extend(lengths)
                return [
                    tuple(float(v) for v in row)
                    for row in model.encode(
                        encoded,
                        batch_size=1,
                        convert_to_numpy=True,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                ]

        encoder = Encoder()
        service = RagRetrievalService(embedding_provider=encoder, index=InMemoryVectorIndex())
        trace["raw_fragment_tokens"] = {
            d["id"]: len(
                model.tokenizer(
                    model_texts(args.engine, "passage", [d["text"]])[0], truncation=False
                )["input_ids"]
            )
            for d in payload["documents"]
            if d["id"] in known_ids
        }
    load_ms = (time.perf_counter() - start) * 1000
    start = time.perf_counter()
    if service:
        service.index(chunks=chunks)
        encoder.role = "query"
    index_ms = (time.perf_counter() - start) * 1000
    runs: dict[str, list[str]] = {}
    elapsed: list[float] = []
    first: list[float] = []
    ranked_regions: dict[str, list[dict[str, Any]]] = {}
    region_by_id = {r["chunk_id"]: r for r in trace["segments"]}
    for repetition in range(4):
        for query in queries:
            start = time.perf_counter()
            if service:
                try:
                    retrieved = service.retrieve(query=query["text"], scope=scope, top_k=50)
                    identifiers = [str(result.chunk.source_fragment_id) for result in retrieved]
                    selected_regions = [
                        region_by_id[str(result.chunk.chunk_id)] for result in retrieved
                    ]
                except FinancialRetrievalQueryRejected:
                    identifiers = []
                    selected_regions = []
            else:
                # The production financial-query guard applies equally to the baseline.
                from app.modules.knowledge.application.retrieval import _FINANCIAL_QUERY_PATTERN

                ranked = (
                    []
                    if _FINANCIAL_QUERY_PATTERN.search(query["text"])
                    else lexical_rank(query["text"], [c.text for c in chunks])
                )
                identifiers = [str(chunks[i].source_fragment_id) for i, _ in ranked]
                selected_regions = [region_by_id[str(chunks[i].chunk_id)] for i, _ in ranked]
            milliseconds = (time.perf_counter() - start) * 1000
            (first if repetition == 0 else elapsed).append(milliseconds)
            if query["id"] in runs and (
                runs[query["id"]] != identifiers or ranked_regions[query["id"]] != selected_regions
            ):
                raise ValueError("NONDETERMINISTIC_RANKING")
            runs[query["id"]] = identifiers
            ranked_regions[query["id"]] = selected_regions
    scores = score_queries(queries, runs, retrieved_regions=ranked_regions)
    p95 = sorted(elapsed)[ceil(len(elapsed) * 0.95) - 1]
    report = {
        "schema_version": 1,
        "engine": args.engine,
        "synthetic_only": True,
        "fixture_sha256": sha256(args.fixture.read_bytes()).hexdigest(),
        "source_trace": trace,
        "metrics": scores,
        "load_ms": load_ms,
        "index_ms": index_ms,
        "first_query_mean_ms": fmean(first),
        "warm_query_mean_ms": fmean(elapsed),
        "warm_query_p95_ms": p95,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "repetitions": 4,
        "peak_cgroup_bytes": int(Path("/sys/fs/cgroup/memory.peak").read_text())
        if Path("/sys/fs/cgroup/memory.peak").is_file()
        else None,
        "runtime_versions": {
            name: __import__("importlib.metadata", fromlist=["version"]).version(name)
            for name in ["torch", "sentence-transformers"]
        },
        "model_manifest": json.loads((args.model_dir / "qualification-manifest.json").read_text())
        if args.model_dir
        else None,
        "ranking_gate": scores["recall_at_1"] >= 0.7
        and scores["recall_at_5"] >= 0.9
        and scores["recall_at_10"] >= 0.95
        and not scores["critical_missing_at_5"]
        and not scores["critical_evidence_missing_at_5"],
        "latency_budget_gate": p95 <= (50 if args.engine == "lexical" else 2000)
        and load_ms <= 180000
        and index_ms <= 180000,
        "no_answer_gate": not scores["no_answer_with_candidates"],
        "production_engine_changed": False,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "status": "MEASURED",
                "engine": args.engine,
                "ranking_gate": report["ranking_gate"],
                "output": str(args.output),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
