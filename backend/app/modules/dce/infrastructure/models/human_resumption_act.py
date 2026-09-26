# ruff: noqa: E501
from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class HumanResumptionActRecord(TenantScopedRecord, Base):
    __tablename__ = "human_resumption_acts"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id", "export_id"], ["contract_query_exports.tenant_id", "contract_query_exports.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "id", name="uq_human_resumption_acts__tenant_id"),
        sa.CheckConstraint("state IN ('ACKNOWLEDGED', 'FOLLOW_UP_REQUIRED', 'BLOCKED')", name="human_resumption_state_closed"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    export_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    state: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    rationale: Mapped[str] = mapped_column(sa.Text, nullable=False)

