from datetime import date
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

from app.modules.patron_action.public.contracts import RecordCaseTeachingApplicabilityRequest
from app.modules.pricing.public.contract_execution_evidence_contracts import (
    RecordContractExecutionEvidenceRequest,
)
from app.modules.pricing.public.post_reception_obligation_contracts import (
    RecordPostReceptionObligationRequest,
    TransitionPostReceptionObligationRequest,
)

"""Human declarations; no banking or legal conclusion is implied."""


Reference = Annotated[str, Field(min_length=1, max_length=1000)]
PaymentFactKind = Literal["INVOICE_DECLARED", "PAYMENT_EXPECTED", "COLLECTION_RECORDED"]


class RecordPaymentFactRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    fact_id: UUID
    cycle_id: UUID
    kind: PaymentFactKind
    amount_minor: Annotated[int, Field(strict=True, gt=0, le=9_000_000_000_000_000)]
    currency_code: str = Field(pattern=r"^[A-Z]{3}$")
    declared_date: date
    source_refs: tuple[Reference, ...] = Field(min_length=1, max_length=32)
    evidence_refs: tuple[Reference, ...] = Field(min_length=1, max_length=32)
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: StrictBool
    expected_dossier_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    compared_to_fact_id: UUID | None = None

    @model_validator(mode="after")
    def confirmed_declaration(self):
        if not self.human_confirmed:
            raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
        if self.compared_to_fact_id == self.fact_id:
            raise ValueError("PAYMENT_FACT_SELF_REFERENCE")
        if self.kind == "INVOICE_DECLARED" and self.compared_to_fact_id is not None:
            raise ValueError("INVOICE_HAS_NO_EXPECTED_PARENT")
        return self


class ClosureReference(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["ACT", "OBLIGATION", "PAYMENT_FACT", "CHANGE_ACTION"]
    record_id: UUID
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")


class ClosureComparison(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    expected: ClosureReference
    actual: ClosureReference
    note: str = Field(min_length=1, max_length=2000)


class ClosureActReview(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    expected_dossier_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    human_confirmed: StrictBool
    justification: str = Field(min_length=1, max_length=2000)
    responsible: str | None = Field(default=None, min_length=1, max_length=500)
    expected_evidence: str | None = Field(default=None, min_length=1, max_length=2000)
    acknowledged_open_obligation_ids: list[UUID] = Field(default_factory=list, max_length=128)
    comparisons: list[ClosureComparison] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def explicit_review(self):
        if not self.human_confirmed:
            raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
        if len(set(self.acknowledged_open_obligation_ids)) != len(
            self.acknowledged_open_obligation_ids
        ):
            raise ValueError("DUPLICATE_OPEN_OBLIGATION")
        return self


class RecordExecutionRexRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    command_id: UUID
    idempotency_key: UUID
    correlation_id: UUID | None = None
    rex_id: UUID
    exit_act_id: UUID
    publish_to_rex: Literal[True]
    lot_reference: str = Field(min_length=1, max_length=120)
    scope: Literal["CASE_ONLY", "LOT_PATTERN"] = "CASE_ONLY"
    validation: Literal["PENDING", "APPROVED"] = "PENDING"
    observation: str = Field(min_length=1, max_length=2000)
    consequence: str = Field(min_length=1, max_length=2000)
    follow_up: str = Field(min_length=1, max_length=2000)
    source_locator: str = Field(min_length=1, max_length=500)
    human_confirmed: StrictBool
    justification: str = Field(min_length=1, max_length=2000)
    expected_dossier_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def explicit_rex(self):
        from app.modules.membership.public.text_safety import contains_forbidden_text

        if any(
            contains_forbidden_text(getattr(self, field))
            for field in (
                "observation",
                "consequence",
                "follow_up",
                "source_locator",
                "lot_reference",
                "justification",
            )
        ):
            raise ValueError("FINANCIAL_TEXT_NOT_PUBLISHABLE")
        if not self.human_confirmed:
            raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
        return self


class RecordClosureActRequest(RecordContractExecutionEvidenceRequest):
    closure_review: ClosureActReview


class RecordClosureObligationRequest(RecordPostReceptionObligationRequest):
    closure_review: ClosureActReview


class RecordExecutionTeachingReuseRequest(RecordCaseTeachingApplicabilityRequest):
    human_confirmed: StrictBool
    expected_target_dossier_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")

    @model_validator(mode="after")
    def explicit_reuse(self):
        if not self.human_confirmed:
            raise ValueError("HUMAN_CONFIRMATION_REQUIRED")
        return self


class ClosureObligationTransitionRequest(TransitionPostReceptionObligationRequest):
    obligation_id: UUID


class ClosureInterviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    command_id: UUID
    idempotency_key: UUID
    interview_id: UUID
    held_on: date
    expires_on: date
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2000)
