import sqlalchemy as sa

def test_payment_timeline_source_schema_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("payment_post_reception_cycles")}
    assert {"tenant_id", "case_id", "trigger_event", "status", "cash_assumption", "post_reception_cost_note"} <= columns
