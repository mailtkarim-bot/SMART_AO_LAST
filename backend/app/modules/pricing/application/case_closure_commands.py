from uuid import UUID

from pydantic import model_validator

from app.modules.patron_action.application.teaching_applicability_commands import (
    RecordCaseTeachingApplicabilityCommand,
)
from app.modules.pricing.application.contract_execution_evidence_commands import (
    RecordContractExecutionEvidenceCommand,
)
from app.modules.pricing.application.post_reception_obligation_commands import (
    RecordPostReceptionObligationCommand,
)
from app.modules.pricing.public.case_closure_contracts import (
    ClosureActReview,
    RecordExecutionRexRequest,
    RecordExecutionTeachingReuseRequest,
    RecordPaymentFactRequest,
)
from app.platform.events.command_contracts import ApplicationCommand


class RecordPaymentFactCommand(RecordPaymentFactRequest, ApplicationCommand):
    command_type = "RecordPaymentFact"
    case_id: UUID


class RecordClosureActCommand(RecordContractExecutionEvidenceCommand):
    command_type = "RecordClosureAct"
    closure_review: ClosureActReview


class RecordClosureObligationCommand(RecordPostReceptionObligationCommand):
    command_type = "RecordClosureObligation"
    closure_review: ClosureActReview


class RecordExecutionRexCommand(RecordExecutionRexRequest, ApplicationCommand):
    command_type = "RecordExecutionRex"
    case_id: UUID


class RecordExecutionTeachingReuseCommand(
    RecordExecutionTeachingReuseRequest, RecordCaseTeachingApplicabilityCommand
):
    command_type = "RecordExecutionTeachingReuse"
    case_id: UUID

    @model_validator(mode="after")
    def same_target(self):
        if self.case_id != self.target_case_id:
            raise ValueError("TARGET_CASE_MISMATCH")
        return self
