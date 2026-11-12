"""Private Patron closure workflow; no external or legal effect."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.modules.pricing.application.case_closure_commands import (
    RecordClosureActCommand,
    RecordClosureObligationCommand,
    RecordExecutionRexCommand,
    RecordExecutionTeachingReuseCommand,
    RecordPaymentFactCommand,
)
from app.modules.pricing.public.case_closure_contracts import (
    RecordClosureActRequest,
    RecordClosureObligationRequest,
    RecordExecutionRexRequest,
    RecordExecutionTeachingReuseRequest,
    RecordPaymentFactRequest,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_case_closure_router(*, service, security_runtime):
    router = APIRouter(prefix="/api/v1/patron/cases/{case_id}/closure", tags=["case-closure"])

    def actor_for(authorization):
        return resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )

    def command_result(case_id, body, command_class, identity, authorization):
        try:
            result = service.record(
                actor=actor_for(authorization),
                command=command_class(**body.model_dump(), case_id=case_id),
                now=datetime.now(UTC),
            )
        except PermissionError as error:
            raise HTTPException(403, "FORBIDDEN") from error
        except CommandExecutionError as error:
            code = str(error)
            status = (
                404
                if "NOT_FOUND" in code or "FORBIDDEN" in code
                else 409
                if any(t in code for t in ("CONFLICT", "REUSED", "IN_PROGRESS", "SOURCE_CHANGED"))
                else 422
            )
            raise HTTPException(
                status, "NOT_FOUND_OR_FORBIDDEN" if status == 404 else code
            ) from error
        except IntegrityError as error:
            raise HTTPException(422, "DECLARATION_NOT_ACCEPTED") from error
        except SQLAlchemyError as error:
            raise HTTPException(503, "RESULT_UNKNOWN") from error
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            content={
                "command_id": str(result.command_id),
                "idempotency_key": str(result.idempotency_key),
                identity: str(getattr(body, identity)),
                "result_code": result.result_code,
                "replayed": result.replayed,
            },
        )

    @router.get("")
    def read(case_id: UUID, authorization: str | None = Header(default=None)):
        try:
            return service.read(
                actor=actor_for(authorization), case_id=case_id, now=datetime.now(UTC)
            )
        except PermissionError as error:
            raise HTTPException(403, "FORBIDDEN") from error
        except CommandExecutionError as error:
            raise HTTPException(404, "NOT_FOUND_OR_FORBIDDEN") from error

    @router.post("/payment-facts")
    def payment_fact(
        case_id: UUID,
        body: RecordPaymentFactRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(case_id, body, RecordPaymentFactCommand, "fact_id", authorization)

    @router.post("/acts")
    def act(
        case_id: UUID,
        body: RecordClosureActRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(case_id, body, RecordClosureActCommand, "act_id", authorization)

    @router.post("/obligations")
    def obligation(
        case_id: UUID,
        body: RecordClosureObligationRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(
            case_id, body, RecordClosureObligationCommand, "obligation_id", authorization
        )

    @router.post("/rex")
    def rex(
        case_id: UUID,
        body: RecordExecutionRexRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(case_id, body, RecordExecutionRexCommand, "rex_id", authorization)

    from app.modules.patron_action.application.case_interview_commands import (
        RecordCaseInterviewCommand,
    )
    from app.modules.pricing.application.payment_cycle_commands import (
        RecordPaymentPostReceptionCycleCommand,
    )
    from app.modules.pricing.application.post_reception_obligation_transition_commands import (
        TransitionPostReceptionObligationCommand,
    )
    from app.modules.pricing.public.case_closure_contracts import (
        ClosureInterviewRequest,
        ClosureObligationTransitionRequest,
    )
    from app.modules.pricing.public.payment_cycle_contracts import RecordPaymentCycleRequest

    @router.post("/cycles")
    def cycle(
        case_id: UUID,
        body: RecordPaymentCycleRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(
            case_id, body, RecordPaymentPostReceptionCycleCommand, "cycle_id", authorization
        )

    @router.post("/obligation-transitions")
    def transition(
        case_id: UUID,
        body: ClosureObligationTransitionRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(
            case_id, body, TransitionPostReceptionObligationCommand, "transition_id", authorization
        )

    @router.post("/interviews")
    def interview(
        case_id: UUID,
        body: ClosureInterviewRequest,
        authorization: str | None = Header(default=None),
    ):
        return command_result(
            case_id, body, RecordCaseInterviewCommand, "interview_id", authorization
        )

    @router.post("/teaching-reuse")
    def reuse(
        case_id: UUID,
        body: RecordExecutionTeachingReuseRequest,
        authorization: str | None = Header(default=None),
    ):
        if body.target_case_id != case_id:
            raise HTTPException(422, "TARGET_CASE_MISMATCH")
        return command_result(
            case_id, body, RecordExecutionTeachingReuseCommand, "applicability_id", authorization
        )

    return router
