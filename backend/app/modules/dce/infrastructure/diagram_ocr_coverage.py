"""Bounded raster ink and independent OCR concordance; never document admission."""

import json
import unicodedata
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
from io import BytesIO

from app.modules.dce.application.conditional_diagram import ConditionalNode
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    RegionToken,
    StructureScope,
    project_candidate_structure,
)
from app.modules.dce.infrastructure.advanced_extraction import RapidOcrAdvancedExtractionAdapter
from app.modules.dce.infrastructure.diagram_image_reader import _dark_pixel
from app.modules.dce.infrastructure.diagram_node_reader import discover_candidate_nodes
from app.modules.dce.infrastructure.diagram_topology_reader import (
    _strokes,
    extract_candidate_topology,
)


@dataclass(frozen=True, slots=True)
class FrameTextReading:
    anchor: RegionAnchor
    text: str
    crop_sha256: str
    extractor_id: str
    extractor_version: str
    failure_code: str | None = None
    crop_recipe: str = "gray-autocontrast-pad8-scale3-lanczos-v1"
    original_text: str | None = None
    original_failure_code: str | None = None
    input_region: RegionAnchor | None = None
    line_readings: tuple["FrameTextReading", ...] = ()
    previous_readings: tuple["FrameTextReading", ...] = ()


@dataclass(frozen=True, slots=True)
class FrameCoverage:
    anchor: RegionAnchor
    token_ids: tuple[str, ...]
    ink_pixels: int
    uncovered_pixels: int
    missing_regions: tuple[RegionAnchor, ...]
    readings: tuple[FrameTextReading, ...]
    state: str
    reason: str


@dataclass(frozen=True, slots=True)
class CoveredOCR:
    scope: StructureScope
    input_sha256: str
    nodes: tuple[ConditionalNode, ...]
    tokens: tuple[RegionToken, ...]
    frames: tuple[FrameCoverage, ...]
    composite_regions: tuple[RegionAnchor, ...]
    extractor_version: str = "frame-ink-concordance-bt601-150dpi-v3"
    semantic_state: str = "UNKNOWN"
    status: str = "REVIEW_REQUIRED"
    admission_granted: bool = False


def _raster_frames(png_bytes, scope, region, tokens, render_dpi):
    extract_candidate_topology(
        png_bytes=png_bytes,
        expected_scope=scope,
        diagram_region=region,
        nodes=(),
        tokens=tokens,
        render_dpi=render_dpi,
    )
    import pymupdf

    pix = pymupdf.Pixmap(png_bytes)
    if pix.alpha or pix.n not in (1, 3):
        raise ValueError("OCR_COVERAGE_IMAGE_INVALID")
    data = pix.samples
    x0, y0, x1, y1 = map(int, region.bbox)
    ink = {
        (x, y)
        for y in range(y0, y1)
        for x in range(x0, x1)
        if _dark_pixel(data, pix.stride, pix.n, x, y, 180)
    }
    strokes = _strokes(ink)
    horizontal = [s for s in strokes if s.start[1] == s.end[1]]
    vertical = [s for s in strokes if s.start[0] == s.end[0]]
    choices = set()
    attempts = 0
    for i, left in enumerate(vertical):
        for right in vertical[i + 1 :]:
            if left.start[0] >= right.start[0]:
                continue
            crossings = [
                h
                for h in horizontal
                if h.start[0] <= left.start[0] + 1
                and h.end[0] >= right.start[0] - 1
                and all(v.start[1] - 1 <= h.start[1] <= v.end[1] + 1 for v in (left, right))
            ]
            crossings = [
                h
                for h in crossings
                if all(
                    h.pixels & v.pixels
                    or any(
                        (x + dx, y + dy) in v.pixels
                        for x, y in h.pixels
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                    )
                    for v in (left, right)
                )
            ]
            crossings.sort(key=lambda h: h.start[1])
            for j, top in enumerate(crossings):
                for bottom in crossings[j + 1 :]:
                    attempts += 1
                    if attempts > 4096:
                        raise ValueError("OCR_COVERAGE_LIMIT")
                    if top.start[1] < bottom.start[1]:
                        choices.add((left.start[0], top.start[1], right.start[0], bottom.start[1]))
    if len(choices) > 64:
        raise ValueError("OCR_COVERAGE_LIMIT")
    composite = set()
    for box in choices:
        children = [
            b
            for b in choices
            if b != box and box[0] <= b[0] < b[2] <= box[2] and box[1] <= b[1] < b[3] <= box[3]
        ]
        children.sort()
        for i, a in enumerate(children):
            for b in children[i + 1 :]:
                if (
                    a[1] == b[1] == box[1]
                    and a[3] == b[3] == box[3]
                    and a[0] == box[0]
                    and a[2] == b[0]
                    and b[2] == box[2]
                ) or (
                    a[0] == b[0] == box[0]
                    and a[2] == b[2] == box[2]
                    and a[1] == box[1]
                    and a[3] == b[1]
                    and b[3] == box[3]
                ):
                    composite.add(box)
    return ink, sorted(choices - composite), sorted(composite)


def extract_raster_frame_regions(
    *,
    png_bytes: bytes,
    expected_scope: StructureScope,
    diagram_region: RegionAnchor,
    render_dpi: int,
) -> tuple[RegionAnchor, ...]:
    _, frames, _ = _raster_frames(png_bytes, expected_scope, diagram_region, (), render_dpi)
    return tuple(RegionAnchor(expected_scope, b) for b in frames)


def _contains(outer, inner):
    return (
        outer[0] <= inner[0] < inner[2] <= outer[2] and outer[1] <= inner[1] < inner[3] <= outer[3]
    )


def _missing_regions(points, scope):
    regions = []
    pending = set(points)
    while pending:
        p = min(pending)
        pending.remove(p)
        component = {p}
        stack = [p]
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if q in pending:
                    pending.remove(q)
                    component.add(q)
                    stack.append(q)
        xs, ys = zip(*component, strict=True)
        regions.append(RegionAnchor(scope, (min(xs), min(ys), max(xs) + 1, max(ys) + 1)))
        if len(regions) > 2048:
            raise ValueError("OCR_COVERAGE_LIMIT")
    return tuple(regions)


def _text(text):
    return (
        " ".join(unicodedata.normalize("NFKC", text).replace("’", "'").split())
        .casefold()
        .replace(" ?", "?")
    )


def _read_crop(image, anchor, adapter, input_region=None, enhance=True):
    from PIL import Image, ImageOps

    crop = (
        ImageOps.expand(ImageOps.autocontrast(ImageOps.grayscale(image)), border=8, fill=255)
        if enhance
        else image
    )
    crop = crop.resize((crop.width * 3, crop.height * 3), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    crop.save(buffer, format="PNG")
    data = buffer.getvalue()
    observation = adapter.extract(media_type="image/png", source_bytes=data)
    text = " ".join(f.text for f in observation.fragments)
    failure = observation.failure_code if not observation.fragments else None
    if len(text) > 1024:
        text = ""
        failure = "OCR_REREAD_LIMIT"
    return FrameTextReading(
        anchor,
        text,
        sha256(data).hexdigest(),
        adapter.extractor_id,
        adapter.extractor_version,
        failure,
        input_region=input_region or anchor,
        crop_recipe="gray-autocontrast-pad8-scale3-lanczos-v1" if enhance else "scale3-lanczos-v1",
    )


def _read_pixel_lines(image, box, scope, adapter):
    rgb = image.convert("RGB")
    data = rgb.tobytes()
    ink = {
        (x, y)
        for y in range(rgb.height)
        for x in range(rgb.width)
        if _dark_pixel(data, rgb.width * 3, 3, x, y, 180)
    }
    rows = sorted({y for x, y in ink})
    bands: list[list[int]] = []
    for y in rows:
        if not bands or y > bands[-1][-1] + 2:
            bands.append([y])
        else:
            bands[-1].append(y)
    # shortcut: at most8dark axial text lines at150DPI; ambiguous/more lines stay UNKNOWN.
    if not 1 <= len(bands) <= 8:
        return ()
    readings = []
    for ys in bands:
        xs = [x for x, y in ink if min(ys) <= y <= max(ys)]
        local = (
            max(0, min(xs) - 1),
            max(0, min(ys) - 1),
            min(rgb.width, max(xs) + 2),
            min(rgb.height, max(ys) + 2),
        )
        anchor = RegionAnchor(
            scope, (box[0] + local[0], box[1] + local[1], box[0] + local[2], box[1] + local[3])
        )
        readings.append(_read_crop(image.crop(local), anchor, adapter))
    return tuple(readings)


def qualify_candidate_ocr_coverage(
    *,
    png_bytes: bytes,
    expected_scope: StructureScope,
    diagram_region: RegionAnchor,
    tokens: tuple[RegionToken, ...],
    ocr_adapter: RapidOcrAdvancedExtractionAdapter | None,
    render_dpi: int,
) -> CoveredOCR:
    if ocr_adapter is not None and type(ocr_adapter) is not RapidOcrAdvancedExtractionAdapter:
        raise ValueError("OCR_ADAPTER_INVALID")
    project_candidate_structure(
        expected_scope=expected_scope, tokens=tokens, diagram_regions=(diagram_region,)
    )
    raw = discover_candidate_nodes(
        png_bytes=png_bytes,
        expected_scope=expected_scope,
        diagram_region=diagram_region,
        tokens=tokens,
        render_dpi=render_dpi,
    )
    ink, frames, composite = _raster_frames(
        png_bytes, expected_scope, diagram_region, tokens, render_dpi
    )
    if len(frames) > 32:
        raise ValueError("OCR_COVERAGE_LIMIT")
    by_frame = dict(zip((a.bbox for a in raw.frame_regions), raw.nodes, strict=True))
    by_id = {t.token_id: t for t in tokens}
    rereads = []
    if ocr_adapter is not None:
        from PIL import Image

        with Image.open(BytesIO(png_bytes)) as image:
            for box in frames:
                interior_box = (box[0] + 2, box[1] + 2, box[2] - 2, box[3] - 2)
                original = image.crop(interior_box)
                reading = _read_crop(
                    original,
                    RegionAnchor(expected_scope, box),
                    ocr_adapter,
                    RegionAnchor(expected_scope, interior_box),
                    enhance=False,
                )
                if reading.failure_code == "OCR_EMPTY_TEXT":
                    previous = reading
                    reading = _read_crop(
                        original,
                        RegionAnchor(expected_scope, box),
                        ocr_adapter,
                        RegionAnchor(expected_scope, interior_box),
                    )
                    reading = replace(reading, previous_readings=(previous,))
                node = by_frame.get(box)
                caption = " ".join(by_id[t].text for t in node.token_ids) if node else ""
                if reading.failure_code == "OCR_EMPTY_TEXT" or (
                    not reading.failure_code
                    and _text(reading.text) != _text(caption)
                    and _text(reading.text).replace(" ", "") == _text(caption).replace(" ", "")
                ):
                    parts = _read_pixel_lines(original, interior_box, expected_scope, ocr_adapter)
                    combined = " ".join(r.text for r in parts)
                    failure = (
                        "OCR_LINE_LIMIT_OR_EMPTY"
                        if not parts
                        else "OCR_LINE_FAILED"
                        if any(r.failure_code for r in parts)
                        else "OCR_REREAD_LIMIT"
                        if len(combined) > 1024
                        else "OCR_LINE_CONTENT_CONFLICT"
                        if reading.text
                        and _text(combined).replace(" ", "") != _text(reading.text).replace(" ", "")
                        else None
                    )
                    reading = replace(
                        reading,
                        text=combined if not failure else reading.text,
                        original_text=reading.text,
                        original_failure_code=reading.failure_code,
                        line_readings=parts,
                        failure_code=failure,
                    )
                rereads.append(reading)
    nodes: list[ConditionalNode] = []
    coverage = []
    for box in frames:
        n = by_frame.get(
            box,
            ConditionalNode(
                "missing",
                "CONDITION",
                RegionAnchor(expected_scope, (box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3)),
                text_state="UNKNOWN",
            ),
        )
        n = replace(n, node_id=f"ocr-node-{len(nodes):02d}")
        # shortcut: dark ink with a2px border guard at150DPI; other fonts/scales need calibration.
        interior = {
            p for p in ink if box[0] + 2 < p[0] < box[2] - 2 and box[1] + 2 < p[1] < box[3] - 2
        }
        boxes = [by_id[t].anchor.bbox for t in n.token_ids]
        missing = {
            p
            for p in interior
            if not any(b[0] - 1 <= p[0] < b[2] + 1 and b[1] - 1 <= p[1] < b[3] + 1 for b in boxes)
        }
        readings = tuple(
            sorted(
                set(r for r in rereads if r.anchor.bbox == box),
                key=lambda r: (r.text, r.crop_sha256, r.extractor_id, r.extractor_version),
            )
        )
        caption = " ".join(by_id[t].text for t in n.token_ids)
        nested = any(b != box and (_contains(box, b) or _contains(b, box)) for b in frames)
        reason = (
            "AMBIGUOUS_FRAMES"
            if nested
            else "NO_TEXT_INK"
            if not interior
            else "NO_OCR"
            if not n.token_ids
            else "UNCOVERED_INK"
            if missing
            else "MISSING_OR_COMPETING_REREAD"
            if len(readings) != 1
            else "REREAD_FAILED"
            if readings[0].failure_code
            else "TEXT_DISAGREEMENT"
            if _text(readings[0].text) != _text(caption)
            else "UNQUALIFIED_RAW_TEXT"
            if n.text_state != "SOURCE_TEXT_CANDIDATE"
            else "INK_AND_TEXT_AGREE"
        )
        state = (
            "INK_AND_TEXT_CONCORDANCE_CANDIDATE" if reason == "INK_AND_TEXT_AGREE" else "UNKNOWN"
        )
        if state == "UNKNOWN":
            n = replace(n, text_state="UNKNOWN")
        central_ink = any(
            box[0] + 6 < x < box[2] - 6 and box[1] + 6 < y < box[3] - 6 for x, y in interior
        )
        if n.token_ids or central_ink:
            nodes.append(n)
        coverage.append(
            FrameCoverage(
                RegionAnchor(expected_scope, box),
                n.token_ids,
                len(interior),
                len(missing),
                _missing_regions(missing, expected_scope),
                readings,
                state,
                reason,
            )
        )
    digest = sha256(
        json.dumps(
            {
                "version": "frame-ink-concordance-bt601-150dpi-v3",
                "raw": raw.input_sha256,
                "frames": [asdict(c) for c in coverage],
            },
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    return CoveredOCR(
        expected_scope,
        digest,
        tuple(nodes),
        raw.tokens,
        tuple(coverage),
        tuple(RegionAnchor(expected_scope, b) for b in composite),
    )
