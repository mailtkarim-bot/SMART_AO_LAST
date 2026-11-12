import struct
import zlib
from dataclasses import replace
from hashlib import sha256
from importlib import import_module
from importlib.util import find_spec
from uuid import UUID

import pytest
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
)


def api(name):
    assert find_spec(name) is not None, "pixel arrowhead/branch evidence implementation missing"
    return import_module(name)


def chunk(kind, payload):
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload))
    )


def raster(*, direction=(0, 1), heads=(0,), shape="arrow", shaft=True, shaft_shift=0):
    pixels = [[255] * 160 for _ in range(160)]
    dx, dy = direction

    def mark(t, longitudinal):
        x, y = 80 - dy * t + dx * longitudinal, 80 + dx * t + dy * longitudinal
        pixels[y][x] = 80

    for offset in heads:
        if shaft:
            for longitudinal in range(-25, 0):
                for t in range(offset - 1, offset + 2):
                    mark(t + shaft_shift, longitudinal)
        if shape == "arrow":
            for longitudinal, radius in enumerate((6, 5, 5, 4, 3, 2, 1, 0)):
                for t in range(offset - radius, offset + radius + 1):
                    mark(t, longitudinal)
        elif shape == "box":
            for longitudinal in range(8):
                for t in range(offset - 5, offset + 6):
                    mark(t, longitudinal)
    data = b"".join(b"\x00" + bytes(row) for row in pixels)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 160, 160, 8, 0, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(data))
        + chunk(b"IEND", b"")
    )


def scope(png):
    return StructureScope(
        UUID(int=1), UUID(int=2), UUID(int=3), "a" * 64, sha256(png).hexdigest(), 42, 160, 160
    )


def detect(png, direction=(0, 1), context=None):
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    pytest.importorskip("pymupdf")
    dx, dy = direction
    return m.detect_terminal_arrowhead(
        png_bytes=png,
        expected_scope=context or scope(png),
        terminal_start=(80 - 20 * dx, 80 - 20 * dy),
        terminal_end=(80, 80),
        render_dpi=150,
    )


@pytest.mark.parametrize("direction", [(0, 1), (0, -1), (1, 0), (-1, 0)])
def test_pixel_head_is_anchored_and_directional_without_business_promotion(direction):
    png = raster(direction=direction)
    result = detect(png, direction)
    assert result.state == "PIXEL_HEAD_CANDIDATE"
    assert result.tip == (80 + 7 * direction[0], 80 + 7 * direction[1])
    assert result.anchor.scope == scope(png)
    assert result.semantic_state == "UNKNOWN" and result.status == "REVIEW_REQUIRED"


@pytest.mark.parametrize(
    "change",
    [
        {"shape": "line"},
        {"shape": "box"},
        {"shaft": False},
        {"direction": (0, -1)},
        {"heads": (-10, 10)},
    ],
)
def test_missing_reversed_detached_or_competing_heads_refuse_to_guess(change):
    result = detect(raster(**change))
    assert result.state == "UNKNOWN" and result.tip is None and result.anchor is None


def test_altered_render_hash_is_rejected():
    png = raster()
    with pytest.raises(ValueError, match="ARROWHEAD_RENDER_MISMATCH"):
        detect(png, context=replace(scope(png), render_sha256="b" * 64))


def test_wrong_page_dimensions_are_rejected_before_decode():
    png = raster()
    with pytest.raises(ValueError, match="ARROWHEAD_IMAGE_INVALID"):
        detect(png, context=replace(scope(png), width=200))


def test_same_pixel_evidence_has_a_deterministic_result():
    png = raster()
    assert detect(png) == detect(png)


def label(text=" OUI ", reread_text=None, foreign=False):
    m = api("app.modules.dce.application.diagram_evidence")
    context = scope(raster())
    raw = RegionToken("raw", text, RegionAnchor(context, (20, 20, 40, 35)))
    reread = (
        None
        if reread_text is None
        else RegionToken(
            "reread",
            reread_text,
            RegionAnchor(
                replace(context, tenant_id=UUID(int=9)) if foreign else context, (20, 20, 40, 35)
            ),
        )
    )
    return m.qualify_branch_label(
        expected_scope=context,
        raw_token=raw,
        reread_token=reread,
        reread_input_sha256="c" * 64 if reread else None,
        reread_extractor_id="smart-ao-rapidocr" if reread else None,
        reread_extractor_version="1" if reread else None,
    )


@pytest.mark.parametrize("text,expected", [(" OUI ", "OUI"), ("non", "NON")])
def test_branch_label_preserves_raw_text_and_never_grants_eligibility(text, expected):
    result = label(text)
    assert result.raw_token.text == text and result.label == expected
    assert result.semantic_state == "UNKNOWN" and result.status == "REVIEW_REQUIRED"


@pytest.mark.parametrize("text", ["Iño", "ELIGIBLE", "NON ELIGIBLE", "OUI NON", ""])
def test_no_fuzzy_or_positive_outcome_is_converted_to_a_branch_label(text):
    assert label(text).label is None


def test_region_reread_can_add_a_candidate_without_overwriting_raw_ocr():
    result = label("Iño", "OUI")
    assert result.label == "OUI" and result.raw_token.text == "Iño"
    assert result.reread_token.text == "OUI" and result.state == "REREAD_LABEL_CANDIDATE"


def test_conflicting_branch_ocr_stays_unknown():
    result = label("NON", "OUI")
    assert result.label is None and result.state == "UNKNOWN"


def test_foreign_reread_scope_is_rejected():
    with pytest.raises(ValueError, match="STRUCTURE_SCOPE_MISMATCH"):
        label("Iño", "OUI", foreign=True)


@pytest.mark.parametrize(
    "raw,reread", [("NON", "?"), ("NON ELIGIBLE", "NON"), ("ELIGIBLE", "OUI"), ("", "OUI")]
)
def test_partial_outcome_or_uncertain_reread_cannot_release_a_branch_label(raw, reread):
    assert label(raw, reread).label is None


def test_other_raster_scale_is_not_silently_assumed():
    png = raster()
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    with pytest.raises(ValueError, match="ARROWHEAD_SCALE_UNQUALIFIED"):
        m.detect_terminal_arrowhead(
            png_bytes=png,
            expected_scope=scope(png),
            terminal_start=(80, 60),
            terminal_end=(80, 80),
            render_dpi=300,
        )


def test_mismatched_reread_region_is_rejected():
    m = api("app.modules.dce.application.diagram_evidence")
    context = scope(raster())
    a = RegionToken("a", "Iño", RegionAnchor(context, (20, 20, 40, 35)))
    b = RegionToken("b", "OUI", RegionAnchor(context, (50, 20, 70, 35)))
    with pytest.raises(ValueError, match="BRANCH_REREAD_REGION_MISMATCH"):
        m.qualify_branch_label(expected_scope=context, raw_token=a, reread_token=b)


def test_diagonal_terminal_stays_unknown():
    png = raster()
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    assert (
        m.detect_terminal_arrowhead(
            png_bytes=png,
            expected_scope=scope(png),
            terminal_start=(50, 50),
            terminal_end=(80, 80),
            render_dpi=150,
        ).state
        == "UNKNOWN"
    )


@pytest.mark.parametrize("point", [(float("nan"), 80), (10**1000, 80), (80, True)])
def test_invalid_terminal_coordinates_are_rejected(point):
    png = raster()
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    with pytest.raises(ValueError, match="ARROWHEAD_PATH_INVALID"):
        m.detect_terminal_arrowhead(
            png_bytes=png,
            expected_scope=scope(png),
            terminal_start=(80, 60),
            terminal_end=point,
            render_dpi=150,
        )


def test_off_center_shaft_is_not_a_direction_proof():
    assert detect(raster(shaft_shift=6)).state == "UNKNOWN"


def test_reread_without_parser_provenance_is_rejected():
    m = api("app.modules.dce.application.diagram_evidence")
    context = scope(raster())
    raw = RegionToken("raw", "Iño", RegionAnchor(context, (20, 20, 40, 35)))
    reread = replace(raw, token_id="reread", text="OUI")
    with pytest.raises(ValueError, match="BRANCH_REREAD_PROVENANCE_REQUIRED"):
        m.qualify_branch_label(expected_scope=context, raw_token=raw, reread_token=reread)


def test_corrupt_png_cannot_produce_pixel_evidence():
    png = raster()[:24] + b"broken"
    with pytest.raises(ValueError, match="ARROWHEAD_IMAGE_INVALID"):
        detect(png)


def test_zero_terminal_segment_is_rejected():
    png = raster()
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    with pytest.raises(ValueError, match="ARROWHEAD_PATH_INVALID"):
        m.detect_terminal_arrowhead(
            png_bytes=png,
            expected_scope=scope(png),
            terminal_start=(80, 80),
            terminal_end=(80, 80),
            render_dpi=150,
        )


def test_terminal_patch_clipped_by_page_edge_stays_unknown():
    png = raster()
    m = api("app.modules.dce.infrastructure.diagram_image_reader")
    assert (
        m.detect_terminal_arrowhead(
            png_bytes=png,
            expected_scope=scope(png),
            terminal_start=(1, 1),
            terminal_end=(1, 10),
            render_dpi=150,
        ).state
        == "UNKNOWN"
    )


def test_parallel_arrow_cannot_be_assigned_to_the_requested_axis():
    assert detect(raster(heads=(10,))).state == "UNKNOWN"


def test_second_head_near_patch_border_is_not_ignored():
    assert detect(raster(heads=(0, 14))).state == "UNKNOWN"


@pytest.mark.parametrize(
    "color,expected",
    [
        ((158, 201, 201), "PIXEL_HEAD_CANDIDATE"),
        ((190, 190, 190), "UNKNOWN"),
        ((255, 255, 255), "UNKNOWN"),
        ((0, 0, 255), "PIXEL_HEAD_CANDIDATE"),
    ],
)
def test_colored_head_uses_strict_bt601_threshold_190(color, expected):
    from io import BytesIO

    from PIL import Image

    im = Image.open(BytesIO(raster())).convert("RGB")
    for y in range(im.height):
        for x in range(im.width):
            if im.getpixel((x, y)) != (255, 255, 255):
                im.putpixel((x, y), color)
    buf = BytesIO()
    im.save(buf, format="PNG")
    result = detect(buf.getvalue())
    assert result.state == expected
    assert result.detector_version == "axis-filled-head-bt601-150dpi-v2"
    assert result.semantic_state == "UNKNOWN" and result.status == "REVIEW_REQUIRED"
