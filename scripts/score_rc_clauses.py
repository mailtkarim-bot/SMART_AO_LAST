"""Score frozen synthetic RC clause annotations against an unchanged candidate report."""

from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path
from typing import Any


def _key(e):
    return (e["source_fragment_id"], e["start_byte"], e["end_byte"], e["subject"], e["lot"])


def _anchor(e, documents, label):
    source = documents.get(e["source_fragment_id"])
    if source is None:
        raise ValueError(label + " anchor source missing")
    raw = source["text"].encode()
    start, end = e["start_byte"], e["end_byte"]
    if (
        not isinstance(start, int)
        or isinstance(start, bool)
        or not isinstance(end, int)
        or isinstance(end, bool)
        or not 0 <= start < end <= len(raw)
        or raw[start:end].decode() != e["excerpt"]
    ):
        raise ValueError(label + " anchor mismatch")
    if label == "actual" and (
        not e.get("source_sha256")
        or source.get("version_id") is not None
        and e.get("dce_version_id") != source["version_id"]
        or source.get("page") is not None
        and (not isinstance(e.get("locator"), dict) or e["locator"].get("page") != source["page"])
    ):
        raise ValueError("actual anchor metadata mismatch")
    if e.get("source_sha256", sha256(raw).hexdigest()) != sha256(raw).hexdigest():
        raise ValueError(label + " anchor source hash mismatch")


def score_clauses(data, report, fixture_sha256):
    if report.get("fixture_sha256") != fixture_sha256:
        raise ValueError("fixture identity mismatch")
    if (
        data.get("synthetic") is not True
        or data.get("held_out") is not True
        or report.get("synthetic_only") is not True
        or report.get("held_out") is not True
        or report.get("admitted") is not False
    ):
        raise ValueError("only non-admitted synthetic held-out reports")
    documents = {d["id"]: d for d in data["documents"]}
    inventory = {e["id"]: e for e in data["clause_inventory"]}
    if len(inventory) != len(data["clause_inventory"]) or len(inventory) > 512:
        raise ValueError("invalid clause inventory")
    for e in inventory.values():
        _anchor(e, documents, "gold")
    rows = []
    for q in data["queries"]:
        if q.get("expected_refusal"):
            rows.append(
                dict(
                    query_id=q["id"],
                    family=q["family"],
                    non_evaluable=True,
                    excluded_clause_ids=q["expected_clause_ids"],
                )
            )
            continue
        expected = {_key(inventory[i]): inventory[i] for i in q["expected_clause_ids"]}
        if len(expected) != len(q["expected_clause_ids"]):
            raise ValueError("duplicate expected clause identity")
        state = report["states"][q["id"]]
        projection = state.get("rc_projection", {})
        projected = projection.get("clauses", []) + projection.get("unknown_regions", [])
        context = state.get("rc_unscoped_evidence", [])
        evidence: dict[tuple[str, int, int, str, int | None], dict[str, Any]] = {}
        for e in projected + context:
            _anchor(e, documents, "actual")
            key = _key(e)
            if key in evidence and any(
                evidence[key].get(k) != e.get(k) for k in ("value", "kind", "directive_signal")
            ):
                raise ValueError("discordant repeated evidence")
            evidence[key] = e
        candidates = {k: e for k, e in evidence.items() if e.get("directive_signal") == "CANDIDATE"}
        projected_candidates = {
            _key(e): e for e in projected if e.get("directive_signal") == "CANDIDATE"
        }
        missing = [e["id"] for k, e in expected.items() if k not in candidates]
        unresolved = sum(
            candidates[k]["value"] == "UNKNOWN" and e["value"] != "UNKNOWN"
            for k, e in expected.items()
            if k in candidates
        )
        wrong = sum(
            e["value"] != "UNKNOWN" and e["value"] != expected[k]["value"]
            for k, e in projected_candidates.items()
            if k in expected
        )
        wrong_kinds = sum(
            e["value"] != "UNKNOWN" and e["kind"] != expected[k]["kind"]
            for k, e in projected_candidates.items()
            if k in expected
        )
        over = sum(
            e["value"] != "UNKNOWN" and expected[k]["value"] == "UNKNOWN"
            for k, e in projected_candidates.items()
            if k in expected
        )
        extra = set(projected_candidates) - set(expected)
        rows.append(
            dict(
                query_id=q["id"],
                family=q["family"],
                non_evaluable=False,
                expected_clauses=len(expected),
                detected_relevant=len(expected) - len(missing),
                missing_clause_ids=missing,
                projected_candidates=len(projected_candidates),
                projected_relevant=len(set(projected_candidates) & set(expected)),
                wrong_known_kinds=wrong_kinds,
                extra_projected_candidates=len(extra),
                wrong_known_values=wrong,
                overcertainty=over,
                unresolved_relevant=unresolved,
                irrelevant_context_clauses=sum(
                    _key(e) not in expected and e["subject"] != "UNKNOWN" for e in context
                ),
                unresolved_regions=sum(
                    e["subject"] == "UNKNOWN" or e.get("directive_signal") != "CANDIDATE"
                    for e in projected
                ),
                known_extra_assertions=sum(
                    projected_candidates[k]["value"] != "UNKNOWN" for k in extra
                ),
            )
        )
    families: dict[str, dict[str, int]] = {}
    counters = (
        "expected_clauses",
        "detected_relevant",
        "projected_candidates",
        "projected_relevant",
        "wrong_known_kinds",
        "extra_projected_candidates",
        "wrong_known_values",
        "overcertainty",
        "unresolved_relevant",
        "irrelevant_context_clauses",
        "unresolved_regions",
        "known_extra_assertions",
    )
    for row in rows:
        family = families.setdefault(
            row["family"], dict(queries=0, non_evaluable=0, **{k: 0 for k in counters})
        )
        family["queries"] += 1
        if row["non_evaluable"]:
            family["non_evaluable"] += 1
        else:
            for k in counters:
                family[k] += row[k]
    totals = {k: sum(f[k] for f in families.values()) for k in counters}
    return dict(
        synthetic_only=True,
        admitted=False,
        fixture_sha256=fixture_sha256,
        profile_id=report.get("profile_id"),
        queries=rows,
        families=families,
        totals=totals,
        candidate_clause_recall=(
            totals["detected_relevant"] / totals["expected_clauses"]
            if totals["expected_clauses"]
            else None
        ),
        limits=[
            "Context outside projection is not an asserted answer.",
            "UNKNOWN remains unresolved, not a false known value.",
            "This scorer never calls or tunes the candidate.",
        ],
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture", "report", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    raw = args.fixture.read_bytes()
    data = json.loads(raw)
    report = json.loads(args.report.read_text())
    result = score_clauses(data, report, sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
