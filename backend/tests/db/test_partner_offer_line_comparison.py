from dataclasses import replace
from types import SimpleNamespace
from uuid import uuid4

import pytest
from app.interfaces.http.routes.patron_partner_offer_line_comparisons import (
    build_patron_partner_offer_line_comparisons_router,
)
from app.modules.pricing.application.partner_offer_line_comparison_commands import (
    PartnerOfferLineGroupCommand,
    PartnerOfferLineMemberCommand,
    RecordPartnerOfferLineComparisonCommand,
)
from app.modules.pricing.application.partner_offer_line_comparison_handler import (
    PartnerOfferLineComparisonService,
    partner_offer_line_comparison_handlers,
)
from app.modules.pricing.infrastructure.models.partner_offer_line_comparison import (
    PartnerOfferLineComparisonRecord,
    PartnerOfferLineMemberRecord,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorKind
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import delete, update
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session
from tests.db.test_partner_offer_scope_review import (
    NOW,
    _receipt,
    _seed,
)
from tests.db.test_partner_offer_scope_review import (
    _command as scope_review_command,
)
from tests.db.test_partner_offer_scope_review import (
    _offer as scope_review_offer,
)


def _member(receipt_event_id, *, unknown=False):
    state = "UNKNOWN" if unknown else "DECLARED"
    return PartnerOfferLineMemberCommand(
        receipt_event_id=receipt_event_id,
        line_locator_state=state,
        line_locator=None if unknown else "Feuille BPU, ligne 14",
        item_reference_state=state,
        item_reference=None if unknown else "LOT-04-A",
        designation_state=state,
        designation=None if unknown else "Terrassement en pleine masse",
        unit_state=state,
        unit=None if unknown else "m3",
        quantity_state=state,
        quantity=None if unknown else "1 250,00",
    )


def _line_command(case_id, scope_review_id, receipt_ids, *, expected_revision=0, unknown=False):
    return RecordPartnerOfferLineComparisonCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        record_id=uuid4(),
        comparison_id=uuid4(),
        case_id=case_id,
        scope_review_id=scope_review_id,
        expected_revision=expected_revision,
        groups=(
            PartnerOfferLineGroupCommand(
                group_id=uuid4(),
                disposition="NEEDS_CLARIFICATION",
                rationale=(
                    "Les postes sont saisis pour revue humaine, sans conclure à la couverture."
                ),
                members=tuple(_member(receipt_id, unknown=unknown) for receipt_id in receipt_ids),
            ),
        ),
    )


def _line_service(session_factory):
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers=partner_offer_line_comparison_handlers(),
    )
    return PartnerOfferLineComparisonService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )


def _confirmed_scope(service, actor, case_id, receipt_ids, *, decision="SAME_SCOPE_CONFIRMED"):
    command = scope_review_command(
        case_id,
        uuid4(),
        receipt_ids,
        decision=decision,
        offers=tuple(scope_review_offer(receipt_id) for receipt_id in receipt_ids),
    )
    service.record(actor=actor, command=command, now=NOW)
    return command


def test_http_line_comparison_is_idempotent_source_backed_and_keeps_unknowns(
    database_engine, session_factory
):
    tenant_id, case_id, actor, scope_service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    scope = _confirmed_scope(scope_service, actor, case_id, (first_id, second_id))
    line_service = _line_service(session_factory)
    line = _line_command(case_id, scope.review_id, (first_id, second_id), unknown=True)

    class Resolver:
        current_actor = actor

        def resolve(self, *, access_token: str):
            assert access_token == "test"
            return self.current_actor

    resolver = Resolver()
    app = FastAPI()
    app.include_router(
        build_patron_partner_offer_line_comparisons_router(
            service=line_service,
            security_runtime=SimpleNamespace(context_resolver=resolver),
        )
    )
    client = TestClient(app)
    path = f"/api/v1/patron/cases/{case_id}/partner-offer-line-comparisons"
    headers = {"Authorization": "Bearer test"}
    body = line.model_dump(mode="json", exclude={"case_id"})

    first = client.post(path, headers=headers, json=body)
    retry = client.post(path, headers=headers, json=body)
    projection = client.get(path, headers=headers)
    assert first.status_code == 201
    assert retry.status_code == 200
    assert retry.json()["replayed"] is True
    assert projection.status_code == 200
    member = next(
        item
        for item in projection.json()["comparisons"][0]["groups"][0]["members"]
        if item["receipt_event_id"] == str(first_id)
    )
    assert member["source_locator"].endswith("v1")
    assert member["quantity_state"] == "UNKNOWN"
    assert member["quantity"] is None
    assert projection.json()["comparisons"][0]["scope_review_id"] == str(scope.review_id)
    assert "amount_as_declared" not in projection.text
    assert "unit_price" not in projection.text

    resolver.current_actor = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    assert client.get(path, headers=headers).status_code == 403


def test_line_comparison_requires_current_confirmed_parent_scope_review(
    database_engine, session_factory
):
    tenant_id, case_id, actor, scope_service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    scope = _confirmed_scope(
        scope_service,
        actor,
        case_id,
        (first_id, second_id),
        decision="NEEDS_CLARIFICATION",
    )

    with pytest.raises(CommandExecutionError, match="PARTNER_SCOPE_REVIEW_NOT_CONFIRMED"):
        _line_service(session_factory).record(
            actor=actor,
            command=_line_command(case_id, scope.review_id, (first_id, second_id)),
            now=NOW,
        )


def test_parent_scope_revision_or_replaced_receipt_requires_line_reassessment(
    database_engine, session_factory
):
    tenant_id, case_id, actor, scope_service = _seed(database_engine, session_factory)
    first_id, first_partner = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    parent = _confirmed_scope(scope_service, actor, case_id, (first_id, second_id))
    service = _line_service(session_factory)
    command = _line_command(case_id, parent.review_id, (first_id, second_id))
    service.record(actor=actor, command=command, now=NOW)

    second_parent = scope_review_command(
        case_id,
        parent.comparison_id,
        (first_id, second_id),
        expected_revision=1,
        decision="NEEDS_CLARIFICATION",
        offers=(scope_review_offer(first_id), scope_review_offer(second_id)),
    )
    scope_service.record(actor=actor, command=second_parent, now=NOW)
    projected = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert projected.comparisons[0].requires_reassessment is True

    _receipt(
        database_engine,
        tenant_id=tenant_id,
        case_id=case_id,
        actor=actor,
        label="A",
        partner_id=first_partner,
        revision=3,
    )
    projected = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert projected.comparisons[0].requires_reassessment is True


def test_database_rejects_update_and_delete_of_line_comparison_history(
    database_engine, session_factory
):
    tenant_id, case_id, actor, scope_service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    parent = _confirmed_scope(scope_service, actor, case_id, (first_id, second_id))
    service = _line_service(session_factory)
    command = _line_command(case_id, parent.review_id, (first_id, second_id))
    service.record(actor=actor, command=command, now=NOW)
    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            update(PartnerOfferLineComparisonRecord)
            .where(PartnerOfferLineComparisonRecord.id == command.record_id)
            .values(scope_review_id=uuid4())
        )
        session.commit()
    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            delete(PartnerOfferLineMemberRecord).where(
                PartnerOfferLineMemberRecord.case_id == case_id
            )
        )
        session.commit()
