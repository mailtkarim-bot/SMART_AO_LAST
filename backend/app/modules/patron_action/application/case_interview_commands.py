# ruff: noqa: I001
from datetime import date
from uuid import UUID
from pydantic import Field
from app.platform.events.command_contracts import ApplicationCommand

class RecordCaseInterviewCommand(ApplicationCommand):
    command_type = "RecordCaseInterview"
    interview_id: UUID
    case_id: UUID
    held_on: date
    source_locator: str = Field(min_length=1, max_length=500)
    rationale: str = Field(min_length=1, max_length=2_000)
    expires_on: date
