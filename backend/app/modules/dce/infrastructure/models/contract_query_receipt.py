# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractQueryReceiptRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_query_receipts"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_contract_query_receipts__tenant_id"),
        sa.CheckConstraint("limit_value > 0 AND limit_value <= 100", name="contract_query_receipt_limit_closed"),
        sa.CheckConstraint("offset_value >= 0", name="contract_query_receipt_offset_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    filters_json: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    order_key: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    limit_value: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    offset_value: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)

