# ruff: noqa: E501, E701, I001
from datetime import UTC, datetime
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, status
from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_unknown_audit_owner_act_commands import RecordPaymentUnknownAuditOwnerActCommand
from app.modules.pricing.public.payment_unknown_audit_owner_act_contracts import RecordPaymentUnknownAuditOwnerActRequest, RecordPaymentUnknownAuditOwnerActResponse
from app.platform.events.dispatcher import CommandContext, CommandDispatcher
from app.platform.security.context import ActorKind
def build_patron_payment_unknown_audit_owner_act_router(*, dispatcher: CommandDispatcher, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-unknown-audit-owner-act"])
    @router.post("/cases/{case_id}/payment-post-reception-unknown-audit-owner-acts", response_model=RecordPaymentUnknownAuditOwnerActResponse)
    def record(case_id: UUID, request: RecordPaymentUnknownAuditOwnerActRequest, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
        result = dispatcher.dispatch(command=RecordPaymentUnknownAuditOwnerActCommand(**request.model_dump(), case_id=case_id), context=CommandContext(tenant_id=actor.tenant_id, actor_id=actor.actor_id, actor_kind=actor.actor_kind.value, received_at=datetime.now(tz=UTC), identity_id=actor.identity_id, membership_id=actor.membership_id, session_id=actor.session_id, case_id=case_id, correlation_id=actor.correlation_id))
        return RecordPaymentUnknownAuditOwnerActResponse(command_id=UUID(result.command_id), idempotency_key=UUID(result.idempotency_key), owner_act_id=request.owner_act_id, result_code=result.result_code, replayed=result.replayed)
    return router
