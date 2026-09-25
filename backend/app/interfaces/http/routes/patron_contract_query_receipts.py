# ruff: noqa: E501
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_query_receipt_handler import (
    ContractQueryReceiptReadService,
)
from app.modules.dce.public.contracts import (
    ContractQueryReceiptPageResponse,
    ContractQueryReceiptResponse,
)


def build_patron_contract_query_receipt_router(*, service: ContractQueryReceiptReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-query-receipts"])
    @router.get("/cases/{case_id}/contract-query-receipts", response_model=ContractQueryReceiptPageResponse)
    def list_receipts(case_id: UUID, limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id, limit=limit, offset=offset)
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return ContractQueryReceiptPageResponse(case_id=case_id, items=[ContractQueryReceiptResponse(receipt_id=row.id, case_id=row.case_id, filters=row.filters_json, order_key=row.order_key, limit_value=row.limit_value, offset_value=row.offset_value, actor_id=row.actor_id, created_at=row.created_at) for row in rows])
    return router
