"""Append a human review only against the exact current dossier snapshot."""

import json
from uuid import UUID

import sqlalchemy as sa

from app.modules.case.infrastructure.analysis_dossier_reader import read_analysis_dossier
from app.modules.case.infrastructure.models.analysis_dossier import (
    AnalysisDossierReviewRecord as Review,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.decision.infrastructure.models.risk import DecisionRiskRecord
from app.modules.pricing.infrastructure.models import (
    FinancialReportSnapshotRecord,
    PricingScenarioRecord,
)
from app.platform.events.dispatcher import CommandExecutionError, HandlerOutcome


class RecordAnalysisDossierHandler:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def execute(self, *, session, command, context):
        if context.actor_kind != "PATRON_ADMIN" or context.membership_id is None:
            raise CommandExecutionError("PATRON_REQUIRED")
        tenant = UUID(str(context.tenant_id))
        case = session.scalar(
            sa.select(CaseRecord)
            .where(CaseRecord.tenant_id == tenant, CaseRecord.id == command.case_id)
            .with_for_update()
        )
        if case is None:
            raise CommandExecutionError("NOT_FOUND_OR_FORBIDDEN")
        # Use the same mutexes as source/treatment writers before the final read.
        for model, identity, conditions in [
            (DecisionRiskRecord, DecisionRiskRecord.id, [DecisionRiskRecord.case_id == case.id]),
            (
                DceRequirementRecord,
                DceRequirementRecord.id,
                [DceRequirementRecord.dce_version_id == case.applicable_dce_version_id],
            ),
            (
                DceDocumentRecord,
                DceDocumentRecord.id,
                [DceDocumentRecord.dce_version_id == case.applicable_dce_version_id],
            ),
            (
                DceVersionRecord,
                DceVersionRecord.id,
                [DceVersionRecord.id == case.applicable_dce_version_id],
            ),
            (
                FinancialReportSnapshotRecord,
                FinancialReportSnapshotRecord.id,
                [FinancialReportSnapshotRecord.case_id == case.id],
            ),
            (
                PricingScenarioRecord,
                PricingScenarioRecord.id,
                [PricingScenarioRecord.case_id == case.id],
            ),
        ]:
            try:
                session.scalars(
                    sa.select(model)
                    .where(model.tenant_id == tenant, *conditions)
                    .order_by(identity)
                    .with_for_update(nowait=True)
                ).all()
            except sa.exc.OperationalError as error:
                if getattr(error.orig, "sqlstate", None) == "55P03":
                    raise CommandExecutionError("STALE_SOURCE_CONTEXT") from error
                raise
        try:
            summary = read_analysis_dossier(
                session, session_factory=self.session_factory, tenant_id=tenant, case_id=case.id
            )
        except ValueError as error:
            raise CommandExecutionError("STALE_SOURCE_CONTEXT") from error
        if (
            not summary
            or summary["source_context_state"] != "CURRENT"
            or summary["dossier_sha256"] != command.dossier_sha256
        ):
            raise CommandExecutionError("STALE_SOURCE_CONTEXT")
        previous = session.scalar(
            sa.select(Review)
            .where(Review.tenant_id == tenant, Review.case_id == case.id)
            .order_by(Review.revision.desc())
            .limit(1)
        )
        revision = previous.revision if previous else 0
        if revision != command.expected_revision:
            raise CommandExecutionError("STALE_DOSSIER_REVISION")
        axes = [a.model_dump(mode="json") for a in command.axes]
        if command.phase == "REVIEWED":
            if (
                not previous
                or previous.phase != "PREPARED"
                or previous.dossier_sha256 != command.dossier_sha256
                or previous.axes_json != axes
            ):
                raise CommandExecutionError("PREPARATION_REQUIRED")
            if summary["truncated"]:
                raise CommandExecutionError("TRUNCATED_DOSSIER")
            for axis in summary["axes"]:
                for item in axis["items"]:
                    assessment = item.get("human_assessment")
                    if (
                        item["source_state"] != "CURRENT_SOURCE"
                        or not assessment
                        or assessment["state"] != "CURRENT"
                        or not assessment.get("treatment")
                    ):
                        raise CommandExecutionError("UNPREPARED_POINTS")
            for axis in command.axes:
                if (
                    axis.state == "POINTS_REVIEWED"
                    and not next(a for a in summary["axes"] if a["code"] == axis.code)["items"]
                ):
                    raise CommandExecutionError("AXIS_WITHOUT_PROVEN_POINTS")
        row = Review(
            id=command.review_id,
            tenant_id=tenant,
            case_id=case.id,
            dce_version_id=case.applicable_dce_version_id,
            revision=revision + 1,
            previous_id=previous.id if previous else None,
            dossier_sha256=command.dossier_sha256,
            phase=command.phase,
            axes_json=axes,
            snapshot_json=json.loads(
                json.dumps(
                    {
                        k: v
                        for k, v in summary.items()
                        if k not in {"dossier_sha256", "dossier_review"}
                    },
                    default=str,
                )
            ),
            justification=command.justification,
            actor_id=UUID(str(context.actor_id)),
            membership_id=UUID(str(context.membership_id)),
            command_id=command.command_id,
            idempotency_key=command.idempotency_key,
        )
        session.add(row)
        session.flush()
        return HandlerOutcome(
            result_code="ANALYSIS_DOSSIER_RECORDED",
            aggregate_refs=(
                dict(
                    aggregate_type="CASE_ANALYSIS_DOSSIER",
                    aggregate_id=str(row.id),
                    aggregate_revision=row.revision,
                ),
            ),
            events=(),
        )
