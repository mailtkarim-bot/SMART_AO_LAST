from dataclasses import replace
from datetime import date
from uuid import uuid4

import pytest
from app.modules.partner.domain.events import (
    PartnerReceipt,
    build_partner_receipt,
    build_partner_request,
    validate_partner_engagement,
)


def test_request_is_only_a_human_declaration_and_keeps_source():
    request = build_partner_request(
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="dce://target/cctp/lot-01",
        rationale="Demande de disponibilité déclarée par le Patron.",
    )
    assert request.partner_kind == "SUPPLIER"
    assert request.source_locator == "dce://target/cctp/lot-01"
    assert request.external_dispatch_performed is False


def test_receipt_keeps_unknown_validity_and_exclusions_distinct_from_none():
    unknown = build_partner_receipt(
        receipt_id=uuid4(),
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="mail://offer/1",
        rationale="Offre reçue.",
        valid_until=None,
        exclusions_state="UNKNOWN",
        exclusions=(),
        mandate_state="NOT_APPLICABLE",
        mandate_source_locator=None,
    )
    declared_none = build_partner_receipt(
        receipt_id=uuid4(),
        partner_kind="SUPPLIER",
        partner_label="Fournisseur déclaré",
        source_locator="mail://offer/2",
        rationale="Offre révisée reçue.",
        valid_until=date(2027, 3, 30),
        exclusions_state="DECLARED",
        exclusions=(),
        mandate_state="NOT_APPLICABLE",
        mandate_source_locator=None,
    )
    assert unknown.validity(date(2026, 9, 30)) == "UNKNOWN"
    assert declared_none.validity(date(2027, 4, 1)) == "EXPIRED"
    assert declared_none.exclusions_state == "DECLARED"
    assert unknown.exclusions_state == "UNKNOWN"


def test_cotraitant_engagement_requires_a_received_sourced_mandate():
    receipt = _cotraitant_receipt(mandate_state="REQUESTED", mandate_source_locator=None)
    with pytest.raises(ValueError, match="PARTNER_MANDATE_NOT_RECEIVED"):
        validate_partner_engagement(
            receipt=receipt, source_locator="agreement://signed/1", rationale="Revue"
        )

    receipt = _cotraitant_receipt(
        mandate_state="RECEIVED", mandate_source_locator="mandate://signed/1"
    )
    engagement = validate_partner_engagement(
        receipt=receipt,
        source_locator="agreement://signed/1",
        rationale="Engagement déclaré par le Patron après réception des pièces.",
    )
    assert engagement.source_receipt_id == receipt.receipt_id
    assert engagement.legal_validity_assessed is False

    with pytest.raises(ValueError, match="COTRAITANT_MANDATE_STATE_REQUIRED"):
        build_partner_receipt(
            receipt_id=uuid4(),
            partner_kind="CO_CONTRACTOR",
            partner_label="Groupement déclaré",
            source_locator="mail://offer/groupement",
            rationale="Offre reçue.",
            valid_until=None,
            exclusions_state="UNKNOWN",
            exclusions=(),
            mandate_state="NOT_APPLICABLE",
            mandate_source_locator=None,
        )


def test_engagement_requires_a_receipt_and_human_evidence():
    receipt = _cotraitant_receipt(
        mandate_state="RECEIVED", mandate_source_locator="mandate://signed/1"
    )
    wrong_event = replace(receipt, event_type="REQUESTED")
    with pytest.raises(ValueError, match="PARTNER_RECEIPT_REQUIRED"):
        validate_partner_engagement(
            receipt=wrong_event, source_locator="agreement://signed/1", rationale="Motif"
        )
    with pytest.raises(ValueError, match="PARTNER_ENGAGEMENT_SOURCE_REQUIRED"):
        validate_partner_engagement(receipt=receipt, source_locator=" ", rationale="Motif")
    with pytest.raises(ValueError, match="PARTNER_ENGAGEMENT_RATIONALE_REQUIRED"):
        validate_partner_engagement(
            receipt=receipt, source_locator="agreement://signed/1", rationale=" "
        )


def _cotraitant_receipt(*, mandate_state, mandate_source_locator) -> PartnerReceipt:
    return build_partner_receipt(
        receipt_id=uuid4(),
        partner_kind="CO_CONTRACTOR",
        partner_label="Groupement déclaré",
        source_locator="mail://offer/groupement",
        rationale="Offre reçue.",
        valid_until=None,
        exclusions_state="UNKNOWN",
        exclusions=(),
        mandate_state=mandate_state,
        mandate_source_locator=mandate_source_locator,
    )
