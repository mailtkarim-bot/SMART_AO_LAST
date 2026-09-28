import sqlalchemy as sa

def test_payment_cycle_write_schema_is_tenant_and_case_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("payment_post_reception_cycles")}
    assert {"id", "tenant_id", "case_id", "actor_id", "status"} <= columns
