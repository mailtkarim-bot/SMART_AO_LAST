# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.human_resumption_timeline_handler import (
    HumanResumptionTimelineReadService,
)
from app.modules.dce.public.contracts import (
    HumanResumptionTimelineEventResponse,
    HumanResumptionTimelineResponse,
)


def build_patron_human_resumption_timeline_router(*, service: HumanResumptionTimelineReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-human-resumption-timeline"])
    @router.get("/contract-query-exports/{export_id}/human-resumption-timeline", response_model=HumanResumptionTimelineResponse)
    def timeline(export_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: rows = service.get_for_export(actor=actor, export_id=export_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return HumanResumptionTimelineResponse(export_id=export_id, items=[HumanResumptionTimelineEventResponse(**row) for row in rows])
    return router
