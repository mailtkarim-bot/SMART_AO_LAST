from uuid import uuid4

import pytest
from pydantic import ValidationError


def test_payment_fact_has_a_closed_kind_and_exact_amount_currency_and_consent():
    from app.modules.pricing.public.case_closure_contracts import RecordPaymentFactRequest

    body = dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correlation_id=uuid4(),
        fact_id=uuid4(),
        cycle_id=uuid4(),
        kind="COLLECTION_RECORDED",
        amount_minor=60000,
        currency_code="EUR",
        declared_date="2026-10-25",
        source_refs=["bank-statement://synthetic/1"],
        evidence_refs=["document://synthetic/1"],
        justification="Constat humain déclaré, aucune banque connectée.",
        human_confirmed=True,
        expected_dossier_sha256="a" * 64,
    )
    assert RecordPaymentFactRequest.model_validate(body).kind == "COLLECTION_RECORDED"
    patches: list[dict[str, object]] = [
        dict(kind="PAID_AUTOMATICALLY"),
        dict(amount_minor=True),
        dict(amount_minor=-1),
        dict(currency_code="EURO"),
        dict(human_confirmed=False),
    ]
    for patch in patches:
        with pytest.raises(ValidationError):
            RecordPaymentFactRequest.model_validate({**body, **patch})


def test_expected_payment_never_becomes_collected_and_partial_difference_is_not_a_balance():
    from app.modules.pricing.application.case_closure_projection import financial_observations

    expected = {
        "fact_id": "expected",
        "kind": "PAYMENT_EXPECTED",
        "amount_minor": 100000,
        "currency_code": "EUR",
        "compared_to_fact_id": None,
    }
    before = financial_observations([expected])
    assert before["collection_state"] == "UNKNOWN" and before["settlement_state"] == "UNKNOWN"
    actual = {
        "fact_id": "actual",
        "kind": "COLLECTION_RECORDED",
        "amount_minor": 60000,
        "currency_code": "EUR",
        "compared_to_fact_id": "expected",
    }
    after = financial_observations([expected, actual])
    assert after["comparisons"][0]["difference_minor"] == -40000
    assert after["settlement_state"] == "UNKNOWN"


def test_closure_review_requires_exact_sources_and_explicit_unknowns():
    from app.modules.pricing.public.case_closure_contracts import ClosureActReview

    body = dict(
        human_confirmed=True,
        justification="Revue de sortie déclarée.",
        expected_dossier_sha256="b" * 64,
        responsible="Conducteur synthétique",
        expected_evidence="PV signé",
        acknowledged_open_obligation_ids=[],
        comparisons=[],
    )
    assert ClosureActReview.model_validate(body).comparisons == []
    with pytest.raises(ValidationError):
        ClosureActReview.model_validate(
            {
                **body,
                "comparisons": [
                    {
                        "expected": {"kind": "ACT", "record_id": uuid4(), "sha256": "bad"},
                        "actual": {"kind": "ACT", "record_id": uuid4(), "sha256": "c" * 64},
                        "note": "Lecture humaine",
                    }
                ],
            }
        )


def test_changed_provenance_is_never_presented_as_a_current_payment_difference():
    from app.modules.pricing.application.case_closure_projection import financial_observations

    base = dict(currency_code="EUR", amount_minor=100, context_state="CURRENT")
    expected = {**base, "fact_id": "e", "kind": "PAYMENT_EXPECTED", "compared_to_fact_id": None}
    actual = {
        **base,
        "fact_id": "a",
        "kind": "COLLECTION_RECORDED",
        "compared_to_fact_id": "e",
        "context_state": "REVIEW_REQUIRED",
    }
    comparison = financial_observations([expected, actual])["comparisons"][0]
    assert (
        comparison["difference_minor"] is None and comparison["source_state"] == "REVIEW_REQUIRED"
    )


def test_closure_money_requires_financial_capability_even_for_patron():
    from dataclasses import replace
    from datetime import UTC, datetime

    from app.modules.pricing.application.case_closure import CaseClosureService
    from app.platform.security.authorization import AuthorizationPolicy
    from app.platform.security.capabilities import Capability

    from tests.db.test_regulatory_profile_persistence import _actor

    now = datetime.now(UTC)
    actor = replace(_actor(uuid4(), uuid4()), authenticated_at=now, mfa_verified_at=now)
    actor = replace(
        actor,
        capabilities=actor.capabilities
        - {Capability.PRICING_READ.value, Capability.PRICING_WRITE.value},
    )
    service = CaseClosureService(reader=None, dispatcher=None, policy=AuthorizationPolicy())
    for write in (False, True):
        with pytest.raises(PermissionError):
            service._authorize(actor, uuid4(), now, write)
