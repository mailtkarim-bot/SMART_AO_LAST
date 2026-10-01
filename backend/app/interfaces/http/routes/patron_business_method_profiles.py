from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.enterprise.application.business_method_profile_handler import (
    BusinessMethodProfileService,
)
from app.modules.enterprise.public.business_method_profile_contracts import (
    AdoptBusinessMethodProfileRequest,
    BusinessMethodProfileAdoptionResponse,
    BusinessMethodProfileContent,
    BusinessMethodProfileReceiptResponse,
    BusinessMethodProfileVersionResponse,
    BusinessMethodProfileVersionsResponse,
    PublishBusinessMethodProfileRequest,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def _receipt(result) -> BusinessMethodProfileReceiptResponse:
    return BusinessMethodProfileReceiptResponse(
        command_id=result.command_id,
        idempotency_key=result.idempotency_key,
        result_code=result.result_code,
        aggregate_refs=list(result.aggregate_refs),
        event_ids=list(result.event_ids),
        replayed=result.replayed,
    )


def build_patron_business_method_profile_router(
    *, service: BusinessMethodProfileService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["business-method-profiles"])

    def actor(authorization: str | None):
        return resolve_bearer_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )

    @router.post(
        "/enterprise/companies/{company_id}/business-method-profile/versions",
        status_code=status.HTTP_201_CREATED,
        response_model=BusinessMethodProfileReceiptResponse,
    )
    def publish_profile(
        company_id: UUID,
        request: PublishBusinessMethodProfileRequest,
        authorization: str | None = Header(default=None),
    ) -> BusinessMethodProfileReceiptResponse:
        try:
            result = service.publish(
                actor=actor(authorization),
                command=request.to_command(company_id=company_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            code = str(error)
            raise HTTPException(
                status_code=404 if code == "NOT_FOUND_OR_FORBIDDEN" else 403,
                detail=code if code == "NOT_FOUND_OR_FORBIDDEN" else "FORBIDDEN",
            ) from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
            if str(error) == "STALE_PROFILE_VERSION":
                raise HTTPException(status_code=409, detail="STALE_PROFILE_VERSION") from error
            raise HTTPException(status_code=422, detail="COMMAND_REJECTED") from error
        receipt = _receipt(result)
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            content=receipt.model_dump(mode="json"),
        )

    @router.get(
        "/enterprise/companies/{company_id}/business-method-profile/versions",
        response_model=BusinessMethodProfileVersionsResponse,
    )
    def list_profile_versions(
        company_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> BusinessMethodProfileVersionsResponse:
        try:
            versions = service.versions(
                actor=actor(authorization), company_id=company_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            code = str(error)
            raise HTTPException(
                status_code=404 if code == "NOT_FOUND_OR_FORBIDDEN" else 403,
                detail=code if code == "NOT_FOUND_OR_FORBIDDEN" else "FORBIDDEN",
            ) from error
        return BusinessMethodProfileVersionsResponse(
            company_id=company_id,
            versions=[
                BusinessMethodProfileVersionResponse(
                    profile_version_id=row.profile_version_id,
                    version=row.version,
                    schema_version=row.schema_version,
                    profile=BusinessMethodProfileContent.model_validate(row.profile),
                    content_sha256=row.content_sha256,
                )
                for row in versions
            ],
        )

    @router.post(
        "/cases/{case_id}/business-method-profile/adoptions",
        status_code=status.HTTP_201_CREATED,
        response_model=BusinessMethodProfileReceiptResponse,
    )
    def adopt_profile(
        case_id: UUID,
        request: AdoptBusinessMethodProfileRequest,
        authorization: str | None = Header(default=None),
    ) -> BusinessMethodProfileReceiptResponse:
        try:
            result = service.adopt(
                actor=actor(authorization),
                command=request.to_command(case_id=case_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            code = str(error)
            raise HTTPException(
                status_code=404 if code == "NOT_FOUND_OR_FORBIDDEN" else 403,
                detail=code if code == "NOT_FOUND_OR_FORBIDDEN" else "FORBIDDEN",
            ) from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_CONFLICT") from error
        except CommandExecutionError as error:
            code = str(error)
            if code in {"NOT_FOUND_OR_FORBIDDEN", "PROFILE_VERSION_NOT_FOUND_OR_FORBIDDEN"}:
                raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
            if code == "STALE_PROFILE_ADOPTION":
                raise HTTPException(status_code=409, detail=code) from error
            raise HTTPException(status_code=422, detail="COMMAND_REJECTED") from error
        receipt = _receipt(result)
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            content=receipt.model_dump(mode="json"),
        )

    @router.get(
        "/cases/{case_id}/business-method-profile/adoption",
        response_model=BusinessMethodProfileAdoptionResponse | None,
    )
    def get_current_adoption(
        case_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> BusinessMethodProfileAdoptionResponse | None:
        try:
            row = service.current_adoption(
                actor=actor(authorization), case_id=case_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            code = str(error)
            raise HTTPException(
                status_code=404 if code == "NOT_FOUND_OR_FORBIDDEN" else 403,
                detail=code if code == "NOT_FOUND_OR_FORBIDDEN" else "FORBIDDEN",
            ) from error
        if row is None:
            return None
        return BusinessMethodProfileAdoptionResponse(
            adoption_id=row.adoption_id,
            case_id=row.case_id,
            adoption_revision=row.adoption_revision,
            profile_version_id=row.profile_version_id,
            profile_version=row.profile_version,
            profile_content_sha256=row.profile_content_sha256,
        )

    return router
