"""Directions and paths derived from discovered routes, never from expected relations."""

import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from hashlib import sha256

from app.modules.dce.application.conditional_diagram import (
    ConditionalAssembly,
    ConditionalNode,
    ConditionalRelationEvidence,
    RelationRequirement,
    _contains,
    _path_near_box,
    assemble_conditional_paths,
)
from app.modules.dce.application.diagram_evidence import (
    ArrowheadEvidence,
    BranchLabelEvidence,
    qualify_branch_label,
)
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
    project_candidate_structure,
)


@dataclass(frozen=True, slots=True)
class DiscoveredRoute:
    route_id: str
    endpoint_ids: tuple[str, str]
    anchor: RegionAnchor
    path: tuple[tuple[float, float], ...]
    geometry_state: str
    heads: tuple[ArrowheadEvidence, ...] = ()


@dataclass(frozen=True, slots=True)
class RouteDecision:
    route: DiscoveredRoute
    source_id: str | None
    target_id: str | None
    labels: tuple[BranchLabelEvidence, ...]
    direction_state: str
    reason: str


@dataclass(frozen=True, slots=True)
class ReconstructedDiagram:
    scope: StructureScope
    input_sha256: str
    decisions: tuple[RouteDecision, ...]
    labels: tuple[BranchLabelEvidence, ...]
    unassigned_labels: tuple[str, ...]
    ambiguous_labels: tuple[str, ...]
    unresolved_routes: tuple[str, ...]
    assembly: ConditionalAssembly
    source_nodes: tuple[ConditionalNode, ...]
    decoder_version: str = "question-ports-150dpi-v3"
    status: str = "REVIEW_REQUIRED"
    business_eligibility: str = "UNKNOWN"
    admission_granted: bool = False


def _serialized(value):
    return json.dumps(asdict(value), sort_keys=True, default=str, allow_nan=False)


def reconstruct_discovered_diagram(
    *,
    expected_scope: StructureScope,
    nodes: tuple[ConditionalNode, ...],
    tokens: tuple[RegionToken, ...],
    routes: tuple[DiscoveredRoute, ...],
    labels: tuple[BranchLabelEvidence, ...],
) -> ReconstructedDiagram:
    if (
        any(not isinstance(v, tuple) for v in (nodes, tokens, routes, labels))
        or len(routes) > 128
        or len(labels) > 128
        or not 1 <= len(nodes) <= 32
    ):
        raise ValueError("DISCOVERED_DIAGRAM_LIMIT")
    project_candidate_structure(
        expected_scope=expected_scope,
        tokens=tokens,
        diagram_regions=tuple(n.anchor for n in nodes)
        + tuple(r.anchor for r in routes)
        + tuple(h.anchor for r in routes for h in r.heads if h.anchor is not None),
    )
    by_node = {n.node_id: n for n in nodes}
    by_token = {t.token_id: t for t in tokens}
    if len(by_node) != len(nodes):
        raise ValueError("DISCOVERED_NODE_INVALID")
    owned = {i for n in nodes for i in n.token_ids}
    questions = set()
    for n in nodes:
        if any(i not in by_token for i in n.token_ids):
            raise ValueError("DISCOVERED_NODE_INVALID")
        text = " ".join(
            t.text
            for t in sorted(
                (by_token[i] for i in n.token_ids),
                key=lambda t: (t.anchor.bbox[1], t.anchor.bbox[0], t.token_id),
            )
        )
        if (
            n.kind in {"ENTRY", "CONDITION"}
            and n.text_state == "SOURCE_TEXT_CANDIDATE"
            and text.rstrip().endswith("?")
            and any(c.isalnum() for c in text)
        ):
            questions.add(n.node_id)
    canonical = []
    identifiers = set()
    pairs = defaultdict(list)
    for r in routes:
        if (
            not isinstance(r.route_id, str)
            or not r.route_id
            or len(r.route_id) > 200
            or r.route_id in identifiers
            or r.route_id in by_node
        ):
            raise ValueError("DISCOVERED_ROUTE_INVALID")
        identifiers.add(r.route_id)
        if (
            not isinstance(r.endpoint_ids, tuple)
            or len(r.endpoint_ids) != 2
            or len(set(r.endpoint_ids)) != 2
            or any(not isinstance(i, str) or not i or len(i) > 200 for i in r.endpoint_ids)
            or r.geometry_state not in {"UNKNOWN", "SOURCE_PATH_CANDIDATE"}
            or not isinstance(r.path, tuple)
            or not 2 <= len(r.path) <= 64
            or not isinstance(r.heads, tuple)
            or len(r.heads) > 8
        ):
            raise ValueError("DISCOVERED_ROUTE_INVALID")
        for p in r.path:
            if (
                not isinstance(p, tuple)
                or len(p) != 2
                or any(type(v) not in (int, float) or not math.isfinite(v) for v in p)
                or not _contains(r.anchor.bbox, (*p, *p))
            ):
                raise ValueError("DISCOVERED_ROUTE_INVALID")
        if sum(math.dist(a, b) for a, b in zip(r.path, r.path[1:], strict=False)) <= 0:
            raise ValueError("DISCOVERED_ROUTE_INVALID")
        heads = []
        for h in r.heads:
            if h.scope != expected_scope:
                raise ValueError("STRUCTURE_SCOPE_MISMATCH")
            if (
                h.state not in {"UNKNOWN", "PIXEL_HEAD_CANDIDATE"}
                or h.semantic_state != "UNKNOWN"
                or h.status != "REVIEW_REQUIRED"
                or h.detector_version
                not in ("axis-filled-head-150dpi-v1", "axis-filled-head-bt601-150dpi-v2")
            ):
                raise ValueError("DISCOVERED_HEAD_INVALID")
            if h.state == "PIXEL_HEAD_CANDIDATE" and (
                h.tip is None
                or h.anchor is None
                or not _contains(h.anchor.bbox, (*h.tip, *h.tip))
                or not _contains(r.anchor.bbox, h.anchor.bbox)
            ):
                raise ValueError("DISCOVERED_HEAD_INVALID")
            if h not in heads:
                heads.append(h)
        path = r.path
        ids = r.endpoint_ids
        if ids[0] > ids[1]:
            ids = (ids[1], ids[0])
            path = tuple(reversed(path))
        r = replace(r, endpoint_ids=ids, path=path, heads=tuple(sorted(heads, key=_serialized)))
        canonical.append(r)
        pairs[ids].append(r.route_id)
    routes = tuple(sorted(canonical, key=lambda r: r.route_id))
    observed = []
    for b in labels:
        rebuilt = qualify_branch_label(
            expected_scope=expected_scope,
            raw_token=b.raw_token,
            reread_token=b.reread_token,
            reread_input_sha256=b.reread_input_sha256,
            reread_extractor_id=b.reread_extractor_id,
            reread_extractor_version=b.reread_extractor_version,
        )
        if rebuilt != b or by_token.get(b.raw_token.token_id) != b.raw_token:
            raise ValueError("DISCOVERED_LABEL_INVALID")
        if b not in observed:
            observed.append(b)
    labels = tuple(sorted(observed, key=_serialized))
    heads_direction = {}
    question_source = {}
    blocked = {}
    for r in routes:
        positives = [h for h in r.heads if h.state == "PIXEL_HEAD_CANDIDATE"]
        if r.geometry_state != "SOURCE_PATH_CANDIDATE" or any(
            i not in by_node for i in r.endpoint_ids
        ):
            blocked[r.route_id] = "UNKNOWN_GEOMETRY_OR_BOUNDARY"
        if len(pairs[r.endpoint_ids]) > 1:
            blocked[r.route_id] = "COMPETING_ROUTES"
        if positives:
            if len(positives) != 1:
                blocked[r.route_id] = "COMPETING_HEADS"
            else:
                near = [
                    i
                    for i, p in enumerate((r.path[0], r.path[-1]))
                    if positives[0].tip is not None and math.dist(positives[0].tip, p) <= 2
                ]
                if len(near) != 1:
                    blocked[r.route_id] = "HEAD_NOT_UNIQUE_AT_ENDPOINT"
                else:
                    target = r.endpoint_ids[near[0]]
                    source = r.endpoint_ids[1 - near[0]]
                    heads_direction[r.route_id] = (source, target, positives[0])
                    if source in questions:
                        question_source[r.route_id] = source
        else:
            qs = [i for i in r.endpoint_ids if i in questions]
            if len(qs) == 1 and any(
                by_node.get(i) and by_node[i].kind == "JUNCTION" for i in r.endpoint_ids
            ):
                question_source[r.route_id] = qs[0]
    attached = defaultdict(list)
    ambiguous = set()
    unassigned = set()
    for b in labels:
        token_id = b.raw_token.token_id
        matches = [
            r
            for r in routes
            if r.route_id in question_source
            and token_id not in owned
            and _contains(r.anchor.bbox, b.raw_token.anchor.bbox)
            and _path_near_box(r.path, b.raw_token.anchor.bbox)
        ]
        if len(matches) == 1:
            attached[matches[0].route_id].append(b)
        elif matches:
            ambiguous.add(token_id)
            for r in matches:
                blocked[r.route_id] = "LABEL_NEAR_COMPETING_ROUTES"
                attached[r.route_id].append(b)
        else:
            unassigned.add(token_id)
    requirements = []
    evidence = []
    decisions = []
    unresolved = []
    for r in routes:
        branch = attached[r.route_id]
        selected_source: str | None = None
        selected_target: str | None = None
        state = "UNKNOWN"
        reason = blocked.get(r.route_id, "NO_DIRECTION_PROOF")
        head = None
        if r.route_id not in blocked:
            if r.route_id in heads_direction:
                selected_source, selected_target, head = heads_direction[r.route_id]
                state = "PIXEL_DIRECTION_CANDIDATE"
                reason = "UNIQUE_ENDPOINT_HEAD"
            elif len(branch) == 1 and branch[0].label is not None:
                selected_source = question_source[r.route_id]
                selected_target = next(i for i in r.endpoint_ids if i != selected_source)
                state = "QUESTION_PORT_DIRECTION_CANDIDATE"
                reason = "UNIQUE_RESPONSE_AT_QUESTION_PORT"
            if branch and (len(branch) != 1 or branch[0].label is None):
                state = "UNKNOWN"
                reason = "LABEL_UNQUALIFIED_OR_COMPETING"
        decisions.append(
            RouteDecision(
                r,
                selected_source,
                selected_target,
                tuple(sorted(branch, key=_serialized)),
                state,
                reason,
            )
        )
        if state == "UNKNOWN":
            unresolved.append(r.route_id)
            continue
        if selected_source is None or selected_target is None:
            raise ValueError("DISCOVERED_DIRECTION_INVALID")
        selected_branch = branch[0] if branch else None
        requirements.append(
            RelationRequirement(
                r.route_id,
                selected_source,
                selected_target,
                selected_branch.raw_token.token_id if selected_branch else None,
                selected_branch.label if selected_branch else None,
            )
        )
        path = r.path if r.endpoint_ids[0] == selected_source else tuple(reversed(r.path))
        if head is not None and head.tip is not None and path[-1] != head.tip:
            path = path + (head.tip,)
        evidence.append(
            ConditionalRelationEvidence(
                r.route_id, r.anchor, path, "SOURCE_PATH_CANDIDATE", selected_branch, head
            )
        )
    tainted = {
        i
        for d in decisions
        if d.direction_state == "UNKNOWN"
        for i in d.route.endpoint_ids
        if i in by_node
    }
    assembly_nodes = tuple(
        replace(n, junction_state="UNKNOWN")
        if n.node_id in tainted and n.kind == "JUNCTION"
        else replace(n, text_state="UNKNOWN")
        if n.node_id in tainted
        else n
        for n in nodes
    )
    if not any(n.kind == "ENTRY" for n in nodes):
        # shortcut: inferred entries belong to the top question band in this downward layout.
        top = min((by_node[i].anchor.bbox[1] for i in questions), default=math.inf)
        band_bottom = min(
            (by_node[i].anchor.bbox[3] for i in questions if by_node[i].anchor.bbox[1] == top),
            default=top,
        )
        top_questions = {
            i
            for i in questions
            if by_node[i].anchor.bbox[1] < band_bottom and by_node[i].anchor.bbox[3] > top
        }
        incoming = {r.target_id for r in requirements}
        outgoing = {r.source_id for r in requirements}
        assembly_nodes = tuple(
            replace(n, kind="ENTRY") if n.node_id in top_questions & outgoing - incoming else n
            for n in assembly_nodes
        )
    assembly = assemble_conditional_paths(
        expected_scope=expected_scope,
        nodes=tuple(sorted(assembly_nodes, key=lambda n: n.node_id)),
        tokens=tuple(sorted(tokens, key=lambda t: t.token_id)),
        required_relations=tuple(requirements),
        evidence=tuple(evidence),
    )
    digest = sha256(
        json.dumps(
            {
                "version": "question-ports-150dpi-v3",
                "assembly": assembly.input_sha256,
                "source_nodes": [_serialized(n) for n in sorted(nodes, key=lambda n: n.node_id)],
                "routes": [_serialized(r) for r in routes],
                "labels": [_serialized(b) for b in labels],
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return ReconstructedDiagram(
        expected_scope,
        digest,
        tuple(decisions),
        labels,
        tuple(sorted(unassigned)),
        tuple(sorted(ambiguous)),
        tuple(sorted(unresolved)),
        assembly,
        tuple(sorted(nodes, key=lambda n: n.node_id)),
    )
