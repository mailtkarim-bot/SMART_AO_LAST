from dataclasses import replace
from datetime import UTC, datetime
from uuid import uuid4

from app.modules.case.application.analysis_summary import project_analysis_cash
from app.modules.membership.application.financial_report import (
    FinancialReportLineProjection,
    FinancialReportProjection,
)


def report():
    return FinancialReportProjection(
        report_id=uuid4(),
        case_id=uuid4(),
        currency_code="EUR",
        calculated_at=datetime(2026, 10, 20, tzinfo=UTC),
        ruleset_version=1,
        summary={"forecast_cashflow_minor": 0},
        lines=(
            FinancialReportLineProjection(
                line_id=uuid4(),
                category="FORECAST_CASHFLOW",
                label="Déclaration humaine synthétique",
                quantity_decimal="1",
                unit="forfait",
                amount_minor=0,
                currency_code="EUR",
            ),
        ),
        status="PUBLISHED",
        aggregate_revision=2,
    )


def test_cash_preserves_explicit_zero_and_exact_declaration_without_inferring_peak():
    native = report()
    item = project_analysis_cash((native,), case_id=native.case_id, source_context_state="CURRENT")[
        0
    ]
    assert item["state"] == "DECLARED"
    assert item["details"]["forecast_cashflow_minor"] == 0
    assert item["details"]["lines"][0]["line_id"] == native.lines[0].line_id
    assert item["revision"] == 2 and item["report_id"] == native.report_id
    assert item["schedule_state"] == item["funding_peak_state"] == item["scope_state"] == "UNKNOWN"


def test_cash_does_not_turn_missing_or_discordant_declarations_into_zero():
    native = report()
    for changed, context in [
        (replace(native, lines=()), "CURRENT"),
        (replace(native, summary={"forecast_cashflow_minor": 1}), "CURRENT"),
        (replace(native, status="DRAFT"), "CURRENT"),
        (native, "REVIEW_REQUIRED"),
    ]:
        item = project_analysis_cash(
            (changed,), case_id=native.case_id, source_context_state=context
        )[0]
        assert item["state"] == "UNKNOWN" and item["details"] is None and item["unknown_reason"]
    assert project_analysis_cash((native,), case_id=uuid4(), source_context_state="CURRENT") == []
