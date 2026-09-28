import sqlalchemy as sa

def test_payment_review_write_schema_is_tenant_scoped_and_closed(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("payment_cycle_reviews")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("payment_cycle_reviews")}
    assert {"id", "tenant_id", "cycle_id", "reviewer_id", "decision", "rationale"} <= columns
    assert any("ACCEPTED_FOR_PLANNING" in check and "REVIEW_REQUIRED" in check for check in checks)
