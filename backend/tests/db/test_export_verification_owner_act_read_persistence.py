import sqlalchemy as sa

def test_owner_act_read_schema_preserves_owner_and_approval(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("export_verification_owner_acts")}
    assert {"tenant_id", "export_id", "owner_id", "approved", "rationale"} <= columns
