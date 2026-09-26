# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.export_operational_handoff_handler import (
    ExportOperationalHandoffReadService,
)
from app.modules.dce.public.contracts import ExportOperationalHandoffResponse


def build_patron_export_operational_handoff_router(*, service: ExportOperationalHandoffReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-export-operational-handoff"])
    @router.get("/contract-query-exports/{export_id}/operational-handoff", response_model=ExportOperationalHandoffResponse)
    def handoff(export_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: result = service.get_for_export(actor=actor, export_id=export_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        if result is None: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
        export, transitions = result
        return ExportOperationalHandoffResponse(export_id=export.id, current_status=export.status, filters=export.filters_json, transition_count=len(transitions), last_transition_at=transitions[-1].created_at if transitions else None)
    return router
