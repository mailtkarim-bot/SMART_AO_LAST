from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import Field, field_validator, model_validator

from app.platform.events.command_contracts import ApplicationCommand

ChangeKind = Literal["ORDER_OF_SERVICE", "CHANGE_REQUEST", "ADDENDUM", "SCHEDULE_CHANGE"]
HandoverApplicability = Literal["APPLICABLE_TO_HANDOVER", "NOT_APPLICABLE", "NEEDS_CLARIFICATION"]


class RecordCaseContractChangeEventCommand(ApplicationCommand):
    command_type = "RecordCaseContractChangeEvent"

    event_id: UUID
    case_id: UUID
    handover_snapshot_id: UUID
    change_kind: ChangeKind
    contract_instrument_version_id: UUID | None = None
    issuer: str | None = Field(default=None, max_length=240)
    summary: str = Field(min_length=1, max_length=2_000)
    scope_note: str = Field(min_length=1, max_length=2_000)
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        min_length=1, max_length=32
    )
    declared_received_at: datetime

    @field_validator("declared_received_at")
    @classmethod
    def received_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("DECLARED_RECEIVED_AT_MUST_BE_TIMEZONE_AWARE")
        return value


class RecordCaseContractChangeApplicabilityCommand(ApplicationCommand):
    command_type = "RecordCaseContractChangeApplicability"

    review_id: UUID
    case_id: UUID
    event_id: UUID
    handover_snapshot_id: UUID
    contract_instrument_version_id: UUID
    expected_revision: int = Field(ge=0)
    decision: HandoverApplicability
    delta_state: Literal["UNKNOWN", "DECLARED"] = "UNKNOWN"
    delta_note: str | None = Field(default=None, max_length=2_000)
    rationale: str = Field(min_length=1, max_length=2_000)
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        min_length=1, max_length=32
    )

    @model_validator(mode="after")
    def delta_note_matches_state(self):
        if self.delta_state == "DECLARED" and not (self.delta_note and self.delta_note.strip()):
            raise ValueError("DECLARED_DELTA_NOTE_REQUIRED")
        if self.delta_state == "UNKNOWN" and self.delta_note is not None:
            raise ValueError("UNKNOWN_DELTA_NOTE_MUST_BE_EMPTY")
        return self


class RecordCaseContractChangeActionCommand(ApplicationCommand):
    command_type = "RecordCaseContractChangeAction"

    action_id: UUID
    case_id: UUID
    event_id: UUID
    applicability_review_id: UUID
    expected_revision: int = Field(ge=0)
    action_summary: str = Field(min_length=1, max_length=2_000)
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        min_length=1, max_length=32
    )
    due_at: datetime | None = None
    due_date_absence_reason: str | None = Field(default=None, max_length=500)

    @field_validator("due_at")
    @classmethod
    def due_at_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("DUE_AT_MUST_BE_TIMEZONE_AWARE")
        return value

    @field_validator("due_date_absence_reason")
    @classmethod
    def absence_reason_must_match_date(cls, value: str | None, info):
        if info.data.get("due_at") is None and not (value and value.strip()):
            raise ValueError("DUE_AT_OR_ABSENCE_REASON_REQUIRED")
        return value.strip() if value else None
