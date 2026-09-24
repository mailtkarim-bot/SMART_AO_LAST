from uuid import uuid4

import pytest
from app.modules.dce.domain.contract_baseline import (
    ContractAssessmentStatus,
    ContractBaselineDeviationImpact,
)


def _proof(**overrides):
    values = {
        "case_id": uuid4(),
        "baseline_observation_id": uuid4(),
        "baseline_source_refs": ("dce://ccap/page-4",),
        "baseline_statement": "Le délai est indiqué dans le CCAP.",
        "deviation_statement": "Le CCAP déroge au document de référence.",
        "impact_statement": "Revue humaine du délai et de la planification requise.",
    }
    values.update(overrides)
    return ContractBaselineDeviationImpact(**values)


def test_baseline_deviation_impact_chain_is_source_bound_and_valid() -> None:
    proof = _proof(status=ContractAssessmentStatus.CONFIRMED)
    proof.validate()


@pytest.mark.parametrize(
    "overrides, error",
    [
        ({"baseline_source_refs": ()}, "BASELINE_SOURCE_REQUIRED"),
        ({"baseline_statement": "  "}, "BASELINE_STATEMENT_REQUIRED"),
        (
            {"status": ContractAssessmentStatus.CONFIRMED, "impact_statement": None},
            "CONFIRMED_CHAIN_INCOMPLETE",
        ),
    ],
)
def test_invalid_or_incomplete_chain_is_rejected(overrides, error) -> None:
    with pytest.raises(ValueError, match=error):
        _proof(**overrides).validate()


def test_source_signal_does_not_require_or_infer_legal_conclusion() -> None:
    proof = _proof(
        deviation_statement=None,
        impact_statement=None,
        status=ContractAssessmentStatus.SOURCE_SIGNAL_ONLY,
    )
    proof.validate()
