from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.interfaces.http.routes.patron_commitment_card import build_patron_commitment_card_router
from app.interfaces.http.routes.patron_decisions import build_patron_decision_router
from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
from app.modules.case.application.analysis_dossier import AnalysisTreatment
from app.modules.case.infrastructure.analysis_assessment_handler import (
    RecordAnalysisAssessmentHandler,
)
from app.modules.dce.application.commands import RecordDceRequirementConfirmationCommand
from app.modules.dce.application.handlers import RecordDceRequirementConfirmationHandler
from app.modules.dce.application.requirement_confirmation import DceRequirementConfirmationService
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.decision.application.finalize import (
    PatronDecisionFinalizationService,
    decision_finalization_handlers,
)
from app.modules.decision.application.lifecycle import (
    PatronDecisionLifecycleService,
    decision_lifecycle_handlers,
)
from app.modules.decision.application.patron_dossier import PatronDecisionDossierService
from app.modules.decision.infrastructure.commitment_service import (
    CommitmentCardService,
    LinkConditionAssessmentHandler,
)
from app.modules.decision.infrastructure.condition_repository import (
    SqlAlchemyDecisionConditionRepository,
)
from app.modules.decision.infrastructure.dossier_reader import SqlAlchemyDecisionDossierReader
from app.modules.decision.infrastructure.models.assessment_link import (
    DecisionConditionAssessmentLinkRecord as Link,
)
from app.modules.decision.infrastructure.repositories import (
    SqlAlchemyDecisionLifecycleRepository,
    SqlAlchemyDecisionRepository,
)
from app.modules.decision.infrastructure.verified_context_reader import (
    SqlAlchemyDecisionVerifiedContextReader,
)
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.security.authenticated_context import AuthenticationContextResolver
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.application.test_analysis_assessment import fields
from tests.application.test_analysis_dossier import treatment
from tests.db.test_case_analysis_summary_sql import requirements_dossier


@pytest.fixture
def workflow(session_factory, tmp_path):
    text = "Lot 6 : maintenir les accès en site occupé. Le transport est exclu de la fourniture."
    seed = requirements_dossier.__wrapped__(
        session_factory,
        tmp_path,
        source_bytes=text.encode(),
        family="CCTP",
    )
    now = datetime.now(UTC)
    actor = ActorContext(
        actor_id=uuid4(),
        identity_id=uuid4(),
        tenant_id=seed[0],
        membership_id=uuid4(),
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=now,
        mfa_verified_at=now,
        correlation_id=uuid4(),
    )
    context = CommandContext(
        tenant_id=actor.tenant_id,
        case_id=seed[1],
        actor_id=actor.actor_id,
        actor_kind=actor.actor_kind.value,
        membership_id=actor.membership_id,
        received_at=now,
    )
    policy = AuthorizationPolicy()

    def repository(session):
        return SqlAlchemyDecisionRepository(session)

    condition_repo = SqlAlchemyDecisionConditionRepository()
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            **decision_lifecycle_handlers(
                lifecycle_repository=SqlAlchemyDecisionLifecycleRepository(),
                repository_factory=repository,
                condition_repository=condition_repo,
            ),
            **decision_finalization_handlers(
                repository_factory=repository,
                verified_context_reader=SqlAlchemyDecisionVerifiedContextReader(),
                condition_repository=condition_repo,
            ),
            "RecordAnalysisAssessment": RecordAnalysisAssessmentHandler(),
            "RecordDceRequirementConfirmation": RecordDceRequirementConfirmationHandler(),
            "LinkDecisionConditionAssessment": LinkConditionAssessmentHandler(),
        },
    )
    with session_factory() as session:
        req = session.scalar(
            sa.select(DceRequirementRecord).where(DceRequirementRecord.tenant_id == seed[0])
        )
        req_id = req.id
    DceRequirementConfirmationService(
        session_factory=session_factory, dispatcher=dispatcher, policy=policy
    ).confirm(
        actor=actor,
        now=now,
        command=RecordDceRequirementConfirmationCommand(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            confirmation_id=uuid4(),
            requirement_id=req_id,
            expected_confirmation_revision=0,
            outcome="CONFIRMED",
            reason_code="SOURCE_REVIEWED",
        ),
    )
    holder = SimpleNamespace(actor=actor)
    security = ConsultationSecurityRuntime(
        context_resolver=cast(
            AuthenticationContextResolver, SimpleNamespace(resolve=lambda **kw: holder.actor)
        ),
        policy=policy,
    )
    service = CommitmentCardService(
        session_factory=session_factory, dispatcher=dispatcher, policy=policy
    )
    app = FastAPI()
    app.include_router(
        build_patron_commitment_card_router(service=service, security_runtime=security)
    )
    app.include_router(
        build_patron_decision_router(
            service=PatronDecisionDossierService(
                reader=SqlAlchemyDecisionDossierReader(session_factory), policy=policy
            ),
            lifecycle_service=PatronDecisionLifecycleService(dispatcher=dispatcher, policy=policy),
            finalization_service=PatronDecisionFinalizationService(
                dispatcher=dispatcher, policy=policy
            ),
            security_runtime=security,
        )
    )
    client = TestClient(app)
    headers = {"Authorization": "Bearer synthetic"}
    url = f"/api/v1/patron/cases/{seed[1]}"
    point = service.read(actor=actor, case_id=seed[1], now=now)["points"][0]["point"]
    assessment = RecordAnalysisAssessmentCommand(
        **{
            **fields(),
            "case_id": seed[1],
            "point_kind": "REQUIREMENT",
            "point_id": req_id,
            "source_context_sha256": point["source_context_sha256"],
            "treatment": AnalysisTreatment(
                **{**treatment(), "hypotheses": "Deux rotations de livraison"}
            ),
        }
    )
    dispatcher.dispatch(command=assessment, context=context)
    return SimpleNamespace(
        client=client,
        headers=headers,
        url=url,
        actor=actor,
        holder=holder,
        case=seed[1],
        assessment=assessment,
        dispatcher=dispatcher,
        context=context,
        service=service,
        now=now,
    )


def prepare_decision(w):
    created = w.client.post(
        w.url + "/decisions",
        headers=w.headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
    )
    assert created.status_code == 201, created.text
    decision = created.json()["decision_id"]
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        context_id=str(uuid4()),
        expected_revision=created.json()["version"],
        rationale="Revue des sources et hypothèses affichées",
        unknowns=["Transport encore à confirmer"],
        references=card["references"],
    )
    frozen = w.client.post(w.url + f"/decisions/{decision}/context", headers=w.headers, json=body)
    assert frozen.status_code == 200, frozen.text
    return decision, frozen.json()


def finalize(w, decision, frozen):
    condition = str(uuid4())
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        expected_revision=frozen["version"],
        displayed_fingerprint=frozen["fingerprint"],
        outcome="CONDITIONAL_GO",
        justification="Engagement soumis au plan d'accès sourcé",
        conditions=[
            dict(
                condition_id=condition,
                label="Confirmer les rotations de livraison",
                owner_actor_id=str(w.actor.actor_id),
                due_date_absence_reason="Calendrier à confirmer",
                failure_consequence="Maintenir la réserve avant engagement",
            )
        ],
    )
    response = w.client.post(
        w.url + f"/decisions/{decision}/go-no-go", headers=w.headers, json=body
    )
    assert response.status_code == 200, response.text
    return condition, response.json()


def link_body(w, revision):
    return dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        link_id=str(uuid4()),
        expected_decision_revision=revision,
        assessment_id=str(w.assessment.assessment_id),
        assessment_revision=1,
        source_context_sha256=w.assessment.source_context_sha256,
        justification="Cette condition reprend la preuve attendue du point exact",
        human_confirmed=True,
    )


def test_native_decision_link_is_exact_idempotent_and_never_satisfies_the_condition(
    session_factory, workflow
):
    w = workflow
    decision, frozen = prepare_decision(w)
    condition, final = finalize(w, decision, frozen)
    url = w.url + f"/decisions/{decision}/conditions/{condition}/assessment-links"
    body = link_body(w, final["version"])
    first = w.client.post(url, headers=w.headers, json=body)
    assert first.status_code == 201, first.text
    assert w.client.post(url, headers=w.headers, json=body).status_code == 200
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    assert card["current_decision"]["conditions"][0]["status"] == "OPEN"
    point = card["points"][0]
    assert point["condition_links"][0]["condition_id"] == condition
    assert point["hypotheses"] == "Deux rotations de livraison"
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(Link).where(Link.case_id == w.case)
            )
            == 1
        )


def test_new_assessment_after_freeze_refuses_finalization(workflow):
    w = workflow
    decision, frozen = prepare_decision(w)
    changed = w.assessment.model_copy(
        update=dict(
            command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4(), expected_revision=1
        )
    )
    w.dispatcher.dispatch(command=changed, context=w.context)
    body = dict(
        command_id=str(uuid4()),
        idempotency_key=str(uuid4()),
        expected_revision=frozen["version"],
        displayed_fingerprint=frozen["fingerprint"],
        outcome="NO_GO",
        justification="Essai source périmée",
        conditions=[],
    )
    response = w.client.post(
        w.url + f"/decisions/{decision}/go-no-go", headers=w.headers, json=body
    )
    assert response.status_code == 409, response.text


@pytest.mark.parametrize("stage", ["freeze", "read"])
def test_financial_right_is_required_for_the_new_assessment_reference(workflow, stage):
    from app.platform.security.capabilities import Capability

    w = workflow
    if stage == "read":
        prepare_decision(w)
    else:
        created = w.client.post(
            w.url + "/decisions",
            headers=w.headers,
            json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
        )
        decision = created.json()["decision_id"]
        card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            context_id=str(uuid4()),
            expected_revision=created.json()["version"],
            rationale="Essai refus financier",
            references=card["references"],
        )
    w.holder.actor = replace(w.actor, capabilities=w.actor.capabilities - {Capability.PRICING_READ})
    response = (
        w.client.get(w.url + "/decision-dossier", headers=w.headers)
        if stage == "read"
        else w.client.post(w.url + f"/decisions/{decision}/context", headers=w.headers, json=body)
    )
    assert response.status_code == 403, response.text


@pytest.mark.parametrize("stage", ["finalize", "resolve"])
def test_financial_scope_follows_the_frozen_assessment_until_resolution(workflow, stage):
    from app.platform.security.capabilities import Capability

    w = workflow
    decision, frozen = prepare_decision(w)
    if stage == "resolve":
        condition, final = finalize(w, decision, frozen)
    w.holder.actor = replace(w.actor, capabilities=w.actor.capabilities - {Capability.PRICING_READ})
    if stage == "finalize":
        response = w.client.post(
            w.url + f"/decisions/{decision}/go-no-go",
            headers=w.headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                expected_revision=frozen["version"],
                displayed_fingerprint=frozen["fingerprint"],
                outcome="NO_GO",
                justification="Essai de droit retiré",
                conditions=[],
            ),
        )
    else:
        response = w.client.post(
            w.url + f"/decisions/{decision}/conditions/{condition}/resolve",
            headers=w.headers,
            json=dict(
                command_id=str(uuid4()),
                idempotency_key=str(uuid4()),
                transition_id=str(uuid4()),
                expected_revision=final["version"],
                target_status="SATISFIED",
                evidence_reference="Plan de livraison synthétique",
            ),
        )
    assert response.status_code == 403, response.text


def test_replaced_assessment_between_card_read_and_freeze_is_a_conflict(workflow):
    w = workflow
    created = w.client.post(
        w.url + "/decisions",
        headers=w.headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
    ).json()
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    w.dispatcher.dispatch(
        command=w.assessment.model_copy(
            update=dict(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                assessment_id=uuid4(),
                expected_revision=1,
            )
        ),
        context=w.context,
    )
    response = w.client.post(
        w.url + f"/decisions/{created['decision_id']}/context",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            context_id=str(uuid4()),
            expected_revision=created["version"],
            rationale="Carte affichée avant nouvel acte",
            references=card["references"],
        ),
    )
    assert response.status_code == 409, response.text


def test_resolution_refuses_an_assessment_replaced_after_the_decision(workflow):
    w = workflow
    decision, frozen = prepare_decision(w)
    condition, final = finalize(w, decision, frozen)
    w.dispatcher.dispatch(
        command=w.assessment.model_copy(
            update=dict(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                assessment_id=uuid4(),
                expected_revision=1,
            )
        ),
        context=w.context,
    )
    response = w.client.post(
        w.url + f"/decisions/{decision}/conditions/{condition}/resolve",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            transition_id=str(uuid4()),
            expected_revision=final["version"],
            target_status="SATISFIED",
            evidence_reference="Preuve sur source antérieure",
        ),
    )
    assert response.status_code == 409, response.text


def test_history_and_exact_receipt_lookup_preserve_the_original_human_act(workflow):
    w = workflow
    decision, frozen = prepare_decision(w)
    finalize(w, decision, frozen)
    changed = w.assessment.model_copy(
        update=dict(
            command_id=uuid4(),
            idempotency_key=uuid4(),
            assessment_id=uuid4(),
            expected_revision=1,
            treatment=AnalysisTreatment(
                **{**treatment(), "hypotheses": "Quatre rotations à revoir"}
            ),
        )
    )
    w.dispatcher.dispatch(command=changed, context=w.context)
    exact = w.client.get(w.url + f"/commitment-card/decisions/{decision}", headers=w.headers)
    assert exact.status_code == 200, exact.text
    old = exact.json()["decision"]
    assert old["state"] == "REVIEW_REQUIRED"
    assert (
        old["assessment_snapshots"][0]["treatment"]["hypotheses"] == "Deux rotations de livraison"
    )
    page = w.client.get(w.url + "/commitment-card/history", headers=w.headers)
    assert page.status_code == 200 and page.json()["history"][0]["decision_id"] == decision
    assert (
        w.client.get(
            w.url + f"/commitment-card/history?before_decision_id={decision}",
            headers=w.headers,
        ).json()["history"]
        == []
    )
    assert (
        w.client.get(w.url + f"/commitment-card/decisions/{uuid4()}", headers=w.headers).status_code
        == 404
    )


def test_current_case_scope_wins_over_an_older_scope_with_more_cycles(session_factory, workflow):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.decision.infrastructure.models.decision import DecisionRecord

    w = workflow
    old, frozen = prepare_decision(w)
    finalize(w, old, frozen)
    with session_factory.begin() as session:
        session.execute(
            sa.update(DecisionRecord).where(DecisionRecord.id == UUID(old)).values(cycle_number=10)
        )
        case = session.get(CaseRecord, w.case)
        case.scope_fingerprint = "e" * 64
        case.scope_json = {"lot": "7"}
        case.aggregate_revision += 1
    created = w.client.post(
        w.url + "/decisions",
        headers=w.headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
    )
    assert created.status_code == 201, created.text
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    assert card["current_decision"]["decision_id"] == created.json()["decision_id"]
    assert any(item["decision_id"] == old for item in card["history"])


def test_assessment_links_are_append_only_and_nonempty_downgrade_is_refused(
    session_factory, workflow
):
    from alembic import command as migration
    from alembic.config import Config
    from app.platform.persistence.schema import EXPECTED_ALEMBIC_HEAD
    from sqlalchemy.exc import DBAPIError
    from tests.support.database import ALEMBIC_INI, DATABASE_URL

    w = workflow
    decision, frozen = prepare_decision(w)
    condition, final = finalize(w, decision, frozen)
    body = link_body(w, final["version"])
    url = w.url + f"/decisions/{decision}/conditions/{condition}/assessment-links"
    assert w.client.post(url, headers=w.headers, json=body).status_code == 201
    for statement in (
        sa.update(Link).where(Link.case_id == w.case).values(justification="Réécriture refusée"),
        sa.delete(Link).where(Link.case_id == w.case),
    ):
        with pytest.raises(DBAPIError), session_factory.begin() as session:
            session.execute(statement)
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
    with pytest.raises(RuntimeError, match="HISTORY_DOWNGRADE_REFUSED"):
        migration.downgrade(config, "20261023_0141")
    with session_factory() as session:
        assert (
            session.execute(sa.text("SELECT version_num FROM alembic_version")).scalar_one()
            == EXPECTED_ALEMBIC_HEAD
        )


@pytest.mark.parametrize("identical", [True, False])
def test_concurrent_condition_source_links_have_one_effect(session_factory, workflow, identical):
    from concurrent.futures import ThreadPoolExecutor

    w = workflow
    decision, frozen = prepare_decision(w)
    condition, final = finalize(w, decision, frozen)
    body = link_body(w, final["version"])
    bodies = [body, body if identical else link_body(w, final["version"])]
    url = w.url + f"/decisions/{decision}/conditions/{condition}/assessment-links"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(lambda payload: w.client.post(url, headers=w.headers, json=payload), bodies)
        )
    assert sorted(r.status_code for r in results) == ([200, 201] if identical else [201, 409]), [
        r.text for r in results
    ]
    with session_factory() as session:
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(Link).where(Link.case_id == w.case)
            )
            == 1
        )


@pytest.mark.parametrize("stage", ["finalize", "resolve"])
def test_private_replay_rechecks_financial_rights(workflow, stage):
    from app.platform.security.capabilities import Capability

    w = workflow
    decision, frozen = prepare_decision(w)
    if stage == "resolve":
        condition, final = finalize(w, decision, frozen)
        url = w.url + f"/decisions/{decision}/conditions/{condition}/resolve"
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            transition_id=str(uuid4()),
            expected_revision=final["version"],
            target_status="SATISFIED",
            evidence_reference="Plan synthétique validé humainement",
        )
    else:
        url = w.url + f"/decisions/{decision}/go-no-go"
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=frozen["version"],
            displayed_fingerprint=frozen["fingerprint"],
            outcome="NO_GO",
            justification="Motivation synthétique",
            conditions=[],
        )
    first = w.client.post(url, headers=w.headers, json=body)
    assert first.status_code == 200, first.text
    w.holder.actor = replace(w.actor, capabilities=w.actor.capabilities - {Capability.PRICING_READ})
    assert w.client.post(url, headers=w.headers, json=body).status_code == 403


@pytest.mark.parametrize("change", ["case", "confirmation"])
def test_native_source_change_before_freeze_is_recoverable(workflow, session_factory, change):
    w = workflow
    created = w.client.post(
        w.url + "/decisions",
        headers=w.headers,
        json=dict(command_id=str(uuid4()), idempotency_key=str(uuid4())),
    ).json()
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    if change == "case":
        from app.modules.case.infrastructure.models.case import CaseRecord

        with session_factory.begin() as session:
            case = session.get(CaseRecord, w.case)
            case.aggregate_revision += 1
    else:
        DceRequirementConfirmationService(
            session_factory=session_factory, dispatcher=w.dispatcher, policy=AuthorizationPolicy()
        ).confirm(
            actor=w.actor,
            now=w.now,
            command=RecordDceRequirementConfirmationCommand(
                command_id=uuid4(),
                idempotency_key=uuid4(),
                confirmation_id=uuid4(),
                requirement_id=w.assessment.point_id,
                expected_confirmation_revision=1,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
            ),
        )
    response = w.client.post(
        w.url + f"/decisions/{created['decision_id']}/context",
        headers=w.headers,
        json=dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            context_id=str(uuid4()),
            expected_revision=created["version"],
            rationale="Anciennes références affichées",
            references=card["references"],
        ),
    )
    assert response.status_code == 409, response.text


def test_current_decision_is_not_lost_beyond_the_first_history_page(session_factory, workflow):
    from datetime import timedelta
    from hashlib import sha256

    from app.modules.decision.infrastructure.models.decision import DecisionRecord
    from tests.db.test_candidate_retrieval_sql import _clone

    w = workflow
    decision, frozen = prepare_decision(w)
    finalize(w, decision, frozen)
    with session_factory.begin() as session:
        original = session.get(DecisionRecord, UUID(decision))
        for index in range(21):
            identity = uuid4()
            timestamp = w.now + timedelta(seconds=index + 1)
            session.add(
                _clone(
                    original,
                    id=identity,
                    scope_fingerprint=sha256(identity.bytes).hexdigest(),
                    decision_key_hash=sha256(str(identity).encode()).hexdigest(),
                    cycle_number=1,
                    aggregate_revision=0,
                    lifecycle="DRAFT",
                    outcome="UNDECIDED",
                    validity="CURRENT",
                    condition_status="NOT_APPLICABLE",
                    context_status="INCOMPLETE",
                    selected_final_context_id=None,
                    successor_decision_id=None,
                    final_justification=None,
                    finalized_by_actor_id=None,
                    finalized_at=None,
                    created_at=timestamp,
                    updated_at=timestamp,
                )
            )
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    assert card["current_decision"]["decision_id"] == decision
    first = w.client.get(w.url + "/commitment-card/history", headers=w.headers).json()
    second = w.client.get(
        w.url + f"/commitment-card/history?before_decision_id={first['next_before_decision_id']}",
        headers=w.headers,
    ).json()
    identifiers = [d["decision_id"] for d in first["history"] + second["history"]]
    assert len(identifiers) == len(set(identifiers)) == 22


def test_visible_impact_missing_its_required_profile_is_explicitly_unbound(
    session_factory, workflow
):
    from app.modules.dce.infrastructure.models.contract_baseline import (
        ContractBaselineDeviationImpactRecord,
    )

    w = workflow
    proof = uuid4()
    with session_factory.begin() as session:
        req = session.get(DceRequirementRecord, w.assessment.point_id)
        session.add(
            ContractBaselineDeviationImpactRecord(
                id=proof,
                tenant_id=w.actor.tenant_id,
                case_id=w.case,
                baseline_observation_id=req.source_observation_id,
                dce_requirement_id=req.id,
                dce_requirement_revision=1,
                proof_revision=1,
                baseline_source_refs_json=[f"DCE_REQUIREMENT:{req.id}@1", "CCTP / ligne1"],
                baseline_statement="Accès à maintenir en site occupé",
                impact_statement="Transport à chiffrer : UNKNOWN",
                status="HUMAN_REVIEW_REQUIRED",
            )
        )
    card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
    assert card["unbound_contract_impacts"] == [str(proof)]
    assert all(r["aggregate_type"] != "CONTRACT_BASELINE_IMPACT" for r in card["references"])


@pytest.mark.parametrize("stage", ["freeze", "finalize"])
def test_concurrent_native_decision_phase_changes_are_conflicts(workflow, stage):
    w = workflow
    decision, frozen = prepare_decision(w)
    if stage == "finalize":
        finalize(w, decision, frozen)
        path = w.url + f"/decisions/{decision}/go-no-go"
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            expected_revision=frozen["version"],
            displayed_fingerprint=frozen["fingerprint"],
            outcome="NO_GO",
            justification="Autre intention concurrente",
            conditions=[],
        )
    else:
        card = w.client.get(w.url + "/commitment-card", headers=w.headers).json()
        path = w.url + f"/decisions/{decision}/context"
        body = dict(
            command_id=str(uuid4()),
            idempotency_key=str(uuid4()),
            context_id=str(uuid4()),
            expected_revision=0,
            rationale="Intention de gel concurrente",
            references=card["references"],
        )
    response = w.client.post(path, headers=w.headers, json=body)
    assert response.status_code == 409, response.text
