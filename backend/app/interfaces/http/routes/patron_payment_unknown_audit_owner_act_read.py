# ruff: noqa: E501, E701, I001
from uuid import UUID
from fastapi import APIRouter, Header, HTTPException, status
from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.pricing.application.payment_unknown_audit_owner_act_read_handler import PaymentUnknownAuditOwnerActReadService
from app.modules.pricing.public.payment_unknown_audit_owner_act_contracts import PaymentUnknownAuditOwnerActReadResponse
def build_patron_payment_unknown_audit_owner_act_read_router(*, service: PaymentUnknownAuditOwnerActReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-payment-unknown-audit-owner-act"])
    @router.get("/cases/{case_id}/payment-post-reception-unknown-audit-owner-act", response_model=PaymentUnknownAuditOwnerActReadResponse | None)
    def read(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: row = service.get_for_case(actor=actor, case_id=case_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return None if row is None else PaymentUnknownAuditOwnerActReadResponse(owner_act_id=row.id, case_id=row.case_id, owner_id=row.owner_id, approved=row.approved, rationale=row.rationale, created_at=row.created_at)
    return router
