"""Persist append-only Patron declarations that an amendment replaces versions."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260929_0112"
down_revision = "20260929_0111"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "contract_instrument_supersessions",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("case_id", sa.UUID(), nullable=False),
        sa.Column("replacing_contract_instrument_version_id", sa.UUID(), nullable=False),
        sa.Column("replaced_contract_instrument_version_id", sa.UUID(), nullable=False),
        sa.Column("rationale", sa.String(2000), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "replacing_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_ci_supersessions_replacing_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "replaced_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_ci_supersessions_replaced_same_case",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_contract_instrument_supersessions__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "id",
            name="uq_contract_instrument_supersessions__tenant_case_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "replacing_contract_instrument_version_id",
            "replaced_contract_instrument_version_id",
            name="uq_contract_instrument_supersessions__declared_pair",
        ),
        sa.CheckConstraint(
            "replacing_contract_instrument_version_id <> replaced_contract_instrument_version_id",
            name="contract_instrument_supersession_distinct_versions",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="contract_instrument_supersession_rationale_required",
        ),
        sa.Index(
            "ix_contract_instrument_supersessions_tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
        sa.Index(
            "ix_contract_instrument_supersessions_replaced",
            "tenant_id",
            "case_id",
            "replaced_contract_instrument_version_id",
        ),
    )
    op.execute("""
        CREATE FUNCTION validate_contract_instrument_supersession() RETURNS trigger AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM contract_instrument_versions
                WHERE tenant_id = NEW.tenant_id
                  AND case_id = NEW.case_id
                  AND id = NEW.replacing_contract_instrument_version_id
                  AND instrument_kind = 'AMENDMENT'
            ) THEN
                RAISE EXCEPTION 'replacing contract instrument must be a declared amendment';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_instrument_supersessions_require_amendment
        BEFORE INSERT ON contract_instrument_supersessions
        FOR EACH ROW EXECUTE FUNCTION validate_contract_instrument_supersession();
    """)
    op.execute("""
        CREATE FUNCTION reject_contract_instrument_supersession_mutation() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'contract instrument supersessions are append-only';
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER contract_instrument_supersessions_append_only
        BEFORE UPDATE OR DELETE ON contract_instrument_supersessions
        FOR EACH ROW EXECUTE FUNCTION reject_contract_instrument_supersession_mutation();
    """)


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS contract_instrument_supersessions_append_only "
        "ON contract_instrument_supersessions"
    )
    op.execute(
        "DROP FUNCTION IF EXISTS reject_contract_instrument_supersession_mutation()"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS contract_instrument_supersessions_require_amendment "
        "ON contract_instrument_supersessions"
    )
    op.execute("DROP FUNCTION IF EXISTS validate_contract_instrument_supersession()")
    op.drop_table("contract_instrument_supersessions")
