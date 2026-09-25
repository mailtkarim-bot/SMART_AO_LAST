import sqlalchemy as sa


def test_contract_query_export_schema_is_closed_and_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("contract_query_exports")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("contract_query_exports")}
    assert {"id", "tenant_id", "case_id", "filters_json", "status", "actor_id"} <= columns
    assert any("REQUESTED" in check and "REFUSED" in check for check in checks)
