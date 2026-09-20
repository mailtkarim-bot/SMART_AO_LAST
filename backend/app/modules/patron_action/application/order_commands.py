from datetime import date
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordCaseOrderCommand(ApplicationCommand):
    """Record one Patron decision to accept or refuse a WON lot as a command."""

    command_type = "RecordCaseOrder"

    order_id: UUID
    outcome_id: UUID
    case_id: UUID
    decision: Literal["ACCEPTED", "REJECTED"]
    rationale: str = Field(min_length=1, max_length=2_000)


class RecordCaseP6ControlCommand(ApplicationCommand):
    """Record the minimal P6 control for one accepted order."""

    command_type = "RecordCaseP6Control"

    p6_control_id: UUID
    order_id: UUID
    case_id: UUID
    decision: Literal["APPROVED", "REJECTED"]
    reservations: list[str] = Field(default_factory=list, max_length=32)
    rationale: str = Field(min_length=1, max_length=2_000)


class RecordCaseP7ResultCommand(ApplicationCommand):
    """Record the execution result after an approved P6 control."""

    command_type = "RecordCaseP7Result"

    p7_result_id: UUID
    p6_control_id: UUID
    case_id: UUID
    result: Literal["COMPLETED", "UNKNOWN", "INTERRUPTED"]
    source_locator: str | None = Field(default=None, max_length=500)
    reason: str | None = Field(default=None, max_length=2_000)
    reservations: list[str] = Field(default_factory=list, max_length=32)


class RecordCaseRexCommand(ApplicationCommand):
    """Record a bounded, explicitly scoped return of experience."""

    command_type = "RecordCaseRex"

    rex_id: UUID
    p7_result_id: UUID
    case_id: UUID
    motif: Literal["KNOWN", "UNKNOWN"]
    scope: Literal["CASE_ONLY", "LOT_PATTERN", "ENTERPRISE_PATTERN"]
    validation: Literal["PENDING", "APPROVED"]
    observation: str = Field(min_length=1, max_length=2_000)
    consequence: str = Field(min_length=1, max_length=2_000)
    follow_up: str = Field(min_length=1, max_length=2_000)
    source_locator: str | None = Field(default=None, max_length=500)


class RecordCaseDispositionCommand(ApplicationCommand):
    """Record an auditable suspension, resumption, or closure of one Case."""

    command_type = "RecordCaseDisposition"

    disposition_id: UUID
    case_id: UUID
    state: Literal["SUSPENDED", "RESUMED", "CLOSED"]
    reason_code: str = Field(min_length=2, max_length=64, pattern=r"^[A-Z0-9_]+$")
    rationale: str = Field(min_length=1, max_length=2_000)
    p7_result_id: UUID | None = None
    source_locator: str | None = Field(default=None, max_length=500)


class RequestCaseExportCommand(ApplicationCommand):
    """Request a prepared export without claiming external delivery."""

    command_type = "RequestCaseExport"

    export_request_id: UUID
    case_id: UUID
    artifact_kind: Literal["CASE_DOSSIER", "P7_RESULT", "REX", "AUDIT_TRAIL"]
    purpose: str = Field(min_length=1, max_length=2_000)
    recipient_label: str | None = Field(default=None, max_length=240)
    source_locator: str | None = Field(default=None, max_length=500)


class RecordCaseRetentionCommand(ApplicationCommand):
    """Record preservation of one internal evidence reference."""

    command_type = "RecordCaseRetention"

    retention_id: UUID
    case_id: UUID
    evidence_locator: str = Field(min_length=1, max_length=500)
    retention_basis: Literal["MARKET_RECORD", "OPEN_LITIGATION", "INTERNAL_POLICY"]
    retain_until: date
    rationale: str = Field(min_length=1, max_length=2_000)
