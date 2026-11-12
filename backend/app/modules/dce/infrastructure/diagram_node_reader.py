"""OCR tokens grouped by uniquely enclosing raster frames, without supplied groups/roles."""

import json
from dataclasses import asdict, dataclass
from hashlib import sha256

from app.modules.dce.application.conditional_diagram import ConditionalNode
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)
from app.modules.dce.infrastructure.diagram_topology_reader import extract_candidate_topology


@dataclass(frozen=True, slots=True)
class CandidateNodes:
    scope: StructureScope
    diagram_region: RegionAnchor
    input_sha256: str
    nodes: tuple[ConditionalNode, ...]
    frame_regions: tuple[RegionAnchor, ...]
    tokens: tuple[RegionToken, ...]
    unassigned_tokens: tuple[str, ...]
    extractor_version: str = "ocr-frame-bt601-150dpi-v2"
    semantic_state: str = "UNKNOWN"
    status: str = "REVIEW_REQUIRED"
    admission_granted: bool = False


def discover_candidate_nodes(
    *,
    png_bytes: bytes,
    expected_scope: StructureScope,
    diagram_region: RegionAnchor,
    tokens: tuple[RegionToken, ...],
    render_dpi: int,
) -> CandidateNodes:
    if not isinstance(tokens, tuple) or len(tokens) > 32:
        raise ValueError("NODE_DISCOVERY_LIMIT")
    # Validate even an empty OCR result using the existing raster/scope boundary.
    extract_candidate_topology(
        png_bytes=png_bytes,
        expected_scope=expected_scope,
        diagram_region=diagram_region,
        nodes=(),
        tokens=tokens,
        render_dpi=render_dpi,
    )
    groups: dict[tuple[float, float, float, float], list[RegionToken]] = {}
    unassigned = []
    ambiguous = set()
    for token in sorted(tokens, key=lambda t: t.token_id):
        probe = ConditionalNode("ocr-probe", "CONDITION", token.anchor)
        result = extract_candidate_topology(
            png_bytes=png_bytes,
            expected_scope=expected_scope,
            diagram_region=diagram_region,
            nodes=(probe,),
            tokens=(),
            render_dpi=render_dpi,
        )
        vertex = next(v for v in result.vertices if v.vertex_id == probe.node_id)
        if vertex.state != "PIXEL_NODE_FRAME_CANDIDATE":
            unassigned.append(token.token_id)
            if probe.node_id in result.ambiguous_nodes:
                ambiguous.add(token.token_id)
        else:
            groups.setdefault(vertex.anchor.bbox, []).append(token)
    by_id = {t.token_id: t for t in tokens}
    remaining = []
    for token_id in unassigned:
        token = by_id[token_id]
        x0, y0, x1, y1 = token.anchor.bbox
        owners = [box for box in groups if box[0] < x0 < x1 < box[2] and box[1] < y0 < y1 < box[3]]
        if len(owners) == 1 and token_id not in ambiguous:
            groups[owners[0]].append(token)
        else:
            remaining.append(token_id)
    unassigned = remaining
    nodes = []
    frames = []
    outcomes = {
        "ELIGIBLE",
        "ÉLIGIBLE",
        "NON ELIGIBLE",
        "NON ÉLIGIBLE",
        "CONTACTER VOTRE CORRESPONDANT CEE CENTRE",
    }
    for index, (box, members) in enumerate(sorted(groups.items())):
        members.sort(key=lambda t: (t.anchor.bbox[1], t.anchor.bbox[0], t.token_id))
        caption = " ".join(t.text.strip() for t in members)
        caption = " ".join(caption.split()).upper()
        bbox = (
            min(t.anchor.bbox[0] for t in members),
            min(t.anchor.bbox[1] for t in members),
            max(t.anchor.bbox[2] for t in members),
            max(t.anchor.bbox[3] for t in members),
        )
        tainted = any(
            box[0] < by_id[i].anchor.bbox[0] < by_id[i].anchor.bbox[2] < box[2]
            and box[1] < by_id[i].anchor.bbox[1] < by_id[i].anchor.bbox[3] < box[3]
            for i in ambiguous
        )
        # shortcut: OCR-bearing axial frames only; qualify other shapes with a new reader.
        nodes.append(
            ConditionalNode(
                f"ocr-node-{index:02d}",
                "OUTCOME" if caption in outcomes else "CONDITION",
                RegionAnchor(expected_scope, bbox),
                tuple(t.token_id for t in members),
                text_state="SOURCE_TEXT_CANDIDATE"
                if not tainted and all(any(c.isalnum() for c in t.text) for t in members)
                else "UNKNOWN",
            )
        )
        frames.append(RegionAnchor(expected_scope, box))
    ordered = tuple(sorted(tokens, key=lambda t: t.token_id))
    digest = sha256(
        json.dumps(
            {
                "version": "ocr-frame-bt601-150dpi-v2",
                "scope": asdict(expected_scope),
                "region": asdict(diagram_region),
                "tokens": [asdict(t) for t in ordered],
            },
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    return CandidateNodes(
        expected_scope,
        diagram_region,
        digest,
        tuple(nodes),
        tuple(frames),
        ordered,
        tuple(unassigned),
    )
