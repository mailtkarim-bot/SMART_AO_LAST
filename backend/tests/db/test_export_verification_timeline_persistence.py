import sqlalchemy as sa

def test_timeline_source_tables_are_present_and_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    tables = set(inspector.get_table_names())
    assert {"export_proof_verifications", "contract_query_export_transitions", "export_verification_owner_acts"} <= tables
    for table in ("export_proof_verifications", "contract_query_export_transitions", "export_verification_owner_acts"):
        assert "tenant_id" in {column["name"] for column in inspector.get_columns(table)}
