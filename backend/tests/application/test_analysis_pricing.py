from dataclasses import replace
from uuid import uuid4

from app.modules.case.application.analysis_summary import project_analysis_pricing
from app.modules.pricing.application.queries import PricingScenarioProjection


def scenario():
    return PricingScenarioProjection(
        scenario_id=uuid4(),
        case_id=uuid4(),
        scenario_key="Prudent",
        scenario_type="PRUDENT",
        version=3,
        state="SELECTED",
        assumptions={"origine": "estimation utilisateur"},
        sales_total_minor=100000,
        total_cost_minor=80000,
        gross_margin_minor=20000,
        gross_margin_rate_bps=2000,
        penalty_reserve_minor=1000,
        retention_reserve_minor=500,
        guarantee_reserve_minor=0,
        floor_margin_rate_bps=1000,
        target_margin_rate_bps=2000,
        break_even_sales_minor=80000,
        floor_sales_minor=88889,
        target_sales_minor=100000,
        source_snapshot_revision=2,
        source_snapshot_id=uuid4(),
        source_basis_state="DECLARED_COMPLETE",
        source_basis_reason=None,
        currency_code="EUR",
    )


def test_price_keeps_native_provenance_without_proving_dce_applicability():
    native = scenario()
    result = project_analysis_pricing(
        (native,), case_id=native.case_id, source_context_state="CURRENT"
    )
    assert result[0]["details"]["assumptions"] == native.assumptions
    assert result[0]["details"]["version"] == 3
    assert result[0]["details"]["source_snapshot_id"] == native.source_snapshot_id
    assert result[0]["dce_applicability"] == "UNKNOWN"
    assert result[0]["state"] == "RECORDED"


def test_price_masks_unproven_archived_and_stale_context_values():
    native = scenario()
    for candidate, context in [
        (
            replace(
                native, source_basis_state="UNKNOWN", source_basis_reason="SOURCE_REVISION_MISMATCH"
            ),
            "CURRENT",
        ),
        (replace(native, state="ARCHIVED"), "CURRENT"),
        (native, "REVIEW_REQUIRED"),
    ]:
        item = project_analysis_pricing(
            (candidate,), case_id=native.case_id, source_context_state=context
        )[0]
        assert item["state"] == "UNKNOWN" and item["details"] is None
        assert item["unknown_reason"]
    assert (
        project_analysis_pricing((native,), case_id=uuid4(), source_context_state="CURRENT") == []
    )
    assert (
        project_analysis_pricing((), case_id=native.case_id, source_context_state="CURRENT") == []
    )
