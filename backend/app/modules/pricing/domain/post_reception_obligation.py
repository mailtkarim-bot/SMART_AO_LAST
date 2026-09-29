from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID


class PostReceptionObligationType(StrEnum):
    OPR = "OPR"
    TESTS = "TESTS"
    COMMISSIONING = "COMMISSIONING"
    TRAINING = "TRAINING"
    DOE_DIUO = "DOE_DIUO"
    RESERVES_LIFTING = "RESERVES_LIFTING"
    GPA = "GPA"
    INITIAL_MAINTENANCE = "INITIAL_MAINTENANCE"
    SPARE_STOCK = "SPARE_STOCK"
    ON_CALL = "ON_CALL"
    ADMIN_CLOSURE = "ADMIN_CLOSURE"
    GUARANTEE_RELEASE = "GUARANTEE_RELEASE"


@dataclass(frozen=True, slots=True)
class PostReceptionObligation:
    case_id: UUID
    origin_reception_act_id: UUID | None
    obligation_type: PostReceptionObligationType
    summary: str
    source_refs: tuple[str, ...]
    due_date: date | None = None
    resource_note: str | None = None
    cost_estimate_note: str | None = None
    fulfillment_proof_refs: tuple[str, ...] = ()
    sanction_ref: str | None = None
    status: str = "REVIEW_REQUIRED"

    def validate(self) -> None:
        if not self.summary.strip():
            raise ValueError("POST_RECEPTION_OBLIGATION_SUMMARY_REQUIRED")
        if not self.source_refs or any(not ref.strip() for ref in self.source_refs):
            raise ValueError("POST_RECEPTION_OBLIGATION_SOURCE_REQUIRED")
        for value, error_code in (
            (self.resource_note, "POST_RECEPTION_OBLIGATION_RESOURCE_INVALID"),
            (self.cost_estimate_note, "POST_RECEPTION_OBLIGATION_COST_INVALID"),
            (self.sanction_ref, "POST_RECEPTION_OBLIGATION_SANCTION_REF_INVALID"),
        ):
            if value is not None and not value.strip():
                raise ValueError(error_code)
        if any(not ref.strip() for ref in self.fulfillment_proof_refs):
            raise ValueError("POST_RECEPTION_OBLIGATION_PROOF_REF_INVALID")
        if self.status != "REVIEW_REQUIRED":
            raise ValueError("POST_RECEPTION_OBLIGATION_INITIAL_STATUS_INVALID")
        if self.obligation_type is PostReceptionObligationType.RESERVES_LIFTING:
            if self.origin_reception_act_id is None:
                raise ValueError("POST_RECEPTION_RECEIPT_SOURCE_REQUIRED")
        elif self.origin_reception_act_id is not None:
            raise ValueError("POST_RECEPTION_RECEIPT_SOURCE_NOT_APPLICABLE")


def build_post_reception_obligation(
    *,
    case_id: UUID,
    origin_reception_act_id: UUID | None = None,
    obligation_type: PostReceptionObligationType,
    summary: str,
    source_refs: tuple[str, ...],
    due_date: date | None = None,
    resource_note: str | None = None,
    cost_estimate_note: str | None = None,
    fulfillment_proof_refs: tuple[str, ...] = (),
    sanction_ref: str | None = None,
) -> PostReceptionObligation:
    obligation = PostReceptionObligation(
        case_id=case_id,
        origin_reception_act_id=origin_reception_act_id,
        obligation_type=obligation_type,
        summary=summary,
        source_refs=source_refs,
        due_date=due_date,
        resource_note=resource_note,
        cost_estimate_note=cost_estimate_note,
        fulfillment_proof_refs=fulfillment_proof_refs,
        sanction_ref=sanction_ref,
    )
    obligation.validate()
    return obligation
