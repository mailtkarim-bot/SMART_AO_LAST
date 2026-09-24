"""Source-bound contract baseline, deviation and operational impact proof."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class ContractAssessmentStatus(StrEnum):
    SOURCE_SIGNAL_ONLY = "SOURCE_SIGNAL_ONLY"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    CONFIRMED = "CONFIRMED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class ContractBaselineDeviationImpact:
    """Smallest auditable chain; it never makes a legal determination."""

    case_id: UUID
    baseline_observation_id: UUID
    baseline_source_refs: tuple[str, ...]
    baseline_statement: str
    deviation_statement: str | None
    impact_statement: str | None
    status: ContractAssessmentStatus = ContractAssessmentStatus.SOURCE_SIGNAL_ONLY

    def validate(self) -> None:
        if not self.baseline_source_refs:
            raise ValueError("BASELINE_SOURCE_REQUIRED")
        if not self.baseline_statement.strip():
            raise ValueError("BASELINE_STATEMENT_REQUIRED")
        if self.deviation_statement is not None and not self.deviation_statement.strip():
            raise ValueError("DEVIATION_STATEMENT_NON_EMPTY")
        if self.impact_statement is not None and not self.impact_statement.strip():
            raise ValueError("IMPACT_STATEMENT_NON_EMPTY")
        if self.status is ContractAssessmentStatus.CONFIRMED and (
            self.deviation_statement is None or self.impact_statement is None
        ):
            raise ValueError("CONFIRMED_CHAIN_INCOMPLETE")
