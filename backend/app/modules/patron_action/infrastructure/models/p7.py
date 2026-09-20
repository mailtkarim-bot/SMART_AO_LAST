from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseP7ResultRecord(TenantScopedRecord, Base):
    __tablename__ = "case_p7_results"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "p6_control_id"],
            ["case_p6_controls.tenant_id", "case_p6_controls.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_p7_results__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "p6_control_id", name="uq_case_p7_results__tenant_id_p6_control_id"
        ),
        sa.CheckConstraint("result IN ('COMPLETED', 'UNKNOWN', 'INTERRUPTED')", name="result"),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    p6_control_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    result: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    reason: Mapped[str | None] = mapped_column(sa.String(2_000))
    reservations_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
