import sqlalchemy as sa

def test_human_resumption_schema_is_tenant_scoped_and_closed(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("human_resumption_acts")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("human_resumption_acts")}
    assert {"id", "tenant_id", "export_id", "actor_id", "state", "rationale"} <= columns
    assert any("ACKNOWLEDGED" in check and "FOLLOW_UP_REQUIRED" in check and "BLOCKED" in check for check in checks)
