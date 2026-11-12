from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PricingPositionReviewRecord(TenantScopedRecord, Base):
    __tablename__ = "pricing_position_reviews"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tenant_id", "case_id", "id"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"],
            ["cases.tenant_id", "cases.id"],
            name="fk_ppr_case",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "position_id"],
            ["pricing_import_rows.tenant_id", "pricing_import_rows.id"],
            name="fk_ppr_position",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "previous_id"],
            [
                "pricing_position_reviews.tenant_id",
                "pricing_position_reviews.case_id",
                "pricing_position_reviews.id",
            ],
            name="fk_ppr_previous",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "requirement_id"],
            ["dce_requirements.tenant_id", "dce_requirements.id"],
            name="fk_ppr_requirement",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "offer_price_id"],
            [
                "partner_offer_price_declarations.tenant_id",
                "partner_offer_price_declarations.case_id",
                "partner_offer_price_declarations.id",
            ],
            name="fk_ppr_offer",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "scope_review_id"],
            [
                "partner_offer_scope_reviews.tenant_id",
                "partner_offer_scope_reviews.case_id",
                "partner_offer_scope_reviews.id",
            ],
            name="fk_ppr_scope",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "position_id", "revision", name="uq_ppr_position_revision"
        ),
        sa.UniqueConstraint("tenant_id", "command_id", name="uq_ppr_command"),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_ppr_idempotency"),
        sa.CheckConstraint("revision > 0", name="revision_positive"),
        sa.CheckConstraint(
            "basis_sha256 ~ '^[a-f0-9]{64}$' AND base_sha256 ~ '^[a-f0-9]{64}$'",
            name="source_hashes",
        ),
        sa.CheckConstraint("jsonb_typeof(source_snapshot_json)='object'", name="source_object"),
        sa.CheckConstraint("length(btrim(justification)) BETWEEN 1 AND 2000", name="justification"),
        sa.Index("ix_ppr_latest", "tenant_id", "case_id", "position_id", "revision"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    position_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    previous_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    requirement_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    offer_price_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    scope_review_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    base_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    basis_sha256: Mapped[str] = mapped_column(sa.CHAR(64), nullable=False)
    source_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    justification: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)


class PricingPositionCostReferenceRecord(TenantScopedRecord, Base):
    __tablename__ = "pricing_position_cost_references"
    __table_args__ = (
        sa.PrimaryKeyConstraint("tenant_id", "case_id", "review_id", "line_id"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "review_id"],
            [
                "pricing_position_reviews.tenant_id",
                "pricing_position_reviews.case_id",
                "pricing_position_reviews.id",
            ],
            name="fk_ppr_cost_review",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "line_id"],
            ["financial_report_lines.tenant_id", "financial_report_lines.id"],
            name="fk_ppr_cost_line",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "report_id"],
            ["financial_report_snapshots.tenant_id", "financial_report_snapshots.id"],
            name="fk_ppr_cost_report",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("report_revision >= 0", name="report_revision"),
        sa.Index("ix_ppr_cost_refs", "tenant_id", "case_id", "line_id"),
    )
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    review_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    line_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    report_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    report_revision: Mapped[int] = mapped_column(sa.Integer, nullable=False)
