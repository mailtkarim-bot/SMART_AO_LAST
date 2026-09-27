import sqlalchemy as sa

def test_unknown_provenance_read_schema_preserves_projection_fields(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("unknown_audit_provenance")}
    assert {"tenant_id", "export_id", "source_type", "source_event_id", "actor_id", "status", "occurred_at", "rationale"} <= columns
