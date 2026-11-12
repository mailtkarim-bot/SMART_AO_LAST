"""Offline semantic-gold trial of the unchanged candidate; never grants admission."""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from dataclasses import asdict
from hashlib import sha256
from math import ceil
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from qualify_btp_retrieval import region_is_covered, score_queries  # noqa: E402
from qualify_candidate_retrieval import (  # noqa: E402
    CandidateRetrievalProfile,
    CandidateRetrievalService,
    CpuCandidateEncoder,
    DataClassification,
    FinancialRetrievalQueryRejected,
    RetrievalChunk,
    RetrievalScope,
)


def eligible_documents(data):
    return {
        d["id"]: d
        for d in data["documents"]
        if all(d[k] == data[k] for k in ("tenant_id", "case_id", "version_id"))
        and d["current"] is True
        and d["extraction_status"] == "COMPLETED"
        and d["classification"] == "INTERNAL_OPERATIONAL"
    }


def validate_gold(data):
    if (
        data.get("schema_version") != 1
        or data.get("synthetic") is not True
        or data.get("kind") != "rc_semantic_measurement"
        or data.get("held_out") is not True
        or data.get("preparation_only") is not False
        or data.get("qualification_protocol", {}).get("status") != "FROZEN_FOR_MEASUREMENT"
    ):
        raise ValueError("frozen synthetic semantic gold required")
    documents = {d["id"]: d for d in data["documents"]}
    if len(documents) != len(data["documents"]):
        raise ValueError("duplicate source")
    for d in documents.values():
        for key in ("id", "tenant_id", "case_id", "version_id"):
            UUID(d[key])
        if d["text_sha256"] != sha256(d["text"].encode()).hexdigest():
            raise ValueError("source hash mismatch")
        if d["classification"] != "INTERNAL_OPERATIONAL":
            raise ValueError("synthetic internal gold required")
    eligible = eligible_documents(data)

    def region_valid(r):
        d = eligible.get(r["source_fragment_id"])
        start, end = r["start_byte"], r["end_byte"]
        return (
            d is not None
            and type(start) is int
            and type(end) is int
            and 0 <= start < end <= len(d["text"].encode())
            and d["text"].encode()[start:end] == r["excerpt"].encode()
            and r["source_sha256"] == d["text_sha256"]
        )

    facts = {f["id"]: f for f in data["source_facts"]}
    if len(facts) != len(data["source_facts"]) or not all(region_valid(f) for f in facts.values()):
        raise ValueError("invalid independent fact gold")
    queries = data["queries"]
    if not queries or len({q["id"] for q in queries}) != len(queries):
        raise ValueError("invalid query identities")
    for q in queries:
        if (
            q["runtime_expectations"] is not None
            or q["query_sha256"] != sha256(q["text"].encode()).hexdigest()
            or len(set(q["gold_sources"])) != len(q["gold_sources"])
            or not set(q["gold_sources"]) <= eligible.keys()
            or set(q["gold_sources"]) != {r["source_fragment_id"] for r in q["gold_regions"]}
            or not all(
                region_valid(r) and r["applicability"] == "UNKNOWN" for r in q["gold_regions"]
            )
            or set(q["fact_ids"])
            != {k for k, f in facts.items() if f["source_fragment_id"] in q["gold_sources"]}
        ):
            raise ValueError("invalid independent semantic query gold")
        if q["semantic_request"]["demand"] == "FINANCIAL" and q["gold_sources"]:
            raise ValueError("financial gold must remain non evaluable")
    protocol = data["qualification_protocol"]
    if (
        protocol["top_k"] != 10
        or protocol["report_at"] != [1, 5, 10]
        or not set(protocol["restricted_source_ids"]) <= eligible.keys()
    ):
        raise ValueError("invalid qualification budget or protection scope")


def fixture_source(data):
    chunks = [
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
    return SimpleNamespace(read_chunks=lambda **kwargs: tuple(chunks))


def score_semantics(data, states):
    eligible = eligible_documents(data)
    restricted = set(data["qualification_protocol"]["restricted_source_ids"])
    queries, runs, regions, parser, financial = [], {}, {}, {}, []
    safety = dict(
        unknown_answer=True,
        source_scope=True,
        financial_refusal=True,
        protected_unknown=True,
        anchor_integrity=True,
    )
    fact_coverage = {}
    for q in data["queries"]:
        state = states[q["id"]]
        found = state["regions"]
        projection = state.get("rc_projection") or {}
        evidence = [
            *projection.get("clauses", []),
            *projection.get("unknown_regions", []),
            *state.get("rc_unscoped_evidence", []),
            *state.get("visit_type_evidence", []),
        ]
        evidence.extend(
            side for link in projection.get("links", []) for side in (link["left"], link["right"])
        )
        referenced_ids = [
            *state.get("review_source_ids", []),
            *(trace["source_fragment_id"] for trace in state.get("score_trace", [])),
        ]
        safety["source_scope"] &= all(source_id in eligible for source_id in referenced_ids)
        safety["unknown_answer"] &= state["answer_state"] == "UNKNOWN"
        checked = [(r, True) for r in [*found, *evidence]]
        checked.extend((r, False) for r in state.get("score_trace", []))
        for r, metadata_required in checked:
            d = eligible.get(r["source_fragment_id"])
            safety["source_scope"] &= d is not None
            if d is None:
                continue
            for field, key in [
                ("tenant_id", "tenant_id"),
                ("case_id", "case_id"),
                ("dce_version_id", "version_id"),
            ]:
                if metadata_required:
                    safety["source_scope"] &= r.get(field) == d[key]
            start, end = r.get("start_byte"), r.get("end_byte")
            valid = (
                type(start) is int
                and type(end) is int
                and 0 <= start < end <= len(d["text"].encode())
                and r.get("source_sha256") == d["text_sha256"]
            )
            safety["anchor_integrity"] &= valid
            if valid and (r in found or not metadata_required):
                safety["anchor_integrity"] &= (
                    r.get("segment_sha256") == sha256(d["text"].encode()[start:end]).hexdigest()
                )
            for a in [*r.get("directive_anchors", []), *r.get("condition_signals", [])]:
                a_start, a_end = a["start_byte"], a["end_byte"]
                safety["anchor_integrity"] &= (
                    valid
                    and type(a_start) is int
                    and type(a_end) is int
                    and start <= a_start < a_end <= end
                    and d["text"].encode()[a_start:a_end] == a["excerpt"].encode()
                )
            if "excerpt" in r and valid:
                safety["anchor_integrity"] &= d["text"].encode()[start:end] == r["excerpt"].encode()
        for e in evidence:
            if e["source_fragment_id"] in restricted:
                safety["protected_unknown"] &= e.get("value") == e.get("kind") == "UNKNOWN"
        qi = state.get("query_intent") or {}
        for a in qi.get("anchors", []):
            start, end = a["start_byte"], a["end_byte"]
            safety["anchor_integrity"] &= (
                type(start) is int
                and type(end) is int
                and 0 <= start < end <= len(q["text"].encode())
                and q["text"].encode()[start:end] == a["excerpt"].encode()
            )
        if qi:
            safety["anchor_integrity"] &= qi.get("query_sha256") == q["query_sha256"]
        if q["semantic_request"]["demand"] == "FINANCIAL":
            financial.append(q["id"])
            safety["financial_refusal"] &= (
                state["reason"] == "FINANCIAL_SCOPE_REFUSED"
                and not found
                and not evidence
                and not qi
                and not state.get("score_trace")
                and not state.get("review_source_ids")
            )
            continue
        queries.append(
            dict(
                id=q["id"],
                expected=q["gold_sources"],
                expected_regions=q["gold_regions"],
                critical=True,
            )
        )
        runs[q["id"]] = [r["source_fragment_id"] for r in found]
        regions[q["id"]] = found
        want = q["semantic_request"]
        comparable = want["subject"] != "MULTIPLE" and want["demand"] in {
            "OBLIGATION",
            "DATE_TIME",
            "LOCATION",
        }
        parser[q["id"]] = dict(
            observed=qi,
            observed_legacy=state.get("specific_intent"),
            semantic_request=want,
            closed_comparable=comparable,
            semantic_match=(
                qi.get("subject") == want["subject"]
                and qi.get("demand") == want["demand"]
                and (qi.get("scope") or {}).get("lot") == want["lot"]
            )
            if comparable
            else None,
            closed_covered=qi.get("coverage") == "COVERED",
        )
        fact_coverage[q["id"]] = {
            f["id"]: region_is_covered(f, found)
            for f in data["source_facts"]
            if f["id"] in q["fact_ids"]
        }
    return dict(
        documentary=score_queries(queries, runs, retrieved_regions=regions),
        parser=parser,
        safety=safety,
        financial_non_evaluable=financial,
        fact_source_coverage=fact_coverage,
        structured_fact_extraction="NOT_EVALUATED",
    )


def run_trial(data, profile, source, encoder):
    validate_gold(data)
    counts = dict(query=0, passage_batches=0, passages=0, source_reads=0)

    class Probe:
        profile_id = encoder.profile_id

        def encode_query(self, text):
            counts["query"] += 1
            return encoder.encode_query(text)

        def encode_passages(self, texts):
            counts["passage_batches"] += 1
            counts["passages"] += len(texts)
            return encoder.encode_passages(texts)

    def read_chunks(**kwargs):
        counts["source_reads"] += 1
        return source.read_chunks(**kwargs)

    service = CandidateRetrievalService(
        profile=profile, source=SimpleNamespace(read_chunks=read_chunks), encoder=Probe()
    )
    scope = RetrievalScope(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )
    states: dict[str, dict] = {}
    cold: list[float] = []
    warm: list[float] = []
    for repetition in range(4):
        for q in data["queries"]:
            start = time.perf_counter()
            try:
                reading = service.retrieve(query=q["text"], scope=scope, top_k=10)
                state = json.loads(json.dumps(asdict(reading), default=str))
                state.pop("hits")
                state["regions"] = [
                    dict(
                        source_fragment_id=str(h.result.chunk.source_fragment_id),
                        tenant_id=str(h.result.chunk.tenant_id),
                        case_id=str(h.result.chunk.case_id),
                        dce_version_id=str(h.result.chunk.dce_version_id),
                        start_byte=h.start_byte,
                        end_byte=h.end_byte,
                        source_sha256=h.source_sha256,
                        segment_sha256=h.segment_sha256,
                        locator=h.result.chunk.locator,
                        score=h.result.score,
                    )
                    for h in reading.hits
                ]
            except FinancialRetrievalQueryRejected:
                state = dict(answer_state="UNKNOWN", reason="FINANCIAL_SCOPE_REFUSED", regions=[])
            (cold if repetition == 0 else warm).append((time.perf_counter() - start) * 1000)
            if repetition and states[q["id"]] != state:
                raise ValueError("candidate retry changed state")
            states[q["id"]] = state
    p95 = sorted(warm)[max(0, ceil(len(warm) * 0.95) - 1)]
    return dict(
        status="MEASURED",
        synthetic_only=True,
        admitted=False,
        production_engine_changed=False,
        profile=asdict(profile),
        profile_id=profile.profile_id,
        states=states,
        scores=score_semantics(data, states),
        encoder_calls=counts,
        first_query_ms=cold[0],
        warm_query_p95_ms=p95,
        interactive_latency=p95 <= data["qualification_protocol"]["latency_budget_ms"],
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture", "profile", "model-dir", "runtime-manifest", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sql", action="store_true")
    args = parser.parse_args(argv)
    data = json.loads(args.fixture.read_text())
    validate_gold(data)
    profile_bytes = args.profile.read_bytes()
    canonical = Path(__file__).resolve().parents[1] / "ops/retrieval-candidate/profile-v10.json"
    if (
        sha256(profile_bytes).hexdigest() != sha256(canonical.read_bytes()).hexdigest()
        or data["qualification_protocol"].get("profile_sha256") != sha256(profile_bytes).hexdigest()
    ):
        raise ValueError("exact frozen v10 profile required")
    profile = CandidateRetrievalProfile(**json.loads(profile_bytes))
    if profile.review_policy != "rc-conditional-v10":
        raise ValueError("unchanged v10 candidate required")
    engine = None
    try:
        source = fixture_source(data)
        if args.sql:
            import sqlalchemy as sa
            from qualify_candidate_sql import SqlAlchemyDceRetrievalSource, seed_fixture
            from sqlalchemy.orm import sessionmaker

            url = sa.engine.make_url(os.environ.get("SMART_AO_TEST_DATABASE_URL", ""))
            if (
                os.environ.get("SMART_AO_TEST_DISPOSABLE_DATABASE") != "1"
                or url.database != "smartao_e5_sql"
                or url.host is not None
                or url.drivername != "postgresql+psycopg"
                or url.username != "proof"
                or url.port is not None
                or dict(url.query) != {"host": "/socket"}
                or any(k in os.environ for k in ("PGHOSTADDR", "PGSERVICE", "PGSERVICEFILE"))
            ):
                raise ValueError("dedicated disposable Unix socket database required")
            engine = sa.create_engine(url)
            factory = sessionmaker(bind=engine, expire_on_commit=False)
            seed_fixture(data, factory)
            source = SqlAlchemyDceRetrievalSource(session_factory=factory)
        encoder = CpuCandidateEncoder(
            profile=profile, model_dir=args.model_dir, runtime_manifest=args.runtime_manifest
        )
        report = run_trial(data, profile, source, encoder)
        report["fixture_sha256"] = sha256(args.fixture.read_bytes()).hexdigest()
        report["transport"] = "SQL" if args.sql else "MEMORY"
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    finally:
        if engine is not None:
            engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
