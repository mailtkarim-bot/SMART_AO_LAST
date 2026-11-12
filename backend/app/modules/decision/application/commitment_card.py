"""Decision view over native analysis facts, never a second ledger."""

from copy import deepcopy
from typing import Any


def project_commitment_points(summary):
    points: dict[str, Any] = {}
    for axis in summary["axes"]:
        for item in axis["items"]:
            key = f"{item['kind']}:{item['item_id']}"
            if key in points:
                points[key]["axes"].append(axis["code"])
                continue
            assessment = item.get("human_assessment")
            current = (
                item["source_state"] == "CURRENT_SOURCE"
                and assessment is not None
                and assessment["state"] == "CURRENT"
                and assessment["source_context_sha256"] == item.get("source_context_sha256")
            )
            treatment = assessment.get("treatment") if current else None
            points[key] = dict(
                point_key=key,
                axes=[axis["code"]],
                point=deepcopy(item),
                hypotheses=treatment.get("hypotheses") if treatment else None,
                relations_state="RECORDED" if item.get("follow_ups") else "UNKNOWN",
            )
    return list(points.values())
