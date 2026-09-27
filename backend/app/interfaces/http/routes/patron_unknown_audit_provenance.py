# ruff: noqa: E501, E701
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.unknown_audit_provenance_handler import (
    UnknownAuditProvenanceReadService,
)
from app.modules.dce.public.contracts import UnknownAuditProvenanceResponse


def build_patron_unknown_audit_provenance_router(*, service: UnknownAuditProvenanceReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-unknown-audit-provenance"])
    @router.get("/contract-query-exports/{export_id}/unknown-provenance", response_model=list[UnknownAuditProvenanceResponse])
    def read_provenance(export_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try: rows = service.get_for_export(actor=actor, export_id=export_id)
        except PermissionError as error: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return [UnknownAuditProvenanceResponse(provenance_id=row.id, export_id=row.export_id, source_type=row.source_type, source_event_id=row.source_event_id, actor_id=row.actor_id, status=row.status, occurred_at=row.occurred_at, rationale=row.rationale) for row in rows]
    return router
