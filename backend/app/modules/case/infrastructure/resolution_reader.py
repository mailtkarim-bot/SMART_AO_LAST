"""SQLAlchemy adapter for the minimal Case « À résoudre » projection."""

from __future__ import annotations

from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.modules.case.application.queries import (
    CaseEconomicCoverageProjection,
    CaseEconomicCoverageStatusProjection,
    CaseResolutionIndexProjection,
    CaseResolutionItemProjection,
    CaseResolutionReader,
    CaseResolutionUnknownReader,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.application.queries import DceContractRiskSignalReader
from app.modules.dce.infrastructure.case_dce_reading_reader import (
    SqlAlchemyCaseDceReadingReader,
)
from app.modules.decision.application.queries import DecisionDocumentContradictionReader
from app.modules.enterprise.infrastructure.models import CaseCapabilityGapRecord
from app.modules.membership.infrastructure.records import (
    CaseAssignmentRecord,
    CollaboratorInformationRequestRecord,
    CollaboratorTaskBlockerRecord,
    CollaboratorTaskRecord,
)
from app.modules.optimization.infrastructure.models import OptimizationRunRecord
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    FinancialReportSnapshotRecord,
    PricingScenarioRecord,
)


class SqlAlchemyCaseResolutionReader(CaseResolutionReader):
    """Build a safe partial index without introducing a universal blocker table."""

    def __init__(
        self,
        session: Session,
        *,
        contract_risk_reader: DceContractRiskSignalReader | None = None,
        contradiction_reader: DecisionDocumentContradictionReader | None = None,
        unknown_reader: CaseResolutionUnknownReader | None = None,
    ) -> None:
        self._session = session
        self._contract_risk_reader = contract_risk_reader
        self._contradiction_reader = contradiction_reader
        self._unknown_reader = unknown_reader

    def get(
        self,
        *,
        tenant_id: UUID,
        case_id: UUID,
        membership_id: UUID | None,
    ) -> CaseResolutionIndexProjection | None:
        case = self._session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
            )
        )
        if case is None:
            return None

        items: list[CaseResolutionItemProjection] = []
        dce_lookup = SqlAlchemyCaseDceReadingReader(self._session).get(
            tenant_id=tenant_id,
            case_id=case_id,
        )
        if dce_lookup is not None and dce_lookup.reading is not None:
            reading = dce_lookup.reading
            for requirement in reading.requirements:
                if requirement.confirmation_outcome not in {
                    "PENDING_HUMAN_CONFIRMATION",
                    "REVIEW_REQUIRED",
                }:
                    continue
                next_action = (
                    "CONFIRM_REQUIREMENT"
                    if requirement.confirmation_outcome == "PENDING_HUMAN_CONFIRMATION"
                    else "REVIEW_REQUIREMENT"
                )
                items.append(
                    CaseResolutionItemProjection(
                        item_id=requirement.requirement_id,
                        item_kind="REQUIREMENT",
                        native_state=requirement.confirmation_outcome,
                        source_refs=(
                            f"dce-version:{reading.dce_version_id}",
                            f"requirement:{requirement.requirement_id}",
                            requirement.source_locator_label,
                        ),
                        resolution_owner=None,
                        next_action=next_action,
                        due_at=None,
                    )
                )

        assignment_filter = []
        if membership_id is not None:
            assignment_filter.extend(
                [
                    CaseAssignmentRecord.membership_id == membership_id,
                    CaseAssignmentRecord.state == "ACTIVE",
                ]
            )
        task_join = sa.and_(
            CollaboratorTaskRecord.tenant_id == CaseAssignmentRecord.tenant_id,
            CollaboratorTaskRecord.assignment_id == CaseAssignmentRecord.id,
            CollaboratorTaskRecord.case_id == case_id,
            CollaboratorTaskRecord.tenant_id == tenant_id,
            *assignment_filter,
        )
        requests = self._session.scalars(
            sa.select(CollaboratorInformationRequestRecord)
            .join(
                CollaboratorTaskRecord,
                sa.and_(
                    CollaboratorInformationRequestRecord.tenant_id
                    == CollaboratorTaskRecord.tenant_id,
                    CollaboratorInformationRequestRecord.task_id == CollaboratorTaskRecord.id,
                ),
            )
            .join(CaseAssignmentRecord, task_join)
            .where(
                CollaboratorInformationRequestRecord.tenant_id == tenant_id,
                CollaboratorInformationRequestRecord.state == "OPEN",
            )
            .order_by(
                CollaboratorInformationRequestRecord.created_at,
                CollaboratorInformationRequestRecord.id,
            )
        ).all()
        items.extend(
            CaseResolutionItemProjection(
                item_id=request.id,
                item_kind="INFORMATION_REQUEST",
                native_state=request.state,
                source_refs=(
                    f"task:{request.task_id}",
                    f"information-request:{request.id}",
                ),
                resolution_owner=None,
                next_action="RESPOND_INFORMATION_REQUEST",
                due_at=request.due_at,
            )
            for request in requests
        )

        blocker_rows = self._session.execute(
            sa.select(CollaboratorTaskBlockerRecord, CollaboratorTaskRecord.due_at)
            .join(
                CollaboratorTaskRecord,
                sa.and_(
                    CollaboratorTaskBlockerRecord.tenant_id == CollaboratorTaskRecord.tenant_id,
                    CollaboratorTaskBlockerRecord.task_id == CollaboratorTaskRecord.id,
                ),
            )
            .join(CaseAssignmentRecord, task_join)
            .where(
                CollaboratorTaskBlockerRecord.tenant_id == tenant_id,
                CollaboratorTaskBlockerRecord.state == "OPEN",
            )
            .order_by(CollaboratorTaskBlockerRecord.created_at, CollaboratorTaskBlockerRecord.id)
        ).all()
        items.extend(
            CaseResolutionItemProjection(
                item_id=blocker.id,
                item_kind="TASK_BLOCKER",
                native_state=blocker.state,
                source_refs=tuple(
                    ref
                    for ref in (
                        f"task:{blocker.task_id}",
                        f"task-blocker:{blocker.id}",
                        blocker.source_locator,
                    )
                    if ref
                ),
                resolution_owner=blocker.resolution_owner,
                next_action="RESOLVE_TASK_BLOCKER",
                due_at=task_due_at,
            )
            for blocker, task_due_at in blocker_rows
        )
        if membership_id is None:
            if self._contract_risk_reader is not None:
                items.extend(
                    CaseResolutionItemProjection(
                        item_id=signal.observation_id,
                        item_kind="RISK",
                        native_state=signal.verification_status,
                        source_refs=(
                            f"dce-version:{signal.dce_version_id}",
                            f"observation:{signal.observation_id}",
                            f"fragment:{signal.fragment_id}",
                            signal.source_locator_label,
                        ),
                        resolution_owner=None,
                        next_action="REVIEW_RISK",
                        due_at=None,
                    )
                    for signal in self._contract_risk_reader.list_for_case(
                        tenant_id=tenant_id,
                        case_id=case_id,
                        limit=100,
                    )
                )
            if self._contradiction_reader is not None:
                items.extend(
                    CaseResolutionItemProjection(
                        item_id=contradiction.contradiction_id,
                        item_kind="CONTRADICTION",
                        native_state=contradiction.verification_status,
                        source_refs=(
                            f"dce-version:{contradiction.dce_version_id}",
                            f"contradiction:{contradiction.contradiction_id}",
                            f"fragment:{contradiction.source_fragment_id}",
                            f"pricing-batch:{contradiction.related_batch_id}",
                            contradiction.source_locator_label,
                        ),
                        resolution_owner=None,
                        next_action="REVIEW_CONTRADICTION",
                        due_at=None,
                    )
                    for contradiction in self._contradiction_reader.detect(
                        tenant_id=tenant_id,
                        case_id=case_id,
                        limit=100,
                    )
                )
            if self._unknown_reader is not None:
                items.extend(
                    CaseResolutionItemProjection(
                        item_id=unknown.unknown_id,
                        item_kind="UNKNOWN",
                        native_state=unknown.native_state,
                        source_refs=unknown.source_refs,
                        resolution_owner=None,
                        next_action=unknown.next_action,
                        due_at=unknown.due_at,
                        impact=unknown.impact,
                    )
                    for unknown in self._unknown_reader.list_for_case(
                        tenant_id=tenant_id,
                        case_id=case_id,
                        limit=100,
                    )
                )
            capability_gaps = self._session.scalars(
                sa.select(CaseCapabilityGapRecord)
                .where(
                    CaseCapabilityGapRecord.tenant_id == tenant_id,
                    CaseCapabilityGapRecord.case_id == case_id,
                )
                .order_by(CaseCapabilityGapRecord.created_at, CaseCapabilityGapRecord.id)
            ).all()
            items.extend(
                CaseResolutionItemProjection(
                    item_id=gap.id,
                    item_kind="CAPABILITY_GAP",
                    native_state=gap.severity,
                    source_refs=tuple(
                        ref
                        for ref in (
                            f"capability-gap:{gap.id}",
                            f"requirement:{gap.requirement_id}" if gap.requirement_id else None,
                            f"task:{gap.task_id}" if gap.task_id else None,
                            gap.source_locator,
                        )
                        if ref
                    ),
                    resolution_owner=None,
                    next_action="REVIEW_CAPABILITY_GAP",
                    due_at=None,
                )
                for gap in capability_gaps
            )
        items.sort(
            key=lambda item: (item.due_at is None, item.due_at, item.item_kind, str(item.item_id))
        )
        economic_coverage = None
        if membership_id is None:
            scenarios = self._session.scalars(
                sa.select(PricingScenarioRecord)
                .where(
                    PricingScenarioRecord.tenant_id == tenant_id,
                    PricingScenarioRecord.case_id == case_id,
                    PricingScenarioRecord.state != "ARCHIVED",
                )
                .order_by(PricingScenarioRecord.created_at.desc(), PricingScenarioRecord.id)
            ).all()
            scenarios_with_assumptions = [
                scenario for scenario in scenarios if scenario.assumptions_json
            ]
            assumptions = CaseEconomicCoverageStatusProjection(
                state="PROVEN" if scenarios_with_assumptions else "NOT_DEMONSTRATED",
                source_refs=tuple(
                    f"pricing-scenario:{scenario.id}:snapshot-revision:{scenario.source_snapshot_revision}"
                    for scenario in scenarios_with_assumptions
                ),
                note=(
                    "Hypothèses conservées sur un scénario de prix sourcé."
                    if scenarios_with_assumptions
                    else "Aucune hypothèse de scénario sourcée pour cette Affaire."
                ),
            )

            latest_capacity_run = self._session.scalar(
                sa.select(OptimizationRunRecord)
                .where(
                    OptimizationRunRecord.tenant_id == tenant_id,
                    OptimizationRunRecord.case_id == case_id,
                )
                .order_by(OptimizationRunRecord.created_at.desc(), OptimizationRunRecord.id.desc())
                .limit(1)
            )
            if latest_capacity_run is None:
                capacity = CaseEconomicCoverageStatusProjection(
                    state="NOT_DEMONSTRATED",
                    source_refs=(),
                    note="Aucun calcul de capacité exposé pour cette Affaire.",
                )
            else:
                capacity_state = {
                    "OPTIMAL": "PROVEN",
                    "FEASIBLE": "PROVEN",
                    "INFEASIBLE": "INFEASIBLE",
                    "UNKNOWN": "UNKNOWN",
                    "MODEL_INVALID": "UNKNOWN",
                }[latest_capacity_run.status]
                capacity = CaseEconomicCoverageStatusProjection(
                    state=capacity_state,
                    source_refs=(
                        f"optimization-run:{latest_capacity_run.id}",
                        f"capacity-source-revision:{latest_capacity_run.source_revision}",
                    ),
                    note=(
                        "Résultat de capacité conservé ; il ne constitue pas une réservation."
                        if capacity_state == "PROVEN"
                        else (
                            "Résultat de capacité non concluant ; aucune disponibilité "
                            "n’est présumée."
                        )
                    ),
                )

            published_snapshot = self._session.scalar(
                sa.select(FinancialReportSnapshotRecord)
                .where(
                    FinancialReportSnapshotRecord.tenant_id == tenant_id,
                    FinancialReportSnapshotRecord.case_id == case_id,
                    FinancialReportSnapshotRecord.state == "PUBLISHED",
                )
                .order_by(
                    FinancialReportSnapshotRecord.published_at.desc(),
                    FinancialReportSnapshotRecord.id.desc(),
                )
                .limit(1)
            )
            forecast_line_ids: list[UUID] = []
            if published_snapshot is not None:
                forecast_line_ids = list(
                    self._session.scalars(
                        sa.select(FinancialReportLineRecord.id)
                        .where(
                            FinancialReportLineRecord.tenant_id == tenant_id,
                            FinancialReportLineRecord.snapshot_id == published_snapshot.id,
                            FinancialReportLineRecord.category == "FORECAST_CASHFLOW",
                        )
                        .order_by(
                            FinancialReportLineRecord.created_at,
                            FinancialReportLineRecord.id,
                        )
                    ).all()
                )
            financing = CaseEconomicCoverageStatusProjection(
                state="FORECAST_PRESENT" if forecast_line_ids else "NOT_DEMONSTRATED",
                source_refs=(
                    tuple(
                        [f"financial-snapshot:{published_snapshot.id}"]
                        + [f"forecast-cashflow-line:{line_id}" for line_id in forecast_line_ids]
                    )
                    if published_snapshot is not None and forecast_line_ids
                    else ()
                ),
                note=(
                    "Prévision de trésorerie sourcée ; le financement reste non démontré."
                    if forecast_line_ids
                    else "Aucune prévision de trésorerie sourcée pour cette Affaire."
                ),
            )
            economic_coverage = CaseEconomicCoverageProjection(
                assumptions=assumptions,
                quote_validity=CaseEconomicCoverageStatusProjection(
                    state="NOT_DEMONSTRATED",
                    source_refs=(),
                    note="Aucun contrat de devis n’est présent ; aucune expiration n’est déduite.",
                ),
                capacity=capacity,
                financing=financing,
            )
        return CaseResolutionIndexProjection(
            case_id=case.id,
            work_label=case.title,
            coverage="PARTIAL",
            items=tuple(items),
            economic_coverage=economic_coverage,
        )
