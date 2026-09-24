from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class RecordRegulatoryProfileCommand(ApplicationCommand):
    """Record one sourced applicability profile version for an Affaire."""

    command_type = "RecordRegulatoryProfile"

    profile_id: UUID
    case_id: UUID
    profile_version: int = Field(ge=1)
    status: Literal["ACTIVE", "FUTURE", "EXPIRED", "UNKNOWN_APPLICABILITY", "REVIEW_REQUIRED"]
    facts: dict[str, object] = Field(min_length=1)
    source_refs: tuple[str, ...] = Field(min_length=1)
    effective_from: datetime | None = None
    effective_until: datetime | None = None
