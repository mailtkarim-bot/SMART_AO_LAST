import sqlalchemy as sa

def test_resumption_filter_source_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("human_resumption_acts")}
    assert {"tenant_id", "export_id", "state"} <= columns
