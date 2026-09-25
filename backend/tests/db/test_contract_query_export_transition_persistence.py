import sqlalchemy as sa


def test_export_transition_schema_is_closed(database_engine: sa.Engine) -> None:
    checks = {item["sqltext"] for item in sa.inspect(database_engine).get_check_constraints("contract_query_export_transitions")}
    assert any("REQUESTED" in check and "READY" in check and "UNKNOWN" in check for check in checks)
