from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseOutcomeRecord(TenantScopedRecord, Base):
    __tablename__ = "case_outcomes"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("tenant_id", "id"),
        sa.CheckConstraint("outcome IN ('WON', 'LOST', 'UNKNOWN')", name="outcome"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    outcome: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    source_locator: Mapped[str | None] = mapped_column(sa.String(500))
    reservations_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    unknown_reason: Mapped[str | None] = mapped_column(sa.String(1000))
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
