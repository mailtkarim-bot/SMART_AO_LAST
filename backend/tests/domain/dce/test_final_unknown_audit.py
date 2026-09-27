from app.modules.dce.domain.final_unknown_audit import build_final_unknown_audit

def test_final_unknown_audit_counts_difficult_states_and_keeps_provenance() -> None:
    audit = build_final_unknown_audit((
        {"status": "UNKNOWN", "source_type": "VERIFICATION"},
        {"status": "BLOCKED", "source_type": "HUMAN_RESUMPTION"},
        {"status": "READY", "source_type": "TRANSITION"},
    ))
    assert audit.counts == {"UNKNOWN": 1, "BLOCKED": 1}
    assert audit.entries[0]["source_type"] == "VERIFICATION"
