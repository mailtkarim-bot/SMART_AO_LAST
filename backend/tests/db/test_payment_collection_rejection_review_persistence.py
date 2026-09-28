# ruff: noqa: E501, I001
import sqlalchemy as sa


def test_payment_collection_rejection_review_schema_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("payment_collection_rejection_reviews")}
    assert {"tenant_id", "case_id", "reviewer_id", "rejected_count", "decision", "rationale"} <= columns
