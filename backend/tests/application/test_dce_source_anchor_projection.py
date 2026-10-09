from __future__ import annotations

import pytest
from app.modules.dce.application.source_anchor_projection import (
    DceSourceLocatorKind,
    resolve_dce_source_locator,
)


@pytest.mark.parametrize(
    ("locator", "expected_kind"),
    [
        ({"kind": "pdf_page", "page": 2, "part": 1}, DceSourceLocatorKind.PDF_PAGE),
        (
            {
                "kind": "pymupdf_block",
                "page": 2,
                "block": 3,
                "bbox": [1.0, 2.0, 30.0, 40.0],
                "part": 1,
            },
            DceSourceLocatorKind.PYMUPDF_BLOCK,
        ),
        (
            {
                "kind": "ocr_page",
                "page": 1,
                "order": 2,
                "bbox": [[1.0, 2.0], [30.0, 2.0], [30.0, 12.0], [1.0, 12.0]],
                "part": 1,
            },
            DceSourceLocatorKind.OCR_PAGE,
        ),
        (
            {"kind": "docx_paragraph", "paragraph": 4, "part": 1},
            DceSourceLocatorKind.DOCX_PARAGRAPH,
        ),
        (
            {"kind": "xlsx_cell", "sheet": "BPU", "cell": "C12", "part": 1},
            DceSourceLocatorKind.XLSX_CELL,
        ),
        ({"kind": "text_line", "line": 8, "part": 1}, DceSourceLocatorKind.TEXT_LINE),
        (
            {"kind": "docling_markdown", "line": 5, "part": 1},
            DceSourceLocatorKind.DOCLING_MARKDOWN,
        ),
    ],
)
def test_resolves_each_locator_kind_currently_emitted(locator, expected_kind) -> None:
    resolved = resolve_dce_source_locator(locator)

    assert resolved is not None
    assert resolved.kind is expected_kind
    expected_coordinates = {key: value for key, value in locator.items() if key != "kind"}
    assert dict(resolved.coordinates) == expected_coordinates


@pytest.mark.parametrize(
    "locator",
    [
        None,
        {"kind": "future_locator", "page": 1},
        {"kind": "pdf_page", "page": True},
        {"kind": "pdf_page", "page": 1, "invented_bbox": [0, 0, 1, 1]},
        {"kind": "pymupdf_block", "page": 1, "block": 1, "bbox": [0, 0, float("nan"), 1]},
        {"kind": "ocr_page", "page": 1, "order": 1, "bbox": [[0, 0], [1, 1]]},
        {"kind": "docx_paragraph", "paragraph": 0},
        {"kind": "xlsx_cell", "sheet": "BPU", "cell": "C0"},
        {"kind": "text_line", "line": 1, "part": False},
        {"kind": "docling_markdown", "line": 1, "extra": "unrecognized"},
    ],
)
def test_unknown_or_malformed_locators_stay_unresolved_without_mutation(locator) -> None:
    before = repr(locator)

    assert resolve_dce_source_locator(locator) is None
    assert repr(locator) == before
