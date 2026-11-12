import struct
import zlib
from hashlib import sha256
from importlib import import_module
from importlib.util import find_spec
from uuid import UUID

import pytest
from app.modules.dce.application.conditional_diagram import ConditionalNode
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)


def image(lines, boxes=(), fill_boxes=()):
    pixels = [bytearray([255] * 240) for _ in range(220)]
    for x0, y0, x1, y1, value in fill_boxes:
        for y in range(y0 + 1, y1):
            for x in range(x0 + 1, x1):
                pixels[y][x] = value
    edges = list(lines) + [
        edge
        for x0, y0, x1, y1 in boxes
        for edge in ((x0, y0, x1, y0), (x0, y1, x1, y1), (x0, y0, x0, y1), (x1, y0, x1, y1))
    ]
    for x0, y0, x1, y1 in edges:
        assert x0 == x1 or y0 == y1
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for x in range(min(x0, x1), max(x0, x1) + 1):
                pixels[y][x] = 70

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        )

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 240, 220, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"".join(b"\0" + p for p in pixels)))
        + chunk(b"IEND", b"")
    )


def extract(
    lines=(),
    boxes=(),
    seed_boxes=(),
    context=None,
    region=None,
    dpi=150,
    names=(),
    label_boxes=(),
    fill_boxes=(),
):
    name = "app.modules.dce.infrastructure.diagram_topology_reader"
    assert find_spec(name), "topology pixel reader missing"
    png = image(lines, boxes, fill_boxes)
    scope = context or StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(png).hexdigest(), 42, 240, 220
    )
    nodes = tuple(
        ConditionalNode(names[i] if names else str(i), "CONDITION", RegionAnchor(scope, b))
        for i, b in enumerate(seed_boxes)
    )
    return import_module(name).extract_candidate_topology(
        png_bytes=png,
        expected_scope=scope,
        diagram_region=region or RegionAnchor(scope, (0, 0, 239, 219)),
        nodes=nodes,
        tokens=tuple(
            RegionToken(str(i), "NON", RegionAnchor(scope, b)) for i, b in enumerate(label_boxes)
        ),
        render_dpi=dpi,
    )


def test_pixels_find_two_frames_and_one_route_without_expected_polylines():
    result = extract(
        [(60, 80, 60, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    assert result.unqualified_nodes == ()
    assert len(result.links) == 1
    assert set(result.links[0].endpoints) == {"0", "1"}
    assert result.links[0].state == "PIXEL_TOPOLOGY_CANDIDATE"
    assert result.links[0].direction_state == "UNKNOWN"
    assert result.status == "REVIEW_REQUIRED" and not result.admission_granted


def test_t_junction_is_discovered_and_preserved():
    result = extract([(20, 100, 200, 100), (100, 100, 100, 200)])
    assert len(result.junctions) == 1
    assert result.junctions[0].state == "PIXEL_JUNCTION_CANDIDATE"
    assert len(result.links) == 3


def test_blank_pixel_gap_is_not_healed_into_a_join():
    result = extract([(20, 100, 200, 100), (100, 102, 100, 200)])
    assert result.junctions == ()
    assert all(v.state == "UNKNOWN" for v in result.vertices)


def test_crossing_four_ports_remains_ambiguous():
    result = extract([(20, 100, 200, 100), (100, 20, 100, 200)])
    assert len(result.junctions) == 1
    assert result.junctions[0].state == "UNKNOWN"
    assert all(e.state == "UNKNOWN" for e in result.links)


def test_frame_border_never_becomes_a_route():
    result = extract(boxes=[(35, 30, 85, 80)], seed_boxes=[(40, 40, 80, 70)])
    assert result.links == () and result.junctions == ()


def test_missing_frame_keeps_seed_and_unknown_explicit():
    result = extract(seed_boxes=[(40, 40, 80, 70)])
    assert result.unqualified_nodes == ("0",)


def test_near_parallel_lines_are_not_merged():
    result = extract([(20, 100, 200, 100), (20, 102, 200, 102)])
    assert len(result.links) == 2 and result.junctions == ()


def test_deterministic_replay_keeps_provenance():
    assert extract([(20, 100, 200, 100)]) == extract([(20, 100, 200, 100)])


def test_render_hash_is_checked():
    scope = StructureScope(UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, "b" * 64, 42, 240, 220)
    with pytest.raises(ValueError, match="TOPOLOGY_RENDER_MISMATCH"):
        extract(context=scope)


def test_scale_is_explicitly_calibrated():
    with pytest.raises(ValueError, match="TOPOLOGY_SCALE_UNQUALIFIED"):
        extract(dpi=300)


def test_touching_rows_with_different_run_ends_form_one_stroke():
    result = extract(
        [(60, 80, 60, 140), (61, 83, 61, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    assert len(result.links) == 1 and result.links[0].state == "PIXEL_TOPOLOGY_CANDIDATE"


def test_wide_whitespace_frame_remains_a_frame():
    result = extract(boxes=[(35, 30, 125, 80)], seed_boxes=[(40, 40, 80, 70)])
    assert result.unqualified_nodes == () and result.links == ()


def test_two_pixel_wide_corner_does_not_invent_a_junction():
    result = extract(
        [(20, 100, 100, 100), (20, 101, 100, 101), (99, 100, 99, 200), (100, 100, 100, 200)]
    )
    assert result.junctions == () and len(result.links) == 1


def test_connected_thin_columns_with_unequal_ends_are_not_parallel_routes():
    result = extract([(60, 30, 60, 130), (61, 34, 61, 130)])
    assert len(result.links) == 1


def test_partial_parallel_row_at_a_t_does_not_create_extra_branches():
    result = extract([(20, 100, 200, 100), (60, 101, 200, 101), (100, 100, 100, 200)])
    assert len(result.junctions) == 1 and len(result.links) == 3


def test_ocr_label_rectangle_does_not_erase_an_underlying_pixel_route():
    result = extract(
        [(60, 80, 60, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
        label_boxes=[(50, 95, 75, 125)],
    )
    assert len(result.links) == 1 and result.links[0].state == "PIXEL_TOPOLOGY_CANDIDATE"


def test_midgray_fill_is_not_interpreted_as_a_stroke_network():
    result = extract(
        [(60, 80, 60, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
        fill_boxes=[(35, 140, 85, 190, 180)],
    )
    assert result.unqualified_nodes == () and len(result.links) == 1


def test_frame_search_is_bounded_in_a_dense_grid():
    lines = [(20, y, 200, y) for y in list(range(40, 58, 2)) + list(range(140, 158, 2))] + [
        (x, 20, x, 190) for x in list(range(30, 48, 2)) + list(range(150, 168, 2))
    ]
    with pytest.raises(ValueError, match="TOPOLOGY_LIMIT"):
        extract(lines, seed_boxes=[(80, 80, 120, 120)])


def test_original_seed_regions_and_raw_tokens_survive_extraction():
    result = extract(
        [(20, 100, 200, 100)], seed_boxes=[(40, 40, 80, 70)], label_boxes=[(50, 95, 75, 125)]
    )
    assert result.seed_nodes[0].anchor.bbox == (40, 40, 80, 70)
    assert result.tokens[0].text == "NON"


def test_closed_stroke_cycle_remains_visible_as_unresolved():
    result = extract(boxes=[(35, 30, 85, 80)])
    assert result.unresolved_regions and result.links == ()


def test_foreign_diagram_region_is_rejected_before_results():
    wrong = StructureScope(UUID(int=9), UUID(int=2), UUID(int=3), "a" * 64, "b" * 64, 42, 240, 220)
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        extract(region=RegionAnchor(wrong, (0, 0, 239, 219)))


@pytest.mark.parametrize("start,end", [(90, 130), (85, 135), (83, 137)])
def test_bare_line_proximity_cannot_bridge_white_pixels_to_a_frame(start, end):
    result = extract(
        [(60, start, 60, end)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    assert all(e.state == "UNKNOWN" for e in result.links)


def test_fractional_raster_region_is_refused():
    png = image([(60, 30, 60, 150)])
    scope = StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(png).hexdigest(), 42, 240, 220
    )
    with pytest.raises(ValueError, match="TOPOLOGY_REGION_INVALID"):
        extract([(60, 30, 60, 150)], context=scope, region=RegionAnchor(scope, (60.5, 0, 239, 219)))


def test_endpoint_attachment_evidence_is_retained():
    result = extract(
        [(60, 80, 60, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    assert len(result.links[0].contacts) == 2
    assert all(c.pixel_path for c in result.links[0].contacts)


def test_centerline_rounding_keeps_only_proven_contacts_of_connected_columns():
    result = extract(
        [(60, 84, 60, 136), (61, 80, 61, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    assert len(result.links) == 1 and result.links[0].state == "PIXEL_TOPOLOGY_CANDIDATE"
    assert len(result.links[0].contacts) == 2


def test_generated_vertex_namespace_cannot_be_overwritten_by_a_seed():
    with pytest.raises(ValueError, match="TOPOLOGY_NODE_INVALID"):
        extract(
            [(20, 100, 200, 100), (100, 100, 100, 200)],
            seed_boxes=[(40, 40, 80, 70)],
            names=("p-100-100",),
        )


def test_every_output_region_is_inside_the_declared_raster_region():
    result = extract([(20, 100, 200, 100), (100, 100, 100, 200)])
    for anchor in (
        [v.anchor for v in result.vertices]
        + [e.anchor for e in result.links]
        + list(result.stroke_regions)
        + list(result.unresolved_regions)
    ):
        b = anchor.bbox
        r = result.diagram_region.bbox
        assert r[0] <= b[0] < b[2] <= r[2] and r[1] <= b[1] < b[3] <= r[3]


def test_broken_route_exposes_an_omission_and_never_a_false_complete_link():
    result = extract(
        [(60, 80, 60, 103), (60, 110, 60, 140)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    expected = {frozenset(("0", "1"))}
    observed = {
        frozenset(e.endpoints) for e in result.links if e.state == "PIXEL_TOPOLOGY_CANDIDATE"
    }
    assert len(expected - observed) == 1 and observed - expected == set()
    assert len(result.links) == 2 and all(e.state == "UNKNOWN" for e in result.links)


@pytest.mark.parametrize("gap", [2, 3])
def test_near_broken_branch_does_not_leave_clean_through_route(gap):
    result = extract(
        [(60, 80, 60, 140), (20, 110, 60 - gap, 110)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    through = next(link for link in result.links if set(link.endpoints) == {"0", "1"})
    assert through.state == "UNKNOWN"
    assert result.unresolved_regions


def test_distant_unconnected_stroke_does_not_taint_route():
    result = extract(
        [(60, 80, 60, 140), (20, 110, 56, 110)],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    through = next(link for link in result.links if set(link.endpoints) == {"0", "1"})
    assert through.state == "PIXEL_TOPOLOGY_CANDIDATE"


@pytest.mark.parametrize(
    "bridge_color,connected",
    [
        ((158, 188, 188), True),
        ((180, 180, 180), False),
        ((169, 185, 185), False),
        ((255, 255, 255), False),
    ],
)
def test_colored_bridge_uses_explicit_luminance_without_inventing_gap(bridge_color, connected):
    from io import BytesIO

    from PIL import Image

    png = image([(60, 80, 60, 140)], [(35, 30, 85, 80), (35, 140, 85, 190)])
    im = Image.open(BytesIO(png)).convert("RGB")
    im.putpixel((60, 110), bridge_color)
    buf = BytesIO()
    im.save(buf, format="PNG")
    raw = buf.getvalue()
    scope = StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(raw).hexdigest(), 42, 240, 220
    )
    nodes = (
        ConditionalNode("a", "CONDITION", RegionAnchor(scope, (40, 40, 80, 70))),
        ConditionalNode("b", "CONDITION", RegionAnchor(scope, (40, 150, 80, 180))),
    )
    result = import_module(
        "app.modules.dce.infrastructure.diagram_topology_reader"
    ).extract_candidate_topology(
        png_bytes=raw,
        expected_scope=scope,
        diagram_region=RegionAnchor(scope, (0, 0, 239, 219)),
        nodes=nodes,
        tokens=(),
        render_dpi=150,
    )
    assert (
        any(
            set(link.endpoints) == {"a", "b"} and link.state == "PIXEL_TOPOLOGY_CANDIDATE"
            for link in result.links
        )
        == connected
    )


@pytest.mark.parametrize("branch", [(20, 110, 56, 110), (64, 110, 105, 110)])
def test_near_miss_distance_uses_stroke_pixels_not_only_centerline(branch):
    result = extract(
        [(59, 80, 59, 140), (60, 80, 60, 140), (61, 80, 61, 140), branch],
        [(35, 30, 85, 80), (35, 140, 85, 190)],
        [(40, 40, 80, 70), (40, 150, 80, 180)],
    )
    through = next(link for link in result.links if set(link.endpoints) == {"0", "1"})
    assert through.state == "UNKNOWN"
    assert result.unresolved_regions
