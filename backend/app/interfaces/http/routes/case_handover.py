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
    AcknowledgeHandoverCommand,
    RecordCaseHandoverSnapshotCommand,
)
from app.modules.patron_action.public.handover_contracts import (
    AcknowledgeHandoverRequest,
    CaseHandoverOfferOptionResponse,
    CaseHandoverOfferOptionsResponse,
    CaseHandoverSnapshotResponse,
    CaseHandoverSnapshotsResponse,
    HandoverContractOptionsResponse,
    RecordCaseHandoverRequest,
    RecordCaseHandoverResponse,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_case_handover_routers(
    *, service: CaseHandoverService, security_runtime: ConsultationSecurityRuntime
) -> tuple[APIRouter, APIRouter]:
    patron = APIRouter(prefix="/api/v1/patron", tags=["case-handover"])
    cases = APIRouter(prefix="/api/v1/cases", tags=["case-handover"])

    @patron.get(
        "/cases/{case_id}/p7-handover-options", response_model=CaseHandoverOfferOptionsResponse
    )
    def list_handover_options(
        case_id: UUID, response: Response, authorization: str | None = Header(default=None)
    ):
        response.headers["Cache-Control"] = "no-store"
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
        except IdempotencyKeyReusedError as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_KEY_REUSED") from error
        except CommandInProgressError as error:
            raise HTTPException(status_code=409, detail="COMMAND_IN_PROGRESS") from error
        except CommandExecutionError as error:
            raise HTTPException(
                status_code=409
                if str(error)
                in {
                    "VERSION_CONFLICT",
                    "HANDOVER_CASE_CONTEXT_CONFLICT",
                    "HANDOVER_OUTCOME_STALE",
                    "HANDOVER_OFFER_VERSION_CONFLICT",
                    "HANDOVER_CONTRACT_VERSION_CONFLICT",
                    "HANDOVER_CONTRACT_SUPERSEDED",
                }
                else status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=str(error),
            ) from error
        response = RecordCaseHandoverResponse(
            status=result.status,
            result_code=result.result_code,
            replayed=result.replayed,
            command_id=UUID(result.command_id),
            idempotency_key=UUID(result.idempotency_key),
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
            content=response.model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )

    @patron.get(
        "/cases/{case_id}/p7-handover/contracts", response_model=HandoverContractOptionsResponse
    )
    def contract_options(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = service.contract_options(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
            conditions = service.condition_options(
                actor=actor, case_id=case_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        payload = HandoverContractOptionsResponse(
            case_id=case_id,
            items=list(rows[:100]),
            source_context_sha256=conditions["source_context_sha256"],
            condition_options=conditions["items"][:100],
            truncated=len(rows) > 100 or len(conditions["items"]) > 100,
        )
        return JSONResponse(
            content=payload.model_dump(mode="json"), headers={"Cache-Control": "no-store"}
        )

    @cases.get("/{case_id}/p7-handover/history", response_model=CaseHandoverSnapshotsResponse)
    def history(
        case_id: UUID,
        response: Response,
        before_snapshot_id: UUID | None = None,
        authorization: str | None = Header(default=None),
    ):
        response.headers["Cache-Control"] = "no-store"
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            rows = service.history(
                actor=actor,
                case_id=case_id,
                before_snapshot_id=before_snapshot_id,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
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
                    view_sha256=row.view_sha256,
                    source_state=row.source_state,
                    source_reasons=list(row.source_reasons),
                    receipts=list(row.receipts),
                    receipts_truncated=row.receipts_truncated,
                )
                for row in rows[:20]
            ],
            next_cursor=rows[19].id if len(rows) > 20 else None,
            truncated=len(rows) > 20,
        )

    @cases.get("/{case_id}/p7-handover/{snapshot_id}", response_model=CaseHandoverSnapshotResponse)
    def read_exact(
        case_id: UUID,
        snapshot_id: UUID,
        response: Response,
        authorization: str | None = Header(default=None),
    ):
        response.headers["Cache-Control"] = "no-store"
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            row = service.read_exact(
                actor=actor, case_id=case_id, snapshot_id=snapshot_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
        return CaseHandoverSnapshotResponse(
            snapshot_id=row.id,
            outcome_id=row.outcome_id,
            lot_reference=row.lot_reference,
            submission_package_id=row.submission_package_id,
            package_version=row.package_version,
            manifest_sha256=row.manifest_sha256,
            revision=row.revision,
            created_at=row.created_at.isoformat(),
            snapshot=row.snapshot_json,
            view_sha256=row.view_sha256,
            source_state=row.source_state,
            source_reasons=list(row.source_reasons),
            receipts=list(row.receipts),
            receipts_truncated=row.receipts_truncated,
        )

    @cases.post(
        "/{case_id}/p7-handover/{snapshot_id}/receipts", response_model=RecordCaseHandoverResponse
    )
    def acknowledge(
        case_id: UUID,
        snapshot_id: UUID,
        request: AcknowledgeHandoverRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            result = service.acknowledge(
                actor=actor,
                command=AcknowledgeHandoverCommand(
                    **request.model_dump(), case_id=case_id, snapshot_id=snapshot_id
                ),
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except IdempotencyKeyReusedError as error:
            raise HTTPException(status_code=409, detail="IDEMPOTENCY_KEY_REUSED") from error
        except CommandInProgressError as error:
            raise HTTPException(status_code=409, detail="COMMAND_IN_PROGRESS") from error
        except CommandExecutionError as error:
            detail = str(error)
            raise HTTPException(
                status_code=404
                if detail == "HANDOVER_SOURCE_NOT_FOUND_OR_FORBIDDEN"
                else 409
                if detail == "HANDOVER_VIEW_CONFLICT"
                else 422,
                detail=detail,
            ) from error
        return JSONResponse(
            status_code=200 if result.replayed else 201,
            content=RecordCaseHandoverResponse(
                status=result.status,
                result_code=result.result_code,
                replayed=result.replayed,
                command_id=UUID(result.command_id),
                idempotency_key=UUID(result.idempotency_key),
            ).model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )

    @cases.get("/{case_id}/p7-handover", response_model=CaseHandoverSnapshotsResponse)
    def read_handover(
        case_id: UUID, response: Response, authorization: str | None = Header(default=None)
    ):
        response.headers["Cache-Control"] = "no-store"
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
                    view_sha256=row.view_sha256,
                    source_state=row.source_state,
                    source_reasons=list(row.source_reasons),
                    receipts=list(row.receipts),
                    receipts_truncated=row.receipts_truncated,
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
            content, digest, content_format = service.download_offer_document(
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
            media_type=(
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if content_format == "DOCX"
                else "text/markdown"
            ),
            headers={
                "Cache-Control": "no-store",
                "Content-Disposition": (
                    'attachment; filename="offre-technique.docx"'
                    if content_format == "DOCX"
                    else 'attachment; filename="offre-technique.md"'
                ),
                "X-Content-Type-Options": "nosniff",
                "X-Content-SHA256": digest,
            },
        )

    return patron, cases
