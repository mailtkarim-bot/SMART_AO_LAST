"""Explicit binary format and immutable buyer-frame provenance; legacy defaults retained."""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision = "20261027_0146"
down_revision = "20261025_0145"
branch_labels = None
depends_on = None


def upgrade():
    for table in ("generated_technical_documents", "technical_response_drafts"):
        op.add_column(
            table,
            sa.Column("content_format", sa.String(16), nullable=False, server_default="MARKDOWN"),
        )
        op.create_check_constraint(
            op.f(f"ck_{table}__content_format"), table, "content_format IN ('MARKDOWN','DOCX')"
        )
    op.add_column(
        "technical_response_drafts", sa.Column("content_provenance_json", JSONB, nullable=True)
    )
    op.create_check_constraint(
        op.f("ck_generated_technical_documents__docx_technical_only"),
        "generated_technical_documents",
        "content_format <> 'DOCX' OR document_kind = 'TECHNICAL_RESPONSE'",
    )
    op.create_check_constraint(
        op.f("ck_technical_response_drafts__content_provenance"),
        "technical_response_drafts",
        "(content_format = 'MARKDOWN' AND content_provenance_json IS NULL) OR "
        "(content_format = 'DOCX' AND content_provenance_json IS NOT NULL "
        "AND jsonb_typeof(content_provenance_json) = 'object')",
    )


def downgrade():
    connection = op.get_bind()
    if connection.execute(
        sa.text(
            "SELECT EXISTS(SELECT 1 FROM technical_response_drafts WHERE content_format='DOCX') "
            "OR EXISTS(SELECT 1 FROM generated_technical_documents WHERE content_format='DOCX')"
        )
    ).scalar():
        raise RuntimeError("BUYER_DOCX_PROOF_LOSS_REFUSED")
    op.drop_constraint(
        op.f("ck_technical_response_drafts__content_provenance"),
        "technical_response_drafts",
        type_="check",
    )
    op.drop_constraint(
        op.f("ck_generated_technical_documents__docx_technical_only"),
        "generated_technical_documents",
        type_="check",
    )
    op.drop_column("technical_response_drafts", "content_provenance_json")
    for table in ("technical_response_drafts", "generated_technical_documents"):
        op.drop_constraint(op.f(f"ck_{table}__content_format"), table, type_="check")
        op.drop_column(table, "content_format")
