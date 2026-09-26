from app.modules.dce.domain.consolidated_unknown_audit import audit_consolidated_statuses

def test_unknown_audit_preserves_difficult_states() -> None:
    audit = audit_consolidated_statuses(("READY", "UNKNOWN", "MISMATCH", "BLOCKED", "FOLLOW_UP_REQUIRED"))
    assert audit.unknown_statuses == ("UNKNOWN", "MISMATCH")
    assert audit.blocking_statuses == ("BLOCKED", "FOLLOW_UP_REQUIRED")
