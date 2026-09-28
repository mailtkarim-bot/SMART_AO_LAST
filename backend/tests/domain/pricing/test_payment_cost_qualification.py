# ruff: noqa: E501, I001
from uuid import uuid4
import pytest
from app.modules.pricing.domain.payment_post_reception_cycle import build_external_payment_signal, build_payment_cost_qualification

def test_qualification_carries_prudent_hypothesis_without_cash_certainty():
    qualification = build_payment_cost_qualification(cash_assumption="Délai prudent 75 jours", post_reception_cost_note="Levée de réserves à chiffrer")
    assert qualification.cash_assumption == "Délai prudent 75 jours"
    assert qualification.post_reception_cost_note == "Levée de réserves à chiffrer"

def test_external_signal_cycle_stays_source_signal_only_after_qualification():
    cycle = build_external_payment_signal(case_id=uuid4(), source_refs=("external://payment/1",), trigger_event="EXTERNAL_PAYMENT_SIGNAL", post_reception_cost_note="GPA initiale")
    qualification = build_payment_cost_qualification(cash_assumption=None, post_reception_cost_note="GPA initiale")
    assert cycle.status.value == "SOURCE_SIGNAL_ONLY"
    assert qualification.cash_assumption is None

def test_qualification_rejects_blank_cash_assumption():
    with pytest.raises(ValueError, match="CASH_ASSUMPTION_NON_EMPTY"):
        build_payment_cost_qualification(cash_assumption="  ", post_reception_cost_note=None)

def test_qualification_rejects_blank_cost_note():
    with pytest.raises(ValueError, match="POST_RECEPTION_COST_NOTE_NON_EMPTY"):
        build_payment_cost_qualification(cash_assumption="Délai prudent", post_reception_cost_note=" ")
