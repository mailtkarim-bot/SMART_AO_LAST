# ruff: noqa: E501
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_baseline_handler import ContractBaselineImpactReadService
from app.modules.dce.public.contracts import (
    ContractBaselineImpactPageResponse,
    ContractBaselineImpactResponse,
)


def build_patron_contract_baseline_impact_router(*, service: ContractBaselineImpactReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-baseline-impacts"])

    @router.get("/cases/{case_id}/contract-baseline-impacts", response_model=ContractBaselineImpactPageResponse)
    def list_impacts(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return ContractBaselineImpactPageResponse(case_id=case_id, items=[ContractBaselineImpactResponse(
            proof_id=row.id, case_id=row.case_id, baseline_observation_id=row.baseline_observation_id,
            proof_revision=row.proof_revision, baseline_source_refs=row.baseline_source_refs_json,
            baseline_statement=row.baseline_statement, deviation_statement=row.deviation_statement,
            impact_statement=row.impact_statement, status=row.status,
        ) for row in rows])
    return router
