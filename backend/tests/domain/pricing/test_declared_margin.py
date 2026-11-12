import pytest
from app.modules.pricing.public.declared_margin import (
    BASE_MARGIN_CATEGORIES,
    calculate_declared_base_margin,
)


def complete(sales=100_003, cost=60_001):
    return [
        ("SALES", sales),
        ("DIRECT_COST", cost),
        ("OVERHEAD", 7_002),
        ("SUBCONTRACTING", 0),
        ("CONTINGENCY", 0),
    ]


def test_declared_margin_reuses_exact_integer_cost_basis_and_ignores_human_margin():
    result = calculate_declared_base_margin(complete() + [("GROSS_MARGIN", 999_999)])
    assert result.state == "CALCULATED"
    assert result.total_cost_minor == 67_003
    assert result.gross_margin_minor == 33_000
    assert result.gross_margin_rate_bps == 3299


@pytest.mark.parametrize("missing", BASE_MARGIN_CATEGORIES)
def test_absent_category_is_not_zero(missing):
    result = calculate_declared_base_margin([line for line in complete() if line[0] != missing])
    assert result.state == "UNKNOWN"
    assert result.missing_categories == (missing,)
    assert result.gross_margin_minor is None
    assert result.gross_margin_rate_bps is None


def test_explicit_zero_sales_keeps_rate_unknown_and_negative_margin_exact():
    result = calculate_declared_base_margin(complete(sales=0))
    assert result.state == "CALCULATED"
    assert result.gross_margin_minor == -67_003
    assert result.gross_margin_rate_bps is None
    assert result.rate_unknown_reason == "ZERO_SALES"


@pytest.mark.parametrize("cost", [-1, True])
def test_invalid_amount_does_not_fabricate_a_margin(cost):
    result = calculate_declared_base_margin(complete(cost=cost))
    assert result.state == "UNKNOWN"
    assert result.unknown_reason == "INVALID_BASE_AMOUNT"
    assert result.gross_margin_minor is None


def test_declared_zero_costs_are_computable():
    result = calculate_declared_base_margin(
        [(c, 100 if c == "SALES" else 0) for c in BASE_MARGIN_CATEGORIES]
    )
    assert result.gross_margin_minor == 100
    assert result.gross_margin_rate_bps == 10_000


@pytest.mark.parametrize(
    "change,reason",
    [
        ("complete", None),
        ("missing", "MISSING_BASE_CATEGORY"),
        ("invalid", "INVALID_BASE_AMOUNT"),
        ("zero", "ZERO_SALES"),
        ("mismatch", "SOURCE_TOTAL_MISMATCH"),
        ("revision", "SOURCE_REVISION_MISMATCH"),
    ],
)
def test_declared_scenario_source_requires_exact_complete_snapshot(change, reason):
    from app.modules.pricing.public.declared_margin import qualify_declared_scenario_source

    lines = complete()
    totals = dict(lines)
    revision = 6
    if change == "missing":
        lines.pop()
    if change == "invalid":
        lines[1] = ("DIRECT_COST", -1)
    if change == "zero":
        lines[0] = ("SALES", 0)
        totals["SALES"] = 0
    if change == "mismatch":
        totals["OVERHEAD"] += 1
    if change == "revision":
        revision += 1
    assert (
        qualify_declared_scenario_source(
            lines, totals, source_revision=revision, expected_revision=6
        )
        == reason
    )


def test_declared_scenario_source_accepts_split_lines_and_ignores_human_margin():
    from app.modules.pricing.public.declared_margin import qualify_declared_scenario_source

    lines = complete() + [("SALES", 7), ("GROSS_MARGIN", 999_999)]
    totals = dict(complete())
    totals["SALES"] += 7
    assert (
        qualify_declared_scenario_source(lines, totals, source_revision=6, expected_revision=6)
        is None
    )
