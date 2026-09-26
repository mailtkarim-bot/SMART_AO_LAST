from app.modules.dce.domain.consolidated_unknown_audit import audit_consolidated_statuses

def test_consolidated_audit_api_contract_keeps_unknowns_and_blockers_distinct() -> None:
    audit = audit_consolidated_statuses(("UNKNOWN", "BLOCKED", "FOLLOW_UP_REQUIRED"))
    assert audit.unknown_statuses == ("UNKNOWN",)
    assert audit.blocking_statuses == ("BLOCKED", "FOLLOW_UP_REQUIRED")
