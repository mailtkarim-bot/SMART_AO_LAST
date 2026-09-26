import sqlalchemy as sa

def test_operational_handoff_source_schema_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("contract_query_exports")}
    assert {"tenant_id", "case_id", "filters_json", "status"} <= columns
