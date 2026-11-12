"""Business regression: no silently omitted lot or invented financial quantity."""

from datetime import UTC, datetime
from io import BytesIO
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from app.modules.pricing.application import import_preview as module
from app.platform.security.context import ActorKind
from openpyxl import Workbook

HEADERS = ["Code", "Désignation", "Quantité", "Prix unitaire"]


def workbook_payload(sheets):
    wb = Workbook()
    wb.remove(wb.active)
    for name, rows in sheets:
        sheet = wb.create_sheet(name)
        for row in rows:
            sheet.append(row)
    out = BytesIO()
    wb.save(out)
    wb.close()
    return out.getvalue()


def preview(payload):
    actor = SimpleNamespace(
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_id=uuid4(),
        tenant_id=uuid4(),
        authenticated_at=datetime.now(UTC),
    )
    policy = SimpleNamespace(authorize=lambda **kw: SimpleNamespace(allowed=True))
    return module.PricingImportPreviewService(policy=policy).preview(
        actor=cast(Any, actor),
        case_id=uuid4(),
        document_kind="DPGF",
        filename="dpgf.xlsx",
        content_type=None,
        payload=payload,
    )


def test_all_tabular_lots_are_present_with_distinct_source_cells():
    result = preview(
        workbook_payload(
            [
                ("Lot 1", [HEADERS, ["A", "Terrassement", 2, 10]]),
                ("Lot 2", [HEADERS, ["B", "Fondations", 3, 20]]),
            ]
        )
    )
    assert result.row_count == result.valid_row_count == 2
    assert result.total_minor == 8000
    assert len({r.row_number for r in result.rows}) == 2
    assert [r.source_locator["sheet"] for r in result.rows] == ["Lot 1", "Lot 2"]
    assert all(r.source_locator["row"] == 2 for r in result.rows)
    assert all(r.source_locator["cells"]["quantity"] == "C2" for r in result.rows)


def test_formula_quantity_never_becomes_the_default_one():
    result = preview(workbook_payload([("Lot", [HEADERS, ["A", "Fondations", "=2+3", 10]])]))
    assert result.valid_row_count == 0
    assert "FORMULA_REQUIRES_REVIEW" in result.rows[0].errors
    assert result.rows[0].quantity_decimal is None
    assert result.total_minor == 0


def test_final_excess_row_is_not_consumed_without_truncation(monkeypatch):
    monkeypatch.setattr(module, "MAX_ROWS", 1)
    result = preview(
        workbook_payload([("Lot", [HEADERS, ["A", "Un", 1, 10], ["B", "Deux", 2, 20]])])
    )
    assert result.truncated and result.limit_reason == "ROW_LIMIT"


def test_unrecognized_nonempty_sheet_cannot_disappear():
    with pytest.raises(ValueError, match="IMPORT_DESIGNATION_COLUMN_REQUIRED"):
        preview(
            workbook_payload(
                [("Lot", [HEADERS, ["A", "Un", 1, 10]]), ("Autre", [["Texte"], ["prix à revoir"]])]
            )
        )


def test_duplicate_price_headers_are_ambiguous():
    with pytest.raises(ValueError, match="IMPORT_HEADER_AMBIGUOUS"):
        preview(
            workbook_payload([("Lot", [["Désignation", "Prix unitaire", "PU"], ["Un", 10, 90]])])
        )


@pytest.mark.parametrize(
    "quantity,unit_price,total",
    [(None, 10, None), (2, 10, "illisible"), (2, -10, 20), (2, 1e20, None)],
)
def test_missing_quantity_or_invalid_supplied_price_never_becomes_valid(
    quantity, unit_price, total
):
    result = preview(
        workbook_payload(
            [
                (
                    "Lot",
                    [
                        ["Désignation", "Quantité", "Prix unitaire", "Montant"],
                        ["Poste", quantity, unit_price, total],
                    ],
                )
            ]
        )
    )
    assert result.valid_row_count == 0 and result.rows[0].errors
    assert result.total_minor == 0


def test_workbook_sum_beyond_database_money_range_is_refused():
    with pytest.raises(ValueError, match="IMPORT_TOTAL_OUT_OF_RANGE"):
        preview(
            workbook_payload(
                [
                    (
                        "Lot",
                        [
                            HEADERS,
                            ["A", "Un", 1, "50000000000000000"],
                            ["B", "Deux", 1, "50000000000000000"],
                        ],
                    )
                ]
            )
        )


def test_broken_worksheet_xml_is_a_controlled_import_refusal():
    from zipfile import ZipFile

    raw = workbook_payload([("Lot", [HEADERS, ["A", "Un", 1, 10]])])
    out = BytesIO()
    with ZipFile(BytesIO(raw)) as source, ZipFile(out, "w") as target:
        for info in source.infolist():
            content = source.read(info.filename)
            if info.filename == "xl/worksheets/sheet1.xml":
                content = content.replace(b"</sheetData>", b"</broken>")
            target.writestr(info, content)
    with pytest.raises(ValueError, match="IMPORT_WORKBOOK_INVALID"):
        preview(out.getvalue())


@pytest.mark.parametrize("kind", ["array", "table"])
def test_non_string_formulas_are_never_imported_as_python_object_text(kind):
    from openpyxl.worksheet.formula import ArrayFormula, DataTableFormula

    wb = Workbook()
    sheet = wb.active
    sheet.append(HEADERS)
    sheet.append(["A", "Poste", 2, 10])
    sheet["B2"] = (
        ArrayFormula(ref="B2", text='="Poste"') if kind == "array" else DataTableFormula(ref="B2")
    )
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    result = preview(stream.getvalue())
    assert result.valid_row_count == 0
    assert "FORMULA_REQUIRES_REVIEW" in result.rows[0].errors
    assert result.rows[0].designation is None


def test_subcent_unit_price_is_not_rounded_before_quantity_without_qualification():
    result = preview(workbook_payload([("Lot", [HEADERS, ["A", "Poste", 10, "0.123"]])]))
    assert result.valid_row_count == 0
    assert "UNIT_PRICE_PRECISION_UNQUALIFIED" in result.rows[0].errors
    assert result.rows[0].unit_price_minor is None
    assert result.total_minor == 0


def test_incorrect_sheet_dimensions_cannot_hide_the_last_position():
    from zipfile import ZipFile

    raw = workbook_payload([("Lot", [HEADERS, ["A", "Un", 1, 10], ["B", "Deux", 2, 20]])])
    stream = BytesIO()
    with ZipFile(BytesIO(raw)) as source, ZipFile(stream, "w") as target:
        for info in source.infolist():
            content = source.read(info.filename)
            if info.filename == "xl/worksheets/sheet1.xml":
                content = content.replace(b"A1:D3", b"A1:D2")
            target.writestr(info, content)
    result = preview(stream.getvalue())
    assert result.row_count == 2 and result.total_minor == 5000


def test_oversized_columns_are_refused_without_silent_cutting():
    wb = Workbook()
    s = wb.active
    s.append(HEADERS)
    s.append(["A", "Poste", 1, 10])
    s.cell(1, 257, "Hors budget")
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    with pytest.raises(ValueError, match="IMPORT_COLUMN_LIMIT"):
        preview(stream.getvalue())


def test_blank_header_scan_has_a_row_budget(monkeypatch):
    monkeypatch.setattr(module, "MAX_ROWS", 2)
    wb = Workbook()
    wb.active.cell(5, 1, "Texte éloigné")
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    with pytest.raises(ValueError, match="IMPORT_ROW_LIMIT"):
        preview(stream.getvalue())
