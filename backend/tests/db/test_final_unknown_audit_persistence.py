import sqlalchemy as sa

def test_final_unknown_audit_sources_are_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    tables = {"unknown_audit_provenance", "contract_query_export_transitions", "human_resumption_acts"}
    assert tables <= set(inspector.get_table_names())
    for table in tables:
        assert "tenant_id" in {column["name"] for column in inspector.get_columns(table)}
