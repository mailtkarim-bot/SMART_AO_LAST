import sqlalchemy as sa

def test_payment_cycle_write_table_is_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("payment_post_reception_cycles")}
    assert {"id", "tenant_id", "case_id", "source_refs_json", "trigger_event", "status", "cash_assumption", "post_reception_cost_note", "actor_id"} <= columns
