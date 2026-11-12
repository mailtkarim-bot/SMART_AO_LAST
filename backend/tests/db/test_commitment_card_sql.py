from typing import Any, cast
from uuid import uuid4

import pytest
from app.modules.decision.infrastructure.commitment_reader import read_commitment_card
from app.modules.decision.infrastructure.repositories import SqlAlchemyDecisionLifecycleRepository
from tests.db.test_analysis_assessment_sql import record_setup
from tests.db.test_case_analysis_summary_sql import dossier as base_dossier


@pytest.fixture
def dossier(session_factory):
    return base_dossier.__wrapped__(session_factory)


def test_card_has_twelve_axes_exact_facts_and_no_invented_links(session_factory, dossier):
    seed, command, dispatcher, context = record_setup(session_factory, dossier)
    dispatcher.dispatch(command=command, context=context)
    with session_factory() as session:
        card = read_commitment_card(
            session, tenant_id=seed[0], case_id=seed[1], session_factory=session_factory
        )
        assert len(card["axes"]) == 12
        point = next(p for p in card["points"] if p["point"]["kind"] == "RISK")
        assert point["point"]["source_excerpt"]
        assert point["point"]["human_assessment"]["assessment_id"] == str(command.assessment_id)
        assert point["relations_state"] == "UNKNOWN"
        assert card["gate_effect"] == "NONE" and card["analysis_complete"] is False


def test_exact_assessment_reference_refuses_stale_revision_and_foreign_scope(
    session_factory, dossier
):
    seed, command, dispatcher, context = record_setup(session_factory, dossier)
    dispatcher.dispatch(command=command, context=context)
    repo = SqlAlchemyDecisionLifecycleRepository()

    def valid(tenant=seed[0], case=seed[1], revision=1):
        with session_factory.begin() as session:
            return repo.context_reference_is_valid(
                session=session,
                tenant_id=tenant,
                case_id=case,
                aggregate_type="ANALYSIS_ASSESSMENT",
                aggregate_id=command.assessment_id,
                aggregate_revision=revision,
                content_hash=command.source_context_sha256,
            )

    assert valid()
    assert not valid(tenant=uuid4()) and not valid(case=uuid4()) and not valid(revision=2)
    next_command = command.model_copy(
        update=dict(
            command_id=uuid4(), idempotency_key=uuid4(), assessment_id=uuid4(), expected_revision=1
        )
    )
    dispatcher.dispatch(command=next_command, context=context)
    assert not valid()


def test_assessment_condition_links_have_native_scope_constraints():
    from app.modules.decision.infrastructure.models.assessment_link import (
        DecisionConditionAssessmentLinkRecord,
    )

    table = DecisionConditionAssessmentLinkRecord.__table__
    assert {
        "case_id",
        "decision_id",
        "condition_id",
        "assessment_id",
        "assessment_revision",
        "source_context_sha256",
    }.issubset(table.columns.keys())
    assert len(table.foreign_key_constraints) >= 4


def test_card_http_is_patron_financial_private_and_tenant_scoped(session_factory, dossier):
    from dataclasses import replace
    from datetime import UTC, datetime
    from types import SimpleNamespace

    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.interfaces.http.routes.patron_commitment_card import (
        build_patron_commitment_card_router,
    )
    from app.modules.decision.infrastructure.commitment_service import CommitmentCardService
    from app.platform.events.dispatcher import CommandDispatcher
    from app.platform.security.authorization import AuthorizationPolicy
    from app.platform.security.capabilities import Capability, capabilities_for
    from app.platform.security.context import ActorContext, ActorKind, MembershipState
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    seed, _ = dossier
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
    holder = SimpleNamespace(actor=actor)
    service = CommitmentCardService(
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
        dispatcher=CommandDispatcher(session_factory=session_factory, handlers={}),
    )
    app = FastAPI()
    app.include_router(
        build_patron_commitment_card_router(
            service=service,
            security_runtime=ConsultationSecurityRuntime(
                context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kw: holder.actor)),
                policy=AuthorizationPolicy(),
            ),
        )
    )
    client = TestClient(app)
    url = f"/api/v1/patron/cases/{seed[1]}/commitment-card"
    headers = {"Authorization": "Bearer synthetic"}
    assert client.get(url, headers=headers).status_code == 200
    for changed in [
        replace(actor, actor_kind=ActorKind.COLLABORATEUR),
        replace(actor, capabilities=actor.capabilities - {Capability.PRICING_READ}),
    ]:
        holder.actor = changed
        assert client.get(url, headers=headers).status_code == 403
    holder.actor = replace(actor, tenant_id=uuid4())
    assert client.get(url, headers=headers).status_code == 404
