# ruff: noqa: I001
import pytest

from app.modules.pricing.domain.post_reception_obligation_transition import (
    PostReceptionObligationStatus,
    build_post_reception_obligation_transition,
)


def test_completion_requires_human_supplied_proof_reference() -> None:
    with pytest.raises(ValueError, match="POST_RECEPTION_COMPLETION_PROOF_REQUIRED"):
        build_post_reception_obligation_transition(
            current_status=PostReceptionObligationStatus.IN_PROGRESS,
            resulting_status=PostReceptionObligationStatus.COMPLETED,
            rationale="Réserves levées",
            evidence_refs=(),
        )


def test_completion_is_explicit_and_retains_proof_reference() -> None:
    transition = build_post_reception_obligation_transition(
        current_status=PostReceptionObligationStatus.IN_PROGRESS,
        resulting_status=PostReceptionObligationStatus.COMPLETED,
        rationale="PV de levée contrôlé par le Patron",
        evidence_refs=("document://pv-levee-reserves",),
    )
    assert transition.resulting_status is PostReceptionObligationStatus.COMPLETED
    assert transition.evidence_refs == ("document://pv-levee-reserves",)


def test_completed_obligation_is_terminal_in_initial_lifecycle() -> None:
    with pytest.raises(ValueError, match="POST_RECEPTION_COMPLETED_IS_TERMINAL"):
        build_post_reception_obligation_transition(
            current_status=PostReceptionObligationStatus.COMPLETED,
            resulting_status=PostReceptionObligationStatus.FOLLOW_UP_REQUIRED,
            rationale="Réouverture",
            evidence_refs=(),
        )
