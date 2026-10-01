from dataclasses import replace
from uuid import uuid4

import pytest
from app.modules.pricing.domain.partner_offer_line_comparison import (
    PartnerOfferLineGroup,
    PartnerOfferLineMember,
    build_partner_offer_line_comparison,
)


def _member(receipt_event_id, *, state="DECLARED", value=""):
    return PartnerOfferLineMember(
        receipt_event_id=receipt_event_id,
        line_locator_state="UNKNOWN" if state == "UNKNOWN" else "DECLARED",
        line_locator=None if state == "UNKNOWN" else "Feuille BPU, ligne 14",
        item_reference_state="UNKNOWN" if state == "UNKNOWN" else "DECLARED",
        item_reference=None if state == "UNKNOWN" else value or "LOT-04-A",
        designation_state="UNKNOWN" if state == "UNKNOWN" else "DECLARED",
        designation=None if state == "UNKNOWN" else "Terrassement en pleine masse",
        unit_state="UNKNOWN" if state == "UNKNOWN" else "DECLARED",
        unit=None if state == "UNKNOWN" else "m3",
        quantity_state="UNKNOWN" if state == "UNKNOWN" else "DECLARED",
        quantity=None if state == "UNKNOWN" else "1 250,00",
    )


def _group(*members, disposition="NEEDS_CLARIFICATION"):
    return PartnerOfferLineGroup(
        group_id=uuid4(),
        disposition=disposition,
        rationale="Rapprochement déclaré par le Patron, à contrôler dans les sources.",
        members=tuple(members),
    )


def test_comparison_preserves_raw_source_fields_and_does_not_add_amounts():
    first_id, second_id = uuid4(), uuid4()
    group = _group(
        _member(first_id, value="A-01"),
        _member(second_id, value="B-02"),
        disposition="LINKED_BY_PATRON",
    )
    result = build_partner_offer_line_comparison(
        comparison_id=uuid4(),
        scope_review_id=uuid4(),
        groups=(group,),
    )

    assert result.groups[0].members[0].quantity == "1 250,00"
    assert result.groups[0].members[0].unit == "m3"
    assert result.groups[0].disposition == "LINKED_BY_PATRON"
    assert not hasattr(result.groups[0].members[0], "amount")


def test_unknown_source_line_fields_remain_unknown_without_inference():
    group = _group(
        _member(uuid4(), state="UNKNOWN"),
        _member(uuid4()),
    )
    result = build_partner_offer_line_comparison(
        comparison_id=uuid4(),
        scope_review_id=uuid4(),
        groups=(group,),
    )

    member = result.groups[0].members[0]
    assert member.line_locator_state == "UNKNOWN"
    assert member.item_reference_state == "UNKNOWN"
    assert member.designation_state == "UNKNOWN"
    assert member.unit_state == "UNKNOWN"
    assert member.quantity_state == "UNKNOWN"
    assert member.quantity is None


def test_declared_field_requires_value_and_unknown_field_cannot_hide_value():
    group = _group(_member(uuid4()), _member(uuid4()))
    first = group.members[0]
    invalid = replace(first, quantity_state="DECLARED", quantity=None)
    with pytest.raises(ValueError, match="PARTNER_OFFER_LINE_DECLARED_VALUE_REQUIRED"):
        build_partner_offer_line_comparison(
            comparison_id=uuid4(),
            scope_review_id=uuid4(),
            groups=(_group(invalid, group.members[1]),),
        )

    hidden = replace(first, quantity_state="UNKNOWN")
    with pytest.raises(ValueError, match="PARTNER_OFFER_LINE_UNKNOWN_VALUE_PRESENT"):
        build_partner_offer_line_comparison(
            comparison_id=uuid4(),
            scope_review_id=uuid4(),
            groups=(_group(hidden, group.members[1]),),
        )


def test_groups_require_distinct_receipts_and_a_nonempty_human_reason():
    receipt = uuid4()
    with pytest.raises(ValueError, match="PARTNER_OFFER_LINE_DUPLICATE_RECEIPT"):
        build_partner_offer_line_comparison(
            comparison_id=uuid4(),
            scope_review_id=uuid4(),
            groups=(_group(_member(receipt), _member(receipt)),),
        )

    group = _group(_member(uuid4()), _member(uuid4()))
    with pytest.raises(ValueError, match="PARTNER_OFFER_LINE_RATIONALE_REQUIRED"):
        build_partner_offer_line_comparison(
            comparison_id=uuid4(),
            scope_review_id=uuid4(),
            groups=(PartnerOfferLineGroup(
                group_id=group.group_id,
                disposition=group.disposition,
                rationale=" ",
                members=group.members,
            ),),
        )
