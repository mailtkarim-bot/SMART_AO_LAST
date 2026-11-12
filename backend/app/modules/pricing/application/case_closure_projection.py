"""Exact pair comparisons of human declarations, never a settlement balance."""

from typing import Any


def financial_observations(facts: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {fact["fact_id"]: fact for fact in facts}
    comparisons = []
    for fact in facts:
        if fact["kind"] != "COLLECTION_RECORDED":
            continue
        parent = by_id.get(fact.get("compared_to_fact_id"))
        if (
            parent is not None
            and parent["kind"] == "PAYMENT_EXPECTED"
            and parent["currency_code"] == fact["currency_code"]
        ):
            comparisons.append(
                {
                    "expected_fact_id": parent["fact_id"],
                    "recorded_fact_id": fact["fact_id"],
                    "currency_code": fact["currency_code"],
                    "difference_minor": None
                    if "REVIEW_REQUIRED" in (fact.get("context_state"), parent.get("context_state"))
                    else fact["amount_minor"] - parent["amount_minor"],
                    "source_state": "REVIEW_REQUIRED"
                    if "REVIEW_REQUIRED" in (fact.get("context_state"), parent.get("context_state"))
                    else "HUMAN_DECLARED",
                    "meaning": "DECLARED_PAIR_DIFFERENCE_ONLY",
                }
            )
    return {
        "collection_state": (
            "HUMAN_RECORDED"
            if any(f["kind"] == "COLLECTION_RECORDED" for f in facts)
            else "UNKNOWN"
        ),
        "settlement_state": "UNKNOWN",
        "comparisons": comparisons,
    }
