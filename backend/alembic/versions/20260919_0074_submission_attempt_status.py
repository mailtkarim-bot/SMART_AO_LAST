"""Allow an explicit human deposit attempt with an unknown external outcome."""

from collections.abc import Sequence

from alembic import op

revision = "20260919_0074"
down_revision = "20260915_0073"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint("evidence_type", "submission_evidence", type_="check")
    op.drop_constraint("status", "submission_evidence", type_="check")
    op.create_check_constraint(
        "evidence_type",
        "submission_evidence",
        "evidence_type IN ('MANUAL_RECEIPT', 'MANUAL_PORTAL_REFERENCE', 'HUMAN_DEPOSIT_ATTEMPT')",
    )
    op.create_check_constraint(
        "status",
        "submission_evidence",
        "status IN ('RECEIVED', 'REJECTED', 'UNKNOWN')",
    )


def downgrade() -> None:
    op.drop_constraint("evidence_type", "submission_evidence", type_="check")
    op.drop_constraint("status", "submission_evidence", type_="check")
    op.execute("DROP TRIGGER IF EXISTS submission_evidence_append_only ON submission_evidence")
    op.execute("DROP FUNCTION IF EXISTS prevent_submission_evidence_mutation()")
    op.execute(
        "DELETE FROM submission_evidence "
        "WHERE evidence_type = 'HUMAN_DEPOSIT_ATTEMPT' OR status = 'UNKNOWN'"
    )
    op.create_check_constraint(
        "evidence_type",
        "submission_evidence",
        "evidence_type IN ('MANUAL_RECEIPT', 'MANUAL_PORTAL_REFERENCE')",
    )
    op.create_check_constraint(
        "status",
        "submission_evidence",
        "status IN ('RECEIVED', 'REJECTED')",
    )
