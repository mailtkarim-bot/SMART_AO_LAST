from dataclasses import replace
from datetime import UTC, date, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.case_partners import build_case_partner_router
from app.modules.partner.application.commands import (
    DeclareCasePartnerEngagementCommand,
    RecordCasePartnerReceiptCommand,
    RecordCasePartnerRequestCommand,
)
from app.modules.partner.application.partner_handler import (
    CasePartnerService,
    partner_event_handlers,
)
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.partner.public.contracts import (
    DeclareCasePartnerEngagementRequest,
    RecordCasePartnerReceiptRequest,
    RecordCasePartnerRequestRequest,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import Capability, capabilities_for
from app.platform.security.context import (
    ActorContext,
    ActorKind,
    AssignmentScope,
    DataClassification,
    MembershipState,
    OperationalProfile,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case

NOW = datetime(2026, 9, 30, 12, tzinfo=UTC)


def _seed(database_engine, session_factory):
    tenant_id, case_id, actor_id, membership_id = uuid4(), uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"par-{tenant_id.hex[:10]}", lifecycle="ACTIVE")
        )
        session.flush()
        session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="p"))
        session.commit()
    actor = ActorContext(
        actor_id=actor_id,
        identity_id=actor_id,
        tenant_id=tenant_id,
        membership_id=membership_id,
        actor_kind=ActorKind.PATRON_ADMIN,
        membership_state=MembershipState.ACTIVE,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
        assigned_case_ids=frozenset(),
        session_id=uuid4(),
        authenticated_at=NOW,
        mfa_verified_at=NOW,
        correlation_id=uuid4(),
    )
    dispatcher = CommandDispatcher(
        session_factory=session_factory, handlers=partner_event_handlers()
    )
    service = CasePartnerService(
        dispatcher=dispatcher, session_factory=session_factory, policy=AuthorizationPolicy()
    )
    return tenant_id, case_id, actor, service


def _request(case_id, partner_id, *, expected_revision=0):
    return RecordCasePartnerRequestCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=expected_revision,
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="dce://lot-01/besoin-material",
        rationale="Demande de disponibilité déclarée avec sa source.",
    )


def _receipt(
    case_id,
    partner_id,
    *,
    expected_revision,
    request_event_id=None,
    kind="SUPPLIER",
    mandate_state="NOT_APPLICABLE",
    mandate_source_locator=None,
    valid_until=date(2027, 3, 30),
    exclusions_state="UNKNOWN",
    exclusions=(),
):
    return RecordCasePartnerReceiptCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=expected_revision,
        request_event_id=request_event_id,
        partner_kind=kind,
        partner_label="Fournisseur déclaré" if kind == "SUPPLIER" else "Groupement déclaré",
        source_locator="offer://received/lot-01",
        rationale="Proposition reçue et enregistrée comme preuve.",
        valid_until=valid_until,
        exclusions_state=exclusions_state,
        exclusions=exclusions,
        mandate_state=mandate_state,
        mandate_source_locator=mandate_source_locator,
    )


def _engagement(case_id, partner_id, receipt_event_id, *, expected_revision):
    return DeclareCasePartnerEngagementCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=expected_revision,
        receipt_event_id=receipt_event_id,
        source_locator="agreement://signed/lot-01",
        rationale="Le Patron déclare l'engagement sur la pièce signée citée.",
    )


def test_request_receipt_and_patron_engagement_remain_separate_and_idempotent(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    partner_id = uuid4()
    request = _request(case_id, partner_id)
    service.record_request(actor=actor, command=request, now=NOW)
    receipt = _receipt(
        case_id,
        partner_id,
        expected_revision=1,
        request_event_id=request.event_id,
        exclusions_state="DECLARED",
        exclusions=("Transport non inclus",),
    )
    service.record_receipt(actor=actor, command=receipt, now=NOW)
    before_engagement = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert [event.record.event_type for event in before_engagement.events] == [
        "REQUESTED",
        "RECEIVED",
    ]
    assert before_engagement.events[1].record.exclusions_json == ["Transport non inclus"]
    assert before_engagement.events[1].validity_current == "VALID"

    command = _engagement(case_id, partner_id, receipt.event_id, expected_revision=2)
    first = service.declare_engagement(actor=actor, command=command, now=NOW)
    replay = service.declare_engagement(actor=actor, command=command, now=NOW)
    assert first.result_code == "CASE_PARTNER_ENGAGEMENT_DECLARED_RECORDED"
    assert replay.replayed is True
    events = service.list_for_case(actor=actor, case_id=case_id, now=NOW).events
    assert [event.record.event_type for event in events] == [
        "REQUESTED",
        "RECEIVED",
        "ENGAGEMENT_DECLARED",
    ]
    assert events[2].record.related_event_id == receipt.event_id
    assert events[2].record.source_locator == "agreement://signed/lot-01"
    with Session(database_engine) as session:
        assert (
            session.scalar(
                sa.select(sa.func.count())
                .select_from(CasePartnerEventRecord)
                .where(
                    CasePartnerEventRecord.tenant_id == tenant_id,
                    CasePartnerEventRecord.case_id == case_id,
                    CasePartnerEventRecord.partner_id == partner_id,
                )
            )
            == 3
        )


def test_cotraitant_requires_received_sourced_mandate_and_revision_conflict_fails_closed(
    database_engine, session_factory
):
    _, case_id, actor, service = _seed(database_engine, session_factory)
    partner_id = uuid4()
    first_receipt = _receipt(
        case_id,
        partner_id,
        expected_revision=0,
        kind="CO_CONTRACTOR",
        mandate_state="REQUESTED",
    )
    service.record_receipt(actor=actor, command=first_receipt, now=NOW)
    with pytest.raises(CommandExecutionError, match="PARTNER_MANDATE_NOT_RECEIVED"):
        service.declare_engagement(
            actor=actor,
            command=_engagement(case_id, partner_id, first_receipt.event_id, expected_revision=1),
            now=NOW,
        )

    corrected_receipt = _receipt(
        case_id,
        partner_id,
        expected_revision=1,
        kind="CO_CONTRACTOR",
        mandate_state="RECEIVED",
        mandate_source_locator="mandate://received/1",
    )
    service.record_receipt(actor=actor, command=corrected_receipt, now=NOW)
    with pytest.raises(CommandExecutionError, match="PARTNER_VERSION_CONFLICT"):
        service.declare_engagement(
            actor=actor,
            command=_engagement(
                case_id, partner_id, corrected_receipt.event_id, expected_revision=1
            ),
            now=NOW,
        )
    service.declare_engagement(
        actor=actor,
        command=_engagement(case_id, partner_id, corrected_receipt.event_id, expected_revision=2),
        now=NOW,
    )


def test_read_is_tenant_scoped_and_collaborator_write_requires_case_action(
    database_engine, session_factory
):
    _, case_id, patron, service = _seed(database_engine, session_factory)
    collaborator = replace(
        patron,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
        assigned_case_ids=frozenset({case_id}),
        assignment_scopes=(
            AssignmentScope(
                case_id=case_id,
                allowed_actions=frozenset({Capability.CASE_PARTNER_READ}),
                allowed_classifications=frozenset({DataClassification.INTERNAL_OPERATIONAL}),
            ),
        ),
        operational_profile=OperationalProfile.RESPONSABLE,
    )
    projection = service.list_for_case(actor=collaborator, case_id=case_id, now=NOW)
    assert projection.can_request is False
    assert projection.can_receive is False
    assert projection.can_declare_engagement is False
    with pytest.raises(PermissionError):
        service.record_request(actor=collaborator, command=_request(case_id, uuid4()), now=NOW)
    foreign_projection = service.list_for_case(
        actor=replace(patron, tenant_id=uuid4()), case_id=case_id, now=NOW
    )
    assert foreign_projection.events == ()
    assert foreign_projection.can_request is False
    assert foreign_projection.can_declare_engagement is False


def test_partner_events_are_append_only_at_the_database_boundary(database_engine, session_factory):
    _, case_id, actor, service = _seed(database_engine, session_factory)
    partner_id = uuid4()
    command = _receipt(case_id, partner_id, expected_revision=0)
    service.record_receipt(actor=actor, command=command, now=NOW)

    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.update(CasePartnerEventRecord)
            .where(CasePartnerEventRecord.event_id == command.event_id)
            .values(rationale="mutated")
        )
        session.commit()

    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.delete(CasePartnerEventRecord).where(
                CasePartnerEventRecord.event_id == command.event_id
            )
        )
        session.commit()


def test_http_to_postgres_partner_lifecycle_keeps_receipt_and_engagement_distinct(
    database_engine, session_factory
):
    _, case_id, actor, service = _seed(database_engine, session_factory)

    class ActorResolver:
        def resolve(self, *, access_token: str):
            assert access_token == "test"
            return actor

    app = FastAPI()
    app.include_router(
        build_case_partner_router(
            service=service,
            security_runtime=SimpleNamespace(context_resolver=ActorResolver()),
        )
    )
    client = TestClient(app)
    headers = {"Authorization": "Bearer test"}
    partner_id = uuid4()
    request = RecordCasePartnerRequestRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=0,
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="dce://lot-01/besoin",
        rationale="Demande sourcée.",
    )
    requested = client.post(
        f"/api/v1/cases/{case_id}/partners/requests",
        headers=headers,
        json=request.model_dump(mode="json"),
    )
    assert requested.status_code == 201

    receipt = RecordCasePartnerReceiptRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=1,
        request_event_id=request.event_id,
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="offer://lot-01",
        rationale="Reçu déclaré.",
        valid_until=None,
        exclusions_state="UNKNOWN",
        mandate_state="NOT_APPLICABLE",
    )
    received = client.post(
        f"/api/v1/cases/{case_id}/partners/receipts",
        headers=headers,
        json=receipt.model_dump(mode="json"),
    )
    assert received.status_code == 201
    timeline = client.get(f"/api/v1/cases/{case_id}/partners", headers=headers)
    assert [row["event_type"] for row in timeline.json()["events"]] == [
        "REQUESTED",
        "RECEIVED",
    ]

    engagement = DeclareCasePartnerEngagementRequest(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        event_id=uuid4(),
        partner_id=partner_id,
        case_id=case_id,
        expected_revision=2,
        receipt_event_id=receipt.event_id,
        source_locator="agreement://signed/1",
        rationale="Déclaration Patron sourcée.",
    )
    payload = engagement.model_dump(mode="json")
    path = f"/api/v1/cases/{case_id}/partners/engagements"
    declared = client.post(path, headers=headers, json=payload)
    replay = client.post(path, headers=headers, json=payload)
    assert declared.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    timeline = client.get(f"/api/v1/cases/{case_id}/partners", headers=headers)
    assert [row["event_type"] for row in timeline.json()["events"]] == [
        "REQUESTED",
        "RECEIVED",
        "ENGAGEMENT_DECLARED",
    ]
