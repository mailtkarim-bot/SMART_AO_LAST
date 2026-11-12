"""Patron-only composition guarded by the existing DCE and risk capabilities."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Query, Response
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.case.application.analysis_assessment import (
    AnalysisAssessmentRequest,
    AnalysisAssessmentService,
    RecordAnalysisAssessmentCommand,
)
from app.modules.case.application.analysis_dossier import (
    AnalysisDossierRequest,
    AnalysisDossierService,
    RecordAnalysisDossierCommand,
)
from app.modules.case.public.analysis_summary_contracts import (
    AnalysisDossierHistoryResponse,
    CaseAnalysisSummaryResponse,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)
from app.platform.security.authorization import AuthorizationRequest, AuthorizationResource
from app.platform.security.capabilities import Capability
from app.platform.security.context import ActorKind, DataClassification


def build_case_analysis_summary_router(*, runtime, security_runtime: ConsultationSecurityRuntime):
    router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

    def authorize_reader(case_id, authorization):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        owner = runtime.get_case_tenant_id(case_id=case_id)
        if owner is None or owner != actor.tenant_id:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        now = datetime.now(tz=UTC)
        for capability, kind, classification in [
            (Capability.CASE_DCE_READ, "CASE_DCE_READING", DataClassification.INTERNAL_OPERATIONAL),
            (
                Capability.DECISION_RISK_READ,
                "DECISION_RISK_REGISTER",
                DataClassification.INTERNAL_OPERATIONAL,
            ),
            (
                Capability.PATRON_ACTION_READ,
                "PATRON_ACTION",
                DataClassification.INTERNAL_OPERATIONAL,
            ),
            (Capability.DECISION_FINALIZE, "DECISION", DataClassification.INTERNAL_OPERATIONAL),
            (
                Capability.PRICING_READ,
                "CONTRACT_BASELINE_IMPACT",
                DataClassification.FINANCIAL_PRIVATE,
            ),
            (
                Capability.FINANCIAL_REPORT_READ,
                "CASE_FINANCIAL_REPORT",
                DataClassification.FINANCIAL_PRIVATE,
            ),
        ]:
            decision = security_runtime.policy.authorize(
                context=actor,
                request=AuthorizationRequest(
                    action=capability,
                    resource=AuthorizationResource(
                        resource_type=kind,
                        resource_id=case_id,
                        tenant_id=owner,
                        classification=classification,
                        case_id=case_id,
                    ),
                    evaluated_at=now,
                ),
            )
            if not decision.allowed:
                if decision.http_status_code == 404:
                    raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
                raise HTTPException(status_code=403, detail="FORBIDDEN")
        return actor

    @router.get("/{case_id}/analysis-summary", response_model=CaseAnalysisSummaryResponse)
    def get_summary(
        case_id: UUID, response: Response, authorization: str | None = Header(default=None)
    ):
        actor = authorize_reader(case_id, authorization)
        try:
            result = runtime.get_case_analysis_summary(tenant_id=actor.tenant_id, case_id=case_id)
        except ValueError as error:
            raise HTTPException(status_code=422, detail="CURRENT_SOURCE_UNPROVEN") from error
        if result is None:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        response.headers["Cache-Control"] = "no-store"
        return CaseAnalysisSummaryResponse.model_validate(result)

    @router.get(
        "/{case_id}/analysis-dossier-history", response_model=AnalysisDossierHistoryResponse
    )
    def get_history(
        case_id: UUID,
        response: Response,
        before_revision: int | None = Query(default=None, ge=1),
        authorization: str | None = Header(default=None),
    ):
        actor = authorize_reader(case_id, authorization)
        try:
            result = runtime.get_case_analysis_dossier_history(
                tenant_id=actor.tenant_id, case_id=case_id, before_revision=before_revision
            )
        except ValueError as error:
            raise HTTPException(status_code=422, detail="HISTORY_INTEGRITY_UNPROVEN") from error
        response.headers["Cache-Control"] = "no-store"
        return AnalysisDossierHistoryResponse.model_validate(result)

    @router.post("/{case_id}/analysis-assessments")
    def record_assessment(
        case_id: UUID,
        request: AnalysisAssessmentRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        owner = runtime.get_case_tenant_id(case_id=case_id)
        if owner is None or owner != actor.tenant_id:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        try:
            result = AnalysisAssessmentService(
                dispatcher=runtime.dispatcher, policy=security_runtime.policy
            ).execute(
                actor=actor,
                command=RecordAnalysisAssessmentCommand(**request.model_dump(), case_id=case_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except IntegrityError as error:
            raise HTTPException(status_code=409, detail="ASSESSMENT_CONFLICT") from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            code = str(error)
            if code == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(status_code=404, detail=code) from error
            if code in {"STALE_ASSESSMENT_REVISION", "STALE_SOURCE_CONTEXT"}:
                raise HTTPException(status_code=409, detail=code) from error
            raise HTTPException(status_code=422, detail="ASSESSMENT_REFUSED") from error
        reference = result.aggregate_refs[0]
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            content=dict(
                assessment_id=str(reference["aggregate_id"]),
                revision=int(reference["aggregate_revision"]),
                command_id=result.command_id,
                idempotency_key=result.idempotency_key,
                replayed=result.replayed,
            ),
        )

    @router.post("/{case_id}/analysis-dossier-reviews")
    def record_dossier(
        case_id: UUID,
        request: AnalysisDossierRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = resolve_bearer_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        if actor.actor_kind is not ActorKind.PATRON_ADMIN or actor.membership_id is None:
            raise HTTPException(status_code=403, detail="FORBIDDEN")
        owner = runtime.get_case_tenant_id(case_id=case_id)
        if owner is None or owner != actor.tenant_id:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN")
        try:
            result = AnalysisDossierService(
                dispatcher=runtime.dispatcher, policy=security_runtime.policy
            ).execute(
                actor=actor,
                command=RecordAnalysisDossierCommand(**request.model_dump(), case_id=case_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except (IntegrityError, IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="DOSSIER_CONFLICT") from error
        except CommandExecutionError as error:
            code = str(error)
            status = (
                409
                if code
                in {"STALE_SOURCE_CONTEXT", "STALE_DOSSIER_REVISION", "PREPARATION_REQUIRED"}
                else 404
                if code == "NOT_FOUND_OR_FORBIDDEN"
                else 422
            )
            raise HTTPException(
                status_code=status,
                detail=code
                if status == 409
                or code in {"UNPREPARED_POINTS", "TRUNCATED_DOSSIER", "AXIS_WITHOUT_PROVEN_POINTS"}
                else "DOSSIER_REFUSED",
            ) from error
        reference = result.aggregate_refs[0]
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            headers={"Cache-Control": "no-store"},
            content=dict(
                review_id=str(reference["aggregate_id"]),
                revision=int(reference["aggregate_revision"]),
                command_id=result.command_id,
                idempotency_key=result.idempotency_key,
                replayed=result.replayed,
            ),
        )

    return router
