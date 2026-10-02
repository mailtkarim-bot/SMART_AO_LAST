"""P7 transfer snapshot writes for the Patron and assigned Conducteur read."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import JSONResponse, Response

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.patron_action.application.case_handover import CaseHandoverService
from app.modules.patron_action.application.handover_commands import (
    RecordCaseHandoverSnapshotCommand,
)
from app.modules.patron_action.public.handover_contracts import (
    CaseHandoverOfferOptionResponse,
    CaseHandoverOfferOptionsResponse,
    CaseHandoverSnapshotResponse,
    CaseHandoverSnapshotsResponse,
    RecordCaseHandoverRequest,
    RecordCaseHandoverResponse,
)
from app.platform.events.dispatcher import CommandExecutionError


def build_case_handover_routers(
    *, service: CaseHandoverService, security_runtime: ConsultationSecurityRuntime
) -> tuple[APIRouter, APIRouter]:
    patron = APIRouter(prefix="/api/v1/patron", tags=["case-handover"])
    cases = APIRouter(prefix="/api/v1/cases", tags=["case-handover"])

    @patron.get(
        "/cases/{case_id}/p7-handover-options", response_model=CaseHandoverOfferOptionsResponse
    )
    def list_handover_options(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            items = service.list_offer_options(
                actor=actor, case_id=case_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return CaseHandoverOfferOptionsResponse(
            case_id=case_id,
            items=[CaseHandoverOfferOptionResponse.model_validate(item) for item in items],
        )

    @patron.post(
        "/cases/{case_id}/p7-handover",
        response_model=RecordCaseHandoverResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def record_handover(
        case_id: UUID,
        request: RecordCaseHandoverRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = service.record(
                actor=actor,
                command=RecordCaseHandoverSnapshotCommand(**request.model_dump(), case_id=case_id),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        response = RecordCaseHandoverResponse(
            status=result.status, result_code=result.result_code, replayed=result.replayed
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
        )

    @cases.get("/{case_id}/p7-handover", response_model=CaseHandoverSnapshotsResponse)
    def read_handover(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = service.read(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return CaseHandoverSnapshotsResponse(
            case_id=case_id,
            items=[
                CaseHandoverSnapshotResponse(
                    snapshot_id=row.id,
                    outcome_id=row.outcome_id,
                    lot_reference=row.lot_reference,
                    submission_package_id=row.submission_package_id,
                    package_version=row.package_version,
                    manifest_sha256=row.manifest_sha256,
                    revision=row.revision,
                    created_at=row.created_at.isoformat(),
                    snapshot=row.snapshot_json,
                )
                for row in rows
            ],
        )

    @cases.get("/{case_id}/p7-handover/{snapshot_id}/offer-document")
    def download_offer_document(
        case_id: UUID,
        snapshot_id: UUID,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            content, digest = service.download_offer_document(
                actor=actor,
                case_id=case_id,
                snapshot_id=snapshot_id,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
            ) from error
        except RuntimeError as error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)
            ) from error
        return Response(
            content=content,
            media_type="text/markdown",
            headers={
                "Cache-Control": "no-store",
                "Content-Disposition": 'attachment; filename="offre-technique.md"',
                "X-Content-SHA256": digest,
            },
        )

    return patron, cases
