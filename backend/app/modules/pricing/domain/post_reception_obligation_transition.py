from dataclasses import dataclass
from enum import StrEnum


class PostReceptionObligationStatus(StrEnum):
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    IN_PROGRESS = "IN_PROGRESS"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    UNKNOWN = "UNKNOWN"
    COMPLETED = "COMPLETED"


_ALLOWED_TRANSITIONS = {
    PostReceptionObligationStatus.REVIEW_REQUIRED: {
        PostReceptionObligationStatus.IN_PROGRESS,
        PostReceptionObligationStatus.FOLLOW_UP_REQUIRED,
        PostReceptionObligationStatus.UNKNOWN,
        PostReceptionObligationStatus.COMPLETED,
    },
    PostReceptionObligationStatus.IN_PROGRESS: {
        PostReceptionObligationStatus.FOLLOW_UP_REQUIRED,
        PostReceptionObligationStatus.UNKNOWN,
        PostReceptionObligationStatus.COMPLETED,
    },
    PostReceptionObligationStatus.FOLLOW_UP_REQUIRED: {
        PostReceptionObligationStatus.IN_PROGRESS,
        PostReceptionObligationStatus.UNKNOWN,
        PostReceptionObligationStatus.COMPLETED,
    },
    PostReceptionObligationStatus.UNKNOWN: {
        PostReceptionObligationStatus.IN_PROGRESS,
        PostReceptionObligationStatus.FOLLOW_UP_REQUIRED,
        PostReceptionObligationStatus.COMPLETED,
    },
    PostReceptionObligationStatus.COMPLETED: set(),
}


@dataclass(frozen=True, slots=True)
class PostReceptionObligationTransition:
    previous_status: PostReceptionObligationStatus
    resulting_status: PostReceptionObligationStatus
    rationale: str
    evidence_refs: tuple[str, ...]


def build_post_reception_obligation_transition(
    *,
    current_status: PostReceptionObligationStatus,
    resulting_status: PostReceptionObligationStatus,
    rationale: str,
    evidence_refs: tuple[str, ...] = (),
) -> PostReceptionObligationTransition:
    if resulting_status not in _ALLOWED_TRANSITIONS[current_status]:
        error = (
            "POST_RECEPTION_COMPLETED_IS_TERMINAL"
            if current_status is PostReceptionObligationStatus.COMPLETED
            else "POST_RECEPTION_TRANSITION_NOT_ALLOWED"
        )
        raise ValueError(error)
    if not rationale.strip():
        raise ValueError("POST_RECEPTION_TRANSITION_RATIONALE_REQUIRED")
    if any(not ref.strip() for ref in evidence_refs):
        raise ValueError("POST_RECEPTION_TRANSITION_PROOF_REF_INVALID")
    if resulting_status is PostReceptionObligationStatus.COMPLETED and not evidence_refs:
        raise ValueError("POST_RECEPTION_COMPLETION_PROOF_REQUIRED")
    return PostReceptionObligationTransition(
        previous_status=current_status,
        resulting_status=resulting_status,
        rationale=rationale,
        evidence_refs=evidence_refs,
    )
