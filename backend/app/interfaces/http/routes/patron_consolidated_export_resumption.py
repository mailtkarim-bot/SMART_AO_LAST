# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.consolidated_export_resumption_handler import (
    ConsolidatedExportResumptionReadService,
)
from app.modules.dce.public.contracts import (
    HumanResumptionTimelineEventResponse,
    HumanResumptionTimelineResponse,
)


def build_patron_consolidated_export_resumption_router(*, service: ConsolidatedExportResumptionReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-consolidated-export-resumption"])
    @router.get("/contract-query-exports/{export_id}/consolidated-resumption", response_model=HumanResumptionTimelineResponse)
    def consolidated(export_id: UUID, export_status: str | None = Query(default=None), resumption_state: str | None = Query(default=None), limit: int = Query(default=50, ge=1, le=100), offset: int = Query(default=0, ge=0), authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: rows = service.get_for_export(actor=actor, export_id=export_id, export_status=export_status, resumption_state=resumption_state, limit=limit, offset=offset)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return HumanResumptionTimelineResponse(export_id=export_id, items=[HumanResumptionTimelineEventResponse(**row) for row in rows])
    return router
