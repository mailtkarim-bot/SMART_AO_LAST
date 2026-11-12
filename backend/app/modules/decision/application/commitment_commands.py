from typing import Literal
from uuid import UUID

from pydantic import Field

from app.platform.events.command_contracts import ApplicationCommand


class LinkConditionAssessmentRequest(ApplicationCommand):
    command_type = "LinkDecisionConditionAssessment"
    link_id: UUID
    assessment_id: UUID
    assessment_revision: int = Field(ge=1)
    source_context_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    expected_decision_revision: int = Field(ge=1)
    justification: str = Field(min_length=1, max_length=2000)
    human_confirmed: Literal[True]


class LinkConditionAssessmentCommand(LinkConditionAssessmentRequest):
    case_id: UUID
    decision_id: UUID
    condition_id: UUID
