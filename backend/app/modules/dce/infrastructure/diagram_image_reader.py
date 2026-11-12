"""Local bounded raster evidence, outside domain and without network or writes."""

import math
import struct
from hashlib import sha256

from app.modules.dce.application.diagram_evidence import ArrowheadEvidence
from app.modules.dce.application.structure_projection import (
    RegionAnchor,
    StructureScope,
    project_candidate_structure,
)


def _dark_pixel(data: bytes, stride: int, channels: int, x: int, y: int, threshold: int) -> bool:
    """BT.601 luma before quantization; retain the calibrated strict threshold."""
    offset = y * stride + x * channels
    if channels == 1:
        return data[offset] < threshold
    if channels != 3:
        raise ValueError("RASTER_CHANNELS_UNQUALIFIED")
    return 299 * data[offset] + 587 * data[offset + 1] + 114 * data[offset + 2] < 1000 * threshold


def _run(row: list[bool], center: int) -> tuple[int, int] | None:
    if not row[center]:
        return None
    left = right = center
    while left > 0 and row[left - 1]:
        left -= 1
    while right + 1 < len(row) and row[right + 1]:
        right += 1
    return left, right


def detect_terminal_arrowhead(
    *,
    png_bytes: bytes,
    expected_scope: StructureScope,
    terminal_start: tuple[float, float],
    terminal_end: tuple[float, float],
    render_dpi: int,
) -> ArrowheadEvidence:
    scope = expected_scope
    project_candidate_structure(expected_scope=scope, tokens=())
    if type(render_dpi) is not int or render_dpi != 150:
        raise ValueError("ARROWHEAD_SCALE_UNQUALIFIED")
    if not isinstance(png_bytes, bytes) or sha256(png_bytes).hexdigest() != scope.render_sha256:
        raise ValueError("ARROWHEAD_RENDER_MISMATCH")
    if (
        not 24 <= len(png_bytes) <= 20_000_000
        or png_bytes[:8] != b"\x89PNG\r\n\x1a\n"
        or png_bytes[12:16] != b"IHDR"
        or struct.unpack(">II", png_bytes[16:24]) != (scope.width, scope.height)
        or scope.width * scope.height > 25_000_000
    ):
        raise ValueError("ARROWHEAD_IMAGE_INVALID")
    for point in (terminal_start, terminal_end):
        if (
            not isinstance(point, tuple)
            or len(point) != 2
            or any(
                type(v) not in (int, float) or (type(v) is float and not math.isfinite(v))
                for v in point
            )
            or not (0 <= point[0] < scope.width and 0 <= point[1] < scope.height)
        ):
            raise ValueError("ARROWHEAD_PATH_INVALID")
    dx, dy = terminal_end[0] - terminal_start[0], terminal_end[1] - terminal_start[1]
    if dx == dy == 0:
        raise ValueError("ARROWHEAD_PATH_INVALID")
    unknown = ArrowheadEvidence(scope, detector_version="axis-filled-head-bt601-150dpi-v2")
    if dx != 0 and dy != 0:
        return unknown
    dx, dy = (0 if dx == 0 else (1 if dx > 0 else -1)), (0 if dy == 0 else (1 if dy > 0 else -1))

    # shortcut: filled axis-aligned heads at150DPI only; calibrate before other raster scales.
    def pixel_point(c: float, r: float) -> tuple[float, float]:
        return (
            round(terminal_end[0]) - dy * (c - 20) + dx * (r - 20),
            round(terminal_end[1]) + dx * (c - 20) + dy * (r - 20),
        )

    corners = [pixel_point(c, r) for c in (0, 40) for r in (0, 40)]
    if any(not (0 <= x < scope.width and 0 <= y < scope.height) for x, y in corners):
        return unknown
    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError("document-advanced extra is required") from exc
    try:
        pix = pymupdf.Pixmap(png_bytes)
        if pix.alpha:
            raise ValueError("ARROWHEAD_IMAGE_INVALID")
        if pix.n not in (1, 3) or (pix.width, pix.height) != (scope.width, scope.height):
            raise ValueError("ARROWHEAD_IMAGE_INVALID")
        data, stride = pix.samples, pix.stride
    except (RuntimeError, ValueError, pymupdf.mupdf.FzErrorBase) as exc:
        raise ValueError("ARROWHEAD_IMAGE_INVALID") from exc
    matrix = []
    for r in range(41):
        row = []
        for c in range(41):
            x, y = pixel_point(c, r)
            row.append(_dark_pixel(data, stride, pix.n, int(x), int(y), 190))
        matrix.append(row)
    candidates: list[tuple[tuple[float, float], RegionAnchor, bool]] = []
    for c in range(4, 37):
        for base in range(12, 29):
            wide = _run(matrix[base], c)
            shaft = [_run(matrix[r], c) for r in range(base - 4, base)]
            if wide is None or not 6 <= wide[1] - wide[0] + 1 <= 17:
                continue
            if any(run is None or run[1] - run[0] + 1 > 3 for run in shaft):
                continue
            if any(run is not None and abs(sum(run) - sum(wide)) > 4 for run in shaft):
                continue
            previous = wide[1] - wide[0] + 1
            center = round((wide[0] + wide[1]) / 2)
            last = base
            narrow = 0
            left, right = wide
            for r in range(base + 1, min(base + 17, 41)):
                run = _run(matrix[r], center)
                if run is None:
                    break
                width = run[1] - run[0] + 1
                if width > previous + 1 or abs(sum(run) - sum(wide)) > 4:
                    break
                narrow = narrow + 1 if width <= 3 else 0
                if narrow > 3:
                    break
                previous, last = width, r
                left, right = min(left, run[0]), max(right, run[1])
            if last - base < 4 or previous > 3 or narrow > 3:
                continue
            run = _run(matrix[last], center)
            if run is None:
                continue
            tip = pixel_point((run[0] + run[1]) / 2, last)
            bounds = [pixel_point(cc, rr) for cc in (left, right + 1) for rr in (base, last + 1)]
            anchor = RegionAnchor(
                scope,
                (
                    min(x for x, _ in bounds),
                    min(y for _, y in bounds),
                    max(x for x, _ in bounds),
                    max(y for _, y in bounds),
                ),
            )
            if not any(math.dist(tip, existing[0]) <= 2 for existing in candidates):
                aligned = (
                    abs(center - 20) <= 2
                    and abs(sum(run) / 2 - 20) <= 2
                    and all(part is not None and abs(sum(part) / 2 - 20) <= 2 for part in shaft)
                )
                candidates.append((tip, anchor, aligned))
    if len(candidates) != 1 or not candidates[0][2]:
        return unknown
    tip, anchor, _ = candidates[0]
    return ArrowheadEvidence(
        scope,
        "PIXEL_HEAD_CANDIDATE",
        tip,
        anchor,
        detector_version="axis-filled-head-bt601-150dpi-v2",
    )
