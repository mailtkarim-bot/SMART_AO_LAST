from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from app.modules.membership.application.financial_report import (
    FinancialReportLineProjection,
    FinancialReportProjection,
)
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    FinancialReportSnapshotRecord,
)


class SqlAlchemyFinancialReportReader:
    """Infrastructure adapter for tenant-scoped financial report projections."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def exists(self, *, tenant_id: UUID, case_id: UUID, report_id: UUID) -> bool:
        with self._session_factory() as session:
            snapshot_id = session.scalar(
                sa.select(FinancialReportSnapshotRecord.id).where(
                    FinancialReportSnapshotRecord.tenant_id == tenant_id,
                    FinancialReportSnapshotRecord.case_id == case_id,
                    FinancialReportSnapshotRecord.id == report_id,
                )
            )
        return snapshot_id is not None

    def get(
        self, *, tenant_id: UUID, case_id: UUID, report_id: UUID, state: str
    ) -> FinancialReportProjection | None:
        with self._session_factory() as session:
            return self.get_in_session(
                session, tenant_id=tenant_id, case_id=case_id, report_id=report_id, state=state
            )

    def list_published_in_session(
        self, session: Session, *, tenant_id: UUID, case_id: UUID, limit: int
    ) -> tuple[FinancialReportProjection, ...]:
        ids = session.scalars(
            sa.select(FinancialReportSnapshotRecord.id)
            .where(
                FinancialReportSnapshotRecord.tenant_id == tenant_id,
                FinancialReportSnapshotRecord.case_id == case_id,
                FinancialReportSnapshotRecord.state == "PUBLISHED",
            )
            .order_by(
                FinancialReportSnapshotRecord.published_at.desc(), FinancialReportSnapshotRecord.id
            )
            .limit(limit)
        )
        return tuple(
            report
            for report_id in ids
            if (
                report := self.get_in_session(
                    session,
                    tenant_id=tenant_id,
                    case_id=case_id,
                    report_id=report_id,
                    state="PUBLISHED",
                )
            )
            is not None
        )

    def get_in_session(
        self, session: Session, *, tenant_id: UUID, case_id: UUID, report_id: UUID, state: str
    ) -> FinancialReportProjection | None:
        snapshot = session.scalar(
            sa.select(FinancialReportSnapshotRecord).where(
                FinancialReportSnapshotRecord.tenant_id == tenant_id,
                FinancialReportSnapshotRecord.case_id == case_id,
                FinancialReportSnapshotRecord.id == report_id,
                FinancialReportSnapshotRecord.state == state,
            )
        )
        if snapshot is None:
            return None
        lines = session.scalars(
            sa.select(FinancialReportLineRecord)
            .where(
                FinancialReportLineRecord.tenant_id == tenant_id,
                FinancialReportLineRecord.snapshot_id == snapshot.id,
            )
            .order_by(FinancialReportLineRecord.created_at, FinancialReportLineRecord.id)
        ).all()
        return FinancialReportProjection(
            report_id=snapshot.id,
            case_id=snapshot.case_id,
            currency_code=snapshot.currency_code,
            calculated_at=snapshot.calculated_at,
            ruleset_version=snapshot.ruleset_version,
            summary={
                "sales_total_minor": snapshot.sales_total_minor,
                "direct_cost_total_minor": snapshot.direct_cost_total_minor,
                "overhead_total_minor": snapshot.overhead_total_minor,
                "subcontracting_total_minor": snapshot.subcontracting_total_minor,
                "contingency_total_minor": snapshot.contingency_total_minor,
                "gross_margin_minor": snapshot.gross_margin_minor,
                "gross_margin_rate_bps": snapshot.gross_margin_rate_bps,
                "forecast_cashflow_minor": snapshot.forecast_cashflow_minor,
            },
            lines=tuple(
                FinancialReportLineProjection(
                    line_id=line.id,
                    category=line.category,
                    label=line.label,
                    quantity_decimal=line.quantity_decimal,
                    unit=line.unit,
                    amount_minor=line.amount_minor,
                    currency_code=snapshot.currency_code,
                )
                for line in lines
            ),
            status=snapshot.state,
            aggregate_revision=snapshot.aggregate_revision,
        )
