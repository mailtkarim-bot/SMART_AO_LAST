from __future__ import annotations

import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID, uuid4

import pytest
from app.modules.case.infrastructure.resolution_reader import SqlAlchemyCaseResolutionReader
from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
    DceRequirementConfirmationCurrentRecord,
    DceRequirementConfirmationRecord,
)
from app.modules.enterprise.infrastructure.models import CaseCapabilityGapRecord
from app.modules.membership.application.collab_info_blockers import (
    CollaboratorInfoBlockerService,
    collaborator_info_blocker_handlers,
)
from app.modules.membership.application.collab_info_blockers_commands import (
    CreateInformationRequestCommand,
    DeclareTaskBlockerCommand,
    RecordInformationRequestResponseCommand,
)
from app.modules.membership.application.collab_work_task import (
    CollaboratorWorkTaskService,
    collaborator_work_task_handlers,
)
from app.modules.membership.application.collab_work_task_commands import (
    CreateTaskFromRequirementCommand,
)
from app.modules.membership.infrastructure.collab_info_blockers_reader import (
    SqlAlchemyCollaboratorInfoBlockerReader,
)
from app.modules.membership.infrastructure.collab_work_task_reader import (
    SqlAlchemyCollaboratorWorkTaskReader,
)
from app.modules.optimization.infrastructure.models import OptimizationRunRecord
from app.modules.pricing.infrastructure.models import (
    FinancialReportLineRecord,
    FinancialReportSnapshotRecord,
    PricingScenarioRecord,
)
from app.platform.events.dispatcher import CommandDispatcher
from app.platform.security.authorization import AuthorizationPolicy

sys.path.insert(0, str(Path(__file__).parent))
from test_collab_work_task import _seed  # noqa: E402

NOW = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)


def _task_service(session_factory) -> CollaboratorWorkTaskService:
    return CollaboratorWorkTaskService(
        reader=SqlAlchemyCollaboratorWorkTaskReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=collaborator_work_task_handlers(),
        ),
        policy=AuthorizationPolicy(),
    )


def _info_service(session_factory) -> CollaboratorInfoBlockerService:
    return CollaboratorInfoBlockerService(
        reader=SqlAlchemyCollaboratorInfoBlockerReader(session_factory),
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers=collaborator_info_blocker_handlers(),
        ),
        policy=AuthorizationPolicy(),
    )


@pytest.mark.db
@pytest.mark.security
def test_case_resolution_index_preserves_native_states_and_assignment_scope(
    session_factory,
) -> None:
    actor, assignment_id, case_id, requirement_id = _seed(session_factory)
    task = _task_service(session_factory).execute(
        actor=actor,
        command=CreateTaskFromRequirementCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            task_id=uuid4(),
            assignment_id=assignment_id,
            case_id=case_id,
            requirement_id=requirement_id,
            task_kind="REQUIREMENT_CHECK",
            title="Vérifier la source",
            objective="Contrôler la page de référence.",
            due_at=NOW.replace(day=20),
        ),
        now=NOW,
    )
    task_id = UUID(str(task.aggregate_refs[0]["aggregate_id"]))
    info = _info_service(session_factory)
    request = CreateInformationRequestCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        request_id=uuid4(),
        task_id=task_id,
        expected_task_revision=0,
        request_kind="MISSING_SOURCE",
        subject="Source de l’exigence",
        question="Quelle page confirme l’exigence ?",
        requested_object="Localisation de la source",
        reason="La preuve doit être retrouvée.",
        priority="HIGH",
        due_at=None,
    )
    info.execute(actor=actor, command=request, now=NOW)
    info.execute(
        actor=actor,
        command=RecordInformationRequestResponseCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            correlation_id=uuid4(),
            request_id=request.request_id,
            expected_revision=0,
            response_text="Réponse reçue, à conserver dans l’historique.",
            source_locator="RC:p8",
            outcome="ANSWERED",
        ),
        now=NOW,
    )
    blocker = DeclareTaskBlockerCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        task_id=task_id,
        expected_revision=0,
        blocker_id=uuid4(),
        blocker_kind="MISSING_INFORMATION",
        description="La source doit encore être contrôlée.",
        source_locator="RC:p8",
        resolution_owner="COLLABORATEUR",
    )
    info.execute(actor=actor, command=blocker, now=NOW)
    with session_factory.begin() as session:
        session.add(
            CaseCapabilityGapRecord(
                id=uuid4(),
                tenant_id=actor.tenant_id,
                case_id=case_id,
                assignment_id=assignment_id,
                capability_id=None,
                requirement_id=requirement_id,
                task_id=None,
                gap_kind="MISSING",
                severity="BLOCKING",
                reason="La capacité de preuve n’est pas encore documentée.",
                source_locator="DCE:p4",
                recommended_action="Rechercher une preuve validée.",
                functional_key=f"case:{case_id}:requirement:{requirement_id}:capability",
                reported_by_membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )

    with session_factory() as session:
        reader = SqlAlchemyCaseResolutionReader(session)
        projection = reader.get(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            membership_id=actor.membership_id,
        )
        foreign_membership = reader.get(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            membership_id=uuid4(),
        )
        patron_projection = reader.get(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            membership_id=None,
        )
        missing_case = reader.get(
            tenant_id=uuid4(),
            case_id=case_id,
            membership_id=None,
        )

    assert projection is not None
    assert projection.coverage == "PARTIAL"
    assert {item.item_kind for item in projection.items} == {"REQUIREMENT", "TASK_BLOCKER"}
    requirement = next(item for item in projection.items if item.item_kind == "REQUIREMENT")
    assert requirement.native_state == "PENDING_HUMAN_CONFIRMATION"
    assert requirement.next_action == "CONFIRM_REQUIREMENT"
    assert requirement.due_at is None
    assert f"requirement:{requirement_id}" in requirement.source_refs
    task_blocker = next(item for item in projection.items if item.item_kind == "TASK_BLOCKER")
    assert task_blocker.native_state == "OPEN"
    assert task_blocker.resolution_owner == "COLLABORATEUR"
    assert task_blocker.next_action == "RESOLVE_TASK_BLOCKER"
    assert task_blocker.due_at == NOW.replace(day=20)
    assert f"task:{task_id}" in task_blocker.source_refs
    assert patron_projection is not None
    capability_gap = next(
        item for item in patron_projection.items if item.item_kind == "CAPABILITY_GAP"
    )
    assert capability_gap.native_state == "BLOCKING"
    assert capability_gap.next_action == "REVIEW_CAPABILITY_GAP"
    assert capability_gap.due_at is None
    assert f"requirement:{requirement_id}" in capability_gap.source_refs
    assert foreign_membership is not None
    assert all(item.item_kind == "REQUIREMENT" for item in foreign_membership.items)
    assert missing_case is None


@pytest.mark.db
@pytest.mark.security
def test_case_resolution_index_exposes_review_required_without_closing_it(session_factory) -> None:
    actor, _, case_id, requirement_id = _seed(session_factory)
    confirmation_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            DceRequirementConfirmationRecord(
                id=confirmation_id,
                tenant_id=actor.tenant_id,
                requirement_id=requirement_id,
                revision=1,
                previous_confirmation_id=None,
                outcome="REVIEW_REQUIRED",
                reason_code="AMBIGUOUS_SOURCE",
                confirmed_by_actor_id=actor.identity_id,
                created_at=NOW,
            )
        )
        session.flush()
        session.add(
            DceRequirementConfirmationCurrentRecord(
                requirement_id=requirement_id,
                tenant_id=actor.tenant_id,
                confirmation_id=confirmation_id,
                revision=1,
                outcome="REVIEW_REQUIRED",
                updated_at=NOW,
            )
        )

    risk = SimpleNamespace(
        observation_id=uuid4(),
        dce_version_id=uuid4(),
        fragment_id=uuid4(),
        source_locator_label="CCAP · page 7",
        verification_status="REVIEW_REQUIRED",
    )
    contradiction = SimpleNamespace(
        contradiction_id=uuid4(),
        dce_version_id=uuid4(),
        source_fragment_id=uuid4(),
        related_batch_id=uuid4(),
        source_locator_label="CCTP · page 3",
        verification_status="REVIEW_REQUIRED",
    )

    class _RiskReader:
        def list_for_case(self, **kwargs):
            return (risk,)

    class _ContradictionReader:
        def detect(self, **kwargs):
            return (contradiction,)

    with session_factory() as session:
        projection = SqlAlchemyCaseResolutionReader(
            session,
            contract_risk_reader=_RiskReader(),
            contradiction_reader=_ContradictionReader(),
        ).get(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            membership_id=None,
        )

    assert projection is not None
    assert {item.item_kind for item in projection.items} == {
        "REQUIREMENT",
        "RISK",
        "CONTRADICTION",
    }
    requirement = next(item for item in projection.items if item.item_kind == "REQUIREMENT")
    assert requirement.native_state == "REVIEW_REQUIRED"
    assert requirement.next_action == "REVIEW_REQUIREMENT"
    risk_item = next(item for item in projection.items if item.item_kind == "RISK")
    assert risk_item.next_action == "REVIEW_RISK"
    assert f"observation:{risk.observation_id}" in risk_item.source_refs
    contradiction_item = next(
        item for item in projection.items if item.item_kind == "CONTRADICTION"
    )
    assert contradiction_item.next_action == "REVIEW_CONTRADICTION"
    assert f"pricing-batch:{contradiction.related_batch_id}" in contradiction_item.source_refs


@pytest.mark.db
@pytest.mark.security
def test_case_resolution_index_exposes_sourced_economic_coverage_to_patron(
    session_factory,
) -> None:
    actor, _assignment_id, case_id, _requirement_id = _seed(session_factory)
    snapshot_id, scenario_id, run_id, forecast_line_id = uuid4(), uuid4(), uuid4(), uuid4()
    with session_factory.begin() as session:
        session.add(
            FinancialReportSnapshotRecord(
                id=snapshot_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                state="PUBLISHED",
                currency_code="EUR",
                ruleset_version=1,
                aggregate_revision=2,
                calculated_at=NOW,
                published_at=NOW,
                sales_total_minor=100,
                direct_cost_total_minor=60,
                overhead_total_minor=10,
                subcontracting_total_minor=5,
                contingency_total_minor=5,
                gross_margin_minor=20,
                gross_margin_rate_bps=2000,
                forecast_cashflow_minor=15,
            )
        )
        session.flush()
        session.add(
            FinancialReportLineRecord(
                id=forecast_line_id,
                tenant_id=actor.tenant_id,
                snapshot_id=snapshot_id,
                category="FORECAST_CASHFLOW",
                label="Prévision encaissement",
                quantity_decimal="1",
                unit="LOT",
                amount_minor=15,
            )
        )
        session.add(
            PricingScenarioRecord(
                id=scenario_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                source_snapshot_id=snapshot_id,
                scenario_key="PRUDENT",
                scenario_type="PRUDENT",
                version=1,
                state="DRAFT",
                assumptions_json={"supplier_buffer_bps": 800},
                sales_total_minor=100,
                total_cost_minor=80,
                gross_margin_minor=20,
                gross_margin_rate_bps=2000,
                penalty_reserve_minor=0,
                retention_reserve_minor=0,
                guarantee_reserve_minor=0,
                floor_margin_rate_bps=1000,
                target_margin_rate_bps=2000,
                break_even_sales_minor=80,
                floor_sales_minor=90,
                target_sales_minor=100,
                source_snapshot_revision=2,
                actor_id=actor.identity_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
        session.add(
            OptimizationRunRecord(
                id=run_id,
                tenant_id=actor.tenant_id,
                case_id=case_id,
                source_revision=3,
                solver_id="google-ortools-cp-sat",
                status="OPTIMAL",
                input_sha256="a" * 64,
                input_snapshot_json={"demands": [], "supplies": []},
                result_snapshot_json={"assignments": []},
                actor_id=actor.identity_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )

    with session_factory() as session:
        projection = SqlAlchemyCaseResolutionReader(session).get(
            tenant_id=actor.tenant_id,
            case_id=case_id,
            membership_id=None,
        )

    assert projection is not None
    assert projection.economic_coverage is not None
    coverage = projection.economic_coverage
    assert coverage.assumptions.state == "PROVEN"
    assert f"pricing-scenario:{scenario_id}:snapshot-revision:2" in coverage.assumptions.source_refs
    assert coverage.quote_validity.state == "NOT_DEMONSTRATED"
    assert coverage.quote_validity.source_refs == ()
    assert coverage.capacity.state == "PROVEN"
    assert f"optimization-run:{run_id}" in coverage.capacity.source_refs
    assert coverage.financing.state == "FORECAST_PRESENT"
    assert f"financial-snapshot:{snapshot_id}" in coverage.financing.source_refs
    assert f"forecast-cashflow-line:{forecast_line_id}" in coverage.financing.source_refs
    assert "financement reste non démontré" in coverage.financing.note
