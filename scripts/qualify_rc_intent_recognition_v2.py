"""Offline intent-only measurement; no source reader, encoder or business action."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.modules.knowledge.application.rc_compositional_intent_v2 import (
    recognize_rc_intent,  # noqa: E402
)


def evaluate(cases):
    rows = []
    for case in cases:
        readings = []
        timings = []
        for _ in range(4):
            start = time.perf_counter()
            readings.append(recognize_rc_intent(case["text"]))
            timings.append((time.perf_counter() - start) * 1000)
        if any(r != readings[0] for r in readings):
            raise ValueError("nondeterministic recognition")
        result = readings[0]
        intent = result.intent
        expected = case["expected_intent"]
        actual = (
            None
            if intent is None
            else dict(
                subject=intent.subject,
                demand=intent.demand,
                coverage=intent.coverage,
                scope_state=intent.scope.state,
                lot=intent.scope.lot,
            )
        )
        anchors = [] if intent is None else [asdict(a) for a in intent.anchors]
        integrity = (
            intent is None
            or intent.query_sha256 == sha256(case["text"].encode()).hexdigest()
            and all(
                case["text"].encode()[a["start_byte"] : a["end_byte"]] == a["excerpt"].encode()
                for a in anchors
            )
        )
        exact = (
            actual == expected
            and result.reason == case["expected_reason"]
            and anchors == case["expected_anchors"]
            and integrity
        )
        rows.append(
            dict(
                id=case["id"],
                actual_intent=actual,
                reason=result.reason,
                anchors=anchors,
                exact=exact,
                anchor_integrity=integrity,
                anchor_exact=anchors == case["expected_anchors"],
                expected_group="FINANCIAL" if expected is None else expected["coverage"],
                component_exact=actual == expected and result.reason == case["expected_reason"],
                expected_positive=bool(expected and expected["coverage"] == "COVERED"),
                covered=bool(intent and intent.coverage == "COVERED"),
                initial_ms=timings[0],
                warm_ms=timings[1:],
            )
        )
    warm = sorted(t for row in rows for t in row["warm_ms"])
    groups: dict[str, dict[str, int]] = {}
    for row in rows:
        group = groups.setdefault(row["expected_group"], dict(count=0, exact=0, promotions=0))
        group["count"] += 1
        group["exact"] += int(row["exact"])
        group["promotions"] += int(row["covered"] and not row["expected_positive"])
    return dict(
        groups=groups,
        recognizer_calls=4 * len(rows),
        gates=dict(
            no_promotions=all(not r["covered"] or r["expected_positive"] for r in rows),
            component_exact=all(r["component_exact"] for r in rows),
            anchors_exact=all(r["anchor_exact"] for r in rows),
            anchor_integrity=all(r["anchor_integrity"] for r in rows),
            all_positive_exact=all(r["exact"] for r in rows if r["expected_positive"]),
        ),
        mechanism="rc-compositional-v2",
        anchor_convention="lexical-cue-v2",
        synthetic_only=True,
        production_engine_changed=False,
        admitted=False,
        source_reads=0,
        encoder_calls=0,
        positive_count=sum(r["expected_positive"] for r in rows),
        positive_exact=sum(r["expected_positive"] and r["exact"] for r in rows),
        covered_count=sum(r["covered"] for r in rows),
        promotions=sum(r["covered"] and not r["expected_positive"] for r in rows),
        anchor_mismatches=sum(not r["anchor_exact"] for r in rows),
        invalid_anchors=sum(not r["anchor_integrity"] for r in rows),
        exact_count=sum(r["exact"] for r in rows),
        case_count=len(rows),
        warm_p95_ms=warm[math.ceil(0.95 * len(warm)) - 1] if warm else None,
        rows=rows,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-manifest", type=Path)
    args = parser.parse_args(argv)
    if ".sealed." in args.fixture.name:
        if args.freeze_manifest is None:
            raise ValueError("candidate freeze required before sealed measurement")
        manifest = json.loads(args.freeze_manifest.read_text())
        essential = {
            "backend/app/modules/knowledge/application/rc_compositional_intent_v2.py",
            "scripts/qualify_rc_intent_recognition_v2.py",
            "backend/tests/application/test_rc_compositional_intent_v2.py",
            "backend/tests/ops/test_rc_intent_recognition_qualification_v2.py",
        }
        if not essential <= set(manifest["files"]):
            raise ValueError("essential candidate files missing from freeze")
        root = Path(__file__).resolve().parents[1]
        for name, expected in manifest["files"].items():
            if sha256((root / name).read_bytes()).hexdigest() != expected:
                raise ValueError("candidate freeze mismatch")
        fixture_key = str(args.fixture.resolve().relative_to(root))
        if fixture_key not in manifest["files"]:
            raise ValueError("sealed fixture missing from freeze")
    data = json.loads(args.fixture.read_text())
    if data.get("synthetic") is not True or not isinstance(data.get("cases"), list):
        raise ValueError("synthetic intent-only cases required")
    if not data["cases"]:
        raise ValueError("nonempty measurement required")
    report = evaluate(data["cases"])
    report["fixture_sha256"] = sha256(args.fixture.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
