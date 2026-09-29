# ruff: noqa: I001
from datetime import date
from uuid import uuid4

import pytest

from app.modules.pricing.domain.post_reception_obligation import (
    PostReceptionObligationType,
    build_post_reception_obligation,
)


def test_builds_sourced_review_required_obligation_without_claiming_completion() -> None:
    obligation = build_post_reception_obligation(
        case_id=uuid4(),
        obligation_type=PostReceptionObligationType.DOE_DIUO,
        summary="Remettre le DOE au maître d’ouvrage",
        source_refs=("ccap://clause/12",),
        due_date=date(2027, 3, 31),
        resource_note="Conducteur travaux",
        cost_estimate_note="À chiffrer",
        fulfillment_proof_refs=(),
        sanction_ref="ccap://clause/18",
    )

    assert obligation.status == "REVIEW_REQUIRED"
    assert obligation.source_refs == ("ccap://clause/12",)
    assert obligation.fulfillment_proof_refs == ()


def test_reserve_lifting_requires_a_source_reception_act() -> None:
    with pytest.raises(ValueError, match="POST_RECEPTION_RECEIPT_SOURCE_REQUIRED"):
        build_post_reception_obligation(
            case_id=uuid4(),
            obligation_type=PostReceptionObligationType.RESERVES_LIFTING,
            summary="Lever les réserves déclarées",
            source_refs=("ccap://clause/24",),
        )


@pytest.mark.parametrize(
    ("summary", "source_refs", "error"),
    [
        ("   ", ("ccap://clause/12",), "POST_RECEPTION_OBLIGATION_SUMMARY_REQUIRED"),
        ("Lever les réserves", (), "POST_RECEPTION_OBLIGATION_SOURCE_REQUIRED"),
    ],
)
def test_rejects_obligation_without_summary_or_source(summary, source_refs, error) -> None:
    with pytest.raises(ValueError, match=error):
        build_post_reception_obligation(
            case_id=uuid4(),
            obligation_type=PostReceptionObligationType.RESERVES_LIFTING,
            summary=summary,
            source_refs=source_refs,
        )
