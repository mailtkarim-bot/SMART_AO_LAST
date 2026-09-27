from app.modules.dce.domain.unknown_audit_closure_summary import build_unknown_audit_closure_summary

def test_closure_summary_keeps_unknowns_open_and_counts_sources() -> None:
    summary = build_unknown_audit_closure_summary((
        {"status": "UNKNOWN", "source_type": "VERIFICATION"},
        {"status": "FOLLOW_UP_REQUIRED", "source_type": "HUMAN_RESUMPTION"},
    ))
    assert summary.status_counts == {"UNKNOWN": 1, "FOLLOW_UP_REQUIRED": 1}
    assert summary.source_counts == {"VERIFICATION": 1, "HUMAN_RESUMPTION": 1}
