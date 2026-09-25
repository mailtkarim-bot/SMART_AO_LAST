import sqlalchemy as sa


def test_export_proof_verification_schema_is_closed_and_tenant_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("export_proof_verifications")}
    checks = {item["sqltext"] for item in inspector.get_check_constraints("export_proof_verifications")}
    assert {"id", "tenant_id", "export_id", "outcome", "calculated_sha256", "checked_by_actor_id"} <= columns
    assert any("MATCH" in check and "MISMATCH" in check and "UNAVAILABLE" in check for check in checks)
