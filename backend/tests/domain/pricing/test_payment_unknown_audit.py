from app.modules.pricing.domain.payment_unknown_audit import build_payment_unknown_audit

def test_payment_unknown_audit_keeps_statuses_and_provenance() -> None:
    audit = build_payment_unknown_audit((
        {"status": "SOURCE_SIGNAL_ONLY", "source_ref": "ccap://p12"},
        {"status": "REVIEW_REQUIRED", "source_ref": "ccap://p13"},
        {"status": "READY", "source_ref": "ignored"},
    ))
    assert audit.status_counts == {"SOURCE_SIGNAL_ONLY": 1, "REVIEW_REQUIRED": 1}
    assert len(audit.entries) == 2
