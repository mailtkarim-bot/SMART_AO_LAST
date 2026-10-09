from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.platform.events.command_contracts import ApplicationCommand

ChangeKind = Literal["ORDER_OF_SERVICE", "CHANGE_REQUEST", "ADDENDUM", "SCHEDULE_CHANGE"]
HandoverApplicability = Literal["APPLICABLE_TO_HANDOVER", "NOT_APPLICABLE", "NEEDS_CLARIFICATION"]
CASE_CONTRACT_CHANGE_EVIDENCE_RETENTION_TOPIC = "case_contract_change_evidence_retention"


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


class RecordCaseContractChangeActionImpactRelationCommand(ApplicationCommand):
    """Patron C4 relation between an existing action and exact C3 declarations."""

    command_type = "RecordCaseContractChangeActionImpactRelation"

    relation_id: UUID
    case_id: UUID
    event_id: UUID
    action_id: UUID
    expected_revision: int = Field(ge=0)
    state: Literal["LINKED", "UNKNOWN", "NOT_APPLICABLE"]
    declaration_ids: tuple[UUID, ...] = Field(default=(), max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)
    unknown_reason: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def state_matches_declarations(self):
        if len(set(self.declaration_ids)) != len(self.declaration_ids):
            raise ValueError("C4_DECLARATION_IDS_MUST_BE_UNIQUE")
        if self.state == "LINKED":
            if not self.declaration_ids or self.unknown_reason is not None:
                raise ValueError("C4_LINKED_REQUIRES_DECLARATIONS")
        elif self.declaration_ids or not (self.unknown_reason and self.unknown_reason.strip()):
            raise ValueError("C4_NON_LINKED_REQUIRES_REASON_AND_NO_DECLARATIONS")
        return self


class PrepareCaseContractChangeEvidenceUploadCommand(ApplicationCommand):
    """Create one server-owned C5 evidence upload intent for an exact C1/C4 pair."""

    command_type = "PrepareCaseContractChangeEvidenceUpload"

    evidence_object_id: UUID
    case_id: UUID
    event_id: UUID
    action_id: UUID
    c4_relation_id: UUID
    evidence_kind: Literal["EXECUTION_EVIDENCE", "EXTERNAL_CONFIRMATION"]
    expected_byte_size: int = Field(gt=0, le=150_000_000)


class ExpireCaseContractChangeEvidenceUploadCommand(ApplicationCommand):
    """System command to close one expired C5 upload and queue private cleanup."""

    command_type = "ExpireCaseContractChangeEvidenceUpload"

    case_id: UUID
    event_id: UUID
    action_id: UUID
    evidence_object_id: UUID


class RecordCaseContractChangeActionExecutionCommand(ApplicationCommand):
    """C5 human declaration; references alone never establish retrieved evidence."""

    command_type = "RecordCaseContractChangeActionExecution"

    act_id: UUID
    case_id: UUID
    event_id: UUID
    action_id: UUID
    c4_relation_id: UUID
    expected_revision: int = Field(ge=0)
    declared_state: Literal[
        "DECLARED_PERFORMED", "DECLARED_PARTIAL", "DECLARED_NOT_PERFORMED", "UNKNOWN"
    ]
    declared_summary: str | None = Field(default=None, max_length=2_000)
    unknown_reason: str | None = Field(default=None, max_length=1_000)
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        default=(), max_length=32
    )
    evidence_object_ids: tuple[UUID, ...] = Field(default=(), max_length=16)
    verified_evidence_object_ids: tuple[UUID, ...] = Field(default=(), max_length=16, exclude=True)
    external_confirmation_state: Literal["UNKNOWN", "NOT_CONFIRMED"] = "UNKNOWN"
    external_confirmation_note: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def validate_declaration(self):
        if self.declared_state == "UNKNOWN":
            if self.declared_summary is not None or not (
                self.unknown_reason and self.unknown_reason.strip()
            ):
                raise ValueError("C5_UNKNOWN_REQUIRES_REASON_ONLY")
        elif not (self.declared_summary and self.declared_summary.strip()) or (
            self.unknown_reason is not None
        ):
            raise ValueError("C5_DECLARATION_REQUIRES_SUMMARY_ONLY")
        if self.external_confirmation_state == "NOT_CONFIRMED":
            if not (self.external_confirmation_note and self.external_confirmation_note.strip()):
                raise ValueError("C5_NOT_CONFIRMED_REQUIRES_NOTE")
        elif self.external_confirmation_note is not None:
            raise ValueError("C5_UNKNOWN_CONFIRMATION_MUST_NOT_HAVE_NOTE")
        if any(not value.strip() for value in self.evidence_refs):
            raise ValueError("C5_EVIDENCE_REFERENCE_MUST_NOT_BE_EMPTY")
        if len(set(self.evidence_object_ids)) != len(self.evidence_object_ids):
            raise ValueError("C5_EVIDENCE_OBJECT_IDS_MUST_BE_UNIQUE")
        if not set(self.verified_evidence_object_ids).issubset(self.evidence_object_ids):
            raise ValueError("C5_VERIFIED_EVIDENCE_MUST_BE_REQUESTED")
        return self


class RecordCaseContractChangeExternalConfirmationCommand(ApplicationCommand):
    """Append a separate human act referencing a retrieved external confirmation."""

    command_type = "RecordCaseContractChangeExternalConfirmation"

    confirmation_id: UUID
    case_id: UUID
    event_id: UUID
    action_id: UUID
    act_id: UUID
    c4_relation_id: UUID
    evidence_object_id: UUID
    expected_revision: int = Field(ge=0)
    received_at: datetime
    external_party: str | None = Field(default=None, max_length=240)
    rationale: str = Field(min_length=1, max_length=2_000)
    verified_evidence_object_id: UUID | None = Field(default=None, exclude=True)

    @field_validator("received_at")
    @classmethod
    def received_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("C5_EXTERNAL_CONFIRMATION_RECEIVED_AT_MUST_BE_AWARE")
        return value

    @field_validator("external_party")
    @classmethod
    def external_party_must_not_be_blank(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None

    @model_validator(mode="after")
    def source_must_be_verified(self):
        if self.verified_evidence_object_id != self.evidence_object_id:
            raise ValueError("C5_EXTERNAL_CONFIRMATION_SOURCE_MUST_BE_VERIFIED")
        return self


class A1EngagementSourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    condition_id: UUID
    requirement_id: UUID
    requirement_revision: int = Field(ge=1)
    impact_id: UUID
    impact_revision: int = Field(ge=1)
    profile_version_id: UUID
    profile_version: int = Field(ge=1)
    profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def validate_impact_declaration_payload(
    *,
    axis: str,
    impact_state: str,
    impact_summary: str | None,
    impact_unknown_reason: str | None,
    measurement_state: str,
    value_as_declared: str | None,
    currency_code: str | None,
    unit: str | None,
    measurement_unknown_reason: str | None,
    evidence_refs: tuple[str, ...] | list[str],
) -> None:
    summary = impact_summary.strip() if impact_summary else None
    impact_reason = impact_unknown_reason.strip() if impact_unknown_reason else None
    measurement_reason = measurement_unknown_reason.strip() if measurement_unknown_reason else None
    if impact_state == "DECLARED":
        if not summary or impact_reason is not None:
            raise ValueError("DECLARED_IMPACT_REQUIRES_SUMMARY")
        if not evidence_refs:
            raise ValueError("DECLARED_IMPACT_REQUIRES_EVIDENCE")
    elif summary is not None or not impact_reason:
        raise ValueError("UNKNOWN_IMPACT_REQUIRES_REASON_AND_NO_SUMMARY")

    if axis == "SCOPE":
        if measurement_state != "NOT_APPLICABLE":
            raise ValueError("SCOPE_MEASUREMENT_MUST_BE_NOT_APPLICABLE")
        if any(
            value is not None
            for value in (value_as_declared, currency_code, unit, measurement_reason)
        ):
            raise ValueError("SCOPE_MUST_NOT_HAVE_QUANTITATIVE_MEASUREMENT")
    elif impact_state == "UNKNOWN":
        if measurement_state != "UNKNOWN" or any(
            value is not None for value in (value_as_declared, currency_code, unit)
        ):
            raise ValueError("UNKNOWN_IMPACT_MUST_NOT_HAVE_MEASUREMENT")
        if measurement_reason is not None:
            raise ValueError("UNKNOWN_IMPACT_MUST_NOT_HAVE_MEASUREMENT_REASON")
    elif measurement_state == "DECLARED":
        if not value_as_declared:
            raise ValueError("DECLARED_MEASUREMENT_REQUIRES_VALUE")
        if measurement_reason is not None:
            raise ValueError("DECLARED_MEASUREMENT_MUST_NOT_HAVE_UNKNOWN_REASON")
        if axis in {"COST", "CASH"}:
            if currency_code is None or unit is not None:
                raise ValueError("MONETARY_MEASUREMENT_REQUIRES_CURRENCY_ONLY")
        elif currency_code is not None or not (unit and unit.strip()):
            raise ValueError("QUANTITY_MEASUREMENT_REQUIRES_UNIT_ONLY")
    elif measurement_state == "UNKNOWN":
        if any(value is not None for value in (value_as_declared, currency_code, unit)):
            raise ValueError("UNKNOWN_MEASUREMENT_MUST_NOT_HAVE_VALUE_OR_UNIT")
        if not measurement_reason:
            raise ValueError("UNKNOWN_MEASUREMENT_REQUIRES_REASON")
    else:
        raise ValueError("QUANTITATIVE_AXIS_REQUIRES_MEASUREMENT_STATE")


class RecordCaseContractChangeEngagementLinkCommand(ApplicationCommand):
    """Human act connecting C1 to exact A1 sources carried in its B1 snapshot."""

    command_type = "RecordCaseContractChangeEngagementLink"

    linkage_id: UUID
    case_id: UUID
    event_id: UUID
    expected_revision: int = Field(ge=0)
    state: Literal["LINKED", "UNKNOWN"]
    selected_sources: tuple[A1EngagementSourceInput, ...] = Field(max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)
    unknown_reason: str | None = Field(default=None, max_length=1_000)

    @model_validator(mode="after")
    def state_matches_sources(self):
        if self.state == "LINKED" and (
            not self.selected_sources or self.unknown_reason is not None
        ):
            raise ValueError("LINKED_REQUIRES_SELECTED_SOURCES")
        if self.state == "UNKNOWN" and (
            self.selected_sources or not (self.unknown_reason and self.unknown_reason.strip())
        ):
            raise ValueError("UNKNOWN_REQUIRES_REASON_AND_NO_SELECTION")
        source_ids = [
            (source.condition_id, source.impact_id, source.impact_revision)
            for source in self.selected_sources
        ]
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("DUPLICATE_A1_SOURCE_SELECTION")
        return self


class RecordCaseContractChangeImpactDeclarationCommand(ApplicationCommand):
    """Human C3 impact declaration for one exact A1 source and current C2 link."""

    command_type = "RecordCaseContractChangeImpactDeclaration"

    declaration_id: UUID
    case_id: UUID
    event_id: UUID
    linkage_id: UUID
    source: A1EngagementSourceInput
    expected_revision: int = Field(ge=0)
    axis: Literal["SCOPE", "COST", "CASH", "SCHEDULE", "CAPACITY"]
    impact_state: Literal["DECLARED", "UNKNOWN"]
    impact_summary: str | None = Field(default=None, max_length=2_000)
    impact_unknown_reason: str | None = Field(default=None, max_length=1_000)
    measurement_state: Literal["DECLARED", "UNKNOWN", "NOT_APPLICABLE"]
    value_as_declared: str | None = Field(
        default=None,
        max_length=80,
        pattern=r"^-?[0-9]+([,.][0-9]{1,6})?$",
    )
    currency_code: str | None = Field(default=None, pattern=r"^[A-Z]{3}$")
    unit: str | None = Field(default=None, max_length=32)
    measurement_unknown_reason: str | None = Field(default=None, max_length=1_000)
    assumptions: tuple[Annotated[str, Field(min_length=1, max_length=500)], ...] = Field(
        default=(), max_length=32
    )
    source_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        min_length=1, max_length=32
    )
    evidence_refs: tuple[Annotated[str, Field(min_length=1, max_length=1_000)], ...] = Field(
        default=(), max_length=32
    )
    rationale: str = Field(min_length=1, max_length=2_000)

    @model_validator(mode="after")
    def validate_declared_impact(self):
        validate_impact_declaration_payload(
            axis=self.axis,
            impact_state=self.impact_state,
            impact_summary=self.impact_summary,
            impact_unknown_reason=self.impact_unknown_reason,
            measurement_state=self.measurement_state,
            value_as_declared=self.value_as_declared,
            currency_code=self.currency_code,
            unit=self.unit,
            measurement_unknown_reason=self.measurement_unknown_reason,
            evidence_refs=self.evidence_refs,
        )
        return self
