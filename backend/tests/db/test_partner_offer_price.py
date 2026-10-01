from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.patron_partner_offer_prices import (
    build_patron_partner_offer_prices_router,
)
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_price_commands import (
    DeclarePartnerOfferPriceCommand,
)
from app.modules.pricing.application.partner_offer_price_handler import (
    PartnerOfferPriceService,
    partner_offer_price_handlers,
)
from app.modules.pricing.infrastructure.models.partner_offer_price import (
    PartnerOfferPriceDeclarationRecord,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError
from app.platform.persistence.models import TenantRecord
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorContext, ActorKind, MembershipState
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
            TenantRecord(id=tenant_id, slug=f"opf-{tenant_id.hex[:10]}", lifecycle="ACTIVE")
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
        session_factory=session_factory,
        handlers=partner_offer_price_handlers(),
    )
    service = PartnerOfferPriceService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    return tenant_id, case_id, actor, service


def _received(database_engine, *, tenant_id, case_id, actor, partner_id=None, revision=1):
    event_id = uuid4()
    partner_id = partner_id or uuid4()
    with Session(database_engine) as session:
        session.add(
            CasePartnerEventRecord(
                event_id=event_id,
                tenant_id=tenant_id,
                case_id=case_id,
                partner_id=partner_id,
                revision=revision,
                event_type="RECEIVED",
                partner_kind="SUPPLIER",
                partner_label="Fournisseur A",
                related_event_id=None,
                source_locator="offre://consultation-7/v1.pdf",
                rationale="Offre reçue pour le lot 7.",
                valid_until=None,
                validity_at_recording="UNKNOWN",
                exclusions_state="UNKNOWN",
                exclusions_json=[],
                mandate_state="NOT_APPLICABLE",
                mandate_source_locator=None,
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=actor.correlation_id,
            )
        )
        session.commit()
    return event_id, partner_id


def _command(case_id, receipt_event_id, *, expected_revision=0):
    return DeclarePartnerOfferPriceCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        declaration_id=uuid4(),
        case_id=case_id,
        receipt_event_id=receipt_event_id,
        expected_revision=expected_revision,
        amount_as_declared="1234,50",
        currency_code="MAD",
    )


def test_price_declaration_is_idempotent_private_and_keeps_unknowns(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    receipt_id, partner_id = _received(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor
    )

    unknown = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert len(unknown.offers) == 1
    assert unknown.offers[0].receipt_event_id == receipt_id
    assert unknown.offers[0].source_locator == "offre://consultation-7/v1.pdf"
    assert unknown.offers[0].declarations == ()

    command = _command(case_id, receipt_id)
    first = service.declare(actor=actor, command=command, now=NOW)
    replay = service.declare(actor=actor, command=command, now=NOW)
    assert first.result_code == "PARTNER_OFFER_PRICE_DECLARED"
    assert replay.replayed is True
    with pytest.raises(CommandExecutionError, match="PARTNER_OFFER_PRICE_DECLARATION_ID_REUSED"):
        service.declare(
            actor=actor,
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "expected_revision": 1,
                }
            ),
            now=NOW,
        )

    declared = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    assert declared.offers[0].partner_id == partner_id
    assert declared.offers[0].declarations[0].amount_as_declared == "1234,50"
    assert declared.offers[0].declarations[0].currency_code == "MAD"

    foreign_tenant_projection = service.list_for_case(
        actor=replace(actor, tenant_id=uuid4()), case_id=case_id, now=NOW
    )
    assert foreign_tenant_projection.offers == ()

    collaborator = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    with pytest.raises(PermissionError):
        service.list_for_case(actor=collaborator, case_id=case_id, now=NOW)
    with pytest.raises(PermissionError):
        service.declare(actor=collaborator, command=_command(case_id, receipt_id), now=NOW)


def test_price_declaration_rejects_foreign_receipt_and_stale_revision(
    database_engine, session_factory
):
    _, case_id, actor, service = _seed(database_engine, session_factory)
    receipt_id, partner_id = _received(
        database_engine, tenant_id=actor.tenant_id, case_id=case_id, actor=actor
    )
    foreign_case_id = uuid4()
    with Session(database_engine) as session:
        session.add(_case(tenant_id=actor.tenant_id, case_id=foreign_case_id, marker="q"))
        session.commit()

    with pytest.raises(CommandExecutionError, match="PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN"):
        service.declare(
            actor=actor,
            command=_command(foreign_case_id, receipt_id),
            now=NOW,
        )
    latest_receipt_id, _ = _received(
        database_engine,
        tenant_id=actor.tenant_id,
        case_id=case_id,
        actor=actor,
        partner_id=partner_id,
        revision=2,
    )
    assert partner_id is not None
    with pytest.raises(CommandExecutionError, match="PARTNER_RECEIPT_VERSION_CONFLICT"):
        service.declare(actor=actor, command=_command(case_id, receipt_id), now=NOW)
    command = _command(case_id, latest_receipt_id)
    service.declare(actor=actor, command=command, now=NOW)
    with pytest.raises(CommandExecutionError, match="PARTNER_OFFER_PRICE_VERSION_CONFLICT"):
        service.declare(
            actor=actor,
            command=_command(case_id, latest_receipt_id),
            now=NOW,
        )


def test_partner_offer_price_rows_are_append_only_at_postgres_boundary(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    receipt_id, _ = _received(database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor)
    command = _command(case_id, receipt_id)
    service.declare(actor=actor, command=command, now=NOW)

    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.update(PartnerOfferPriceDeclarationRecord)
            .where(PartnerOfferPriceDeclarationRecord.id == command.declaration_id)
            .values(amount_as_declared="0")
        )
        session.commit()
    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.delete(PartnerOfferPriceDeclarationRecord).where(
                PartnerOfferPriceDeclarationRecord.id == command.declaration_id
            )
        )
        session.commit()


def test_postgres_rejects_price_linked_to_a_superseded_partner_receipt(
    database_engine, session_factory
):
    tenant_id, case_id, actor, _service = _seed(database_engine, session_factory)
    old_receipt_id, partner_id = _received(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor
    )
    _received(
        database_engine,
        tenant_id=tenant_id,
        case_id=case_id,
        actor=actor,
        partner_id=partner_id,
        revision=2,
    )

    with (
        pytest.raises(DBAPIError, match="latest received version"),
        Session(database_engine) as session,
    ):
        session.add(
            PartnerOfferPriceDeclarationRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=case_id,
                receipt_event_id=old_receipt_id,
                revision=1,
                amount_as_declared="100",
                currency_code="EUR",
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=actor.correlation_id,
            )
        )
        session.commit()


def test_http_price_projection_is_patron_only_and_contains_only_the_declared_value(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    receipt_id, _ = _received(database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor)

    class Resolver:
        current_actor = actor

        def resolve(self, *, access_token: str):
            assert access_token == "test"
            return self.current_actor

    resolver = Resolver()
    app = FastAPI()
    app.include_router(
        build_patron_partner_offer_prices_router(
            service=service,
            security_runtime=SimpleNamespace(context_resolver=resolver),
        )
    )
    client = TestClient(app)
    headers = {"Authorization": "Bearer test"}
    path = f"/api/v1/patron/cases/{case_id}/partner-offer-prices"
    unknown = client.get(path, headers=headers)
    assert unknown.status_code == 200
    assert unknown.json()["offers"][0]["price_state"] == "UNKNOWN"
    assert "amount_as_declared" not in unknown.text

    body = {
        "command_id": str(uuid4()),
        "idempotency_key": str(uuid4()),
        "declaration_id": str(uuid4()),
        "expected_revision": 0,
        "amount_as_declared": "1234,50",
        "currency_code": "MAD",
    }
    declared = client.post(f"{path}/{receipt_id}/declarations", headers=headers, json=body)
    assert declared.status_code == 201
    visible = client.get(path, headers=headers)
    assert visible.status_code == 200
    assert visible.json()["offers"][0]["price_state"] == "DECLARED"
    assert visible.json()["offers"][0]["declarations"][0]["amount_as_declared"] == "1234,50"

    resolver.current_actor = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    forbidden = client.get(path, headers=headers)
    assert forbidden.status_code == 403
    assert "1234,50" not in forbidden.text
