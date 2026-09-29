"""Create sourced contract instrument versions and link them to human acts."""

# ruff: noqa: E501
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260929_0111"
down_revision = "20260929_0110"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contract_instrument_versions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("instrument_kind", sa.String(24), nullable=False),
        sa.Column("version_reference", sa.String(500), nullable=False),
        sa.Column("source_refs_json", JSONB(), nullable=False),
        sa.Column("evidence_refs_json", JSONB(), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_instrument_versions__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_contract_instrument_versions__tenant_case_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "instrument_kind",
            "version_reference",
            name="uq_contract_instrument_versions__declared_reference",
        ),
        sa.CheckConstraint(
            "instrument_kind IN ('SIGNED_CONTRACT', 'AMENDMENT')",
            name="contract_instrument_version_kind_closed",
        ),
        sa.CheckConstraint(
            "length(trim(version_reference)) > 0",
            name="contract_instrument_version_reference_required",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) > 0",
            name="contract_instrument_version_sources_required",
        ),
        sa.CheckConstraint(
            "jsonb_array_length(evidence_refs_json) > 0",
            name="contract_instrument_version_proofs_required",
        ),
        sa.Index(
            "ix_contract_instrument_versions_tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
    )
    op.execute("""
        CREATE FUNCTION reject_contract_instrument_version_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'contract instrument versions are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_instrument_versions_append_only
        BEFORE UPDATE OR DELETE ON contract_instrument_versions
        FOR EACH ROW EXECUTE FUNCTION reject_contract_instrument_version_mutation();
    """)
    op.add_column(
        "contract_execution_evidence",
        sa.Column("contract_instrument_version_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_contract_execution_evidence__contract_instrument_version",
        "contract_execution_evidence",
        "contract_instrument_versions",
        ["tenant_id", "case_id", "contract_instrument_version_id"],
        ["tenant_id", "case_id", "id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_contract_execution_evidence__contract_instrument_version",
        "contract_execution_evidence",
        type_="foreignkey",
    )
    op.drop_column("contract_execution_evidence", "contract_instrument_version_id")
    op.execute(
        "DROP TRIGGER IF EXISTS contract_instrument_versions_append_only ON contract_instrument_versions"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_contract_instrument_version_mutation()")
    op.drop_table("contract_instrument_versions")
