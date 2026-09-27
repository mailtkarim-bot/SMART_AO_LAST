from app.modules.pricing.domain.payment_unknown_audit import build_payment_unknown_audit

def test_payment_unknown_audit_projection_keeps_prudent_states() -> None:
    audit = build_payment_unknown_audit((
        {"status": "UNKNOWN", "source_ref": "ccap://p14"},
        {"status": "REVIEW_REQUIRED", "source_ref": "ccap://p15"},
    ))
    assert audit.status_counts == {"UNKNOWN": 1, "REVIEW_REQUIRED": 1}
    assert all("source_ref" in entry for entry in audit.entries)
