from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.case.application.regulatory_profile import RegulatoryProfileService
from app.modules.case.application.regulatory_profile_commands import RecordRegulatoryProfileCommand
from app.modules.case.application.regulatory_profile_handler import RegulatoryProfileReadService
from app.modules.case.public.regulatory_profile_contracts import (
    RecordRegulatoryProfileRequest,
    RecordRegulatoryProfileResponse,
    RegulatoryProfilePageResponse,
    RegulatoryProfileProjection,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_patron_regulatory_profile_router(
    *,
    service: RegulatoryProfileService,
    read_service: RegulatoryProfileReadService,
    security_runtime: ConsultationSecurityRuntime,
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-regulatory-profiles"])

    @router.get(
        "/cases/{case_id}/regulatory-profiles",
        response_model=RegulatoryProfilePageResponse,
    )
    def list_regulatory_profiles(
        case_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> RegulatoryProfilePageResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            rows = read_service.list_for_case(
                actor=actor,
                case_id=case_id,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return RegulatoryProfilePageResponse(
            case_id=case_id,
            items=[
                RegulatoryProfileProjection(
                    profile_id=row.id,
                    case_id=row.case_id,
                    profile_version=row.profile_version,
                    status=row.status,
                    facts=row.facts_json,
                    source_refs=row.source_refs_json,
                    effective_from=row.effective_from,
                    effective_until=row.effective_until,
                )
                for row in rows
            ],
        )

    @router.post(
        "/cases/{case_id}/regulatory-profiles",
        response_model=RecordRegulatoryProfileResponse,
    )
    def record_regulatory_profile(
        case_id: UUID,
        request: RecordRegulatoryProfileRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            result = service.execute(
                actor=actor,
                command=RecordRegulatoryProfileCommand(**request.model_dump(), case_id=case_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except (IdempotencyKeyReusedError, CommandInProgressError) as error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="IDEMPOTENCY_CONFLICT"
            ) from error
        except CommandExecutionError as error:
            code = (
                status.HTTP_404_NOT_FOUND
                if str(error) == "CASE_NOT_FOUND_OR_FORBIDDEN"
                else status.HTTP_422_UNPROCESSABLE_CONTENT
            )
            raise HTTPException(status_code=code, detail=str(error)) from error
        reference = result.aggregate_refs[0]
        response = RecordRegulatoryProfileResponse(
            command_id=UUID(result.command_id),
            idempotency_key=UUID(result.idempotency_key),
            result_code="REGULATORY_PROFILE_RECORDED",
            profile_id=UUID(str(reference["aggregate_id"])),
            version=int(reference["aggregate_revision"]),
            event_ids=[UUID(event_id) for event_id in result.event_ids],
            replayed=result.replayed,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    return router
