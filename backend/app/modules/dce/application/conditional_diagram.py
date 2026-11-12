"""Bounded documentary path assembly; no real-world eligibility or admission."""

import json
import math
from dataclasses import asdict, dataclass, replace
from hashlib import sha256

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
class ConditionalNode:
    node_id: str
    kind: str
    anchor: RegionAnchor
    token_ids: tuple[str, ...] = ()
    junction_state: str | None = None
    text_state: str | None = None


@dataclass(frozen=True, slots=True)
class RelationRequirement:
    relation_id: str
    source_id: str
    target_id: str
    branch_token_id: str | None = None
    branch_label: str | None = None


@dataclass(frozen=True, slots=True)
class ConditionalRelationEvidence:
    relation_id: str
    anchor: RegionAnchor
    path: tuple[tuple[float, float], ...]
    geometry_state: str
    branch: BranchLabelEvidence | None = None
    head: ArrowheadEvidence | None = None


@dataclass(frozen=True, slots=True)
class PathCondition:
    node_id: str
    token_ids: tuple[str, ...]
    raw_text: str
    branch_label: str | None
    branch_evidence: BranchLabelEvidence | None = None


@dataclass(frozen=True, slots=True)
class ConditionalPath:
    node_ids: tuple[str, ...]
    relation_ids: tuple[str, ...]
    conditions: tuple[PathCondition, ...]
    endpoint_text: str
    document_outcome: str
    state: str
    unknown_relation_ids: tuple[str, ...]
    semantic_state: str = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ConditionalAssembly:
    scope: StructureScope
    input_sha256: str
    tokens: tuple[RegionToken, ...]
    nodes: tuple[ConditionalNode, ...]
    paths: tuple[ConditionalPath, ...]
    required_relations: tuple[RelationRequirement, ...]
    evidence: tuple[ConditionalRelationEvidence, ...]
    missing_relations: tuple[str, ...]
    unqualified_relations: tuple[str, ...]
    ambiguous_relations: tuple[str, ...]
    unqualified_nodes: tuple[str, ...]
    dead_end_nodes: tuple[str, ...]
    unreachable_nodes: tuple[str, ...]
    assembler_version: str = "1"
    status: str = "REVIEW_REQUIRED"
    business_eligibility: str = "UNKNOWN"
    admission_granted: bool = False


def _contains(outer, inner):
    return (
        outer[0] <= inner[0]
        and outer[1] <= inner[1]
        and outer[2] >= inner[2]
        and outer[3] >= inner[3]
    )


def _gap(point, box):
    return math.hypot(
        max(box[0] - point[0], 0, point[0] - box[2]), max(box[1] - point[1], 0, point[1] - box[3])
    )


def _path_near_box(path, box):
    # The label must intersect a20pixel corridor around a declared route segment.
    lower, upper = (box[0] - 20, box[1] - 20), (box[2] + 20, box[3] + 20)
    for start, end in zip(path, path[1:], strict=False):
        lo, hi = 0.0, 1.0
        for axis in (0, 1):
            delta = end[axis] - start[axis]
            if delta == 0:
                if not lower[axis] <= start[axis] <= upper[axis]:
                    hi = -1.0
            else:
                a, b = sorted(
                    ((lower[axis] - start[axis]) / delta, (upper[axis] - start[axis]) / delta)
                )
                lo, hi = max(lo, a), min(hi, b)
        if lo <= hi:
            return True
    return False


def assemble_conditional_paths(
    *,
    expected_scope: StructureScope,
    tokens: tuple[RegionToken, ...],
    nodes: tuple[ConditionalNode, ...],
    required_relations: tuple[RelationRequirement, ...],
    evidence: tuple[ConditionalRelationEvidence, ...],
) -> ConditionalAssembly:
    if any(not isinstance(v, tuple) for v in (tokens, nodes, required_relations, evidence)):
        raise ValueError("DIAGRAM_INPUT_INVALID")
    if (
        not 1 <= len(nodes) <= 32
        or len(required_relations) > 64
        or len(evidence) > 128
        or len(tokens) > 128
    ):
        raise ValueError("DIAGRAM_LIMIT")
    anchors = (
        [n.anchor for n in nodes]
        + [e.anchor for e in evidence]
        + [e.head.anchor for e in evidence if e.head is not None and e.head.anchor is not None]
    )
    project_candidate_structure(
        expected_scope=expected_scope, tokens=tokens, diagram_regions=tuple(anchors)
    )
    if expected_scope.width * expected_scope.height > 25_000_000:
        raise ValueError("DIAGRAM_LIMIT")
    by_token = {t.token_id: t for t in tokens}
    by_node = {n.node_id: n for n in nodes}
    by_relation = {r.relation_id: r for r in required_relations}
    identifiers = [n.node_id for n in nodes] + [r.relation_id for r in required_relations]
    if any(not isinstance(i, str) or not i or len(i) > 200 for i in identifiers) or len(
        set(identifiers)
    ) != len(identifiers):
        raise ValueError("DIAGRAM_IDENTIFIER_INVALID")
    text = {}
    unknown_nodes = set()
    owned: set[str] = set()
    for n in nodes:
        if (
            n.kind not in {"ENTRY", "CONDITION", "JUNCTION", "OUTCOME"}
            or not isinstance(n.token_ids, tuple)
            or len(n.token_ids) > 16
        ):
            raise ValueError("DIAGRAM_NODE_INVALID")
        if (
            len(set(n.token_ids)) != len(n.token_ids)
            or any(i not in by_token for i in n.token_ids)
            or (n.kind == "JUNCTION" and n.token_ids)
        ):
            raise ValueError("DIAGRAM_NODE_INVALID")
        if any(i in owned for i in n.token_ids):
            raise ValueError("DIAGRAM_NODE_AMBIGUOUS")
        owned.update(n.token_ids)
        if any(not _contains(n.anchor.bbox, by_token[i].anchor.bbox) for i in n.token_ids):
            raise ValueError("DIAGRAM_NODE_INVALID")
        ordered = sorted(
            (by_token[i] for i in n.token_ids),
            key=lambda t: (t.anchor.bbox[1], t.anchor.bbox[0], t.token_id),
        )
        text[n.node_id] = " ".join(t.text for t in ordered).strip()
        by_node[n.node_id] = replace(n, token_ids=tuple(t.token_id for t in ordered))
        if n.kind == "JUNCTION":
            if n.junction_state not in {None, "UNKNOWN", "SOURCE_JUNCTION_CANDIDATE"}:
                raise ValueError("DIAGRAM_NODE_INVALID")
            if n.junction_state != "SOURCE_JUNCTION_CANDIDATE":
                unknown_nodes.add(n.node_id)
        elif n.junction_state is not None:
            raise ValueError("DIAGRAM_NODE_INVALID")
        if n.text_state not in {None, "UNKNOWN", "SOURCE_TEXT_CANDIDATE"}:
            raise ValueError("DIAGRAM_NODE_INVALID")
        if n.kind != "JUNCTION" and (
            n.text_state != "SOURCE_TEXT_CANDIDATE" or not any(c.isalnum() for c in text[n.node_id])
        ):
            unknown_nodes.add(n.node_id)
        contained = {t.token_id for t in tokens if _contains(n.anchor.bbox, t.anchor.bbox)}
        cut = any(
            max(n.anchor.bbox[0], t.anchor.bbox[0]) < min(n.anchor.bbox[2], t.anchor.bbox[2])
            and max(n.anchor.bbox[1], t.anchor.bbox[1]) < min(n.anchor.bbox[3], t.anchor.bbox[3])
            and not _contains(n.anchor.bbox, t.anchor.bbox)
            for t in tokens
        )
        if contained != set(n.token_ids) or cut or (n.kind != "JUNCTION" and not text[n.node_id]):
            unknown_nodes.add(n.node_id)
    nodes = tuple(by_node[i] for i in sorted(by_node))
    outgoing: dict[str, list[RelationRequirement]] = {n.node_id: [] for n in nodes}
    for r in required_relations:
        if (
            r.source_id not in by_node
            or r.target_id not in by_node
            or ((r.branch_label is None) != (r.branch_token_id is None))
        ):
            raise ValueError("DIAGRAM_REFERENCE_MISMATCH")
        if r.branch_label is not None and (
            r.branch_label not in {"OUI", "NON"} or r.branch_token_id not in by_token
        ):
            raise ValueError("DIAGRAM_REFERENCE_MISMATCH")
        if by_node[r.source_id].kind == "OUTCOME":
            raise ValueError("DIAGRAM_REFERENCE_MISMATCH")
        outgoing[r.source_id].append(r)
    for node_id, rows in outgoing.items():
        rows.sort(key=lambda r: r.relation_id)
        if (
            by_node[node_id].kind == "CONDITION"
            and len(rows) > 1
            and any(r.branch_label is None for r in rows)
        ):
            unknown_nodes.add(node_id)
        labels = [r.branch_label for r in rows if r.branch_label is not None]
        if len(set(labels)) != len(labels):
            raise ValueError("DIAGRAM_BRANCH_AMBIGUOUS")
    if any(by_node[r.target_id].kind == "ENTRY" for r in required_relations):
        raise ValueError("DIAGRAM_ENTRY_HAS_INCOMING")
    visited = set()
    active = set()

    def check_cycle(node_id):
        if node_id in active:
            raise ValueError("DIAGRAM_CYCLE")
        if node_id in visited:
            return
        active.add(node_id)
        for r in outgoing[node_id]:
            check_cycle(r.target_id)
        active.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(by_node):
        check_cycle(node_id)
    observed: dict[str, list[ConditionalRelationEvidence]] = {
        r.relation_id: [] for r in required_relations
    }
    for e in evidence:
        if e.relation_id not in by_relation or e.geometry_state not in {
            "UNKNOWN",
            "SOURCE_PATH_CANDIDATE",
        }:
            raise ValueError("DIAGRAM_REFERENCE_MISMATCH")
        r = by_relation[e.relation_id]
        if (
            not isinstance(e.path, tuple)
            or len(e.path) > 64
            or (e.geometry_state == "SOURCE_PATH_CANDIDATE" and len(e.path) < 2)
        ):
            raise ValueError("DIAGRAM_PATH_INVALID")
        for point in e.path:
            if (
                not isinstance(point, tuple)
                or len(point) != 2
                or any(
                    type(v) not in (int, float) or (type(v) is float and not math.isfinite(v))
                    for v in point
                )
                or not _contains(e.anchor.bbox, (*point, *point))
            ):
                raise ValueError("DIAGRAM_PATH_INVALID")
        if e.path and (
            sum(math.dist(a, b) for a, b in zip(e.path, e.path[1:], strict=False)) <= 0
            or _gap(e.path[0], by_node[r.source_id].anchor.bbox) > 20
            or _gap(e.path[-1], by_node[r.target_id].anchor.bbox) > 20
        ):
            raise ValueError("DIAGRAM_PATH_INVALID")
        if e.head is not None:
            h = e.head
            if h.scope != expected_scope:
                raise ValueError("STRUCTURE_SCOPE_MISMATCH")
            if (
                h.semantic_state != "UNKNOWN"
                or h.status != "REVIEW_REQUIRED"
                or h.state not in {"UNKNOWN", "PIXEL_HEAD_CANDIDATE"}
            ):
                raise ValueError("DIAGRAM_HEAD_INVALID")
            if h.state == "PIXEL_HEAD_CANDIDATE" and (
                h.anchor is None
                or h.tip is None
                or not e.path
                or h.tip != e.path[-1]
                or not _contains(e.anchor.bbox, h.anchor.bbox)
                or not _contains(h.anchor.bbox, (*h.tip, *h.tip))
            ):
                raise ValueError("DIAGRAM_HEAD_INVALID")
        if e.branch is not None:
            b = e.branch
            rebuilt = qualify_branch_label(
                expected_scope=expected_scope,
                raw_token=b.raw_token,
                reread_token=b.reread_token,
                reread_input_sha256=b.reread_input_sha256,
                reread_extractor_id=b.reread_extractor_id,
                reread_extractor_version=b.reread_extractor_version,
            )
            if (
                rebuilt != b
                or r.branch_token_id != b.raw_token.token_id
                or by_token.get(b.raw_token.token_id) != b.raw_token
                or not _contains(e.anchor.bbox, b.raw_token.anchor.bbox)
            ):
                raise ValueError("DIAGRAM_LABEL_EVIDENCE_INVALID")
        if e not in observed[e.relation_id]:
            observed[e.relation_id].append(e)
    missing = {i for i, es in observed.items() if not es}
    ambiguous = {i for i, es in observed.items() if len(es) > 1}
    unqualified = set()
    qualified = {}
    for i, es in observed.items():
        if len(es) != 1:
            continue
        e = es[0]
        r = by_relation[i]
        valid = e.geometry_state == "SOURCE_PATH_CANDIDATE"
        if by_node[r.target_id].kind != "JUNCTION":
            valid = valid and e.head is not None and e.head.state == "PIXEL_HEAD_CANDIDATE"
        if r.branch_label is not None:
            valid = (
                valid
                and e.branch is not None
                and e.branch.label == r.branch_label
                and _path_near_box(e.path, e.branch.raw_token.anchor.bbox)
            )
        if valid:
            qualified[i] = e
        else:
            unqualified.add(i)
    paths: list[ConditionalPath] = []
    reached = set()
    dead_ends = set()
    outcome_labels = {
        "ELIGIBLE": "DOCUMENT_ELIGIBLE_CEE",
        "ÉLIGIBLE": "DOCUMENT_ELIGIBLE_CEE",
        "NON ELIGIBLE": "DOCUMENT_NON_ELIGIBLE_CEE",
        "NON ÉLIGIBLE": "DOCUMENT_NON_ELIGIBLE_CEE",
        "CONTACTER VOTRE CORRESPONDANT CEE CENTRE": "CONTACT_CEE_CORRESPONDENT",
    }

    def walk(node_ids, relation_ids):
        node_id = node_ids[-1]
        n = by_node[node_id]
        reached.add(node_id)
        if n.kind != "OUTCOME" and outgoing[node_id]:
            for r in outgoing[node_id]:
                walk(node_ids + (r.target_id,), relation_ids + (r.relation_id,))
            return
        if len(paths) >= 128:
            raise ValueError("DIAGRAM_LIMIT")
        if n.kind != "OUTCOME":
            dead_ends.add(node_id)
        unresolved = tuple(i for i in relation_ids if i not in qualified)
        conditions = []
        for j, seen in enumerate(node_ids):
            source = by_node[seen]
            if source.kind not in {"ENTRY", "CONDITION"}:
                continue
            label = None
            if j < len(relation_ids):
                r = by_relation[relation_ids[j]]
                if r.branch_label is not None:
                    label = r.branch_label if r.relation_id in qualified else "UNKNOWN"
            branch = None
            if j < len(relation_ids) and len(observed[relation_ids[j]]) == 1:
                branch = observed[relation_ids[j]][0].branch
            conditions.append(PathCondition(seen, source.token_ids, text[seen], label, branch))
        outcome = (
            outcome_labels.get(" ".join(text[node_id].upper().split()), "UNKNOWN")
            if n.kind == "OUTCOME"
            else "UNKNOWN"
        )
        if unresolved or any(i in unknown_nodes for i in node_ids):
            outcome = "UNKNOWN"
        state = "SOURCE_CONDITIONAL_PATH_CANDIDATE" if outcome != "UNKNOWN" else "UNKNOWN"
        paths.append(
            ConditionalPath(
                node_ids, relation_ids, tuple(conditions), text[node_id], outcome, state, unresolved
            )
        )

    roots = sorted(n.node_id for n in nodes if n.kind == "ENTRY")
    if not roots:
        raise ValueError("DIAGRAM_ENTRY_REQUIRED")
    for node_id in roots:
        walk((node_id,), ())
    canonical = {
        "version": "1",
        "scope": asdict(expected_scope),
        "tokens": [asdict(t) for t in sorted(tokens, key=lambda t: t.token_id)],
        "nodes": [asdict(n) for n in sorted(nodes, key=lambda n: n.node_id)],
        "requirements": [
            asdict(r) for r in sorted(required_relations, key=lambda r: r.relation_id)
        ],
        "evidence": sorted(
            json.dumps(asdict(e), sort_keys=True, default=str, allow_nan=False)
            for es in observed.values()
            for e in es
        ),
    }
    digest = sha256(
        json.dumps(canonical, sort_keys=True, default=str, allow_nan=False).encode()
    ).hexdigest()
    return ConditionalAssembly(
        scope=expected_scope,
        input_sha256=digest,
        tokens=tuple(sorted(tokens, key=lambda t: t.token_id)),
        nodes=nodes,
        paths=tuple(paths),
        required_relations=tuple(sorted(required_relations, key=lambda r: r.relation_id)),
        evidence=tuple(
            sorted(
                (e for es in observed.values() for e in es),
                key=lambda e: json.dumps(asdict(e), sort_keys=True, default=str, allow_nan=False),
            )
        ),
        missing_relations=tuple(sorted(missing)),
        unqualified_relations=tuple(sorted(unqualified)),
        ambiguous_relations=tuple(sorted(ambiguous)),
        unqualified_nodes=tuple(sorted(unknown_nodes)),
        dead_end_nodes=tuple(sorted(dead_ends)),
        unreachable_nodes=tuple(sorted(set(by_node) - reached)),
    )
