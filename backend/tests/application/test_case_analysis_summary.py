from uuid import uuid4


def test_twelve_axes_never_infer_completion_or_applicability():
    from app.modules.case.application.analysis_summary import build_analysis_summary

    case, version = uuid4(), uuid4()
    result = build_analysis_summary(
        case_id=case,
        dce_version_id=version,
        case_scope_kind="SINGLE_LOT",
        requirements=(),
        risks=(),
        coverage=None,
        truncated=False,
    )
    assert len(result["axes"]) == 12 and len({a["code"] for a in result["axes"]}) == 12
    assert not result["analysis_complete"] and result["status"] == "REVIEW_REQUIRED"
    assert all(a["status"] == "NON_EVALUATED" for a in result["axes"])


def test_only_closed_native_types_group_items_and_keep_unknown_fields():
    from app.modules.case.application.analysis_summary import build_analysis_summary

    requirement = dict(
        item_id=str(uuid4()),
        kind="REQUIREMENT",
        native_type="CANDIDATURE_DOCUMENT",
        native_state="CONFIRMED",
        source_state="CURRENT_SOURCE",
    )
    risk = dict(
        item_id=str(uuid4()),
        kind="RISK",
        native_type="CCTP",
        native_state="OPEN",
        source_state="UNKNOWN",
    )
    result = build_analysis_summary(
        case_id=uuid4(),
        dce_version_id=uuid4(),
        case_scope_kind="MULTI_LOT",
        requirements=(requirement,),
        risks=(risk,),
        coverage=None,
        truncated=True,
    )
    assert result["truncated"] and result["axes"][1]["status"] == "REVIEW_REQUIRED"
    assert result["axes"][2]["status"] == "REVIEW_REQUIRED"
    for a in result["axes"]:
        for i in a["items"]:
            assert i["applicability"] == "UNKNOWN" and i["responsible"] is None
            assert i["consequences"] == "UNKNOWN" and i["action"] is None
    assert all(not a["items"] for a in result["axes"] if a["code"] in {"PRICE", "CASH", "CAPACITY"})
