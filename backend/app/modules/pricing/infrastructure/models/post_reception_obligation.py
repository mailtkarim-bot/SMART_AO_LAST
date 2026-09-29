# ruff: noqa: E501, I001
from __future__ import annotations

from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PostReceptionObligationRecord(TenantScopedRecord, Base):
    __tablename__ = "post_reception_obligations"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "origin_reception_act_id"],
            [
                "contract_execution_evidence.tenant_id",
                "contract_execution_evidence.case_id",
                "contract_execution_evidence.id",
            ],
            ondelete="RESTRICT",
            name="fk_post_reception_obligation_origin_reception_same_case",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_post_reception_obligations__tenant_id"),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "id", name="uq_post_reception_obligations__tenant_case_id"
        ),
        sa.CheckConstraint(
            "origin_reception_act_id IS NULL OR obligation_type = 'RESERVES_LIFTING'",
            name="post_reception_obligation_reception_link_type",
        ),
        sa.CheckConstraint(
            "obligation_type IN ('OPR', 'TESTS', 'COMMISSIONING', 'TRAINING', 'DOE_DIUO', 'RESERVES_LIFTING', 'GPA', 'INITIAL_MAINTENANCE', 'SPARE_STOCK', 'ON_CALL', 'ADMIN_CLOSURE', 'GUARANTEE_RELEASE')",
            name="post_reception_obligation_type_closed",
        ),
        sa.CheckConstraint(
            "status = 'REVIEW_REQUIRED'", name="post_reception_obligation_initial_status"
        ),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    obligation_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    origin_reception_act_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    summary: Mapped[str] = mapped_column(sa.Text, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    due_date: Mapped[date | None] = mapped_column(sa.Date)
    resource_note: Mapped[str | None] = mapped_column(sa.Text)
    cost_estimate_note: Mapped[str | None] = mapped_column(sa.Text)
    fulfillment_proof_refs_json: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    sanction_ref: Mapped[str | None] = mapped_column(sa.Text)
    status: Mapped[str] = mapped_column(
        sa.String(24), nullable=False, server_default="REVIEW_REQUIRED"
    )
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
