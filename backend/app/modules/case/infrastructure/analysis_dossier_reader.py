"""One database snapshot for the dossier and all native supplementary reads."""

from app.modules.case.infrastructure.analysis_summary_reader import (
    SqlAlchemyCaseAnalysisSummaryReader,
)


def read_analysis_dossier(session, *, session_factory, tenant_id, case_id):
    summary = SqlAlchemyCaseAnalysisSummaryReader(session).get(tenant_id=tenant_id, case_id=case_id)
    if summary is not None:
        from app.modules.case.application.analysis_summary import project_analysis_pricing
        from app.modules.pricing.infrastructure.scenario_reader import (
            SqlAlchemyPricingScenarioReader,
        )

        scenarios = SqlAlchemyPricingScenarioReader(session_factory).list_for_case_in_session(
            session, tenant_id=tenant_id, case_id=case_id, limit=101
        )
        price = next(axis for axis in summary["axes"] if axis["code"] == "PRICE")
        price["pricing_scenarios"] = project_analysis_pricing(
            scenarios[:100],
            case_id=case_id,
            source_context_state=summary["source_context_state"],
        )
        summary["truncated"] = summary["truncated"] or len(scenarios) > 100
        if price["pricing_scenarios"]:
            price["status"] = "REVIEW_REQUIRED"
        from app.modules.case.application.analysis_summary import project_analysis_cash
        from app.modules.membership.infrastructure.financial_report_reader import (
            SqlAlchemyFinancialReportReader,
        )

        reports = SqlAlchemyFinancialReportReader(session_factory).list_published_in_session(
            session, tenant_id=tenant_id, case_id=case_id, limit=21
        )
        cash = next(axis for axis in summary["axes"] if axis["code"] == "CASH")
        cash["cash_reports"] = project_analysis_cash(
            reports[:20],
            case_id=case_id,
            source_context_state=summary["source_context_state"],
        )
        cash["pricing_scenarios"] = price["pricing_scenarios"]
        summary["truncated"] = summary["truncated"] or len(reports) > 20
        if cash["cash_reports"] or cash["pricing_scenarios"]:
            cash["status"] = "REVIEW_REQUIRED"
    if summary is not None:
        from app.modules.case.application.analysis_summary import project_analysis_capacity
        from app.modules.optimization.infrastructure.dated_service import (
            read_dated_capacity_in_session,
        )

        plans = read_dated_capacity_in_session(session, tenant_id=tenant_id, case_id=case_id)
        capacity = next(axis for axis in summary["axes"] if axis["code"] == "CAPACITY")
        projected = project_analysis_capacity(
            plans, case_id=case_id, source_context_state=summary["source_context_state"]
        )
        # Keep existing dossier hashes identical when no capacity has ever been recorded.
        if projected:
            capacity["capacity_plans"] = projected
            capacity["status"] = "REVIEW_REQUIRED"
        summary["truncated"] = summary["truncated"] or plans["history_has_more"]
    if summary is not None:
        import sqlalchemy as sa

        from app.modules.case.application.analysis_dossier import dossier_digest
        from app.modules.case.infrastructure.models.analysis_dossier import (
            AnalysisDossierReviewRecord as Review,
        )
        from app.modules.case.infrastructure.models.case import CaseRecord

        case = session.scalar(
            sa.select(CaseRecord).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
        )
        summary["case_scope_fingerprint"] = case.scope_fingerprint
        summary["dossier_sha256"] = dossier_digest(summary)
        latest = session.scalar(
            sa.select(Review)
            .where(Review.tenant_id == tenant_id, Review.case_id == case_id)
            .order_by(Review.revision.desc())
            .limit(1)
        )
        summary["dossier_review"] = None
        if latest:
            current = latest.dossier_sha256 == summary["dossier_sha256"]
            summary["dossier_review"] = dict(
                review_id=latest.id,
                revision=latest.revision,
                phase=latest.phase,
                state="CURRENT" if current else "REVIEW_REQUIRED",
                dossier_sha256=latest.dossier_sha256,
                actor_id=latest.actor_id if current else None,
                created_at=latest.created_at,
                axes=latest.axes_json if current else [],
                justification=latest.justification if current else None,
            )
    return summary


def read_analysis_dossier_history(session, *, tenant_id, case_id, before_revision=None):
    import sqlalchemy as sa

    from app.modules.case.application.analysis_dossier import dossier_digest
    from app.modules.case.infrastructure.models.analysis_dossier import (
        AnalysisDossierReviewRecord as Review,
    )

    query = sa.select(Review).where(Review.tenant_id == tenant_id, Review.case_id == case_id)
    if before_revision is not None:
        query = query.where(Review.revision < before_revision)
    rows = session.scalars(query.order_by(Review.revision.desc()).limit(21)).all()
    entries = []
    for row in rows[:20]:
        snapshot = row.snapshot_json
        if (
            dossier_digest(snapshot) != row.dossier_sha256
            or snapshot.get("case_id") != str(case_id)
            or snapshot.get("dce_version_id") != str(row.dce_version_id)
        ):
            raise ValueError("HISTORICAL_DOSSIER_INTEGRITY_UNPROVEN")
        entries.append(
            dict(
                review_id=row.id,
                revision=row.revision,
                phase=row.phase,
                state="HISTORICAL",
                dossier_sha256=row.dossier_sha256,
                dce_version_id=row.dce_version_id,
                actor_id=row.actor_id,
                created_at=row.created_at,
                axes=row.axes_json,
                justification=row.justification,
                snapshot=snapshot,
            )
        )
    return dict(
        case_id=case_id,
        entries=entries,
        next_before_revision=entries[-1]["revision"] if len(rows) > 20 else None,
    )
