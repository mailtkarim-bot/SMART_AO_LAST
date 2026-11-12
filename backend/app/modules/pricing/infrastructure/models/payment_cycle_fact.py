"""Append-only financial declarations scoped to the exact native cycle and Case."""

from datetime import date
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class PaymentCycleFactRecord(TenantScopedRecord, Base):
    __tablename__ = "payment_cycle_facts"
    __table_args__ = (
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "cycle_id"],
            [
                "payment_post_reception_cycles.tenant_id",
                "payment_post_reception_cycles.case_id",
                "payment_post_reception_cycles.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "cycle_id", "compared_to_fact_id"],
            [
                "payment_cycle_facts.tenant_id",
                "payment_cycle_facts.case_id",
                "payment_cycle_facts.cycle_id",
                "payment_cycle_facts.id",
            ],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint(
            "tenant_id", "case_id", "cycle_id", "id", name="uq_payment_facts__context"
        ),
        sa.CheckConstraint(
            "kind IN ('INVOICE_DECLARED','PAYMENT_EXPECTED','COLLECTION_RECORDED')",
            name="payment_fact_kind",
        ),
        sa.CheckConstraint(
            "amount_minor > 0 AND amount_minor <= 9000000000000000", name="payment_fact_amount"
        ),
        sa.CheckConstraint("currency_code ~ '^[A-Z]{3}$'", name="payment_fact_currency"),
        sa.CheckConstraint(
            "jsonb_array_length(source_refs_json) BETWEEN 1 AND 32 "
            "AND jsonb_array_length(evidence_refs_json) BETWEEN 1 AND 32",
            name="payment_fact_sources",
        ),
        sa.CheckConstraint("length(trim(justification)) > 0", name="payment_fact_justification"),
        sa.CheckConstraint(
            "compared_to_fact_id IS NULL OR "
            "(compared_to_fact_id <> id AND kind <> 'INVOICE_DECLARED')",
            name="payment_fact_parent",
        ),
        sa.Index("ix_payment_fact_tenant_case", "tenant_id", "case_id", "created_at", "id"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    cycle_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    compared_to_fact_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True))
    kind: Mapped[str] = mapped_column(sa.String(24), nullable=False)
    amount_minor: Mapped[int] = mapped_column(sa.BigInteger, nullable=False)
    currency_code: Mapped[str] = mapped_column(sa.String(3), nullable=False)
    declared_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    source_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    evidence_refs_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    justification: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    source_snapshot_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
