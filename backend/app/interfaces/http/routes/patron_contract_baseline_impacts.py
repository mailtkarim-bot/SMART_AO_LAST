# ruff: noqa: E501
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_baseline_commands import (
    RecordContractBaselineImpactCommand,
)
from app.modules.dce.application.contract_baseline_handler import (
    ContractBaselineImpactReadService,
    ContractBaselineImpactWriteService,
)
from app.modules.dce.public.contracts import (
    ContractBaselineImpactPageResponse,
    ContractBaselineImpactResponse,
    RecordContractBaselineImpactRequest,
    RecordContractBaselineImpactResponse,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_patron_contract_baseline_impact_router(
    *,
    service: ContractBaselineImpactReadService,
    security_runtime: ConsultationSecurityRuntime,
    write_service: ContractBaselineImpactWriteService | None = None,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-baseline-impacts"])

    @router.get(
        "/cases/{case_id}/contract-baseline-impacts",
        response_model=ContractBaselineImpactPageResponse,
    )
    def list_impacts(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return ContractBaselineImpactPageResponse(
            case_id=case_id,
            items=[
                ContractBaselineImpactResponse(
                    proof_id=row.id,
                    case_id=row.case_id,
                    baseline_observation_id=row.baseline_observation_id,
                    dce_requirement_id=getattr(row, "dce_requirement_id", None),
                    dce_requirement_revision=getattr(row, "dce_requirement_revision", None),
                    proof_revision=row.proof_revision,
                    baseline_source_refs=row.baseline_source_refs_json,
                    baseline_statement=row.baseline_statement,
                    deviation_statement=row.deviation_statement,
                    impact_statement=row.impact_statement,
                    status=row.status,
                )
                for row in rows
            ],
        )

    if write_service is not None:

        @router.post(
            "/cases/{case_id}/contract-baseline-impacts",
            response_model=RecordContractBaselineImpactResponse,
        )
        def record_impact(
            case_id: UUID,
            request: RecordContractBaselineImpactRequest,
            authorization: str | None = Header(default=None),
        ):
            actor = resolve_bearer_context(
                authorization=authorization, context_resolver=security_runtime.context_resolver
            )
            command = RecordContractBaselineImpactCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                proof_id=request.proof_id,
                case_id=case_id,
                dce_requirement_id=request.dce_requirement_id,
                dce_requirement_revision=request.dce_requirement_revision,
                proof_revision=1,
                baseline_source_refs=tuple(request.baseline_source_refs),
                baseline_statement=request.baseline_statement,
                deviation_statement=request.deviation_statement,
                impact_statement=request.impact_statement,
                status="HUMAN_REVIEW_REQUIRED",
            )
            try:
                result = write_service.execute(
                    actor=actor, command=command, now=datetime.now(tz=UTC)
                )
            except PermissionError as error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
                ) from error
            except CommandExecutionError as error:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=str(error)
                ) from error
            response = RecordContractBaselineImpactResponse(
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
                proof_id=request.proof_id,
                proof_revision=1,
                result_code=result.result_code,
                status="HUMAN_REVIEW_REQUIRED",
                replayed=result.replayed,
            )
            return JSONResponse(
                status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
                content=response.model_dump(mode="json"),
            )

    return router
