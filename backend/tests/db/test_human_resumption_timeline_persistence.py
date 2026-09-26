import sqlalchemy as sa

def test_resumption_timeline_source_tables_are_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    assert "contract_query_export_transitions" in inspector.get_table_names()
    assert "human_resumption_acts" in inspector.get_table_names()
    for table in ("contract_query_export_transitions", "human_resumption_acts"):
        assert "tenant_id" in {column["name"] for column in inspector.get_columns(table)}
