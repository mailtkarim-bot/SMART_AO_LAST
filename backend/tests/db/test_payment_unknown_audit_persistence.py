import sqlalchemy as sa

def test_payment_unknown_audit_source_schema_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("payment_post_reception_cycles")}
    assert {"tenant_id", "case_id", "source_refs_json", "status", "cash_assumption"} <= columns
