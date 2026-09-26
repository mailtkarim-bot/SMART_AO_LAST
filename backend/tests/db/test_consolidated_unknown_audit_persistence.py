import sqlalchemy as sa

def test_consolidated_audit_sources_are_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    for table in ("contract_query_export_transitions", "human_resumption_acts"):
        assert "tenant_id" in {column["name"] for column in inspector.get_columns(table)}
