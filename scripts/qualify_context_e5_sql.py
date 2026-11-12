"""Offline measurement of the frozen context adapter; never activates a retrieval engine."""

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
from app.modules.knowledge.application.context_candidate_retrieval import (  # noqa: E402
    ContextCandidateRetrieval,
)
from app.modules.knowledge.application.retrieval import (
    FinancialRetrievalQueryRejected,  # noqa: E402
)
from qualify_btp_retrieval import region_is_covered  # noqa: E402
from qualify_candidate_sql import (  # noqa: E402
    CandidateRetrievalProfile,
    CpuCandidateEncoder,
    RetrievalScope,
    SqlAlchemyDceRetrievalSource,
    seed_fixture,
)
from qualify_rc_semantic import fixture_source, score_semantics, validate_gold  # noqa: E402
from score_rc_clauses import _anchor  # noqa: E402


def disposable_url():
    import sqlalchemy as sa

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
    return url


def clause_metrics(data, states):
    documents = {d["id"]: d for d in data["documents"]}
    inventory = {c["id"]: c for c in data["clause_inventory"]}
    rows, missing = [], []
    actual_count = 0
    extras: list[dict] = []
    for q in data["queries"]:
        if q.get("expected_refusal"):
            continue
        state = states[q["id"]]
        projection = state.get("rc_projection") or {}
        actual = projection.get("clauses", []) + projection.get("unknown_regions", [])
        actual_count += len(actual)
        for a in actual:
            _anchor(a, documents, "actual")
        expected = [inventory[i] for i in q["expected_clause_ids"]]
        matched: set[int] = set()
        for c in expected:
            _anchor(c, documents, "gold")
            exact = [
                (i, a)
                for i, a in enumerate(actual)
                if all(
                    a.get(k) == c.get(k)
                    for k in ("source_fragment_id", "start_byte", "end_byte", "subject", "lot")
                )
            ]
            matched.update(i for i, _ in exact)
            conditions = c.get("context_regions", [])
            for region in conditions:
                _anchor(region, documents, "gold")

            def linked_context(a):
                return [
                    a,
                    *(
                        dict(anchor, source_fragment_id=a["source_fragment_id"])
                        for anchor in [
                            *a.get("condition_signals", []),
                            *a.get("directive_anchors", []),
                        ]
                    ),
                ]

            conditions_preserved = (
                any(
                    all(region_is_covered(r, linked_context(a)) for r in conditions)
                    for _, a in exact
                )
                if conditions
                else True
            )
            good = any(
                a.get("value") == c.get("value") and a.get("kind") == c.get("kind")
                for _, a in exact
            )
            rows.append(
                dict(
                    query=q["id"],
                    clause=c["id"],
                    source_covered=region_is_covered(c, state["regions"][:5]),
                    source_covered_at_10=region_is_covered(c, state["regions"]),
                    conditions_preserved=conditions_preserved,
                    family=q["family"],
                    projected_exact=bool(exact),
                    value_kind_exact=good,
                    fully_proven=good and conditions_preserved,
                )
            )
            if not exact:
                missing.append(q["id"] + ":" + c["id"])
        extras.extend(
            dict(query=q["id"], evidence=a) for i, a in enumerate(actual) if i not in matched
        )
    n = len(rows)
    projected = sum(r["value_kind_exact"] for r in rows)
    strata = {}
    for family in sorted({r["family"] for r in rows}):
        subset = [r for r in rows if r["family"] == family]
        strata[family] = dict(
            expected=len(subset),
            source_at_5=sum(r["source_covered"] for r in subset),
            source_at_10=sum(r["source_covered_at_10"] for r in subset),
            correct_projection=sum(r["value_kind_exact"] for r in subset),
        )
    return dict(
        strata=strata,
        rows=rows,
        missing_projection=missing,
        extra_projection=extras,
        source_recall=sum(r["source_covered"] for r in rows) / n if n else None,
        projected_recall=projected / n if n else None,
        fully_proven_recall=sum(r["fully_proven"] for r in rows) / n if n else None,
        missing_source_context=[
            r["query"] + ":" + r["clause"]
            for r in rows
            if r["projected_exact"] and not r["conditions_preserved"]
        ],
        projected_precision=projected / actual_count if actual_count else None,
        value_kind_exact=sum(r["value_kind_exact"] for r in rows),
        expected=n,
    )


def run_trial(data, profile, source, encoder):
    validate_gold(data)
    counts = dict(query=0, passages=0, source_reads=0)
    encoded_queries = []

    class Probe:
        profile_id = encoder.profile_id

        def encode_query(self, text):
            counts["query"] += 1
            encoded_queries.append(text)
            return encoder.encode_query(text)

        def encode_passages(self, texts):
            counts["passages"] += len(texts)
            return encoder.encode_passages(texts)

    def read(**kw):
        counts["source_reads"] += 1
        return source.read_chunks(**kw)

    adapter = ContextCandidateRetrieval(
        transport_profile=profile, source=SimpleNamespace(read_chunks=read), encoder=Probe()
    )
    scope = RetrievalScope(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )
    states: dict[str, dict] = {}
    recognitions = {}
    cold: list[float] = []
    warm: list[float] = []
    fidelity = dict(raw_query=True, anchors=True, query_hash=True, contexts_exact=True)
    for repetition in range(4):
        for q in data["queries"]:
            start = time.perf_counter()
            before = len(encoded_queries)
            try:
                result = adapter.retrieve(query=q["text"], scope=scope, top_k=10)
                reading = result.reading
                recognition = json.loads(json.dumps(asdict(result.recognition), default=str))
                recognitions[q["id"]] = recognition
                raw = q["text"].encode()
                intent = recognition.get("intent") or {}
                fidelity["query_hash"] &= intent.get("query_sha256") == sha256(raw).hexdigest()
                anchors = list(recognition.get("context_evidence", []))
                anchors += intent.get("evidence", [])
                anchors += intent.get("anchors", [])
                lot = intent.get("scope") or {}
                if lot.get("state") == "CANDIDATE":
                    fidelity["anchors"] &= 0 <= lot["start_byte"] < lot["end_byte"] <= len(raw)
                for a in anchors:
                    fidelity["anchors"] &= (
                        raw[a["start_byte"] : a["end_byte"]] == a["excerpt"].encode()
                    )
                fidelity["contexts_exact"] &= [
                    a["excerpt"] for a in recognition.get("context_evidence", [])
                ] == q["expected_contexts"]
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
            fidelity["raw_query"] &= all(t == q["text"] for t in encoded_queries[before:])
            (cold if repetition == 0 else warm).append((time.perf_counter() - start) * 1000)
            if repetition and states[q["id"]] != state:
                raise ValueError("candidate retry changed state")
            states[q["id"]] = state
    before_control = dict(counts)
    control_query = data["qualification_protocol"].get("control_query")
    control = None
    if control_query:
        c = adapter.retrieve(query=control_query, scope=scope, top_k=10)
        control = dict(
            not_scored=True,
            query=control_query,
            state=c.reading.state,
            reason=c.reading.reason,
            hits=len(c.reading.hits),
            encoder_calls={k: counts[k] - before_control[k] for k in counts},
        )
    return dict(
        control=control,
        synthetic_only=True,
        held_out=True,
        admitted=False,
        production_engine_changed=False,
        profile_id=profile.profile_id,
        adapter_id=adapter.adapter_id,
        states=states,
        recognitions=recognitions,
        scores=score_semantics(data, states),
        clauses=clause_metrics(data, states),
        fidelity=fidelity,
        refusal_checks={
            q["id"]: dict(
                unknown=states[q["id"]]["answer_state"] == "UNKNOWN",
                no_hits=not states[q["id"]]["regions"],
            )
            for q in data["queries"]
            if q.get("answerability") in {"NO_EVIDENCE", "FINANCIAL_REFUSAL"}
        },
        ambiguous_report_unknown={
            q["id"]: states[q["id"]]["answer_state"] == "UNKNOWN"
            and not any(
                e.get("value") != "UNKNOWN"
                and e.get("source_fragment_id")
                in data["qualification_protocol"].get("ambiguous_report_source_ids", [])
                for e in (states[q["id"]].get("rc_projection") or {}).get("clauses", [])
            )
            for q in data["queries"]
            if q.get("answerability") == "PARTIAL_REPORT_UNKNOWN"
        },
        encoder_calls=before_control,
        first_query_ms=cold[0],
        warm_query_p95_ms=sorted(warm)[ceil(0.95 * len(warm)) - 1],
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )


def sql_runtime(data, factory, profile, encoder):
    from dataclasses import replace
    from datetime import timedelta
    from uuid import uuid5

    import sqlalchemy as sa
    from qualify_candidate_sql import (
        NOW,
        DceDocumentExtractionFragmentRecord,
        DceDocumentExtractionRecord,
    )

    source = SqlAlchemyDceRetrievalSource(session_factory=factory)
    scope = RetrievalScope(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )
    with factory() as session:
        manifest = {
            str(r.id): dict(text_sha256=r.text_sha256, text=r.text, locator=r.locator_json)
            for r in session.scalars(sa.select(DceDocumentExtractionFragmentRecord))
        }
    for d in data["documents"]:
        row = manifest[d["id"]]
        if (
            row["text"] != d["text"]
            or row["text_sha256"] != d["text_sha256"]
            or row["locator"]["page"] != d["page"]
        ):
            raise ValueError("SQL fragment fidelity mismatch")

    class Probe:
        profile_id = encoder.profile_id
        after_query = staticmethod(lambda: None)

        def encode_query(self, text):
            value = encoder.encode_query(text)
            self.after_query()
            return value

        def encode_passages(self, texts):
            return encoder.encode_passages(texts)

    probe = Probe()
    adapter = ContextCandidateRetrieval(transport_profile=profile, source=source, encoder=probe)
    query = data["qualification_protocol"]["control_query"]

    def no_source_proofs(reading):
        return (
            not reading.hits
            and not reading.score_trace
            and not reading.review_source_ids
            and not reading.visit_type_evidence
            and not reading.rc_unscoped_evidence
            and not reading.rc_projection.clauses
            and not reading.rc_projection.links
            and not reading.rc_projection.unknown_regions
            and reading.answer_state == "UNKNOWN"
        )

    foreign = adapter.retrieve(query=query, scope=replace(scope, tenant_id=UUID(int=987654)))
    other_case = adapter.retrieve(query=query, scope=replace(scope, case_id=UUID(int=987655)))
    d = next(d for d in data["documents"] if d["page"] == 15)
    fragment = UUID(d["id"])

    def invalidate():
        with factory.begin() as session:
            session.add(
                DceDocumentExtractionRecord(
                    id=uuid5(fragment, "context-refusal"),
                    tenant_id=scope.tenant_id,
                    dce_version_id=scope.dce_version_id,
                    dce_document_id=uuid5(fragment, "document"),
                    input_sha256=d["text_sha256"],
                    extractor_id="context-proof",
                    extractor_version="1",
                    status="REVIEW_REQUIRED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC_INCOMPLETE",
                    created_at=NOW + timedelta(seconds=1),
                )
            )

    probe.after_query = invalidate
    changed = adapter.retrieve(query=query, scope=scope)
    probe.after_query = lambda: None
    later = source.read_chunks(
        tenant_id=scope.tenant_id, case_id=scope.case_id, dce_version_id=scope.dce_version_id
    )
    with factory() as session:
        historical = session.get(DceDocumentExtractionFragmentRecord, fragment) is not None
    return dict(
        fragment_manifest=manifest,
        checks=dict(
            fragment_fidelity=True,
            foreign_tenant=no_source_proofs(foreign.reading),
            foreign_affaire=no_source_proofs(other_case.reading),
            invalidation=changed.reading.reason == "SOURCE_CHANGED"
            and no_source_proofs(changed.reading),
            invalidated_fragment_absent=all(c.source_fragment_id != fragment for c in later),
            history_preserved=historical,
        ),
    )


def verify_freeze(path, root):
    data = json.loads(path.read_text())
    for name, digest in data.items():
        p = root / name
        if sha256(p.read_bytes()).hexdigest() != digest:
            raise ValueError("frozen measurement input changed: " + name)
    return data


REQUIRED_FILES = (
    "scripts/qualify_context_e5_sql.py",
    "scripts/qualify_candidate_sql.py",
    "scripts/qualify_rc_semantic.py",
    "scripts/qualify_candidate_retrieval.py",
    "scripts/qualify_btp_retrieval.py",
    "scripts/score_rc_clauses.py",
    "backend/app/modules/knowledge/application/context_candidate_retrieval.py",
    "backend/app/modules/knowledge/application/candidate_retrieval.py",
    "backend/app/modules/knowledge/application/rc_context_intent_v3.py",
    "backend/app/modules/knowledge/application/rc_compositional_intent_v2.py",
    "backend/app/modules/knowledge/application/rc_compositional_intent.py",
    "backend/app/modules/knowledge/application/rc_query_intent.py",
    "backend/app/modules/knowledge/application/rc_query_scope.py",
    "backend/app/modules/knowledge/application/rc_candidate_conflicts.py",
    "backend/app/modules/knowledge/application/retrieval.py",
    "backend/app/modules/knowledge/application/service.py",
    "backend/app/modules/knowledge/domain/embedding_profile.py",
    "backend/app/modules/knowledge/domain/retrieval.py",
    "backend/app/modules/knowledge/infrastructure/candidate_embeddings.py",
    "backend/app/modules/knowledge/infrastructure/dce_source.py",
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture", "profile", "model-dir", "runtime-manifest", "freeze", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--sql", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    freeze = verify_freeze(args.freeze, root)
    for p in (args.fixture, args.profile, Path(__file__)):
        if str(p.resolve().relative_to(root)) not in freeze:
            raise ValueError("measurement input absent from freeze")
    if not set(REQUIRED_FILES) <= freeze.keys():
        raise ValueError("measurement dependencies absent from freeze")
    data = json.loads(args.fixture.read_text())
    validate_gold(data)
    profile = CandidateRetrievalProfile(**json.loads(args.profile.read_text()))
    engine = None
    try:
        source = fixture_source(data)
        if args.sql:
            import sqlalchemy as sa
            from sqlalchemy.orm import sessionmaker

            engine = sa.create_engine(disposable_url())
            factory = sessionmaker(bind=engine, expire_on_commit=False)
            seed_fixture(data, factory)
            source = SqlAlchemyDceRetrievalSource(session_factory=factory)
        encoder = CpuCandidateEncoder(
            profile=profile, model_dir=args.model_dir, runtime_manifest=args.runtime_manifest
        )
        report = run_trial(data, profile, source, encoder)
        report["fixture_sha256"] = sha256(args.fixture.read_bytes()).hexdigest()
        report["transport"] = "SQL" if args.sql else "MEMORY"
        if args.sql:
            report["sql_runtime"] = sql_runtime(data, factory, profile, encoder)
        verify_freeze(args.freeze, root)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    finally:
        if engine is not None:
            engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
