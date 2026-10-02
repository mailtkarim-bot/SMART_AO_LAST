"""Persist A1 links between conditional decisions and exact evidence."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20261001_0123"
down_revision = "20260930_0122"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "contract_baseline_deviation_impacts",
        sa.Column("dce_requirement_id", sa.UUID(), nullable=True),
    )
    op.add_column(
        "contract_baseline_deviation_impacts",
        sa.Column("dce_requirement_revision", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        "ck_contract_baseline_impacts_requirement_pair",
        "contract_baseline_deviation_impacts",
        "(dce_requirement_id IS NULL AND dce_requirement_revision IS NULL) OR "
        "(dce_requirement_id IS NOT NULL AND dce_requirement_revision > 0)",
    )
    op.create_foreign_key(
        "fk_contract_baseline_impacts_dce_requirement",
        "contract_baseline_deviation_impacts",
        "dce_requirements",
        ["tenant_id", "dce_requirement_id"],
        ["tenant_id", "id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_decision_conditions_tenant_decision_id",
        "decision_conditions",
        ["tenant_id", "decision_id", "id"],
    )
    op.create_table(
        "decision_condition_contract_evidence_links",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("decision_id", sa.UUID(), nullable=False),
        sa.Column("condition_id", sa.UUID(), nullable=False),
        sa.Column("context_id", sa.UUID(), nullable=False),
        sa.Column("dce_requirement_id", sa.UUID(), nullable=False),
        sa.Column("dce_requirement_revision", sa.Integer(), nullable=False),
        sa.Column("contract_impact_id", sa.UUID(), nullable=False),
        sa.Column("proof_revision", sa.Integer(), nullable=False),
        sa.Column("profile_version_id", sa.UUID(), nullable=False),
        sa.Column("profile_version", sa.Integer(), nullable=False),
        sa.Column("profile_content_sha256", sa.CHAR(64), nullable=False),
        sa.Column("created_by_actor_id", sa.UUID(), nullable=False),
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
            ["tenant_id", "decision_id"],
            ["decisions.tenant_id", "decisions.id"],
            name="fk_decision_condition_contract_links__decision",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "decision_id", "condition_id"],
            [
                "decision_conditions.tenant_id",
                "decision_conditions.decision_id",
                "decision_conditions.id",
            ],
            name="fk_decision_condition_contract_links__condition",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "decision_id", "context_id"],
            [
                "decision_contexts.tenant_id",
                "decision_contexts.decision_id",
                "decision_contexts.id",
            ],
            name="fk_decision_condition_contract_links__context",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "contract_impact_id"],
            [
                "contract_baseline_deviation_impacts.tenant_id",
                "contract_baseline_deviation_impacts.id",
            ],
            name="fk_decision_condition_contract_links__impact",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "dce_requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_decision_condition_contract_links__requirement",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "profile_version_id", "profile_version", "profile_content_sha256"],
            [
                "enterprise_business_method_profile_versions.tenant_id",
                "enterprise_business_method_profile_versions.id",
                "enterprise_business_method_profile_versions.version_number",
                "enterprise_business_method_profile_versions.content_sha256",
            ],
            name="fk_decision_condition_contract_links__profile",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_decision_condition_contract_links__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id", "command_id", name="uq_decision_condition_contract_links__command"
        ),
        sa.UniqueConstraint(
            "tenant_id", "idempotency_key", name="uq_decision_condition_contract_links__idempotency"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "decision_id",
            "condition_id",
            "contract_impact_id",
            "proof_revision",
            name="uq_decision_condition_contract_links__relation",
        ),
        sa.CheckConstraint(
            "dce_requirement_revision > 0 AND proof_revision > 0 AND profile_version > 0",
            name="ck_decision_condition_contract_links_revisions",
        ),
        sa.CheckConstraint(
            "profile_content_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_decision_condition_contract_links_profile_hash",
        ),
    )
    op.create_index(
        "ix_decision_condition_contract_links__tenant_decision",
        "decision_condition_contract_evidence_links",
        ["tenant_id", "decision_id", "condition_id"],
    )
    op.execute("""
        CREATE FUNCTION reject_a1_condition_evidence_mutation() RETURNS trigger AS $$
        BEGIN RAISE EXCEPTION 'decision_condition_contract_evidence_links is append-only'; END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER a1_condition_evidence_append_only
        BEFORE UPDATE OR DELETE ON decision_condition_contract_evidence_links
        FOR EACH ROW EXECUTE FUNCTION reject_a1_condition_evidence_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS a1_condition_evidence_append_only "
        "ON decision_condition_contract_evidence_links"
    )
    op.execute("DROP FUNCTION IF EXISTS reject_a1_condition_evidence_mutation()")
    op.drop_index(
        "ix_decision_condition_contract_links__tenant_decision",
        table_name="decision_condition_contract_evidence_links",
    )
    op.drop_table("decision_condition_contract_evidence_links")
    op.drop_constraint(
        "uq_decision_conditions_tenant_decision_id", "decision_conditions", type_="unique"
    )
    op.drop_constraint(
        "fk_contract_baseline_impacts_dce_requirement",
        "contract_baseline_deviation_impacts",
        type_="foreignkey",
    )
    op.drop_constraint(
        "ck_contract_baseline_impacts_requirement_pair",
        "contract_baseline_deviation_impacts",
        type_="check",
    )
    op.drop_column("contract_baseline_deviation_impacts", "dce_requirement_revision")
    op.drop_column("contract_baseline_deviation_impacts", "dce_requirement_id")
