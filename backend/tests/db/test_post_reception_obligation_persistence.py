# ruff: noqa: E501, I001
import sqlalchemy as sa


def test_post_reception_obligation_table_is_tenant_scoped_and_constrained(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {
        column["name"]
        for column in inspector.get_columns("post_reception_obligations")
    }
    assert {
        "tenant_id",
        "case_id",
        "obligation_type",
        "summary",
        "source_refs_json",
        "due_date",
        "resource_note",
        "cost_estimate_note",
        "fulfillment_proof_refs_json",
        "sanction_ref",
        "status",
        "actor_id",
    } <= columns
    assert inspector.get_check_constraints("post_reception_obligations")
