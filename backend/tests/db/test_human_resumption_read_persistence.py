import sqlalchemy as sa

def test_human_resumption_read_schema_preserves_act_fields(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("human_resumption_acts")}
    assert {"tenant_id", "export_id", "actor_id", "state", "rationale"} <= columns
