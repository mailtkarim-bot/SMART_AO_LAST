from datetime import date
from uuid import uuid4

import pytest


def payload(**changes):
    return dict(
        period_start="2026-11-01",
        period_end="2026-11-30",
        status="ACTIVE",
        assumptions="Flux déclarés synthétiques, périmètre partiel.",
        openings=[dict(currency_code="EUR", amount_minor=0, source_refs=["balance://test"])],
        flows=[
            dict(
                flow_id=uuid4(),
                direction="OUTFLOW",
                currency_code="EUR",
                amount_minor=100,
                declared_date="2026-11-02",
                source_refs=["cost://test"],
            )
        ],
        **changes,
    )


def test_declared_cash_keeps_zero_missing_currency_and_partial_scope_distinct():
    from app.modules.pricing.domain.cash_schedule import CashDeclaration, project_schedule

    d = CashDeclaration(**payload())
    result = project_schedule(d)
    assert result["currencies"][0]["closing_minor"] == "-100"
    assert result["scope_state"] == "PARTIAL" and result["settlement_state"] == "UNKNOWN"
    d = d.model_copy(update={"openings": []})
    assert project_schedule(d)["currencies"][0]["closing_minor"] is None


def test_unknown_dates_or_amounts_do_not_produce_a_false_cumulative_balance():
    from app.modules.pricing.domain.cash_schedule import CashDeclaration, project_schedule

    d = CashDeclaration(**payload())
    d.flows[0].declared_date = None
    assert project_schedule(d)["currencies"][0]["closing_minor"] is None
    d.flows[0].declared_date = date(2026, 11, 2)
    d.flows[0].amount_minor = None
    assert project_schedule(d)["currencies"][0]["closing_minor"] is None


def test_cash_amounts_are_exact_and_currencies_never_converted():
    from app.modules.pricing.domain.cash_schedule import CashDeclaration, project_schedule

    d = CashDeclaration(**payload())
    d.openings[0].amount_minor = 9000000000000000
    d.flows[0].amount_minor = 1
    result = project_schedule(d)
    assert result["currencies"][0]["closing_minor"] == "8999999999999999"
    d.flows[0].currency_code = "USD"
    assert {c["currency_code"] for c in project_schedule(d)["currencies"]} == {"EUR", "USD"}


def test_cash_dates_duplicates_and_false_integer_inputs_are_refused():
    from app.modules.pricing.domain.cash_schedule import CashDeclaration
    from pydantic import ValidationError

    d = payload()
    d["flows"][0]["declared_date"] = "2026-12-01"
    with pytest.raises(ValidationError):
        CashDeclaration(**d)

    d = payload()
    d["flows"][0]["amount_minor"] = True
    with pytest.raises(ValidationError):
        CashDeclaration(**d)


def test_declared_totals_beyond_javascript_integer_precision_are_decimal_strings():
    from app.modules.pricing.domain.cash_schedule import CashDeclaration, project_schedule

    d = CashDeclaration(**payload())
    d.flows[0].direction = "INFLOW"
    d.flows[0].amount_minor = 9000000000000000
    d.flows.append(d.flows[0].model_copy(update={"flow_id": uuid4()}))
    assert project_schedule(d)["currencies"][0]["closing_minor"] == "18000000000000000"
