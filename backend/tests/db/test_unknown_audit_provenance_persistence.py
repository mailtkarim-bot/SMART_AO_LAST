import sqlalchemy as sa

def test_unknown_provenance_schema_is_tenant_scoped_and_source_closed(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("unknown_audit_provenance")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("unknown_audit_provenance")}
    assert {"tenant_id", "export_id", "source_type", "source_event_id", "actor_id", "status", "occurred_at", "rationale"} <= columns
    assert any("TRANSITION" in check and "HUMAN_RESUMPTION" in check and "VERIFICATION" in check for check in checks)
