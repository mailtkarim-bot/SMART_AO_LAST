"""Bounded axial raster topology. No expected routes, direction or business admission."""

import json
import math
import struct
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from hashlib import sha256

from app.modules.dce.application.conditional_diagram import ConditionalNode
from app.modules.dce.application.diagram_evidence import ArrowheadEvidence
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
    project_candidate_structure,
)
from app.modules.dce.infrastructure.diagram_image_reader import (
    _dark_pixel,
    detect_terminal_arrowhead,
)


@dataclass(frozen=True, slots=True)
class TopologyVertex:
    vertex_id: str
    kind: str
    anchor: RegionAnchor
    state: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EndpointContact:
    vertex_id: str
    endpoint: tuple[int, int]
    state: str
    pixel_path: tuple[tuple[int, int], ...] = ()
    head: ArrowheadEvidence | None = None


@dataclass(frozen=True, slots=True)
class TopologyLink:
    endpoints: tuple[str, str]
    path: tuple[tuple[int, int], ...]
    anchor: RegionAnchor
    state: str
    contacts: tuple[EndpointContact, ...] = ()
    direction_state: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class CandidateTopology:
    scope: StructureScope
    diagram_region: RegionAnchor
    input_sha256: str
    vertices: tuple[TopologyVertex, ...]
    links: tuple[TopologyLink, ...]
    junctions: tuple[TopologyVertex, ...]
    unqualified_nodes: tuple[str, ...]
    stroke_regions: tuple[RegionAnchor, ...]
    unresolved_regions: tuple[RegionAnchor, ...]
    seed_nodes: tuple[ConditionalNode, ...]
    tokens: tuple[RegionToken, ...]
    extractor_version: str = "axial-bt601-150dpi-v4"
    semantic_state: str = "UNKNOWN"
    status: str = "REVIEW_REQUIRED"
    admission_granted: bool = False
    ambiguous_nodes: tuple[str, ...] = ()


@dataclass
class _Stroke:
    start: tuple[int, int]
    end: tuple[int, int]
    pixels: set[tuple[int, int]]


def _bounds(points, scope):
    xs, ys = zip(*points, strict=True)
    return RegionAnchor(scope, (min(xs), min(ys), max(xs) + 1, max(ys) + 1))


def _strokes(ink):
    result = []
    for vertical in (False, True):
        rows = defaultdict(list)
        for x, y in ink:
            rows[x if vertical else y].append(y if vertical else x)
        candidates: set[tuple[int, int]] = set()
        for row in sorted(rows):
            values = sorted(rows[row])
            start = previous = values[0]
            for value in values[1:] + [values[-1] + 2]:
                if value != previous + 1:
                    if previous - start + 1 >= 18:
                        candidates.update(
                            (row, c) if vertical else (c, row) for c in range(start, previous + 1)
                        )
                    start = value
                previous = value
        components = 0
        while candidates:
            components += 1
            if components > 512:
                raise ValueError("TOPOLOGY_LIMIT")
            first = min(candidates)
            candidates.remove(first)
            component = {first}
            pending = [first]
            while pending:
                x, y = pending.pop()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    point = (x + dx, y + dy)
                    if point in candidates:
                        candidates.remove(point)
                        component.add(point)
                        pending.append(point)
            xs, ys = zip(*component, strict=True)
            low, high = (min(xs), max(xs)) if vertical else (min(ys), max(ys))
            if high - low > 2:
                continue
            center = round((low + high) / 2)
            start, end = (
                ((center, min(ys)), (center, max(ys)))
                if vertical
                else ((min(xs), center), (max(xs), center))
            )
            result.append(_Stroke(start, end, component))
    if len(result) > 256:
        raise ValueError("TOPOLOGY_LIMIT")
    return result


def _contains(box, point):
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def _frames(nodes, strokes):
    horizontal = [s for s in strokes if s.start[1] == s.end[1]]
    vertical = [s for s in strokes if s.start[0] == s.end[0]]
    frames = {}
    unknown = set()
    ambiguous = set()
    for n in nodes:
        x0, y0, x1, y1 = n.anchor.bbox
        tops = [
            s
            for s in horizontal
            if y0 - 64 <= s.start[1] < y0 and s.start[0] <= x0 and s.end[0] >= x1
        ]
        bottoms = [
            s
            for s in horizontal
            if y1 < s.start[1] <= y1 + 64 and s.start[0] <= x0 and s.end[0] >= x1
        ]
        lefts = [
            s
            for s in vertical
            if x0 - 64 <= s.start[0] < x0 and s.start[1] <= y0 and s.end[1] >= y1
        ]
        rights = [
            s
            for s in vertical
            if x1 < s.start[0] <= x1 + 64 and s.start[1] <= y0 and s.end[1] >= y1
        ]
        if math.prod(map(len, (tops, bottoms, lefts, rights))) > 4096:
            raise ValueError("TOPOLOGY_LIMIT")
        choices = set()
        for t in tops:
            for b in bottoms:
                for left in lefts:
                    for r in rights:
                        if all(
                            h.start[0] <= v.start[0] + 1
                            and h.end[0] >= v.start[0] - 1
                            and v.start[1] <= h.start[1] + 1
                            and v.end[1] >= h.start[1] - 1
                            for h in (t, b)
                            for v in (left, r)
                        ):
                            choices.add((left.start[0], t.start[1], r.start[0], b.start[1]))
        if len(choices) == 1:
            frames[n.node_id] = choices.pop()
        else:
            unknown.add(n.node_id)
            if len(choices) > 1:
                ambiguous.add(n.node_id)
    owners = defaultdict(list)
    for name, box in frames.items():
        owners[box].append(name)
    for names in owners.values():
        if len(names) > 1:
            unknown.update(names)
            ambiguous.update(names)
    return frames, unknown, ambiguous


def _pixel_contact(point, target, ink):
    if point not in ink:
        offsets = ((1, 0), (-1, 0)) if point[0] == target[0] else ((0, 1), (0, -1))
        alternatives = [
            (point[0] + dx, point[1] + dy)
            for dx, dy in offsets
            if (point[0] + dx, point[1] + dy) in ink
        ]
        if len(alternatives) != 1:
            return ()
        point = alternatives[0]
    box = (
        min(point[0], target[0]) - 2,
        min(point[1], target[1]) - 2,
        max(point[0], target[0]) + 2,
        max(point[1], target[1]) + 2,
    )
    parents = {point: None}
    pending = deque([point])
    while pending:
        p = pending.popleft()
        if p == target:
            route = []
            while p is not None:
                route.append(p)
                p = parents[p]
            return tuple(reversed(route))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (p[0] + dx, p[1] + dy)
            if q in ink and q not in parents and _contains(box, q):
                parents[q] = p
                pending.append(q)
    return ()


def extract_candidate_topology(
    *,
    png_bytes: bytes,
    expected_scope: StructureScope,
    diagram_region: RegionAnchor,
    nodes: tuple[ConditionalNode, ...],
    tokens: tuple[RegionToken, ...],
    render_dpi: int,
) -> CandidateTopology:
    scope = expected_scope
    if type(render_dpi) is not int or render_dpi != 150:
        raise ValueError("TOPOLOGY_SCALE_UNQUALIFIED")
    if (
        not isinstance(nodes, tuple)
        or not isinstance(tokens, tuple)
        or len(nodes) > 32
        or len(tokens) > 128
    ):
        raise ValueError("TOPOLOGY_LIMIT")
    project_candidate_structure(
        expected_scope=scope,
        tokens=tokens,
        diagram_regions=(diagram_region,) + tuple(n.anchor for n in nodes),
    )
    if any(n.kind not in {"ENTRY", "CONDITION", "OUTCOME"} for n in nodes) or len(
        {n.node_id for n in nodes}
    ) != len(nodes):
        raise ValueError("TOPOLOGY_NODE_INVALID")
    if any(
        not isinstance(n.node_id, str)
        or not n.node_id
        or len(n.node_id) > 200
        or n.node_id.startswith("p-")
        for n in nodes
    ):
        raise ValueError("TOPOLOGY_NODE_INVALID")
    if not isinstance(png_bytes, bytes) or sha256(png_bytes).hexdigest() != scope.render_sha256:
        raise ValueError("TOPOLOGY_RENDER_MISMATCH")
    if (
        not 24 <= len(png_bytes) <= 20_000_000
        or png_bytes[:8] != b"\x89PNG\r\n\x1a\n"
        or png_bytes[12:16] != b"IHDR"
        or struct.unpack(">II", png_bytes[16:24]) != (scope.width, scope.height)
        or scope.width * scope.height > 25_000_000
    ):
        raise ValueError("TOPOLOGY_IMAGE_INVALID")
    if any(int(v) != v for v in diagram_region.bbox):
        raise ValueError("TOPOLOGY_REGION_INVALID")
    x0, y0, x1, y1 = map(int, diagram_region.bbox)
    if (x1 - x0) * (y1 - y0) > 1_000_000 or x1 > scope.width or y1 > scope.height:
        raise ValueError("TOPOLOGY_LIMIT")
    if any(
        not (
            x0 <= n.anchor.bbox[0] < n.anchor.bbox[2] <= x1
            and y0 <= n.anchor.bbox[1] < n.anchor.bbox[3] <= y1
        )
        for n in nodes
    ):
        raise ValueError("TOPOLOGY_NODE_OUTSIDE_REGION")
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("document-advanced extra is required") from exc
    try:
        pix = pymupdf.Pixmap(png_bytes)
        if pix.alpha:
            raise ValueError("TOPOLOGY_IMAGE_INVALID")
        if pix.n not in (1, 3) or (pix.width, pix.height) != (scope.width, scope.height):
            raise ValueError("TOPOLOGY_IMAGE_INVALID")
        data, stride = pix.samples, pix.stride
    except (RuntimeError, ValueError, pymupdf.mupdf.FzErrorBase) as exc:
        raise ValueError("TOPOLOGY_IMAGE_INVALID") from exc
    # shortcut: dark axial strokes >=18px, <=3px thick at150DPI; other layouts stay unqualified.
    ink = {
        (x, y)
        for y in range(y0, y1)
        for x in range(x0, x1)
        if _dark_pixel(data, stride, pix.n, x, y, 180)
    }
    frames, unknown, ambiguous = _frames(nodes, _strokes(ink))
    masks = [tuple(v + (-1 if i < 2 else 1) for i, v in enumerate(b)) for b in frames.values()]
    remaining = {p for p in ink if not any(_contains(b, p) for b in masks)}
    strokes = _strokes(remaining)
    stroke_bounds = tuple(_bounds(stroke.pixels, scope) for stroke in strokes)
    splits = [{s.start, s.end} for s in strokes]
    near_misses = set()
    for i, a in enumerate(strokes):
        for j in range(i + 1, len(strokes)):
            b = strokes[j]
            if (a.start[0] == a.end[0]) == (b.start[0] == b.end[0]):
                continue
            h, v = (b, a) if a.start[0] == a.end[0] else (a, b)
            p = (v.start[0], h.start[1])
            hb, vb = (
                (stroke_bounds[j].bbox, stroke_bounds[i].bbox)
                if a.start[0] == a.end[0]
                else (stroke_bounds[i].bbox, stroke_bounds[j].bbox)
            )
            near = (
                hb[0] - 3 <= vb[2] - 1
                and vb[0] <= hb[2] - 1 + 3
                and hb[1] - 3 <= vb[3] - 1
                and vb[1] <= hb[3] - 1 + 3
            )
            if not near:
                continue
            contact = a.pixels & b.pixels or {
                q
                for q in a.pixels
                if any(
                    (q[0] + dx, q[1] + dy) in b.pixels
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                )
            }
            exact = (
                h.start[0] - 1 <= p[0] <= h.end[0] + 1 and v.start[1] - 1 <= p[1] <= v.end[1] + 1
            )
            if not contact or not exact:
                near_misses.add(p)
            if contact and exact:
                for index in (i, j):
                    splits[index] = {
                        q for q in splits[index] if max(abs(q[0] - p[0]), abs(q[1] - p[1])) > 2
                    }
                    splits[index].add(p)
    graph = defaultdict(set)
    for s, split_points in zip(strokes, splits, strict=True):
        ordered = sorted(
            split_points, key=lambda p: (p[1], p[0]) if s.start[0] == s.end[0] else (p[0], p[1])
        )
        for a, b in zip(ordered, ordered[1:], strict=False):
            if a != b:
                graph[a].add(b)
                graph[b].add(a)
    vertices = {}
    contacts = {}
    seed_vertices = {
        n.node_id: TopologyVertex(
            n.node_id,
            "NODE",
            RegionAnchor(scope, frames.get(n.node_id, n.anchor.bbox)),
            "PIXEL_NODE_FRAME_CANDIDATE" if n.node_id not in unknown else "UNKNOWN",
        )
        for n in nodes
    }
    for p, neighbors in sorted(graph.items()):
        degree = len(neighbors)
        if degree == 2:
            continue
        name = f"p-{p[0]}-{p[1]}"
        kind = "JUNCTION" if degree >= 3 else "DANGLING"
        state = "PIXEL_JUNCTION_CANDIDATE" if degree == 3 else "UNKNOWN"
        if degree == 1:
            q = next(iter(neighbors))
            dx, dy = p[0] - q[0], p[1] - q[1]
            attachments = []
            for node_id, b in frames.items():
                if (
                    dx == 0
                    and b[0] <= p[0] <= b[2]
                    and (0 <= b[1] - p[1] <= 10 if dy > 0 else 0 <= p[1] - b[3] <= 10)
                ):
                    attachments.append(node_id)
                if (
                    dy == 0
                    and b[1] <= p[1] <= b[3]
                    and (0 <= b[0] - p[0] <= 10 if dx > 0 else 0 <= p[0] - b[2] <= 10)
                ):
                    attachments.append(node_id)
            if len(attachments) == 1:
                node_id = attachments[0]
                b = frames[node_id]
                target = (
                    (p[0], b[1] if dy > 0 else b[3])
                    if dx == 0
                    else (b[0] if dx > 0 else b[2], p[1])
                )
                pixel_path = _pixel_contact(p, target, ink)
                proof = None
                if pixel_path:
                    proof = EndpointContact(node_id, p, "PIXEL_FRAME_CONTACT", pixel_path)
                else:
                    head = detect_terminal_arrowhead(
                        png_bytes=png_bytes,
                        expected_scope=scope,
                        terminal_start=q,
                        terminal_end=p,
                        render_dpi=render_dpi,
                    )
                    if (
                        head.state == "PIXEL_HEAD_CANDIDATE"
                        and head.tip is not None
                        and head.anchor is not None
                        and math.dist(head.tip, target) <= 2
                        and all(x0 <= x < x1 and y0 <= y < y1 for x, y in (head.tip,))
                        and x0 <= head.anchor.bbox[0] < head.anchor.bbox[2] <= x1
                        and y0 <= head.anchor.bbox[1] < head.anchor.bbox[3] <= y1
                    ):
                        proof = EndpointContact(node_id, p, "PIXEL_HEAD_AT_FRAME", head=head)
                if proof is not None:
                    contacts[p] = proof
                    vertices[p] = seed_vertices[node_id]
                    continue
        vertices[p] = TopologyVertex(name, kind, _bounds((p,), scope), state)
    used = set()
    links = []
    for start in sorted(vertices):
        for neighbor in sorted(graph[start]):
            if frozenset((start, neighbor)) in used:
                continue
            points = [start, neighbor]
            used.add(frozenset((start, neighbor)))
            while points[-1] not in vertices:
                following = next(iter(graph[points[-1]] - {points[-2]}))
                used.add(frozenset((points[-1], following)))
                points.append(following)
                if len(points) > 512:
                    raise ValueError("TOPOLOGY_LIMIT")
            a, b = vertices[start], vertices[points[-1]]
            if a.vertex_id > b.vertex_id:
                a, b = b, a
                points.reverse()
            state = (
                "PIXEL_TOPOLOGY_CANDIDATE"
                if a.state != "UNKNOWN"
                and b.state != "UNKNOWN"
                and a.vertex_id != b.vertex_id
                and not any(
                    _contains(
                        (min(u[0], v[0]), min(u[1], v[1]), max(u[0], v[0]), max(u[1], v[1])), p
                    )
                    for u, v in zip(points, points[1:], strict=False)
                    for p in near_misses
                )
                else "UNKNOWN"
            )
            links.append(
                TopologyLink(
                    (a.vertex_id, b.vertex_id),
                    tuple(points),
                    _bounds(points, scope),
                    state,
                    tuple(contacts[v] for v in (points[0], points[-1]) if v in contacts),
                )
            )
    if len(links) > 128:
        raise ValueError("TOPOLOGY_LIMIT")
    residual = {p for p, qs in graph.items() if any(frozenset((p, q)) not in used for q in qs)}
    all_vertices = {v.vertex_id: v for v in vertices.values()}
    all_vertices.update(seed_vertices)
    ordered_vertices = tuple(all_vertices[i] for i in sorted(all_vertices))
    digest = sha256(
        json.dumps(
            {
                "scope": asdict(scope),
                "region": asdict(diagram_region),
                "nodes": [asdict(n) for n in sorted(nodes, key=lambda n: n.node_id)],
                "tokens": [asdict(t) for t in sorted(tokens, key=lambda t: t.token_id)],
                "version": "axial-bt601-150dpi-v4",
            },
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    return CandidateTopology(
        scope,
        diagram_region,
        digest,
        ordered_vertices,
        tuple(sorted(links, key=lambda e: (e.endpoints, e.path))),
        tuple(v for v in ordered_vertices if v.kind == "JUNCTION"),
        tuple(sorted(unknown)),
        stroke_bounds,
        ((_bounds(residual, scope),) if residual else ())
        + tuple(_bounds((p,), scope) for p in sorted(near_misses)),
        tuple(sorted(nodes, key=lambda n: n.node_id)),
        tuple(sorted(tokens, key=lambda t: t.token_id)),
        ambiguous_nodes=tuple(sorted(ambiguous)),
    )
