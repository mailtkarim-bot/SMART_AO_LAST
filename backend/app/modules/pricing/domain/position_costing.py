"""Read registered costs, never infer an allocation, conversion or economic GO."""

from datetime import date
from decimal import Decimal, InvalidOperation


def project_position_costing(snapshot, *, current, reused_cost_ids, today):
    if not current:
        return dict(
            state="REVIEW_REQUIRED",
            cost_state="UNKNOWN",
            coverage_state="UNKNOWN",
            declared_cost_minor=None,
            currency_code=None,
            costs=[],
            requirement=None,
            offer=None,
            scope=None,
            limitations=["SOURCE_REVIEW_REQUIRED"],
        )
    costs = snapshot.get("costs", [])
    requirement = snapshot.get("requirement")
    offer = snapshot.get("offer")
    scope = snapshot.get("scope")
    limits = []
    if snapshot.get("import_origin", {}).get("state") != "MATCHED_BY_HASH":
        limits.append("IMPORTED_DCE_ORIGIN_UNKNOWN")
    if not requirement:
        limits.append("NO_DCE_REQUIREMENT")
    if not costs:
        limits.append("NO_REGISTERED_COST")
    if not offer:
        limits.append("NO_PARTNER_OFFER")
    if any(
        c["line_id"] in reused_cost_ids and c.get("allocated_amount_minor") is None for c in costs
    ):
        limits.append("COST_REUSE_REVIEW_REQUIRED")
    currencies = {c["currency_code"] for c in costs}
    if len(currencies) > 1:
        limits.append("CURRENCY_MISMATCH")
    currency = next(iter(currencies)) if len(currencies) == 1 else None
    if len({c.get("report_id") for c in costs}) > 1:
        limits.append("MULTIPLE_COST_BASES_REVIEW_REQUIRED")
    imported_unit = snapshot.get("import", {}).get("unit")
    imported_quantity = snapshot.get("import", {}).get("quantity_decimal")
    if imported_quantity is not None and any(
        c["unit"] == imported_unit
        and not _same_quantity(c.get("quantity_decimal"), imported_quantity)
        for c in costs
    ):
        limits.append("QUANTITY_SCOPE_REVIEW_REQUIRED")
    if imported_unit is None:
        limits.append("IMPORTED_UNIT_UNKNOWN")
    elif any(c["unit"] != imported_unit for c in costs):
        limits.append("UNIT_SCOPE_REVIEW_REQUIRED")
    if offer:
        limits.append("OFFER_TOTAL_IS_NOT_POSITION_COST")
        if currency and offer["currency_code"] != currency:
            limits.append("OFFER_CURRENCY_MISMATCH")
        if not offer.get("valid_until"):
            limits.append("OFFER_VALIDITY_UNKNOWN")
        elif date.fromisoformat(offer["valid_until"]) < today:
            limits.append("OFFER_EXPIRED")
        if offer.get("exclusions_state") != "DECLARED":
            limits.append("OFFER_EXCLUSIONS_UNKNOWN")
        elif offer.get("exclusions"):
            limits.append("OFFER_EXCLUSIONS_PRESENT")
    if scope and scope.get("decision") != "SAME_SCOPE_CONFIRMED":
        limits.append("PARTNER_SCOPE_REVIEW_REQUIRED")
    if scope and scope.get("exclusions_review_state") != "REVIEWED":
        limits.append("EXCLUSIONS_REVIEW_REQUIRED")
    if not scope or scope["transport_state"] == "UNKNOWN":
        limits.append("TRANSPORT_UNKNOWN")
    elif scope["transport_state"] in {"EXCLUDED", "SEPARATE"}:
        limits.append("TRANSPORT_NOT_INCLUDED")
    total = (
        sum(c.get("allocated_amount_minor", c["amount_minor"]) for c in costs)
        if costs and currency
        else None
    )
    if total is not None and not 0 <= total <= 2**63 - 1:
        limits.append("COST_TOTAL_OUT_OF_RANGE")
        total = None
    if "COST_REUSE_REVIEW_REQUIRED" in limits or "MULTIPLE_COST_BASES_REVIEW_REQUIRED" in limits:
        total = None
    return dict(
        state="CURRENT",
        cost_state="DECLARED" if total is not None else "UNKNOWN",
        coverage_state="UNKNOWN",
        declared_cost_minor=total,
        currency_code=currency,
        costs=costs,
        requirement=requirement,
        offer=offer,
        scope=scope,
        limitations=limits,
    )


def _same_quantity(left, right):
    try:
        return Decimal(left) == Decimal(right)
    except (InvalidOperation, TypeError, ValueError):
        return False
