import sqlalchemy as sa


def test_export_transition_stores_local_proof_hash(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("contract_query_export_transitions")}
    assert "local_proof_ref" in columns
    assert "local_proof_sha256" in columns
