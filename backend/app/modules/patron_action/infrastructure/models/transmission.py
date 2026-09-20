from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class CaseOutcomeTransmissionRecord(TenantScopedRecord, Base):
    __tablename__ = "case_outcome_transmissions"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "outcome_id"],
            ["case_outcomes.tenant_id", "case_outcomes.id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("tenant_id", "id", name="uq_case_outcome_transmissions__tenant_id_id"),
        sa.UniqueConstraint(
            "tenant_id", "outcome_id", name="uq_case_outcome_transmissions__tenant_id_outcome_id"
        ),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    outcome_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    lot_reference: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    recipient: Mapped[str] = mapped_column(sa.String(120), nullable=False)
    reservations_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    membership_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    command_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    correlation_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
