"""Append-only human linkage of native cost facts to an imported position."""

from uuid import UUID

import sqlalchemy as sa

from app.modules.pricing.infrastructure.models.financial import PricingImportRowRecord as Row
from app.modules.pricing.infrastructure.models.position_review import (
    PricingPositionCostReferenceRecord as CostRef,
)
from app.modules.pricing.infrastructure.models.position_review import (
    PricingPositionReviewRecord as Review,
)
from app.modules.pricing.infrastructure.position_reader import (
    allocation_usage,
    base_snapshot,
    case_batch,
    cost_sources,
    digest,
    import_origin,
    offer_sources,
    requirement_sources,
    scope_sources,
    selected_snapshot,
)
from app.platform.events.dispatcher import CommandExecutionError, HandlerOutcome


class RecordPricingPositionReviewHandler:
    def execute(self, *, session, command, context):
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("FORBIDDEN")
        tenant = UUID(str(context.tenant_id))
        try:
            case, batch, revision = case_batch(
                session,
                tenant=tenant,
                case_id=command.case_id,
                batch_id=command.batch_id,
                lock=True,
            )
        except PermissionError as error:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN") from error
        row = session.scalar(
            sa.select(Row).where(
                Row.tenant_id == tenant, Row.batch_id == batch.id, Row.id == command.position_id
            )
        )
        if row is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        from app.modules.pricing.application.import_commands import PricingImportSourceLocator

        try:
            PricingImportSourceLocator.model_validate(row.source_locator_json)
        except ValueError as error:
            raise CommandExecutionError("POSITION_IMPORT_SOURCE_UNPROVEN") from error
        if row.error_codes_json:
            raise CommandExecutionError("POSITION_IMPORT_SOURCE_UNPROVEN")
        base = base_snapshot(
            case,
            batch,
            row,
            revision,
            import_origin(session, tenant=tenant, case=case, batch=batch),
        )
        if digest(base) != command.position_context_sha256:
            raise CommandExecutionError("POSITION_SOURCE_CONFLICT")
        exists = session.scalar(
            sa.select(Review.id).where(
                Review.tenant_id == tenant,
                Review.case_id == case.id,
                Review.id == command.record_id,
            )
        )
        if exists:
            raise CommandExecutionError("POSITION_REVISION_CONFLICT")
        previous = session.scalar(
            sa.select(Review)
            .where(
                Review.tenant_id == tenant, Review.case_id == case.id, Review.position_id == row.id
            )
            .order_by(Review.revision.desc())
            .limit(1)
        )
        current_revision = previous.revision if previous else 0
        if current_revision != command.expected_revision:
            raise CommandExecutionError("POSITION_REVISION_CONFLICT")
        if command.requirement_id:
            from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
            from app.modules.dce.infrastructure.models.dce_version import (
                DceDocumentRecord,
                DceVersionRecord,
            )

            native = session.scalar(
                sa.select(DceRequirementRecord)
                .where(
                    DceRequirementRecord.tenant_id == tenant,
                    DceRequirementRecord.id == command.requirement_id,
                )
                .with_for_update()
            )
            if native is None:
                raise CommandExecutionError("POSITION_SOURCE_CONFLICT")
            requirements, _ = requirement_sources(session, tenant=tenant, case=case)
            req = requirements.get(str(command.requirement_id))
            if req is None:
                raise CommandExecutionError("POSITION_SOURCE_CONFLICT")
            anchor = req["source_anchor"]
            session.scalar(
                sa.select(DceDocumentRecord)
                .where(
                    DceDocumentRecord.tenant_id == tenant,
                    DceDocumentRecord.id == UUID(anchor["dce_document_id"]),
                )
                .with_for_update()
            )
            session.scalar(
                sa.select(DceVersionRecord)
                .where(
                    DceVersionRecord.tenant_id == tenant,
                    DceVersionRecord.id == UUID(anchor["dce_version_id"]),
                )
                .with_for_update()
            )
        requirements, _ = requirement_sources(session, tenant=tenant, case=case)
        costs, _ = cost_sources(
            session,
            tenant=tenant,
            case_id=case.id,
            line_ids=[r.line_id for r in command.cost_refs],
            lock=True,
        )
        offers, _ = offer_sources(session, tenant=tenant, case_id=case.id)
        scopes, _ = scope_sources(session, tenant=tenant, case_id=case.id)
        try:
            snapshot = selected_snapshot(
                base, command, requirements=requirements, costs=costs, offers=offers, scopes=scopes
            )
        except ValueError as error:
            raise CommandExecutionError("POSITION_SOURCE_CONFLICT") from error
        for selected_cost in snapshot["costs"]:
            source_cost = costs[selected_cost["line_id"]]
            usage = allocation_usage(
                session, tenant=tenant, case_id=case.id, cost=source_cost, exclude_position=row.id
            )
            explicit = selected_cost.get("allocated_amount_minor")
            if (explicit is not None or usage["explicit_reference_count"]) and (
                usage["unresolved_reference_count"]
                or (usage["allocated_amount_minor"] or 0)
                + (explicit if explicit is not None else source_cost["amount_minor"])
                > source_cost["amount_minor"]
            ):
                raise CommandExecutionError("POSITION_ALLOCATION_REJECTED")
        record = Review(
            id=command.record_id,
            tenant_id=tenant,
            case_id=case.id,
            position_id=row.id,
            revision=current_revision + 1,
            previous_id=previous.id if previous else None,
            requirement_id=command.requirement_id,
            offer_price_id=command.offer_price_id,
            scope_review_id=command.scope_review_id,
            base_sha256=digest(base),
            basis_sha256=digest(snapshot),
            source_snapshot_json=snapshot,
            justification=command.justification,
            actor_id=context.actor_id,
            membership_id=context.membership_id,
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
        )
        session.add(record)
        session.flush()
        session.add_all(
            CostRef(
                tenant_id=tenant,
                case_id=case.id,
                review_id=record.id,
                line_id=UUID(c["line_id"]),
                report_id=UUID(c["report_id"]),
                report_revision=c["report_revision"],
            )
            for c in snapshot["costs"]
        )
        return HandlerOutcome(
            result_code="PRICING_POSITION_REVIEW_RECORDED",
            events=(),
            aggregate_refs=(
                {
                    "aggregate_type": "PricingPositionReview",
                    "aggregate_id": str(record.id),
                    "aggregate_revision": record.revision,
                },
            ),
        )
