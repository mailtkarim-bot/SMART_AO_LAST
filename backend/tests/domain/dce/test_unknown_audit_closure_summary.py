from app.modules.dce.domain.unknown_audit_closure_summary import build_unknown_audit_closure_summary

def test_closure_summary_counts_and_keeps_open_entries() -> None:
    summary = build_unknown_audit_closure_summary((
        {"status": "UNKNOWN", "source_type": "VERIFICATION"},
        {"status": "BLOCKED", "source_type": "HUMAN_RESUMPTION"},
        {"status": "READY", "source_type": "TRANSITION"},
    ))
    assert summary.status_counts == {"UNKNOWN": 1, "BLOCKED": 1}
    assert summary.source_counts == {"VERIFICATION": 1, "HUMAN_RESUMPTION": 1}
    assert len(summary.open_entries) == 2
