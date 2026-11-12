from datetime import date
from typing import Any


def test_missing_cost_never_uses_imported_price_or_offer_total():
    from app.modules.pricing.domain.position_costing import project_position_costing

    snapshot: dict[str, Any] = {
        "import": {"total_minor": 50000, "unit": "m2"},
        "costs": [],
        "requirement": None,
        "offer": {
            "amount_as_declared": "9999",
            "currency_code": "EUR",
            "valid_until": None,
            "exclusions_state": "UNKNOWN",
            "exclusions": [],
        },
        "scope": None,
    }
    result = project_position_costing(
        snapshot, current=True, reused_cost_ids=set(), today=date(2026, 10, 23)
    )
    assert result["declared_cost_minor"] is None
    assert result["cost_state"] == result["coverage_state"] == "UNKNOWN"
    assert "NO_REGISTERED_COST" in result["limitations"]


def test_only_current_same_currency_costs_are_added_and_reuse_is_visible():
    from app.modules.pricing.domain.position_costing import project_position_costing

    snapshot: dict[str, Any] = {
        "import": {"unit": "m2"},
        "costs": [
            {"line_id": "a", "amount_minor": 100, "currency_code": "EUR", "unit": "m2"},
            {"line_id": "b", "amount_minor": 200, "currency_code": "EUR", "unit": "m2"},
        ],
        "requirement": None,
        "offer": None,
        "scope": None,
    }

    def project(**changes):
        return project_position_costing(
            snapshot, current=True, reused_cost_ids=set(), today=date(2026, 10, 23), **changes
        )

    assert project()["declared_cost_minor"] == 300
    assert project()["coverage_state"] == "UNKNOWN"
    result = project_position_costing(
        snapshot, current=True, reused_cost_ids={"a"}, today=date(2026, 10, 23)
    )
    assert (
        result["declared_cost_minor"] is None
        and "COST_REUSE_REVIEW_REQUIRED" in result["limitations"]
    )
    snapshot["costs"][1]["currency_code"] = "USD"
    assert (
        project()["declared_cost_minor"] is None and "CURRENCY_MISMATCH" in project()["limitations"]
    )


def test_stale_context_never_transfers_costs_to_current_projection():
    from app.modules.pricing.domain.position_costing import project_position_costing

    result = project_position_costing(
        {"costs": [{"amount_minor": 100}]},
        current=False,
        reused_cost_ids=set(),
        today=date(2026, 10, 23),
    )
    assert result["costs"] == [] and result["declared_cost_minor"] is None
    assert result["state"] == "REVIEW_REQUIRED"


def test_quantities_and_multiple_economic_bases_are_not_silently_equated():
    from app.modules.pricing.domain.position_costing import project_position_costing

    snapshot: dict[str, Any] = {
        "import": {"unit": "u", "quantity_decimal": "2"},
        "costs": [
            {
                "line_id": "a",
                "report_id": "base1",
                "amount_minor": 100,
                "currency_code": "EUR",
                "unit": "u",
                "quantity_decimal": "1",
            },
            {
                "line_id": "b",
                "report_id": "base2",
                "amount_minor": 200,
                "currency_code": "EUR",
                "unit": "u",
                "quantity_decimal": "2",
            },
        ],
    }
    result = project_position_costing(
        snapshot, current=True, reused_cost_ids=set(), today=date(2026, 10, 23)
    )
    assert result["declared_cost_minor"] is None
    assert "MULTIPLE_COST_BASES_REVIEW_REQUIRED" in result["limitations"]
    assert "QUANTITY_SCOPE_REVIEW_REQUIRED" in result["limitations"]


def test_equal_decimal_quantities_do_not_create_a_false_warning():
    from app.modules.pricing.domain.position_costing import project_position_costing

    snapshot: dict[str, Any] = {
        "import": {"unit": "m2", "quantity_decimal": "2"},
        "costs": [
            {
                "line_id": "a",
                "report_id": "r",
                "amount_minor": 100,
                "currency_code": "EUR",
                "unit": "m2",
                "quantity_decimal": "2.0",
            }
        ],
    }
    result = project_position_costing(
        snapshot, current=True, reused_cost_ids=set(), today=date(2026, 10, 23)
    )
    assert "QUANTITY_SCOPE_REVIEW_REQUIRED" not in result["limitations"]


def test_explicit_shared_amount_is_used_without_claiming_coverage():
    from app.modules.pricing.domain.position_costing import project_position_costing

    result = project_position_costing(
        {
            "import": {"unit": "u"},
            "costs": [
                {
                    "line_id": "shared",
                    "report_id": "r",
                    "amount_minor": 12000,
                    "allocated_amount_minor": 4500,
                    "currency_code": "EUR",
                    "unit": "u",
                }
            ],
        },
        current=True,
        reused_cost_ids={"shared"},
        today=date(2026, 11, 5),
    )
    assert result["declared_cost_minor"] == 4500
    assert result["coverage_state"] == "UNKNOWN"
    assert "COST_REUSE_REVIEW_REQUIRED" not in result["limitations"]


def test_allocation_contract_rejects_non_integer_or_out_of_range_amounts():
    from uuid import uuid4

    import pytest
    from app.modules.pricing.application.position_commands import PositionCostReference
    from pydantic import ValidationError

    for amount in ["-1", "1.5", "01", "9223372036854775808", " 1", 4500, True]:
        with pytest.raises(ValidationError):
            PositionCostReference(line_id=uuid4(), report_revision=0, allocated_amount_minor=amount)


def test_legacy_cost_reference_keeps_its_original_serialized_intent():
    from uuid import uuid4

    from app.modules.pricing.application.position_commands import PositionCostReference

    identity = uuid4()
    assert PositionCostReference(line_id=identity, report_revision=0).model_dump(mode="json") == {
        "line_id": str(identity),
        "report_revision": 0,
    }
