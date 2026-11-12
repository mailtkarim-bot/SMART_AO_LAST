from copy import deepcopy
from typing import Any


def test_stale_action_invalidates_linked_closure_records_without_rewriting_reviews():
    from app.modules.pricing.infrastructure.case_closure_reader import (
        _invalidate_comparisons,
        fingerprint,
    )

    action = {"id": "a", "context_state": "UNKNOWN"}
    ref = {"kind": "CHANGE_ACTION", "record_id": "a", "sha256": fingerprint(action)}
    act: dict[str, Any] = {
        "id": "r",
        "context_state": "CURRENT",
        "closure_review_json": {
            "human_confirmed": True,
            "comparisons": [{"expected": ref, "actual": ref}],
        },
    }
    act_ref = {"kind": "ACT", "record_id": "r", "sha256": fingerprint(act)}
    obligation = {
        "id": "o",
        "context_state": "CURRENT",
        "closure_review_json": {"comparisons": [{"expected": act_ref, "actual": act_ref}]},
    }
    captured = deepcopy(act["closure_review_json"])
    action["context_state"] = "REVIEW_REQUIRED"
    _invalidate_comparisons([act], [obligation], [], [action])
    assert act["context_state"] == obligation["context_state"] == "REVIEW_REQUIRED"
    assert act["closure_review_json"] == captured and captured["human_confirmed"] is True


def test_unknown_source_is_not_promoted_or_invalidated_without_a_change():
    from app.modules.pricing.infrastructure.case_closure_reader import (
        _invalidate_comparisons,
        fingerprint,
    )

    action = {"id": "a", "context_state": "UNKNOWN"}
    ref = {"kind": "CHANGE_ACTION", "record_id": "a", "sha256": fingerprint(action)}
    act: dict[str, Any] = {
        "id": "r",
        "context_state": "UNKNOWN",
        "closure_review_json": {"comparisons": [{"expected": ref, "actual": ref}]},
    }
    before = deepcopy(act)
    _invalidate_comparisons([act], [], [], [action])
    assert act == before


def test_origin_reception_dependency_is_reopened_without_an_explicit_comparison():
    from app.modules.pricing.infrastructure.case_closure_reader import (
        _invalidate_comparisons,
        fingerprint,
    )

    action = {"id": "a", "context_state": "UNKNOWN"}
    ref = {"kind": "CHANGE_ACTION", "record_id": "a", "sha256": fingerprint(action)}
    act = {
        "id": "r",
        "context_state": "CURRENT",
        "closure_review_json": {"comparisons": [{"expected": ref, "actual": ref}]},
    }
    obligation = {
        "id": "o",
        "context_state": "CURRENT",
        "origin_context_state": "CURRENT",
        "origin_reception_act_id": "r",
        "declared_status": "COMPLETED",
        "closure_review_json": {"human_confirmed": True, "comparisons": []},
    }
    captured = deepcopy(obligation["closure_review_json"])
    action["context_state"] = "REVIEW_REQUIRED"
    _invalidate_comparisons([act], [obligation], [], [action])
    assert obligation["context_state"] == obligation["origin_context_state"] == "REVIEW_REQUIRED"
    assert obligation["declared_status"] == "COMPLETED"
    assert obligation["closure_review_json"] == captured
