import sqlalchemy as sa


def test_owner_act_schema_is_tenant_scoped_and_independent(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("export_verification_owner_acts")}
    foreign_keys = inspector.get_foreign_keys("export_verification_owner_acts")
    assert {"id", "tenant_id", "export_id", "owner_id", "approved", "rationale"} <= columns
    assert any("contract_query_exports" in str(key["referred_table"]) for key in foreign_keys)
    assert "export_proof_verifications" not in str(foreign_keys)
