from uuid import uuid4

import pytest
from app.modules.pricing.domain.partner_offer_scope_review import (
    PartnerOfferScopeFact,
    build_partner_offer_scope_review,
)


def _fact(
    receipt_event_id,
    *,
    inclusion_state="DECLARED",
    exclusions_review_state="REVIEWED",
    transport_state="INCLUDED",
):
    return PartnerOfferScopeFact(
        receipt_event_id=receipt_event_id,
        inclusion_state=inclusion_state,
        included_scope_note=(
            "Terrassement et évacuation inclus." if inclusion_state == "DECLARED" else None
        ),
        exclusions_review_state=exclusions_review_state,
        transport_state=transport_state,
        transport_note=("Transport au site inclus." if transport_state != "UNKNOWN" else None),
    )


def test_scope_review_records_same_scope_as_a_human_act():
    receipt_ids = (uuid4(), uuid4())
    review = build_partner_offer_scope_review(
        comparison_id=uuid4(),
        decision="SAME_SCOPE_CONFIRMED",
        rationale="Les périmètres ont été relus contre les sources des deux offres.",
        offers=tuple(_fact(receipt_id) for receipt_id in receipt_ids),
    )
    assert review.decision == "SAME_SCOPE_CONFIRMED"
    assert tuple(offer.receipt_event_id for offer in review.offers) == receipt_ids


def test_same_scope_is_refused_when_inclusions_exclusions_review_or_transport_are_unknown():
    facts = (
        _fact(uuid4()),
        _fact(uuid4(), inclusion_state="UNKNOWN", transport_state="UNKNOWN"),
    )
    with pytest.raises(ValueError, match="PARTNER_SCOPE_REVIEW_INCOMPLETE"):
        build_partner_offer_scope_review(
            comparison_id=uuid4(),
            decision="SAME_SCOPE_CONFIRMED",
            rationale="Revue partielle.",
            offers=facts,
        )


def test_same_scope_is_refused_until_each_source_exclusion_list_is_reviewed():
    facts = (_fact(uuid4()), _fact(uuid4(), exclusions_review_state="UNKNOWN"))
    with pytest.raises(ValueError, match="PARTNER_SCOPE_REVIEW_INCOMPLETE"):
        build_partner_offer_scope_review(
            comparison_id=uuid4(),
            decision="SAME_SCOPE_CONFIRMED",
            rationale="Une liste d’exclusions n’a pas été relue.",
            offers=facts,
        )


@pytest.mark.parametrize("decision", ["DIFFERENT_SCOPE", "NEEDS_CLARIFICATION"])
def test_unresolved_scope_facts_remain_unknown(decision):
    facts = (
        _fact(uuid4(), inclusion_state="UNKNOWN", transport_state="UNKNOWN"),
        _fact(uuid4()),
    )
    review = build_partner_offer_scope_review(
        comparison_id=uuid4(),
        decision=decision,
        rationale="Un élément reste à confirmer.",
        offers=facts,
    )
    assert review.offers[0].inclusion_state == "UNKNOWN"
    assert review.offers[0].transport_state == "UNKNOWN"


@pytest.mark.parametrize(
    ("offers", "decision", "rationale", "error"),
    [
        ((), "NEEDS_CLARIFICATION", "Revue", "PARTNER_SCOPE_REVIEW_MINIMUM_OFFERS"),
        ((_fact(uuid4()),), "NEEDS_CLARIFICATION", "Revue", "PARTNER_SCOPE_REVIEW_MINIMUM_OFFERS"),
        ("duplicate", "DIFFERENT_SCOPE", "Motif", "PARTNER_SCOPE_REVIEW_DUPLICATE_RECEIPT"),
        (
            (_fact(uuid4()), _fact(uuid4())),
            "OPEN",
            "Motif",
            "PARTNER_SCOPE_REVIEW_DECISION_UNKNOWN",
        ),
        (
            (_fact(uuid4()), _fact(uuid4())),
            "DIFFERENT_SCOPE",
            " ",
            "PARTNER_SCOPE_REVIEW_RATIONALE_REQUIRED",
        ),
    ],
)
def test_scope_review_rejects_invalid_contract(offers, decision, rationale, error):
    if offers == "duplicate":
        receipt_id = uuid4()
        offers = (_fact(receipt_id), _fact(receipt_id))
    with pytest.raises(ValueError, match=error):
        build_partner_offer_scope_review(
            comparison_id=uuid4(),
            decision=decision,
            rationale=rationale,
            offers=offers,
        )
