"""Closed DCE locator projections for immutable extraction fragments."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class DceSourceLocatorKind(StrEnum):
    PDF_PAGE = "pdf_page"
    PYMUPDF_BLOCK = "pymupdf_block"
    OCR_PAGE = "ocr_page"
    DOCX_PARAGRAPH = "docx_paragraph"
    XLSX_CELL = "xlsx_cell"
    TEXT_LINE = "text_line"
    DOCLING_MARKDOWN = "docling_markdown"


class DceSourceAnchorLocatorState(StrEnum):
    RESOLVED = "RESOLVED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class DceSourceLocator:
    kind: DceSourceLocatorKind
    coordinates: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class DceSourceAnchorProjection:
    """Read-only identity and source lineage resolved from one DCE fragment."""

    source_anchor_id: UUID
    dce_version_id: UUID
    dce_document_id: UUID
    extraction_id: UUID
    fragment_ordinal: int
    source_sha256: str
    extractor_id: str
    extractor_version: str
    fragment_sha256: str
    locator: DceSourceLocator | None

    @property
    def locator_state(self) -> DceSourceAnchorLocatorState:
        return (
            DceSourceAnchorLocatorState.RESOLVED
            if self.locator is not None
            else DceSourceAnchorLocatorState.UNKNOWN
        )


_POSITIVE_FIELDS: dict[DceSourceLocatorKind, frozenset[str]] = {
    DceSourceLocatorKind.PDF_PAGE: frozenset({"page"}),
    DceSourceLocatorKind.PYMUPDF_BLOCK: frozenset({"page", "block"}),
    DceSourceLocatorKind.OCR_PAGE: frozenset({"page", "order"}),
    DceSourceLocatorKind.DOCX_PARAGRAPH: frozenset({"paragraph"}),
    DceSourceLocatorKind.XLSX_CELL: frozenset(),
    DceSourceLocatorKind.TEXT_LINE: frozenset({"line"}),
    DceSourceLocatorKind.DOCLING_MARKDOWN: frozenset({"line"}),
}
_CELL_REFERENCE = re.compile(r"^[A-Z]{1,3}[1-9][0-9]{0,6}$")


def resolve_dce_source_locator(value: object) -> DceSourceLocator | None:
    """Resolve only the locator shapes emitted by current DCE extractors.

    Historical, unsupported, or malformed JSON stays in its immutable fragment
    and projects as UNKNOWN; this reader never repairs or rewrites it.
    """
    if not isinstance(value, dict) or not isinstance(value.get("kind"), str):
        return None
    try:
        kind = DceSourceLocatorKind(value["kind"])
    except ValueError:
        return None

    allowed_fields = set(_POSITIVE_FIELDS[kind]) | {"kind", "part"}
    if kind in {DceSourceLocatorKind.PYMUPDF_BLOCK, DceSourceLocatorKind.OCR_PAGE}:
        allowed_fields.add("bbox")
    elif kind is DceSourceLocatorKind.XLSX_CELL:
        allowed_fields.update({"sheet", "cell"})
    if set(value) - allowed_fields:
        return None
    if any(
        field not in value or not _positive_integer(value[field])
        for field in _POSITIVE_FIELDS[kind]
    ):
        return None
    if "part" in value and not _positive_integer(value["part"]):
        return None
    if kind is DceSourceLocatorKind.PYMUPDF_BLOCK and not _valid_pdf_bbox(value.get("bbox")):
        return None
    if (
        kind is DceSourceLocatorKind.OCR_PAGE
        and "bbox" in value
        and not _valid_ocr_bbox(value["bbox"])
    ):
        return None
    if kind is DceSourceLocatorKind.XLSX_CELL and not _valid_xlsx_cell(
        value.get("sheet"), value.get("cell")
    ):
        return None

    return DceSourceLocator(
        kind=kind,
        coordinates={key: item for key, item in value.items() if key != "kind"},
    )


def _positive_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _finite_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _valid_pdf_bbox(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(_finite_number(coordinate) for coordinate in value)
        and value[2] >= value[0]
        and value[3] >= value[1]
    )


def _valid_ocr_bbox(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(
            isinstance(point, list)
            and len(point) == 2
            and all(_finite_number(coordinate) and coordinate >= 0 for coordinate in point)
            for point in value
        )
    )


def _valid_xlsx_cell(sheet: object, cell: object) -> bool:
    return (
        isinstance(sheet, str)
        and bool(sheet.strip())
        and len(sheet) <= 80
        and "\n" not in sheet
        and "\r" not in sheet
        and isinstance(cell, str)
        and _CELL_REFERENCE.fullmatch(cell) is not None
    )
