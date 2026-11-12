"""Transactional cash declarations, using the existing Case lock and financial records."""

from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.pricing.domain.cash_schedule import CashDeclaration, project_schedule
from app.modules.pricing.infrastructure.case_closure_reader import (
    _record,
    case_source_identity,
    fingerprint,
    source_context_state,
)
from app.modules.pricing.infrastructure.models.cash_schedule import CashScheduleRevisionRecord
from app.modules.pricing.infrastructure.models.financial import (
    FinancialReportLineRecord,
    FinancialReportSnapshotRecord,
)
from app.modules.pricing.infrastructure.models.payment_cycle_fact import PaymentCycleFactRecord
from app.modules.pricing.infrastructure.models.payment_post_reception_cycle import (
    PaymentPostReceptionCycleRecord,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandHandler,
    HandlerOutcome,
    PendingDomainEvent,
)


def cash_view(session, tenant_id, case_id):
    case = session.scalar(
        sa.select(CaseRecord)
        .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
        .with_for_update(read=True)
    )
    if case is None:
        return None
    identity = case_source_identity(session, case)
    sources = []
    cycles = {
        r.id: r
        for r in session.scalars(
            sa.select(PaymentPostReceptionCycleRecord).where(
                PaymentPostReceptionCycleRecord.tenant_id == tenant_id,
                PaymentPostReceptionCycleRecord.case_id == case_id,
            )
        ).all()
    }
    facts = list(
        session.scalars(
            sa.select(PaymentCycleFactRecord)
            .where(
                PaymentCycleFactRecord.tenant_id == tenant_id,
                PaymentCycleFactRecord.case_id == case_id,
            )
            .order_by(PaymentCycleFactRecord.created_at.desc(), PaymentCycleFactRecord.id)
            .limit(201)
        ).all()
    )
    by_id = {r.id: r for r in facts[:200]}
    for f in facts[:200]:
        cycle = cycles.get(f.cycle_id)
        if f.kind == "INVOICE_DECLARED" or cycle is None:
            continue
        if source_context_state(
            f.source_snapshot_json.get("case_source"), identity
        ) == "REVIEW_REQUIRED" or f.source_snapshot_json.get("cycle") != _record(cycle):
            continue
        root, visited = f, {f.id}
        while root.compared_to_fact_id in by_id and root.compared_to_fact_id not in visited:
            root = by_id[root.compared_to_fact_id]
            visited.add(root.id)
        if root.compared_to_fact_id is not None:
            continue
        sources.append(
            dict(
                id=f"FACT:{f.id}",
                group=f"PAYMENT:{root.id}",
                direction="INFLOW",
                currency_code=f.currency_code,
                amount_minor=f.amount_minor,
                declared_date=f.declared_date.isoformat(),
                label=f"{f.kind} — {f.id}",
                sha256=fingerprint(_record(f)),
                source_refs=f.source_refs_json,
            )
        )
    report = session.scalar(
        sa.select(FinancialReportSnapshotRecord)
        .where(
            FinancialReportSnapshotRecord.tenant_id == tenant_id,
            FinancialReportSnapshotRecord.case_id == case_id,
            FinancialReportSnapshotRecord.state == "PUBLISHED",
        )
        .order_by(
            FinancialReportSnapshotRecord.published_at.desc(), FinancialReportSnapshotRecord.id
        )
        .limit(1)
    )
    lines = []
    if report:
        lines = list(
            session.scalars(
                sa.select(FinancialReportLineRecord)
                .where(
                    FinancialReportLineRecord.tenant_id == tenant_id,
                    FinancialReportLineRecord.snapshot_id == report.id,
                )
                .order_by(FinancialReportLineRecord.id)
                .limit(201)
            ).all()
        )
        for line in lines[:200]:
            if line.category not in {
                "SALES",
                "DIRECT_COST",
                "OVERHEAD",
                "SUBCONTRACTING",
                "CONTINGENCY",
            }:
                continue
            if not 0 <= line.amount_minor <= 9_000_000_000_000_000:
                continue
            sources.append(
                dict(
                    id=f"LINE:{line.id}",
                    group=f"LINE:{line.id}",
                    direction="INFLOW" if line.category == "SALES" else "OUTFLOW",
                    currency_code=report.currency_code,
                    amount_minor=line.amount_minor,
                    declared_date=None,
                    label=f"{line.category} — {line.label}",
                    sha256=fingerprint(dict(report=_record(report), line=_record(line))),
                    source_refs=[f"financial-report://{report.id}/line/{line.id}"],
                    financial_report=dict(
                        report_id=str(report.id),
                        revision=report.aggregate_revision,
                        state=report.state,
                    ),
                )
            )
    catalog = {s["id"]: s for s in sources}
    records = list(
        session.scalars(
            sa.select(CashScheduleRevisionRecord)
            .where(
                CashScheduleRevisionRecord.tenant_id == tenant_id,
                CashScheduleRevisionRecord.case_id == case_id,
            )
            .order_by(CashScheduleRevisionRecord.revision.desc())
            .limit(51)
        ).all()
    )
    history = []
    for row in records[:50]:
        state = source_context_state(row.source_snapshot_json.get("case_source"), identity)
        selected = row.source_snapshot_json.get("sources", {})
        if any(
            key not in catalog or catalog[key]["sha256"] != digest
            for key, digest in selected.items()
        ):
            state = "REVIEW_REQUIRED"
        projection = project_schedule(CashDeclaration(**row.declaration_json))
        if state == "REVIEW_REQUIRED":
            for group in projection["currencies"]:
                group["closing_minor"] = None
                for flow in group["rows"]:
                    flow["cumulative_minor"] = None
        history.append(
            dict(
                id=str(row.id),
                revision=row.revision,
                declaration=row.declaration_json,
                source_snapshot=row.source_snapshot_json,
                actor_id=str(row.actor_id),
                created_at=row.created_at.isoformat(),
                justification=row.justification,
                human_confirmed=row.human_confirmed,
                context_state=state,
                projection=projection,
            )
        )
    view = dict(
        case_id=str(case_id),
        case_source=identity,
        sources=sources,
        catalog_truncated=len(facts) > 200 or len(lines) > 200,
        current=history[0] if history else None,
        history=history,
        history_truncated=len(records) > 50,
        revision=records[0].revision if records else 0,
    )
    view["view_sha256"] = fingerprint(view)
    return view


class SqlAlchemyCashScheduleReader:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def read(self, *, tenant_id, case_id):
        with self._session_factory() as session:
            return cash_view(session, tenant_id, case_id)


class RecordCashScheduleHandler(CommandHandler):
    def execute(self, *, session, command, context):
        tenant = context.tenant_id
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("CASE_NOT_FOUND_OR_FORBIDDEN")
        view = cash_view(session, tenant, command.case_id)
        if (
            command.expected_revision != view["revision"]
            or command.expected_view_sha256 != view["view_sha256"]
        ):
            raise CommandExecutionError("CASH_VIEW_CONFLICT")
        catalog = {s["id"]: s for s in view["sources"]}
        selected, groups = {}, set()
        for flow in command.declaration.flows:
            if not flow.native_source_id:
                continue
            source = catalog.get(flow.native_source_id)
            if source is None:
                raise CommandExecutionError("CASH_SOURCE_NOT_FOUND_OR_FORBIDDEN")
            if source["group"] in groups:
                raise CommandExecutionError("CASH_NATIVE_SOURCE_DUPLICATED")
            if (
                source["currency_code"] != flow.currency_code
                or source["direction"] != flow.direction
                or source["amount_minor"] != flow.amount_minor
                or (
                    source["declared_date"] is not None
                    and source["declared_date"]
                    != (flow.declared_date.isoformat() if flow.declared_date else None)
                )
            ):
                raise CommandExecutionError("CASH_NATIVE_SOURCE_MISMATCH")
            groups.add(source["group"])
            selected[source["id"]] = source["sha256"]
        revision = view["revision"] + 1
        session.add(
            CashScheduleRevisionRecord(
                id=command.revision_id,
                tenant_id=tenant,
                case_id=command.case_id,
                revision=revision,
                declaration_json=command.declaration.model_dump(mode="json"),
                source_snapshot_json=dict(
                    case_source=view["case_source"],
                    sources=selected,
                    source_details={key: catalog[key] for key in selected},
                    observed_view_sha256=command.expected_view_sha256,
                ),
                justification=command.justification,
                human_confirmed=True,
                actor_id=UUID(str(context.actor_id)),
            )
        )
        return HandlerOutcome(
            result_code="CASH_SCHEDULE_RECORDED",
            aggregate_refs=(
                {
                    "aggregate_type": "CASH_SCHEDULE",
                    "aggregate_id": str(command.revision_id),
                    "aggregate_revision": revision,
                },
            ),
            events=(
                PendingDomainEvent(
                    aggregate_type="CASH_SCHEDULE",
                    aggregate_id=command.revision_id,
                    aggregate_revision=revision,
                    event_type="CASH_SCHEDULE_RECORDED",
                    payload={"case_id": str(command.case_id), "revision": revision},
                ),
            ),
        )
