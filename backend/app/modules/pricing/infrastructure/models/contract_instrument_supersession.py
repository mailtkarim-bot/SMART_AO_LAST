from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.platform.persistence.base import Base, TenantScopedRecord


class ContractInstrumentSupersessionRecord(TenantScopedRecord, Base):
    __tablename__ = "contract_instrument_supersessions"
    __table_args__ = (
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id"], ["cases.tenant_id", "cases.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "replacing_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_ci_supersessions_replacing_same_case",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id", "case_id", "replaced_contract_instrument_version_id"],
            [
                "contract_instrument_versions.tenant_id",
                "contract_instrument_versions.case_id",
                "contract_instrument_versions.id",
            ],
            ondelete="RESTRICT",
            name="fk_ci_supersessions_replaced_same_case",
        ),
        sa.UniqueConstraint(
            "tenant_id", "id", name="uq_contract_instrument_supersessions__tenant_id"
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "id",
            name="uq_contract_instrument_supersessions__tenant_case_id",
        ),
        sa.UniqueConstraint(
            "tenant_id",
            "case_id",
            "replacing_contract_instrument_version_id",
            "replaced_contract_instrument_version_id",
            name="uq_contract_instrument_supersessions__declared_pair",
        ),
        sa.CheckConstraint(
            "replacing_contract_instrument_version_id <> replaced_contract_instrument_version_id",
            name="contract_instrument_supersession_distinct_versions",
        ),
        sa.CheckConstraint(
            "length(trim(rationale)) > 0",
            name="contract_instrument_supersession_rationale_required",
        ),
        sa.Index(
            "ix_contract_instrument_supersessions_tenant_case_created",
            "tenant_id",
            "case_id",
            "created_at",
            "id",
        ),
        sa.Index(
            "ix_contract_instrument_supersessions_replaced",
            "tenant_id",
            "case_id",
            "replaced_contract_instrument_version_id",
        ),
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    case_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    replacing_contract_instrument_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    replaced_contract_instrument_version_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False
    )
    rationale: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    actor_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
    )
