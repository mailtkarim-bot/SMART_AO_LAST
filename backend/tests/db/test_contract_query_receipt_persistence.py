import sqlalchemy as sa


def test_contract_query_receipt_schema_is_tenant_scoped_and_bounded(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("contract_query_receipts")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("contract_query_receipts")}
    assert {"id", "tenant_id", "case_id", "filters_json", "order_key", "limit_value", "offset_value", "actor_id"} <= columns
    assert any("limit_value" in check for check in checks)
    assert any("offset_value" in check for check in checks)
