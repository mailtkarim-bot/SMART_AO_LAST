# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_cycle_handler import PaymentCycleReadService
from app.modules.pricing.public.payment_cycle_contracts import (
    PaymentUnknownAuditEntryResponse,
    PaymentUnknownAuditResponse,
)


def build_patron_payment_unknown_audit_router(*, service: PaymentCycleReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-unknown-audit"])
    @router.get("/cases/{case_id}/payment-post-reception-unknown-audit", response_model=PaymentUnknownAuditResponse)
    def audit(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: result = service.audit_for_case(actor=actor, case_id=case_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return PaymentUnknownAuditResponse(status_counts=result.status_counts, entries=[PaymentUnknownAuditEntryResponse(cycle_id=entry["cycle_id"], status=entry["status"], source_refs=entry["source_refs"], trigger_event=entry["trigger_event"]) for entry in result.entries], rejected_count=getattr(result, "rejected_count", 0))
    return router
