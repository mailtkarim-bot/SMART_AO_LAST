from uuid import uuid4

from app.modules.case.application.analysis_summary import build_analysis_summary


def test_follow_ups_keep_exact_records_only_under_current_source_context():
    follow_up = {"record_id": uuid4(), "kind": "ACTION", "state": "OPEN"}
    item = dict(
        item_id=uuid4(),
        kind="RISK",
        native_type="CCAP",
        source_state="CURRENT_SOURCE",
        follow_ups=[follow_up],
    )

    def project(state):
        return build_analysis_summary(
            case_id=uuid4(),
            dce_version_id=uuid4(),
            case_scope_kind="CUSTOM",
            requirements=(),
            risks=(item,),
            coverage=None,
            truncated=False,
            source_context_state=state,
        )["axes"][4]["items"][0]

    assert project("CURRENT")["follow_up_state"] == "RECORDED"
    assert project("CURRENT")["follow_ups"] == [follow_up]
    assert project("REVIEW_REQUIRED")["follow_ups"] == []
    item["source_state"] = "UNKNOWN"
    assert project("CURRENT")["follow_up_state"] == "UNKNOWN"
    assert project("CURRENT")["follow_ups"] == []


def test_follow_up_output_budget_is_visible_and_never_means_complete():
    records = [{"record_id": uuid4()} for _ in range(301)]
    item = dict(
        item_id=uuid4(),
        kind="RISK",
        native_type="CCAP",
        source_state="CURRENT_SOURCE",
        follow_ups=records,
    )
    result = build_analysis_summary(
        case_id=uuid4(),
        dce_version_id=uuid4(),
        case_scope_kind="CUSTOM",
        requirements=(),
        risks=(item,),
        coverage=None,
        truncated=False,
        source_context_state="CURRENT",
    )
    assert result["truncated"] and not result["analysis_complete"]
    assert len(result["axes"][4]["items"][0]["follow_ups"]) == 300


def test_exact_excerpt_preserves_utf8_and_refuses_split_or_oversize_regions():
    from app.modules.case.application.analysis_summary import exact_source_excerpt

    text = "Préambule : échéance à confirmer."
    start = len("Préambule : ".encode())
    end = len(text.encode())
    assert exact_source_excerpt(text, start, end) == "échéance à confirmer."
    assert exact_source_excerpt(text, start + 1, end) is None
    assert exact_source_excerpt(text, -1, end) is None
    assert exact_source_excerpt(text, 0, end + 1) is None
    assert exact_source_excerpt("a" * 8001, 0, 8001) is None
    assert exact_source_excerpt("a" * 8000, 0, 8000) == "a" * 8000
