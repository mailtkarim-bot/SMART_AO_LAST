# ruff: noqa: E501, E701
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_cycle_review_commands import (
    RecordPaymentCycleReviewCommand,
)
from app.modules.pricing.public.payment_cycle_review_contracts import (
    RecordPaymentCycleReviewRequest,
    RecordPaymentCycleReviewResponse,
)
from app.platform.events.dispatcher import CommandDispatcher, CommandExecutionError


def build_patron_payment_cycle_review_router(*, dispatcher: CommandDispatcher, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-cycle-review"])
    @router.post("/payment-cycles/{cycle_id}/reviews", response_model=RecordPaymentCycleReviewResponse)
    def review(cycle_id: UUID, request: RecordPaymentCycleReviewRequest, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        from app.platform.events.dispatcher import CommandContext
        from app.platform.security.context import ActorKind
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        try:
            result = dispatcher.dispatch(command=RecordPaymentCycleReviewCommand(**request.model_dump(), cycle_id=cycle_id), context=CommandContext(tenant_id=actor.tenant_id, actor_id=actor.actor_id, actor_kind=ActorKind.PATRON_ADMIN.value, received_at=datetime.now(tz=UTC), identity_id=actor.identity_id, membership_id=actor.membership_id, session_id=actor.session_id, case_id=None, correlation_id=actor.correlation_id))
        except CommandExecutionError as error: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
        response = RecordPaymentCycleReviewResponse(command_id=UUID(result.command_id), idempotency_key=UUID(result.idempotency_key), review_id=request.review_id, result_code=result.result_code, replayed=result.replayed)
        return JSONResponse(status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED, content=response.model_dump(mode="json"))
    return router
