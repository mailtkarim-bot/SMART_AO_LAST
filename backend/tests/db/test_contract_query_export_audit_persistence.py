import sqlalchemy as sa

def test_export_audit_tables_are_present_and_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    assert "contract_query_exports" in inspector.get_table_names()
    assert "contract_query_export_transitions" in inspector.get_table_names()
    export_columns = {column["name"] for column in inspector.get_columns("contract_query_exports")}
    transition_columns = {column["name"] for column in inspector.get_columns("contract_query_export_transitions")}
    assert {"tenant_id", "case_id", "status"} <= export_columns
    assert {"tenant_id", "export_id", "from_status", "to_status"} <= transition_columns
