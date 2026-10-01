"""Persist immutable business-method profile versions and case adoptions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260930_0122"
down_revision = "20260930_0121"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _append_only(table_name: str, function_name: str) -> None:
    op.execute(
        f"CREATE FUNCTION {function_name}() RETURNS trigger AS $$ "
        f"BEGIN RAISE EXCEPTION '{table_name} is append-only'; END; $$ LANGUAGE plpgsql"
    )
    op.execute(
        f"CREATE TRIGGER {table_name}_append_only BEFORE UPDATE OR DELETE ON {table_name} "
        f"FOR EACH ROW EXECUTE FUNCTION {function_name}()"
    )


def upgrade() -> None:
    op.execute("""
        CREATE FUNCTION reject_contract_baseline_deviation_impact_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'contract_baseline_deviation_impacts is append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_baseline_deviation_impacts_append_only
        BEFORE UPDATE OR DELETE ON contract_baseline_deviation_impacts
        FOR EACH ROW EXECUTE FUNCTION reject_contract_baseline_deviation_impact_mutation();
    """)
    op.create_table(
        "enterprise_business_method_profile_versions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("schema_version", sa.Integer(), nullable=False),
        sa.Column("profile_json", JSONB(), nullable=False),
        sa.Column("content_sha256", sa.CHAR(64), nullable=False),
        sa.Column("created_by_actor_id", sa.UUID(), nullable=False),
        sa.Column("created_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "company_id"],
            ["enterprise_companies.tenant_id", "enterprise_companies.id"],
            name="fk_business_method_profile_version__company",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "created_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_business_method_profile_version__membership",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_business_method_profile_version__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "company_id",
            "version_number",
            name="uq_business_method_profile_version__number",
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_business_method_profile_version__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", "content_sha256", name="uq_business_method_profile_version__hash"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "id",
            "version_number",
            "content_sha256",
            name="uq_business_method_profile_version__snapshot",
        ),
        sa.CheckConstraint("version_number > 0", name="vnum"),
        sa.CheckConstraint("schema_version = 1", name="schema"),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'", name="hash"
        ),
        sa.CheckConstraint(
            "jsonb_typeof(profile_json) = 'object' "
            "AND profile_json ? 'schema_version' "
            "AND profile_json ->> 'schema_version' = '1' "
            "AND jsonb_typeof(profile_json -> 'terminology') = 'object' "
            "AND jsonb_typeof(profile_json -> 'additional_checks') = 'array' "
            "AND jsonb_array_length(profile_json -> 'additional_checks') <= 40 "
            "AND octet_length(profile_json::text) <= 16000",
            name="shape",
        ),
    )
    op.create_index(
        "ix_business_method_profile_versions__tenant_company_version",
        "enterprise_business_method_profile_versions",
        ["tenant_id", "company_id", "version_number"],
    )
    op.create_index(
        "ix_enterprise_business_method_profile_versions_tenant_id",
        "enterprise_business_method_profile_versions",
        ["tenant_id"],
    )
    op.create_table(
        "case_business_method_profile_adoptions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("profile_version_id", sa.UUID(), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("profile_content_sha256", sa.CHAR(64), nullable=False),
        sa.Column("adoption_revision", sa.Integer(), nullable=False),
        sa.Column("created_by_actor_id", sa.UUID(), nullable=False),
        sa.Column("created_by_membership_id", sa.UUID(), nullable=False),
        sa.Column("command_id", sa.UUID(), nullable=False),
        sa.Column("idempotency_key", sa.UUID(), nullable=False),
        sa.Column("correlation_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"],
            name="fk_case_business_method_adoption__case", ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_version_id", "profile_version", "profile_content_sha256"],
            [
                "enterprise_business_method_profile_versions.tenant_id",
                "enterprise_business_method_profile_versions.id",
                "enterprise_business_method_profile_versions.version_number",
                "enterprise_business_method_profile_versions.content_sha256",
            ],
            name="fk_case_business_method_adoption__profile_hash",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "created_by_membership_id"],
            ["tenant_memberships.tenant_id", "tenant_memberships.id"],
            name="fk_case_business_method_adoption__membership",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_business_method_adoption__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_case_business_method_adoption__command"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "adoption_revision",
            name="uq_case_business_method_adoption__revision",
        ),
        sa.CheckConstraint("adoption_revision > 0", name="arev"),
        sa.CheckConstraint("profile_version > 0", name="pver"),
        sa.CheckConstraint("profile_content_sha256 ~ '^[0-9a-f]{64}$'", name="hash"),
    )
    op.create_index(
        "ix_case_business_method_adoptions__tenant_case_revision",
        "case_business_method_profile_adoptions",
        ["tenant_id", "case_id", "adoption_revision"],
    )
    op.create_index(
        "ix_case_business_method_profile_adoptions_tenant_id",
        "case_business_method_profile_adoptions",
        ["tenant_id"],
    )
    _append_only(
        "enterprise_business_method_profile_versions",
        "reject_business_method_profile_version_mutation",
    )
    _append_only(
        "case_business_method_profile_adoptions",
        "reject_case_business_method_profile_adoption_mutation",
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS contract_baseline_deviation_impacts_append_only "
        "ON contract_baseline_deviation_impacts"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_contract_baseline_deviation_impact_mutation()")
    for table, function in (
        (
            "case_business_method_profile_adoptions",
            "reject_case_business_method_profile_adoption_mutation",
        ),
        (
            "enterprise_business_method_profile_versions",
            "reject_business_method_profile_version_mutation",
        ),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {table}_append_only ON {table}")
        op.execute(f"DROP FUNCTION IF EXISTS {function}()")
    op.drop_index(
        "ix_case_business_method_profile_adoptions_tenant_id",
        table_name="case_business_method_profile_adoptions",
    )
    op.drop_index(
        "ix_case_business_method_adoptions__tenant_case_revision",
        table_name="case_business_method_profile_adoptions",
    )
    op.drop_table("case_business_method_profile_adoptions")
    op.drop_index(
        "ix_enterprise_business_method_profile_versions_tenant_id",
        table_name="enterprise_business_method_profile_versions",
    )
    op.drop_index(
        "ix_business_method_profile_versions__tenant_company_version",
        table_name="enterprise_business_method_profile_versions",
    )
    op.drop_table("enterprise_business_method_profile_versions")
