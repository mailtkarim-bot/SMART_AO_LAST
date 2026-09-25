# ruff: noqa: E501
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_query_export_handler import ContractQueryExportReadService
from app.modules.dce.public.contracts import (
    ContractQueryExportPageResponse,
    ContractQueryExportResponse,
)


def build_patron_contract_query_export_router(*, service: ContractQueryExportReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-query-exports"])
    @router.get("/cases/{case_id}/contract-query-exports", response_model=ContractQueryExportPageResponse)
    def list_exports(case_id: UUID, limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id, limit=limit, offset=offset)
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return ContractQueryExportPageResponse(case_id=case_id, items=[ContractQueryExportResponse(export_id=row.id, case_id=row.case_id, filters=row.filters_json, status=row.status, actor_id=row.actor_id, created_at=row.created_at) for row in rows])
    return router
