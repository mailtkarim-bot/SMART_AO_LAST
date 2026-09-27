from app.modules.dce.domain.final_unknown_audit import build_final_unknown_audit

def test_final_unknown_audit_projection_keeps_counts_and_provenance() -> None:
    audit = build_final_unknown_audit((
        {"status": "UNKNOWN", "source_type": "VERIFICATION"},
        {"status": "MISMATCH", "source_type": "VERIFICATION"},
        {"status": "BLOCKED", "source_type": "HUMAN_RESUMPTION"},
    ))
    assert audit.counts == {"UNKNOWN": 1, "MISMATCH": 1, "BLOCKED": 1}
    assert all("source_type" in entry for entry in audit.entries)
