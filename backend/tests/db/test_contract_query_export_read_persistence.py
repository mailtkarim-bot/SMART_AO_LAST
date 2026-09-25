import sqlalchemy as sa

def test_contract_query_export_status_constraint_is_closed(database_engine: sa.Engine) -> None:
    checks = {item["sqltext"] for item in sa.inspect(database_engine).get_check_constraints("contract_query_exports")}
    assert any("REQUESTED" in check and "UNKNOWN" in check and "REFUSED" in check for check in checks)
