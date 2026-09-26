# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.human_resumption_read_handler import HumanResumptionReadService
from app.modules.dce.public.contracts import HumanResumptionResponse


def build_patron_human_resumption_router(*, service: HumanResumptionReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-human-resumption"])
    @router.get("/contract-query-exports/{export_id}/human-resumption", response_model=HumanResumptionResponse)
    def read_act(export_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: act = service.get_for_export(actor=actor, export_id=export_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        if act is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
        return HumanResumptionResponse(act_id=act.id, export_id=act.export_id, actor_id=act.actor_id, state=act.state, rationale=act.rationale, created_at=act.created_at)
    return router
