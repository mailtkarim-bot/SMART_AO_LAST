# ruff: noqa: E501
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_query_export_transition_handler import (
    ContractQueryExportAuditReadService,
)
from app.modules.dce.public.contracts import (
    ContractQueryExportAuditResponse,
    ContractQueryExportResponse,
    ContractQueryExportTransitionResponse,
)


def build_patron_contract_query_export_audit_router(*, service: ContractQueryExportAuditReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-query-export-audit"])
    @router.get("/cases/{case_id}/contract-query-exports/{export_id}/audit", response_model=ContractQueryExportAuditResponse)
    def audit(case_id: UUID, export_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            result = service.get_for_case(actor=actor, case_id=case_id, export_id=export_id)
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND")
        export, transitions = result
        return ContractQueryExportAuditResponse(export=ContractQueryExportResponse(export_id=export.id, case_id=export.case_id, filters=export.filters_json, status=export.status, actor_id=export.actor_id, created_at=export.created_at), transitions=[ContractQueryExportTransitionResponse(transition_id=row.id, from_status=row.from_status, to_status=row.to_status, local_proof_ref=row.local_proof_ref, created_at=row.created_at) for row in transitions])
    return router
