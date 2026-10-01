from dataclasses import replace
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.patron_partner_offer_scope_reviews import (
    build_patron_partner_offer_scope_reviews_router,
)
from app.modules.partner.infrastructure.models.partner_event import CasePartnerEventRecord
from app.modules.pricing.application.partner_offer_scope_review_commands import (
    PartnerOfferScopeReviewOfferCommand,
    RecordPartnerOfferScopeReviewCommand,
)
from app.modules.pricing.application.partner_offer_scope_review_handler import (
    PartnerOfferScopeReviewService,
    partner_offer_scope_review_handlers,
)
from app.modules.pricing.infrastructure.models.partner_offer_scope_review import (
    PartnerOfferScopeReviewOfferRecord,
    PartnerOfferScopeReviewRecord,
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
            TenantRecord(id=tenant_id, slug=f"osr-{tenant_id.hex[:10]}", lifecycle="ACTIVE")
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
        handlers=partner_offer_scope_review_handlers(),
    )
    service = PartnerOfferScopeReviewService(
        dispatcher=dispatcher,
        session_factory=session_factory,
        policy=AuthorizationPolicy(),
    )
    return tenant_id, case_id, actor, service


def _receipt(
    database_engine,
    *,
    tenant_id,
    case_id,
    actor,
    label,
    partner_id=None,
    revision=1,
    exclusions_state="DECLARED",
):
    event_id, partner_id = uuid4(), partner_id or uuid4()
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
                partner_label=label,
                related_event_id=None,
                source_locator=f"offre://{label}/v{revision}",
                rationale=f"Périmètre déclaré {label}.",
                valid_until=None,
                validity_at_recording="UNKNOWN",
                exclusions_state=exclusions_state,
                exclusions_json=[] if exclusions_state == "UNKNOWN" else ["Dépose des déchets"],
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


def _offer(
    receipt_event_id,
    *,
    inclusion_state="DECLARED",
    exclusions_review_state="REVIEWED",
    transport_state="INCLUDED",
):
    return PartnerOfferScopeReviewOfferCommand(
        receipt_event_id=receipt_event_id,
        inclusion_state=inclusion_state,
        included_scope_note="Terrassement du lot 7 inclus."
        if inclusion_state == "DECLARED"
        else None,
        exclusions_review_state=exclusions_review_state,
        transport_state=transport_state,
        transport_note="Transport au site inclus." if transport_state != "UNKNOWN" else None,
    )


def _command(
    case_id,
    comparison_id,
    receipt_ids,
    *,
    expected_revision=0,
    decision="SAME_SCOPE_CONFIRMED",
    offers=None,
):
    return RecordPartnerOfferScopeReviewCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        review_id=uuid4(),
        comparison_id=comparison_id,
        case_id=case_id,
        expected_revision=expected_revision,
        decision=decision,
        rationale="Le Patron a comparé les portées contre les reçus sources.",
        offers=tuple(offers or (_offer(receipt_id) for receipt_id in receipt_ids)),
    )


def test_same_scope_review_is_patron_only_append_only_and_idempotent(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    command = _command(case_id, uuid4(), (first_id, second_id))

    first = service.record(actor=actor, command=command, now=NOW)
    replay = service.record(actor=actor, command=command, now=NOW)
    assert first.result_code == "PARTNER_SCOPE_REVIEW_RECORDED"
    assert replay.replayed is True
    projected = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    review = projected.reviews[0]
    assert review.decision == "SAME_SCOPE_CONFIRMED"
    assert review.revision == 1
    assert {offer.receipt_event_id for offer in review.offers} == {first_id, second_id}
    assert all(offer.exclusions_state == "DECLARED" for offer in review.offers)
    assert all(offer.exclusions_review_state == "REVIEWED" for offer in review.offers)
    assert all(offer.receipt_is_current for offer in review.offers)
    assert all(not hasattr(offer, "amount_as_declared") for offer in review.offers)

    collaborator = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    with pytest.raises(PermissionError):
        service.list_for_case(actor=collaborator, case_id=case_id, now=NOW)
    with pytest.raises(PermissionError):
        service.record(actor=collaborator, command=command, now=NOW)


def test_unknown_or_different_scope_remains_explicit_and_cannot_be_called_same(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine,
        tenant_id=tenant_id,
        case_id=case_id,
        actor=actor,
        label="A",
        exclusions_state="UNKNOWN",
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    same_scope = _command(case_id, uuid4(), (first_id, second_id))
    with pytest.raises(CommandExecutionError, match="PARTNER_SCOPE_REVIEW_EXCLUSIONS_UNKNOWN"):
        service.record(actor=actor, command=same_scope, now=NOW)

    false_exclusion_ack = _command(
        case_id,
        uuid4(),
        (first_id, second_id),
        decision="NEEDS_CLARIFICATION",
        offers=(
            _offer(first_id, exclusions_review_state="REVIEWED"),
            _offer(second_id),
        ),
    )
    with pytest.raises(CommandExecutionError, match="PARTNER_SCOPE_REVIEW_EXCLUSIONS_UNKNOWN"):
        service.record(actor=actor, command=false_exclusion_ack, now=NOW)

    unresolved = _command(
        case_id,
        uuid4(),
        (first_id, second_id),
        decision="NEEDS_CLARIFICATION",
        offers=(
            _offer(
                first_id,
                inclusion_state="UNKNOWN",
                exclusions_review_state="UNKNOWN",
                transport_state="UNKNOWN",
            ),
            _offer(second_id),
        ),
    )
    service.record(actor=actor, command=unresolved, now=NOW)
    projection = service.list_for_case(actor=actor, case_id=case_id, now=NOW).reviews[0]
    assert projection.decision == "NEEDS_CLARIFICATION"
    unknown_offer = next(offer for offer in projection.offers if offer.receipt_event_id == first_id)
    assert unknown_offer.inclusion_state == "UNKNOWN"
    assert unknown_offer.exclusions_review_state == "UNKNOWN"
    assert unknown_offer.transport_state == "UNKNOWN"


def test_foreign_tenant_receipts_and_cases_are_not_observable_or_reviewable(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    own_receipt_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )

    foreign_tenant_id, foreign_case_id = uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(
                id=foreign_tenant_id,
                slug=f"osr-foreign-{foreign_tenant_id.hex[:8]}",
                lifecycle="ACTIVE",
            )
        )
        session.flush()
        session.add(_case(tenant_id=foreign_tenant_id, case_id=foreign_case_id, marker="f"))
        session.commit()
    foreign_receipt_id, _ = _receipt(
        database_engine,
        tenant_id=foreign_tenant_id,
        case_id=foreign_case_id,
        actor=actor,
        label="Foreign",
    )

    projection = service.list_for_case(actor=actor, case_id=foreign_case_id, now=NOW)
    assert projection.reviews == ()

    foreign_receipt_review = _command(
        case_id, uuid4(), (own_receipt_id, foreign_receipt_id)
    )
    with pytest.raises(CommandExecutionError, match="PARTNER_RECEIPT_NOT_FOUND_OR_FORBIDDEN"):
        service.record(actor=actor, command=foreign_receipt_review, now=NOW)

    foreign_case_review = _command(foreign_case_id, uuid4(), (own_receipt_id, foreign_receipt_id))
    with pytest.raises(CommandExecutionError, match="CASE_NOT_FOUND_OR_FORBIDDEN"):
        service.record(actor=actor, command=foreign_case_review, now=NOW)


def test_comparison_revisions_keep_membership_and_append_prior_review(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    first_id, first_partner = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    third_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="C"
    )
    comparison_id = uuid4()
    first = _command(case_id, comparison_id, (first_id, second_id), decision="NEEDS_CLARIFICATION")
    service.record(actor=actor, command=first, now=NOW)

    revised = _command(
        case_id,
        comparison_id,
        (first_id, second_id),
        expected_revision=1,
        decision="DIFFERENT_SCOPE",
    )
    service.record(actor=actor, command=revised, now=NOW)
    projection = service.list_for_case(actor=actor, case_id=case_id, now=NOW)
    matching = [review for review in projection.reviews if review.comparison_id == comparison_id]
    assert [review.revision for review in matching] == [1, 2]
    assert matching[0].decision == "NEEDS_CLARIFICATION"
    assert matching[1].decision == "DIFFERENT_SCOPE"

    changed_members = _command(
        case_id,
        comparison_id,
        (first_id, third_id),
        expected_revision=2,
        decision="DIFFERENT_SCOPE",
    )
    with pytest.raises(CommandExecutionError, match="PARTNER_SCOPE_REVIEW_MEMBER_SET_CONFLICT"):
        service.record(actor=actor, command=changed_members, now=NOW)

    _receipt(
        database_engine,
        tenant_id=tenant_id,
        case_id=case_id,
        actor=actor,
        label="A",
        partner_id=first_partner,
        revision=3,
    )
    stale_review = service.list_for_case(actor=actor, case_id=case_id, now=NOW).reviews[0]
    stale_a = next(offer for offer in stale_review.offers if offer.partner_id == first_partner)
    assert stale_a.receipt_is_current is False
    assert stale_review.decision == "NEEDS_CLARIFICATION"


def test_postgres_append_only_and_deferred_same_scope_validation(database_engine, session_factory):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )
    command = _command(case_id, uuid4(), (first_id, second_id))
    service.record(actor=actor, command=command, now=NOW)

    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.update(PartnerOfferScopeReviewRecord)
            .where(PartnerOfferScopeReviewRecord.id == command.review_id)
            .values(decision="DIFFERENT_SCOPE")
        )
        session.commit()

    unknown_exclusions_id, _ = _receipt(
        database_engine,
        tenant_id=tenant_id,
        case_id=case_id,
        actor=actor,
        label="Unknown exclusions",
        exclusions_state="UNKNOWN",
    )
    invalid_ack = _command(
        case_id,
        uuid4(),
        (unknown_exclusions_id, second_id),
        decision="NEEDS_CLARIFICATION",
        offers=(
            _offer(unknown_exclusions_id, exclusions_review_state="REVIEWED"),
            _offer(second_id),
        ),
    )
    with (
        pytest.raises(DBAPIError, match="reviewed exclusions require a declared source"),
        Session(database_engine) as session,
    ):
        session.add(
            PartnerOfferScopeReviewRecord(
                id=invalid_ack.review_id,
                tenant_id=tenant_id,
                case_id=case_id,
                comparison_id=invalid_ack.comparison_id,
                revision=1,
                decision=invalid_ack.decision,
                rationale=invalid_ack.rationale,
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=invalid_ack.command_id,
                idempotency_key=invalid_ack.idempotency_key,
                correlation_id=actor.correlation_id,
            )
        )
        session.flush()
        session.add_all(
            PartnerOfferScopeReviewOfferRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=case_id,
                review_id=invalid_ack.review_id,
                receipt_event_id=offer.receipt_event_id,
                inclusion_state=offer.inclusion_state,
                included_scope_note=offer.included_scope_note,
                exclusions_review_state=offer.exclusions_review_state,
                transport_state=offer.transport_state,
                transport_note=offer.transport_note,
            )
            for offer in invalid_ack.offers
        )
        session.commit()
    with pytest.raises(DBAPIError, match="append-only"), Session(database_engine) as session:
        session.execute(
            sa.delete(PartnerOfferScopeReviewOfferRecord).where(
                PartnerOfferScopeReviewOfferRecord.review_id == command.review_id
            )
        )
        session.commit()

    invalid = _command(
        case_id,
        uuid4(),
        (first_id, second_id),
        offers=(_offer(first_id, inclusion_state="UNKNOWN"), _offer(second_id)),
    )
    with (
        pytest.raises(DBAPIError, match="reviewed exclusions"),
        Session(database_engine) as session,
    ):
        session.add(
            PartnerOfferScopeReviewRecord(
                id=invalid.review_id,
                tenant_id=tenant_id,
                case_id=case_id,
                comparison_id=invalid.comparison_id,
                revision=1,
                decision="SAME_SCOPE_CONFIRMED",
                rationale=invalid.rationale,
                actor_id=actor.actor_id,
                membership_id=actor.membership_id,
                command_id=invalid.command_id,
                idempotency_key=invalid.idempotency_key,
                correlation_id=actor.correlation_id,
            )
        )
        session.flush()
        session.add_all(
            PartnerOfferScopeReviewOfferRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                case_id=case_id,
                review_id=invalid.review_id,
                receipt_event_id=offer.receipt_event_id,
                inclusion_state=offer.inclusion_state,
                included_scope_note=offer.included_scope_note,
                exclusions_review_state=offer.exclusions_review_state,
                transport_state=offer.transport_state,
                transport_note=offer.transport_note,
            )
            for offer in invalid.offers
        )
        session.commit()


def test_http_scope_review_reuses_command_on_retry_and_keeps_unknowns(
    database_engine, session_factory
):
    tenant_id, case_id, actor, service = _seed(database_engine, session_factory)
    first_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="A"
    )
    second_id, _ = _receipt(
        database_engine, tenant_id=tenant_id, case_id=case_id, actor=actor, label="B"
    )

    class Resolver:
        current_actor = actor

        def resolve(self, *, access_token: str):
            assert access_token == "test"
            return self.current_actor

    resolver = Resolver()
    app = FastAPI()
    app.include_router(
        build_patron_partner_offer_scope_reviews_router(
            service=service,
            security_runtime=SimpleNamespace(context_resolver=resolver),
        )
    )
    client = TestClient(app)
    path = f"/api/v1/patron/cases/{case_id}/partner-offer-scope-reviews"
    headers = {"Authorization": "Bearer test"}
    command = _command(
        case_id,
        uuid4(),
        (first_id, second_id),
        decision="NEEDS_CLARIFICATION",
        offers=(
            _offer(first_id, inclusion_state="UNKNOWN", transport_state="UNKNOWN"),
            _offer(second_id),
        ),
    )
    body = command.model_dump(mode="json", exclude={"case_id"})
    first = client.post(path, headers=headers, json=body)
    replay = client.post(path, headers=headers, json=body)
    assert first.status_code == 201
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    result = client.get(path, headers=headers)
    assert result.status_code == 200
    assert result.json()["reviews"][0]["decision"] == "NEEDS_CLARIFICATION"
    unknown_review_offer = next(
        offer
        for offer in result.json()["reviews"][0]["offers"]
        if offer["receipt_event_id"] == str(first_id)
    )
    assert unknown_review_offer["transport_state"] == "UNKNOWN"
    assert "amount_as_declared" not in result.text

    resolver.current_actor = replace(
        actor,
        actor_kind=ActorKind.COLLABORATEUR,
        capabilities=capabilities_for(ActorKind.COLLABORATEUR),
    )
    denied = client.get(path, headers=headers)
    assert denied.status_code == 403
    assert "NEEDS_CLARIFICATION" not in denied.text
