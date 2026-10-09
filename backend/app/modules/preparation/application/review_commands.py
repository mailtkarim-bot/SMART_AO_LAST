from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.platform.events.command_contracts import ApplicationCommand

_FINANCIAL_TERMS = (
    "prix",
    "coût",
    "cout",
    "marge",
    "trésorerie",
    "tresorerie",
    "chiffrage",
    "devis",
)


def _reject_financial_text(value: str | None) -> str | None:
    if value is not None and any(term in value.casefold() for term in _FINANCIAL_TERMS):
        raise ValueError("FINANCIAL_DATA_FORBIDDEN")
    return value


class RequestPreparationReviewCommand(ApplicationCommand):
    """Request a human review of one immutable technical document version."""

    command_type = "RequestPreparationReview"

    review_id: UUID
    package_id: UUID
    target_document_id: UUID | None = None
    target_version: int | None = Field(default=None, gt=0)
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    expected_package_revision: int = Field(ge=0)

    @model_validator(mode="after")
    def require_exact_target(self):
        if self.target_draft_id is not None:
            if self.target_draft_version is None or self.target_content_sha256 is None:
                raise ValueError("REVIEW_TARGET_INCOMPLETE")
        elif self.target_document_id is None or self.target_version is None:
            raise ValueError("REVIEW_TARGET_INCOMPLETE")
        return self


class DecidePreparationReviewCommand(ApplicationCommand):
    """Record one immutable human review decision."""

    command_type = "DecidePreparationReview"

    review_id: UUID
    package_id: UUID
    target_document_id: UUID | None = None
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    expected_review_revision: int = Field(ge=1)
    decision_code: Literal["ACCEPTED", "CORRECTIONS_REQUIRED", "REJECTED"]
    decision_note: str | None = Field(default=None, max_length=2000)

    _decision_note_without_finance = field_validator("decision_note", mode="before")(
        _reject_financial_text
    )


class AddPreparationCorrectionCommand(ApplicationCommand):
    """Record one targeted correction without mutating the reviewed target."""

    command_type = "AddPreparationCorrection"

    review_id: UUID
    package_id: UUID
    target_document_id: UUID | None = None
    target_draft_id: UUID | None = None
    target_draft_version: int | None = Field(default=None, gt=0)
    target_content_sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    correction_code: Literal[
        "SOURCE_MISSING", "SOURCE_WRONG", "SECTION_INCOMPLETE", "WORDING_UNCLEAR"
    ]
    instruction: str = Field(min_length=1, max_length=2000)
    source_locator: str | None = Field(default=None, max_length=500)
    corrected_content: str | None = Field(default=None, min_length=1, max_length=100_000)

    _instruction_without_finance = field_validator("instruction", mode="before")(
        _reject_financial_text
    )
    _corrected_content_without_finance = field_validator("corrected_content", mode="before")(
        _reject_financial_text
    )


class CreateTechnicalResponseDraftCommand(ApplicationCommand):
    """Create an immutable, non-financial response draft version."""

    command_type = "CreateTechnicalResponseDraft"

    draft_id: UUID
    package_id: UUID
    source_document_id: UUID
    expected_package_revision: int = Field(ge=0)
    section_codes: list[str] = Field(min_length=1, max_length=32)
    source_refs: list[UUID] = Field(min_length=1, max_length=64)
    responsible_role: Literal["COLLABORATEUR"] = "COLLABORATEUR"
