import sqlalchemy as sa


def test_regulatory_profiles_migration_is_tenant_scoped_and_status_closed(
    database_engine: sa.Engine,
) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("regulatory_profiles")}
    checks = {check["sqltext"] for check in inspector.get_check_constraints("regulatory_profiles")}
    indexes = {index["name"] for index in inspector.get_indexes("regulatory_profiles")}

    assert {
        "id",
        "tenant_id",
        "case_id",
        "profile_version",
        "status",
        "facts_json",
        "source_refs_json",
        "effective_from",
        "effective_until",
    } <= columns
    assert any("ACTIVE" in check and "FUTURE" in check for check in checks)
    assert any("profile_version" in check for check in checks)
    assert "ix_regulatory_profiles__tenant_case_version" in indexes
