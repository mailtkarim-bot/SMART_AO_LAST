# ruff: noqa: E501, I001
import sqlalchemy as sa


def test_payment_unknown_audit_owner_act_schema_is_tenant_scoped(database_engine: sa.Engine) -> None:
    columns = {column["name"] for column in sa.inspect(database_engine).get_columns("payment_unknown_audit_owner_acts")}
    assert {"tenant_id", "case_id", "owner_id", "approved", "rationale"} <= columns
