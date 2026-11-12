#!/usr/bin/env python3
"""Measure exact source support in the native RC register, never semantic completeness."""

import argparse
import json
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path


def normalized(text):
    text = unicodedata.normalize("NFKC", text).replace("’", "'")
    return re.sub(r"\s+", "", text).casefold()


def measure(ledger, reference, projection_dir):
    projection_dir = Path(projection_dir)
    points = []
    cache = {}
    for point in reference["points"]:
        rows = [
            row
            for row in ledger["ledger"]
            if row["case_alias"] == point["case_alias"]
            and row["content_sha256"] == point["source_sha256"]
        ]
        result = {
            **point,
            "source_text_found": False,
            "status": "SOURCE_NOT_IN_INVENTORY",
            "normalized_value_accuracy": "NOT_MEASURED",
            "matched_requirement_kinds": [],
            "version_hashes": sorted({row["root_version"] for row in rows}),
        }
        if not rows:
            points.append(result)
            continue
        projection = None
        for row in rows:
            artifact = row.get("projection_file")
            if artifact:
                if Path(artifact).name != artifact or (projection_dir / artifact).is_symlink():
                    raise ValueError("INVALID_PROJECTION_PATH")
                if artifact not in cache:
                    cache[artifact] = json.loads((projection_dir / artifact).read_text())
                projection = cache[artifact]
                break
        if projection is not None and projection.get("source_sha256") != point["source_sha256"]:
            result["status"] = "SOURCE_NOT_ELIGIBLE"
            result["diagnostic"] = "PROJECTION_SOURCE_HASH_MISMATCH"
            points.append(result)
            continue
        if projection is None:
            result["status"] = "SOURCE_NOT_ELIGIBLE"
            points.append(result)
            continue
        page_fragments = [
            f for f in projection["fragments"] if f["locator_json"].get("page") == point["page"]
        ]
        evidence = normalized(point["evidence"])
        result["source_text_found"] = bool(evidence) and evidence in normalized(
            " ".join(f["text"] for f in page_fragments)
        )
        if projection["status"] != "COMPLETED" or not any(
            row["status"] == "COMPLETED" for row in rows
        ):
            result["status"] = "SOURCE_NOT_ELIGIBLE"
        elif not result["source_text_found"]:
            result["status"] = "SOURCE_TEXT_NOT_FOUND"
        elif not point["expected_requirement_kinds"]:
            result["status"] = "NO_TARGET_RULE_IN_RC_REGISTER"
        else:
            analysis = projection.get("analysis") or {}
            ordinals = {
                s["fragment_id"]: s["ordinal"] for s in analysis.get("source_fragments", [])
            }
            page_ordinals = {f["ordinal"] for f in page_fragments}
            supported = [
                o["requirement_kind"]
                for o in analysis.get("observations", [])
                if o["requirement_kind"] in point["expected_requirement_kinds"]
                and ordinals.get(o["fragment_id"]) in page_ordinals
                and evidence in normalized(o["excerpt"])
            ]
            result["matched_requirement_kinds"] = sorted(set(supported))
            result["status"] = "SIGNAL_SUPPORTED" if supported else "CONFIRMED_SIGNAL_OMISSION"
        points.append(result)
    return {
        "schema_version": 1,
        "scope": (
            "native extraction/classification/RC lexical register; "
            "technical reference, not Golden DCE"
        ),
        "points": points,
        "counts": dict(Counter(p["status"] for p in points)),
        "source_text_comparison": (
            "NFKC/casefold/apostrophes; layout whitespace ignored; digits and punctuation retained"
        ),
        "normalized_value_accuracy": "NOT_MEASURED",
        "whole_dce_analysis_claim": False,
        "human_validation": "NOT_PERFORMED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--output-file", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_file.absolute()
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("OUTPUT_SYMLINK")
    if any(
        (p / ".git").is_file() or (p / ".git" / "HEAD").is_file()
        for p in (output.parent, *output.parent.parents)
    ):
        raise ValueError("OUTPUT_INSIDE_GIT")
    if output in {args.ledger.absolute(), args.reference.absolute()}:
        raise ValueError("OUTPUT_INPUT_OVERLAP")
    value = measure(
        json.loads(args.ledger.read_text()),
        json.loads(args.reference.read_text()),
        args.ledger.parent,
    )
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(output.parent, 0o700)
    with os.fdopen(
        os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), "w"
    ) as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
