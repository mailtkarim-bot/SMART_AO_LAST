import sqlalchemy as sa

def test_closure_summary_source_table_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("unknown_audit_provenance")}
    assert {"tenant_id", "export_id", "source_type", "status"} <= columns
