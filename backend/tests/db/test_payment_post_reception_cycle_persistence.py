import sqlalchemy as sa

def test_payment_cycle_schema_is_tenant_scoped_and_status_closed(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("payment_post_reception_cycles")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("payment_post_reception_cycles")}
    assert {"tenant_id", "case_id", "source_refs_json", "trigger_event", "status", "cash_assumption", "post_reception_cost_note"} <= columns
    assert any("SOURCE_SIGNAL_ONLY" in check and "REVIEW_REQUIRED" in check and "UNKNOWN" in check for check in checks)
