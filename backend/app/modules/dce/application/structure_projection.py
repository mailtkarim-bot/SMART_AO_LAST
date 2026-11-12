"""Pure source-bound candidates; geometry never admits a document or a business value."""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import asdict, dataclass
from hashlib import sha256
from uuid import UUID

Box = tuple[float, float, float, float]
MAX_REGIONS = 512
STRUCTURE_PROJECTOR_VERSION = "2"


@dataclass(frozen=True, slots=True)
class StructureScope:
    tenant_id: UUID
    document_id: UUID
    version_id: UUID
    source_sha256: str
    render_sha256: str
    page: int
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class RegionAnchor:
    scope: StructureScope
    bbox: Box


@dataclass(frozen=True, slots=True)
class RegionToken:
    token_id: str
    text: str
    anchor: RegionAnchor


@dataclass(frozen=True, slots=True)
class RegionCell:
    cell_id: str
    anchor: RegionAnchor


@dataclass(frozen=True, slots=True)
class ArrowPathEvidence:
    """Render-bound ordered pixel-path candidate supplied by an independent line detector."""

    trace_id: str
    scope: StructureScope
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    context_ids: tuple[str, ...]
    polyline: tuple[tuple[float, float], ...]
    arrowhead_tip: tuple[float, float]
    evidence_region: RegionAnchor
    detector_id: str
    detector_version: str
    evidence_sha256: str
    render_sha256: str


@dataclass(frozen=True, slots=True)
class CandidateNode:
    text: str
    token_ids: tuple[str, ...]
    anchor: RegionAnchor
    polarity: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CandidateCell:
    cell_id: str
    anchor: RegionAnchor
    token_ids: tuple[str, ...]
    text: str | None
    state: str
    value: None = None
    value_state: str = "UNKNOWN"
    row: None = None
    column: None = None


@dataclass(frozen=True, slots=True)
class CandidateRelation:
    kind: str
    anchor: RegionAnchor
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    semantic_state: str = "UNKNOWN"
    context_ids: tuple[str, ...] = ()
    path: tuple[tuple[float, float], ...] = ()
    path_state: str = "UNKNOWN"
    arrowhead_tip: tuple[float, float] | None = None
    detector_id: str | None = None
    evidence_sha256: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateStructure:
    scope: StructureScope
    input_sha256: str
    nodes: tuple[CandidateNode, ...]
    cells: tuple[CandidateCell, ...]
    relations: tuple[CandidateRelation, ...]
    projector_version: str = STRUCTURE_PROJECTOR_VERSION
    status: str = "REVIEW_REQUIRED"
    business_eligibility: str = "UNKNOWN"
    lot_applicability: str = "UNKNOWN"
    admission_granted: bool = False


def _contains(outer: Box, inner: Box) -> bool:
    return (
        outer[0] <= inner[0]
        and outer[1] <= inner[1]
        and outer[2] >= inner[2]
        and outer[3] >= inner[3]
    )


def _adjacent_negative(negative: RegionToken, outcome: RegionToken) -> bool:
    n, e = negative.anchor.bbox, outcome.anchor.bbox
    overlap = max(0.0, min(n[2], e[2]) - max(n[0], e[0]))
    return (
        n[1] <= e[1]
        and abs(e[1] - n[3]) <= max(n[3] - n[1], e[3] - e[1])
        and overlap >= 0.5 * min(n[2] - n[0], e[2] - e[0])
    )


def project_candidate_structure(
    *,
    expected_scope: StructureScope,
    tokens: tuple[RegionToken, ...],
    cells: tuple[RegionCell, ...] = (),
    diagram_regions: tuple[RegionAnchor, ...] = (),
    arrow_traces: tuple[ArrowPathEvidence, ...] = (),
) -> CandidateStructure:
    scope = expected_scope
    if (
        any(not isinstance(v, UUID) for v in (scope.tenant_id, scope.document_id, scope.version_id))
        or any(
            not isinstance(v, str) or re.fullmatch(r"[0-9a-f]{64}", v) is None
            for v in (scope.source_sha256, scope.render_sha256)
        )
        or any(type(v) is not int or v <= 0 for v in (scope.page, scope.width, scope.height))
    ):
        raise ValueError("STRUCTURE_SCOPE_INVALID")
    if len(tokens) + len(cells) + len(diagram_regions) + len(arrow_traces) > MAX_REGIONS:
        raise ValueError("STRUCTURE_LIMIT")
    anchors = (
        [t.anchor for t in tokens]
        + [c.anchor for c in cells]
        + list(diagram_regions)
        + [trace.evidence_region for trace in arrow_traces]
    )
    for anchor in anchors:
        if anchor.scope != scope:
            raise ValueError("STRUCTURE_SCOPE_MISMATCH")
        b = anchor.bbox
        if (
            not isinstance(b, tuple)
            or len(b) != 4
            or any(
                type(v) not in (int, float) or (type(v) is float and not math.isfinite(v))
                for v in b
            )
            or not (0 <= b[0] < b[2] <= scope.width and 0 <= b[1] < b[3] <= scope.height)
        ):
            raise ValueError("STRUCTURE_REGION_INVALID")
    identifiers = (
        [t.token_id for t in tokens]
        + [c.cell_id for c in cells]
        + [trace.trace_id for trace in arrow_traces]
    )
    if any(not isinstance(i, str) or not i or len(i) > 200 for i in identifiers):
        raise ValueError("STRUCTURE_IDENTIFIER_INVALID")
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("STRUCTURE_IDENTIFIER_DUPLICATE")
    if any(not isinstance(t.text, str) or len(t.text) > 1000 for t in tokens):
        raise ValueError("STRUCTURE_TEXT_LIMIT")
    token_by_id = {t.token_id: t for t in tokens}
    for trace in arrow_traces:
        if trace.scope != scope or trace.render_sha256 != scope.render_sha256:
            raise ValueError("STRUCTURE_SCOPE_MISMATCH")
        if (
            not isinstance(trace.source_ids, tuple)
            or not trace.source_ids
            or not isinstance(trace.target_ids, tuple)
            or not trace.target_ids
            or not isinstance(trace.context_ids, tuple)
            or any(
                not isinstance(i, str) or not i
                for i in trace.source_ids + trace.target_ids + trace.context_ids
            )
            or len(set(trace.source_ids + trace.target_ids + trace.context_ids))
            != len(trace.source_ids + trace.target_ids + trace.context_ids)
            or any(
                identifier not in token_by_id
                for identifier in trace.source_ids + trace.target_ids + trace.context_ids
            )
        ):
            raise ValueError("STRUCTURE_ARROW_AMBIGUOUS")
        if (
            trace.detector_id != "opencv-houghlinesp-candidate"
            or trace.detector_version != "1"
            or not isinstance(trace.evidence_sha256, str)
            or trace.evidence_sha256 != scope.render_sha256
        ):
            raise ValueError("STRUCTURE_ARROW_EVIDENCE_REQUIRED")
        if not isinstance(trace.polyline, tuple) or not 2 <= len(trace.polyline) <= 256:
            raise ValueError("STRUCTURE_ARROW_INVALID")
        if (
            not isinstance(trace.arrowhead_tip, tuple)
            or len(trace.arrowhead_tip) != 2
            or trace.arrowhead_tip != trace.polyline[-1]
        ):
            raise ValueError("STRUCTURE_ARROW_INVALID")
        roi = trace.evidence_region.bbox
        roi_area = (roi[2] - roi[0]) * (roi[3] - roi[1])
        if roi_area > scope.width * scope.height * 0.30:
            raise ValueError("STRUCTURE_ARROW_REGION_AMBIGUOUS")
        for point in trace.polyline:
            if (
                not isinstance(point, tuple)
                or len(point) != 2
                or any(
                    type(value) not in (int, float)
                    or (type(value) is float and not math.isfinite(value))
                    for value in point
                )
                or not (0 <= point[0] <= scope.width and 0 <= point[1] <= scope.height)
                or not _contains(roi, (point[0], point[1], point[0], point[1]))
            ):
                raise ValueError("STRUCTURE_ARROW_INVALID")
        path_length = sum(
            math.dist(a, b) for a, b in zip(trace.polyline, trace.polyline[1:], strict=False)
        )
        if path_length <= 0 or path_length > 2 * math.hypot(scope.width, scope.height):
            raise ValueError("STRUCTURE_ARROW_INVALID")
        endpoints = trace.source_ids + trace.target_ids + trace.context_ids
        if any(not _contains(roi, token_by_id[identifier].anchor.bbox) for identifier in endpoints):
            raise ValueError("STRUCTURE_ARROW_REGION_AMBIGUOUS")
        for arrow_token_group in (trace.source_ids, trace.target_ids):
            for index, left_id in enumerate(arrow_token_group):
                left = token_by_id[left_id]
                for right_id in arrow_token_group[index + 1 :]:
                    right = token_by_id[right_id]
                    if (
                        left.text.strip().casefold() == right.text.strip().casefold()
                        and left.anchor.bbox == right.anchor.bbox
                    ):
                        raise ValueError("STRUCTURE_ARROW_AMBIGUOUS")

        def region_gap(point: tuple[float, float], box: Box) -> float:
            dx = max(box[0] - point[0], 0.0, point[0] - box[2])
            dy = max(box[1] - point[1], 0.0, point[1] - box[3])
            return math.hypot(dx, dy)

        if (
            min(region_gap(trace.polyline[0], token_by_id[i].anchor.bbox) for i in trace.source_ids)
            > 48
        ):
            raise ValueError("STRUCTURE_ARROW_ENDPOINT_REQUIRED")
        if (
            min(
                region_gap(trace.arrowhead_tip, token_by_id[i].anchor.bbox)
                for i in trace.target_ids
            )
            > 20
        ):
            raise ValueError("STRUCTURE_ARROW_ENDPOINT_REQUIRED")

    tokens = tuple(sorted(tokens, key=lambda t: t.token_id))
    cells = tuple(sorted(cells, key=lambda c: c.cell_id))
    diagram_regions = tuple(sorted(diagram_regions, key=lambda a: a.bbox))
    arrow_traces = tuple(sorted(arrow_traces, key=lambda trace: trace.trace_id))
    manifest = json.dumps(
        {
            "version": STRUCTURE_PROJECTOR_VERSION,
            "scope": asdict(scope),
            "tokens": [asdict(token) for token in tokens],
            "cells": [asdict(cell) for cell in cells],
            "diagrams": [asdict(anchor) for anchor in diagram_regions],
            "arrows": [asdict(trace) for trace in arrow_traces],
        },
        sort_keys=True,
        default=str,
        allow_nan=False,
    )

    arrow_pairs = [
        (frozenset(trace.source_ids), frozenset(trace.target_ids)) for trace in arrow_traces
    ]
    if len(set(arrow_pairs)) != len(arrow_pairs):
        raise ValueError("STRUCTURE_ARROW_AMBIGUOUS")
    owners = {
        t.token_id: [c.cell_id for c in cells if _contains(c.anchor.bbox, t.anchor.bbox)]
        for t in tokens
    }
    negatives = [t for t in tokens if t.text.strip().casefold() in {"non", "not"}]
    outcomes = [t for t in tokens if t.text.strip().casefold() in {"eligible", "éligible"}]
    pairs = [
        (n, e)
        for n in negatives
        for e in outcomes
        if _adjacent_negative(n, e)
        and (
            not cells or (len(owners[n.token_id]) == 1 and owners[n.token_id] == owners[e.token_id])
        )
    ]
    negative_counts = Counter(n.token_id for n, _ in pairs)
    outcome_counts = Counter(e.token_id for _, e in pairs)
    joined = {
        e.token_id: n
        for n, e in pairs
        if negative_counts[n.token_id] == outcome_counts[e.token_id] == 1
    }
    consumed = {t.token_id for t in joined.values()}
    nodes = []
    for t in tokens:
        if t.token_id in consumed:
            continue
        negative = joined.get(t.token_id)
        if negative is None:
            nodes.append(CandidateNode(t.text, (t.token_id,), t.anchor))
        else:
            n, e = negative.anchor.bbox, t.anchor.bbox
            anchor = RegionAnchor(
                scope, (min(n[0], e[0]), min(n[1], e[1]), max(n[2], e[2]), max(n[3], e[3]))
            )
            nodes.append(
                CandidateNode(
                    f"{negative.text} {t.text}",
                    (negative.token_id, t.token_id),
                    anchor,
                    "NEGATED_CANDIDATE",
                )
            )

    projected_cells = []
    relations = []
    for c in cells:
        contained = [t for t in tokens if owners[t.token_id] == [c.cell_id]]
        ambiguous = any(
            (c.cell_id in owners[t.token_id] and len(owners[t.token_id]) > 1)
            or (
                max(c.anchor.bbox[0], t.anchor.bbox[0]) < min(c.anchor.bbox[2], t.anchor.bbox[2])
                and max(c.anchor.bbox[1], t.anchor.bbox[1])
                < min(c.anchor.bbox[3], t.anchor.bbox[3])
                and not _contains(c.anchor.bbox, t.anchor.bbox)
            )
            for t in tokens
        )
        ordered = sorted(contained, key=lambda t: (t.anchor.bbox[1], t.anchor.bbox[0], t.token_id))
        text = " ".join(t.text for t in ordered).strip() if ordered and not ambiguous else None
        projected_cells.append(
            CandidateCell(
                c.cell_id,
                c.anchor,
                tuple(t.token_id for t in ordered),
                text or None,
                "SOURCE_TEXT_CANDIDATE" if text else "UNKNOWN",
            )
        )
        for t in contained:
            relations.append(
                CandidateRelation(
                    "GEOMETRIC_CONTAINMENT_ONLY", c.anchor, (c.cell_id,), (t.token_id,)
                )
            )
    # shortcut: arrow direction/path needs separate evidence; OCR order cannot supply it.
    relations.extend(CandidateRelation("DIAGRAM_EDGE", a, (), ()) for a in diagram_regions)
    relations.extend(
        CandidateRelation(
            kind="ARROW_PATH_CANDIDATE",
            anchor=trace.evidence_region,
            source_ids=trace.source_ids,
            target_ids=trace.target_ids,
            semantic_state="UNKNOWN",
            context_ids=trace.context_ids,
            path=trace.polyline,
            path_state="SOURCE_PATH_CANDIDATE",
            arrowhead_tip=trace.arrowhead_tip,
            detector_id=trace.detector_id,
            evidence_sha256=trace.evidence_sha256,
        )
        for trace in arrow_traces
    )
    return CandidateStructure(
        scope,
        sha256(manifest.encode()).hexdigest(),
        tuple(nodes),
        tuple(projected_cells),
        tuple(relations),
    )
