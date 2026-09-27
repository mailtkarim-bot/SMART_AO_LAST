def test_closure_review_uses_existing_provenance_sources(database_engine) -> None:
    from sqlalchemy import inspect
    tables = set(inspect(database_engine).get_table_names())
    assert "unknown_audit_provenance" in tables
