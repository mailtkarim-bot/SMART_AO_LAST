"""Frozen synthetic intent-only measurement; no retrieval or model activation."""

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
from app.modules.knowledge.application.rc_actor_intent_v4 import recognize_rc_intent  # noqa: E402


def evaluate(cases):
    if not cases or len({c["id"] for c in cases}) != len(cases):
        raise ValueError("unique nonempty intent cases required")
    rows = []
    warm = []
    for c in cases:
        q, want = c["text"], c["expected"]
        if not isinstance(q, str) or not q.strip() or type(want["covered"]) is not bool:
            raise ValueError("invalid synthetic case")
        if (
            want["covered"]
            and not {
                "covered",
                "subject",
                "lot",
                "actor",
                "object",
                "request",
                "action",
                "contexts",
            }
            <= want.keys()
        ):
            raise ValueError("all positive components required")
        raw = q.encode()
        if c.get("query_sha256", sha256(raw).hexdigest()) != sha256(raw).hexdigest():
            raise ValueError("query hash mismatch")
        outputs, elapsed = [], []
        for _ in range(4):
            start = time.perf_counter()
            outputs.append(recognize_rc_intent(q))
            elapsed.append((time.perf_counter() - start) * 1000)
        if any(r != outputs[0] for r in outputs):
            raise ValueError("unstable recognition")
        warm.extend(elapsed[1:])
        r = outputs[0]
        intent = r.intent
        covered = bool(intent and intent.coverage == "COVERED")
        anchors = [] if intent is None else list(intent.anchors)
        anchors.extend(
            a
            for a in (r.actor, r.object_evidence, r.action_evidence, r.attachment_evidence)
            if a is not None
        )
        anchors.extend(b.context for b in r.contexts)
        anchors.extend(b.owner for b in r.contexts if b.owner is not None)
        integrity = all(
            type(a.start_byte) is int
            and type(a.end_byte) is int
            and 0 <= a.start_byte < a.end_byte <= len(raw)
            and raw[a.start_byte : a.end_byte] == a.excerpt.encode()
            for a in anchors
        )
        integrity &= intent is None or intent.query_sha256 == sha256(raw).hexdigest()
        actual = dict(
            covered=covered,
            subject=intent.subject if intent else None,
            lot=intent.scope.lot if intent else None,
            actor=r.actor.excerpt if r.actor else None,
            object=r.object_evidence.excerpt if r.object_evidence else None,
            action=r.action_evidence.excerpt if r.action_evidence else None,
            request=next((a.excerpt for a in intent.anchors if a.signal == "DEMAND"), None)
            if intent
            else None,
            contexts=[
                dict(excerpt=b.context.excerpt, owner=b.owner.excerpt if b.owner else None)
                for b in r.contexts
            ],
        )
        components = {k: actual.get(k) == v for k, v in want.items() if k != "financial"}
        if want.get("covered") and covered:
            assert intent is not None
            components["demand"] = intent.demand == "OBLIGATION"
            components["scope"] = intent.scope.state == (
                "UNKNOWN" if want["lot"] is None else "CANDIDATE"
            )
        if want.get("financial"):
            components["financial"] = (
                intent is None and r.reason == "FINANCIAL_SCOPE_REFUSED" and not anchors
            )
        exact = all(components.values()) and integrity
        rows.append(
            dict(
                id=c["id"],
                expected_positive=want["covered"],
                covered=covered,
                actual=actual,
                components=components,
                exact=exact,
                anchor_integrity=integrity,
                reading=asdict(r),
                initial_ms=elapsed[0],
                warm_ms=elapsed[1:],
            )
        )
    return dict(
        synthetic_only=True,
        admitted=False,
        production_engine_changed=False,
        mechanism="rc-actor-intent-v4",
        source_reads=0,
        encoder_calls=0,
        case_count=len(rows),
        positive_count=sum(r["expected_positive"] for r in rows),
        positive_exact=sum(r["expected_positive"] and r["exact"] for r in rows),
        exact_count=sum(r["exact"] for r in rows),
        promotions=sum(r["covered"] and not r["expected_positive"] for r in rows),
        invalid_anchors=sum(not r["anchor_integrity"] for r in rows),
        warm_p95_ms=sorted(warm)[math.ceil(0.95 * len(warm)) - 1],
        rows=rows,
    )


def verify_freeze(manifest, root):
    required = {
        "backend/app/modules/knowledge/application/rc_actor_intent_v4.py",
        "scripts/qualify_rc_actor_intent_v4.py",
        "backend/tests/application/test_rc_actor_intent_v4.py",
        "backend/tests/ops/test_rc_actor_intent_v4_qualification.py",
    }
    if not required <= set(manifest["files"]):
        raise ValueError("essential frozen candidate inputs missing")
    for name, digest in manifest["files"].items():
        if sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError("frozen input mismatch: " + name)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("fixture", "freeze-manifest", "output"):
        p.add_argument("--" + name, type=Path, required=True)
    args = p.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(args.freeze_manifest.read_text())
    verify_freeze(manifest, root)
    fixture_key = str(args.fixture.resolve().relative_to(root))
    if fixture_key not in manifest["files"]:
        raise ValueError("sealed fixture absent from measurement freeze")
    data = json.loads(args.fixture.read_text())
    if data.get("synthetic") is not True or data.get("held_out") is not True:
        raise ValueError("frozen synthetic held-out fixture required")
    report = evaluate(data["cases"])
    verify_freeze(manifest, root)
    report["fixture_sha256"] = sha256(args.fixture.read_bytes()).hexdigest()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
