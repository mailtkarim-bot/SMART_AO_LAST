"""Current, tenant-scoped source facts for human pricing-position reviews."""

from __future__ import annotations

import hashlib
import json
from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.analysis_summary_reader import (
    SqlAlchemyCaseAnalysisSummaryReader,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.partner.infrastructure.models.partner_event import (
    CasePartnerEventRecord as Receipt,
)
from app.modules.pricing.domain.position_costing import project_position_costing
from app.modules.pricing.infrastructure.models.financial import (
    FinancialReportLineRecord as Line,
)
from app.modules.pricing.infrastructure.models.financial import (
    FinancialReportSnapshotRecord as Report,
)
from app.modules.pricing.infrastructure.models.financial import (
    PricingImportBatchRecord as Batch,
)
from app.modules.pricing.infrastructure.models.financial import (
    PricingImportRowRecord as Row,
)
from app.modules.pricing.infrastructure.models.financial import (
    PricingImportTransitionRecord as Transition,
)
from app.modules.pricing.infrastructure.models.partner_offer_price import (
    PartnerOfferPriceDeclarationRecord as Price,
)
from app.modules.pricing.infrastructure.models.partner_offer_scope_review import (
    PartnerOfferScopeReviewOfferRecord as ScopeOffer,
)
from app.modules.pricing.infrastructure.models.partner_offer_scope_review import (
    PartnerOfferScopeReviewRecord as Scope,
)
from app.modules.pricing.infrastructure.models.position_review import (
    PricingPositionCostReferenceRecord as CostRef,
)
from app.modules.pricing.infrastructure.models.position_review import (
    PricingPositionReviewRecord as Review,
)

COST_CATEGORIES = ("DIRECT_COST", "OVERHEAD", "SUBCONTRACTING", "CONTINGENCY")
PAGE_SIZE = 50
SOURCE_LIMIT = 1000


def canonical(value):
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str))


def digest(value):
    return hashlib.sha256(
        json.dumps(canonical(value), sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def public_snapshot(value):
    result = canonical(value)
    result.get("import", {}).pop("source_sha256", None)
    result.pop("tenant_id", None)
    result.pop("case_scope_fingerprint", None)
    return result


def case_batch(session, *, tenant, case_id, batch_id, lock=False):
    query = sa.select(CaseRecord).where(CaseRecord.tenant_id == tenant, CaseRecord.id == case_id)
    case = session.scalar(query.with_for_update() if lock else query)
    batch_query = sa.select(Batch).where(
        Batch.tenant_id == tenant, Batch.case_id == case_id, Batch.id == batch_id
    )
    batch = session.scalar(batch_query.with_for_update() if lock else batch_query)
    if case is None or batch is None:
        raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
    revision = (
        session.scalar(
            sa.select(sa.func.max(Transition.version)).where(
                Transition.tenant_id == tenant, Transition.batch_id == batch_id
            )
        )
        or batch.aggregate_revision
    )
    return case, batch, revision


def import_origin(session, *, tenant, case, batch):
    from app.modules.dce.infrastructure.models.dce_version import (
        DceDocumentRecord as Document,
    )
    from app.modules.dce.infrastructure.models.dce_version import (
        DceVersionRecord as Version,
    )

    unknown = dict(
        state="UNKNOWN",
        document_id=None,
        dce_version_id=case.applicable_dce_version_id,
        filename=None,
        reason="NO_EXACT_CURRENT_DCE_MATCH",
    )
    if case.applicable_dce_version_id is None or case.dce_freshness != "CURRENT":
        return unknown
    rows = session.execute(
        sa.select(Document, Version)
        .join(
            Version,
            sa.and_(Version.tenant_id == Document.tenant_id, Version.id == Document.dce_version_id),
        )
        .where(
            Document.tenant_id == tenant,
            Document.dce_version_id == case.applicable_dce_version_id,
            Document.sha256 == batch.source_sha256,
            Version.lifecycle == "ADMITTED",
            Version.integrity == "VERIFIED",
        )
        .limit(2)
    ).all()
    if len(rows) != 1:
        return unknown
    doc, version = rows[0]
    return canonical(
        dict(
            state="MATCHED_BY_HASH",
            document_id=doc.id,
            dce_version_id=version.id,
            filename=doc.original_filename,
            reason=None,
        )
    )


def base_snapshot(case, batch, row, revision, origin):
    return canonical(
        dict(
            tenant_id=case.tenant_id,
            case_id=case.id,
            dce_version_id=case.applicable_dce_version_id,
            case_scope_fingerprint=case.scope_fingerprint,
            dce_freshness=case.dce_freshness,
            case_lifecycle=case.lifecycle,
            import_origin=origin,
            case_scope_kind=case.scope_kind,
            case_scope=case.scope_json,
            **{
                "import": dict(
                    position_id=row.id,
                    batch_id=batch.id,
                    batch_revision=revision,
                    row_number=row.row_number,
                    source_sha256=batch.source_sha256,
                    source_locator=row.source_locator_json,
                    designation=row.designation,
                    quantity_decimal=row.quantity_decimal,
                    unit=row.unit,
                    total_minor=row.total_minor,
                    errors=row.error_codes_json,
                )
            },
        )
    )


def requirement_sources(session, *, tenant, case):
    if case.applicable_dce_version_id is None:
        return {}, False
    summary = SqlAlchemyCaseAnalysisSummaryReader(session).get(tenant_id=tenant, case_id=case.id)
    if summary is None:
        return {}, False
    result = {}
    for axis in summary["axes"]:
        for p in axis["items"]:
            if (
                p["kind"] == "REQUIREMENT"
                and p["native_state"] == "CONFIRMED"
                and p["source_state"] == "CURRENT_SOURCE"
            ):
                result[str(p["item_id"])] = canonical(
                    dict(
                        requirement_id=p["item_id"],
                        revision=p["native_revision"],
                        native_type=p["native_type"],
                        source_context_sha256=p["source_context_sha256"],
                        source_anchor=p["source_anchor"],
                        excerpt=p["source_excerpt"],
                        start_byte_offset=p["start_byte_offset"],
                        end_byte_offset=p["end_byte_offset"],
                        applicability="UNKNOWN",
                    )
                )
    return result, summary["truncated"]


def cost_sources(session, *, tenant, case_id, line_ids=None, search="", lock=False):
    q = (
        sa.select(Line, Report)
        .join(Report, sa.and_(Report.tenant_id == Line.tenant_id, Report.id == Line.snapshot_id))
        .where(
            Line.tenant_id == tenant,
            Report.case_id == case_id,
            Line.category.in_(COST_CATEGORIES),
            Report.state.in_(("DRAFT", "PUBLISHED")),
        )
    )
    if line_ids is not None:
        q = q.where(Line.id.in_(line_ids))
    if search:
        q = q.where(Line.label.ilike(f"%{search}%"))
    q = q.order_by(Report.id, Line.id)
    if lock:
        q = q.with_for_update(of=Report)
    if line_ids is None:
        q = q.limit(SOURCE_LIMIT + 1)
    rows = session.execute(q).all()
    result = {
        str(line.id): canonical(
            dict(
                line_id=line.id,
                report_id=report.id,
                report_revision=report.aggregate_revision,
                report_state=report.state,
                category=line.category,
                label=line.label,
                quantity_decimal=line.quantity_decimal,
                unit=line.unit,
                amount_minor=line.amount_minor,
                currency_code=report.currency_code,
            )
        )
        for line, report in rows
    }
    return result, len(rows) > SOURCE_LIMIT


def offer_sources(session, *, tenant, case_id):
    latest_receipts = (
        sa.select(Receipt.partner_id, sa.func.max(Receipt.revision).label("revision"))
        .where(
            Receipt.tenant_id == tenant,
            Receipt.case_id == case_id,
            Receipt.event_type == "RECEIVED",
        )
        .group_by(Receipt.partner_id)
        .subquery()
    )
    latest_prices = (
        sa.select(Price.receipt_event_id, sa.func.max(Price.revision).label("revision"))
        .where(Price.tenant_id == tenant, Price.case_id == case_id)
        .group_by(Price.receipt_event_id)
        .subquery()
    )
    rows = session.execute(
        sa.select(Price, Receipt)
        .join(
            Receipt,
            sa.and_(
                Receipt.tenant_id == Price.tenant_id,
                Receipt.case_id == Price.case_id,
                Receipt.event_id == Price.receipt_event_id,
            ),
        )
        .join(
            latest_receipts,
            sa.and_(
                latest_receipts.c.partner_id == Receipt.partner_id,
                latest_receipts.c.revision == Receipt.revision,
            ),
        )
        .join(
            latest_prices,
            sa.and_(
                latest_prices.c.receipt_event_id == Price.receipt_event_id,
                latest_prices.c.revision == Price.revision,
            ),
        )
        .where(
            Price.tenant_id == tenant, Price.case_id == case_id, Receipt.event_type == "RECEIVED"
        )
        .order_by(Price.id)
        .limit(SOURCE_LIMIT + 1)
    ).all()
    result = {
        str(p.id): canonical(
            dict(
                price_id=p.id,
                revision=p.revision,
                receipt_event_id=r.event_id,
                receipt_revision=r.revision,
                partner_id=r.partner_id,
                partner_label=r.partner_label,
                source_locator=r.source_locator,
                amount_as_declared=p.amount_as_declared,
                currency_code=p.currency_code,
                valid_until=r.valid_until,
                exclusions_state=r.exclusions_state,
                exclusions=r.exclusions_json,
            )
        )
        for p, r in rows
    }
    return result, len(rows) > SOURCE_LIMIT


def scope_sources(session, *, tenant, case_id):
    latest = (
        sa.select(Scope.comparison_id, sa.func.max(Scope.revision).label("revision"))
        .where(Scope.tenant_id == tenant, Scope.case_id == case_id)
        .group_by(Scope.comparison_id)
        .subquery()
    )
    rows = session.execute(
        sa.select(Scope, ScopeOffer)
        .join(
            ScopeOffer,
            sa.and_(
                ScopeOffer.tenant_id == Scope.tenant_id,
                ScopeOffer.case_id == Scope.case_id,
                ScopeOffer.review_id == Scope.id,
            ),
        )
        .join(
            latest,
            sa.and_(
                latest.c.comparison_id == Scope.comparison_id, latest.c.revision == Scope.revision
            ),
        )
        .where(Scope.tenant_id == tenant, Scope.case_id == case_id)
        .order_by(Scope.id, ScopeOffer.receipt_event_id)
        .limit(SOURCE_LIMIT + 1)
    ).all()
    result = {
        (str(r.id), str(o.receipt_event_id)): canonical(
            dict(
                review_id=r.id,
                revision=r.revision,
                comparison_id=r.comparison_id,
                decision=r.decision,
                receipt_event_id=o.receipt_event_id,
                transport_state=o.transport_state,
                transport_note=o.transport_note,
                exclusions_review_state=o.exclusions_review_state,
            )
        )
        for r, o in rows
    }
    return result, len(rows) > SOURCE_LIMIT


def selected_snapshot(base, refs, *, requirements, costs, offers, scopes):
    requirement = requirements.get(str(refs.requirement_id)) if refs.requirement_id else None
    if refs.requirement_id and (
        requirement is None or requirement["revision"] != refs.requirement_revision
    ):
        raise ValueError("POSITION_SOURCE_CONFLICT")
    selected = []
    for ref in refs.cost_refs:
        cost = costs.get(str(ref.line_id))
        if cost is None or cost["report_revision"] != ref.report_revision:
            raise ValueError("POSITION_SOURCE_CONFLICT")
        if ref.allocated_amount_minor is not None:
            amount = int(ref.allocated_amount_minor)
            if amount > cost["amount_minor"] or amount > 2**63 - 1:
                raise ValueError("POSITION_ALLOCATION_OUT_OF_RANGE")
            cost = dict(cost, allocated_amount_minor=amount)
        selected.append(cost)
    offer = offers.get(str(refs.offer_price_id)) if refs.offer_price_id else None
    if refs.offer_price_id and (offer is None or offer["revision"] != refs.offer_price_revision):
        raise ValueError("POSITION_SOURCE_CONFLICT")
    scope = (
        scopes.get((str(refs.scope_review_id), offer["receipt_event_id"]))
        if refs.scope_review_id and offer
        else None
    )
    if refs.scope_review_id and scope is None:
        raise ValueError("POSITION_SOURCE_CONFLICT")
    return canonical(
        dict(
            base,
            requirement=requirement,
            costs=selected,
            cost_ids=[c["line_id"] for c in selected],
            offer=offer,
            scope=scope,
        )
    )


def refs_from_record(record):
    from types import SimpleNamespace

    from app.modules.pricing.application.position_commands import PositionCostReference

    s = record.source_snapshot_json
    return SimpleNamespace(
        requirement_id=record.requirement_id,
        requirement_revision=(s.get("requirement") or {}).get("revision"),
        cost_refs=[
            PositionCostReference(
                line_id=c["line_id"],
                report_revision=c["report_revision"],
                allocated_amount_minor=str(c["allocated_amount_minor"])
                if "allocated_amount_minor" in c
                else None,
            )
            for c in s["costs"]
        ],
        offer_price_id=record.offer_price_id,
        offer_price_revision=(s.get("offer") or {}).get("revision"),
        scope_review_id=record.scope_review_id,
    )


def read_positions(session, *, tenant, case_id, batch_id, offset, search, today):
    case, batch, revision = case_batch(session, tenant=tenant, case_id=case_id, batch_id=batch_id)
    rows = list(
        session.scalars(
            sa.select(Row)
            .where(Row.tenant_id == tenant, Row.batch_id == batch_id)
            .order_by(Row.row_number)
            .offset(offset)
            .limit(PAGE_SIZE + 1)
        )
    )
    requirements, req_limited = requirement_sources(session, tenant=tenant, case=case)
    costs, cost_limited = cost_sources(session, tenant=tenant, case_id=case_id, search=search)
    offers, offer_limited = offer_sources(session, tenant=tenant, case_id=case_id)
    scopes, scope_limited = scope_sources(session, tenant=tenant, case_id=case_id)
    latest = (
        sa.select(Review.position_id, sa.func.max(Review.revision).label("revision"))
        .where(Review.tenant_id == tenant, Review.case_id == case_id)
        .group_by(Review.position_id)
        .subquery()
    )
    records = {
        a.position_id: a
        for a in session.scalars(
            sa.select(Review)
            .join(
                latest,
                sa.and_(
                    latest.c.position_id == Review.position_id, latest.c.revision == Review.revision
                ),
            )
            .where(
                Review.tenant_id == tenant,
                Review.case_id == case_id,
                Review.position_id.in_([r.id for r in rows[:PAGE_SIZE]]),
            )
        )
    }
    used = session.execute(
        sa.select(CostRef.line_id, sa.func.count(sa.distinct(Review.position_id)))
        .join(
            Review,
            sa.and_(
                Review.tenant_id == CostRef.tenant_id,
                Review.case_id == CostRef.case_id,
                Review.id == CostRef.review_id,
            ),
        )
        .join(
            latest,
            sa.and_(
                latest.c.position_id == Review.position_id, latest.c.revision == Review.revision
            ),
        )
        .where(CostRef.tenant_id == tenant, CostRef.case_id == case_id)
        .group_by(CostRef.line_id)
    ).all()
    reused = {str(identity) for identity, count in used if count > 1}
    selected_cost_ids = {
        UUID(c["line_id"])
        for a in records.values()
        for c in a.source_snapshot_json.get("costs", [])
    }
    exact_costs, _ = (
        cost_sources(session, tenant=tenant, case_id=case_id, line_ids=selected_cost_ids)
        if selected_cost_ids
        else ({}, False)
    )
    origin = import_origin(session, tenant=tenant, case=case, batch=batch)
    positions = []
    for row in rows[:PAGE_SIZE]:
        base = base_snapshot(case, batch, row, revision, origin)
        source_proven = bool(row.source_locator_json) and not row.error_codes_json
        record = records.get(row.id)
        current = source_proven
        snapshot = dict(base, requirement=None, costs=[], offer=None, scope=None)
        if record:
            snapshot = record.source_snapshot_json
            try:
                refreshed = selected_snapshot(
                    base,
                    refs_from_record(record),
                    requirements=requirements,
                    costs=exact_costs,
                    offers=offers,
                    scopes=scopes,
                )
                linked = set(
                    session.scalars(
                        sa.select(CostRef.line_id).where(
                            CostRef.tenant_id == tenant,
                            CostRef.case_id == case_id,
                            CostRef.review_id == record.id,
                        )
                    )
                )
                current = (
                    current
                    and digest(snapshot) == record.basis_sha256 == digest(refreshed)
                    and linked == {UUID(c["line_id"]) for c in snapshot["costs"]}
                )
            except (ValueError, KeyError, TypeError):
                current = False
        projected = project_position_costing(
            public_snapshot(snapshot), current=current, reused_cost_ids=reused, today=today
        )
        positions.append(
            dict(
                projected,
                position_id=row.id,
                source_state="CURRENT_SOURCE" if source_proven else "UNKNOWN",
                position_context_sha256=digest(base),
                import_source=public_snapshot(base)["import"],
                import_origin=origin,
                review_id=record.id if record else None,
                revision=record.revision if record else 0,
                actor_id=record.actor_id if record and current else None,
                created_at=record.created_at if record else None,
                justification=record.justification if record and current else None,
                applicability="UNKNOWN",
            )
        )
    allocation_reviews = allocation_records(session, tenant=tenant, case_id=case_id)
    allocation_context: dict[UUID, tuple[bool, set[str]]] = {}
    return dict(
        case_id=case_id,
        batch_id=batch_id,
        dce_version_id=case.applicable_dce_version_id,
        coverage_state="UNKNOWN",
        positions=positions,
        next_offset=offset + PAGE_SIZE if len(rows) > PAGE_SIZE else None,
        offset=offset,
        sources=dict(
            requirements=list(requirements.values()),
            costs=[
                dict(
                    c,
                    allocation_summary=allocation_usage(
                        session,
                        tenant=tenant,
                        case_id=case_id,
                        cost=c,
                        records=allocation_reviews,
                        context_cache=allocation_context,
                    ),
                )
                for c in list(costs.values())[:SOURCE_LIMIT]
            ],
            offers=list(offers.values())[:SOURCE_LIMIT],
            scopes=list(scopes.values())[:SOURCE_LIMIT],
        ),
        sources_limited=dict(
            requirements=req_limited, costs=cost_limited, offers=offer_limited, scopes=scope_limited
        ),
    )


def allocation_records(session, *, tenant, case_id):
    latest = (
        sa.select(Review.position_id, sa.func.max(Review.revision).label("revision"))
        .where(Review.tenant_id == tenant, Review.case_id == case_id)
        .group_by(Review.position_id)
        .subquery()
    )
    return list(
        session.scalars(
            sa.select(Review)
            .join(
                latest,
                sa.and_(
                    latest.c.position_id == Review.position_id, latest.c.revision == Review.revision
                ),
            )
            .where(Review.tenant_id == tenant, Review.case_id == case_id)
        )
    )


def allocation_usage(
    session, *, tenant, case_id, cost, exclude_position=None, records=None, context_cache=None
):
    """A stale declaration is unresolved, never silently reused or released."""
    if records is None:
        records = allocation_records(session, tenant=tenant, case_id=case_id)
    if context_cache is None:
        context_cache = {}
    total, explicit, unresolved = 0, 0, 0
    for record in records:
        if record.position_id == exclude_position:
            continue
        if record.id not in context_cache:
            saved = record.source_snapshot_json
            linked = {
                str(x)
                for x in session.scalars(
                    sa.select(CostRef.line_id).where(
                        CostRef.tenant_id == tenant,
                        CostRef.case_id == case_id,
                        CostRef.review_id == record.id,
                    )
                )
            }
            valid = digest(saved) == record.basis_sha256 and linked == {
                c.get("line_id") for c in saved.get("costs", [])
            }
            try:
                case, batch, revision = case_batch(
                    session,
                    tenant=tenant,
                    case_id=case_id,
                    batch_id=UUID(saved["import"]["batch_id"]),
                )
                row = session.scalar(
                    sa.select(Row).where(
                        Row.tenant_id == tenant,
                        Row.batch_id == batch.id,
                        Row.id == record.position_id,
                    )
                )
                valid = (
                    valid
                    and row is not None
                    and record.base_sha256
                    == digest(
                        base_snapshot(
                            case,
                            batch,
                            row,
                            revision,
                            import_origin(session, tenant=tenant, case=case, batch=batch),
                        )
                    )
                )
            except (KeyError, ValueError, TypeError, PermissionError):
                valid = False
            context_cache[record.id] = (valid, linked)
        valid, linked = context_cache[record.id]
        matching = [
            c
            for c in record.source_snapshot_json.get("costs", [])
            if c.get("line_id") == cost["line_id"]
        ]
        if not valid and (matching or cost["line_id"] in linked):
            unresolved += 1
            continue
        for saved in matching:
            if saved.get("report_revision") != cost["report_revision"]:
                continue
            source = {k: v for k, v in saved.items() if k != "allocated_amount_minor"}
            if source != cost or "allocated_amount_minor" not in saved:
                unresolved += 1
            else:
                total += int(saved["allocated_amount_minor"])
                explicit += 1
    valid_total = explicit > 0 and not unresolved and 0 <= total <= cost["amount_minor"]
    return dict(
        allocated_amount_minor=total if valid_total else None,
        remaining_amount_minor=cost["amount_minor"] - total if valid_total else None,
        state="DECLARED" if valid_total else "UNKNOWN",
        explicit_reference_count=explicit,
        unresolved_reference_count=unresolved,
    )
