from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import ValidationError

from app.interfaces.http.dependencies.auth import resolve_bearer_context as _resolve_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.preparation.application.commands import (
    EvaluatePreparationReadinessCommand,
    GenerateTechnicalDocumentCommand,
)
from app.modules.preparation.application.plan_commands import (
    CreatePreparationResponsePlanCommand,
)
from app.modules.preparation.application.review import PreparationReviewService
from app.modules.preparation.application.review_commands import (
    AddPreparationCorrectionCommand,
    CreateBuyerDocxResponseDraftCommand,
    CreateTechnicalResponseDraftCommand,
    DecidePreparationReviewCommand,
    RequestPreparationReviewCommand,
)
from app.modules.preparation.application.service import PreparationService
from app.modules.preparation.public.contracts import (
    AddPreparationCorrectionRequest,
    BuyerDocxInputsRequest,
    CreateBuyerDocxResponseDraftRequest,
    CreatePreparationResponsePlanRequest,
    CreateTechnicalResponseDraftRequest,
    DecidePreparationReviewRequest,
    EvaluatePreparationReadinessRequest,
    GeneratedDocumentProjection,
    GenerateTechnicalDocumentRequest,
    PreparationAggregateReference,
    PreparationCommandResponse,
    PreparationPackageProjection,
    PreparationReadinessProjection,
    PreparationResponseDraftListResponse,
    PreparationResponsePlanListResponse,
    PreparationResponsePlanProjection,
    PreparationReviewCorrectionProjection,
    PreparationReviewListResponse,
    PreparationReviewProjection,
    RequestPreparationReviewRequest,
    ResponseCoverageProjection,
    SelectedResponseDraft,
    TechnicalResponseDraftProjection,
)
from app.platform.events.dispatcher import (
    CommandExecutionError,
    CommandInProgressError,
    IdempotencyKeyReusedError,
)


def build_preparation_router(
    *, service: PreparationService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/collaborator", tags=["preparation"])

    @router.post(
        "/preparation/{package_id}/response-coverage", response_model=ResponseCoverageProjection
    )
    def read_response_coverage(
        package_id: UUID,
        selection: SelectedResponseDraft,
        authorization: str | None = Header(default=None),
    ):
        return _coverage_read(service, security_runtime, package_id, selection, authorization)

    @router.get("/preparation/{package_id}", response_model=PreparationPackageProjection)
    def read_package(
        package_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> PreparationPackageProjection:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            package, readiness, documents, response_drafts, draft_contents = (
                service.read_package_with_verified_drafts(
                    actor=actor, package_id=package_id, now=datetime.now(tz=UTC)
                )
            )
        except PermissionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
                ) from error
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return PreparationPackageProjection(
            package_id=package.id,
            case_id=package.case_id,
            assignment_id=package.assignment_id,
            dce_version_id=package.dce_version_id,
            state=package.state,
            aggregate_revision=package.aggregate_revision,
            latest_readiness=(
                PreparationReadinessProjection(
                    readiness_id=readiness.id,
                    revision=readiness.revision,
                    state=readiness.state,
                    blocker_codes=list(readiness.blocker_codes_json),
                    warning_codes=list(readiness.warning_codes_json),
                    checked_requirement_count=readiness.checked_requirement_count,
                    checked_task_count=readiness.checked_task_count,
                )
                if readiness is not None
                else None
            ),
            generated_documents=[
                GeneratedDocumentProjection(
                    document_id=document.id,
                    version=document.version,
                    document_kind=document.document_kind,
                    content_format=getattr(document, "content_format", "MARKDOWN"),
                    state=document.state,
                    readiness_revision=_readiness_revision(document=document, readiness=readiness),
                )
                for document in documents
            ],
            response_drafts=[
                TechnicalResponseDraftProjection(
                    draft_id=draft.draft_id,
                    version=draft.version,
                    state=draft.state,
                    section_codes=list(draft.section_codes_json),
                    source_refs=list(draft.source_refs_json),
                    responsible_role=draft.responsible_role,
                    content_sha256=getattr(draft, "content_sha256", None),
                    content_format=getattr(draft, "content_format", "MARKDOWN"),
                    content_provenance=getattr(draft, "content_provenance_json", None),
                    response_plan_id=getattr(draft, "response_plan_id", None),
                    response_plan_version=getattr(draft, "response_plan_version", None),
                    content=draft_contents.get((draft.draft_id, draft.version)),
                )
                for draft in response_drafts
            ],
        )

    @router.get(
        "/preparation/{package_id}/documents/{document_id}/content",
        responses={
            200: {"description": "Contenu Markdown privé d’un document généré."},
            401: {"description": "Bearer absent, invalide ou expiré."},
            403: {"description": "Document réservé au collaborateur affecté."},
            404: {"description": "Package ou document absent du tenant."},
            503: {"description": "Contenu privé temporairement indisponible."},
        },
    )
    def read_generated_document(
        package_id: UUID,
        document_id: UUID,
        download: bool = False,
        authorization: str | None = Header(default=None),
    ) -> StreamingResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            document, content = service.read_generated_document(
                actor=actor,
                package_id=package_id,
                document_id=document_id,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(status_code=404, detail="NOT_FOUND_OR_FORBIDDEN") from error
            raise HTTPException(status_code=403, detail="FORBIDDEN") from error
        except RuntimeError as error:
            if str(error) == "GENERATED_DOCUMENT_UNAVAILABLE":
                raise HTTPException(status_code=503, detail="DOCUMENT_UNAVAILABLE") from error
            raise
        disposition = "attachment" if download else "inline"
        is_docx = getattr(document, "content_format", "MARKDOWN") == "DOCX"
        extension = "docx" if is_docx else "md"
        filename = f"{document.document_kind.lower()}-v{document.version}.{extension}"
        return StreamingResponse(
            iter((content,)),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            if is_docx
            else "text/markdown",
            headers={
                "Content-Disposition": f'{disposition}; filename="{filename}"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @router.get("/preparation/{package_id}/response-drafts/{draft_id}/versions/{version}/content")
    def owned_response_content(
        package_id: UUID,
        draft_id: UUID,
        version: int,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        return _response_artifact_response(service, actor, package_id, draft_id, version)

    @router.post(
        "/cases/{case_id}/preparation/readiness",
        status_code=status.HTTP_201_CREATED,
        response_model=PreparationCommandResponse,
    )
    def evaluate_readiness(
        case_id: UUID,
        request: EvaluatePreparationReadinessRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch(
            service=service,
            actor=actor,
            command=EvaluatePreparationReadinessCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                package_id=request.package_id,
                case_id=case_id,
                assignment_id=request.assignment_id,
                dce_version_id=request.dce_version_id,
                expected_revision=request.expected_revision,
            ),
        )

    @router.post(
        "/preparation/{package_id}/documents",
        status_code=status.HTTP_201_CREATED,
        response_model=PreparationCommandResponse,
    )
    def generate_document(
        package_id: UUID,
        request: GenerateTechnicalDocumentRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch(
            service=service,
            actor=actor,
            command=GenerateTechnicalDocumentCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                package_id=package_id,
                document_id=request.command_id,
                expected_revision=request.expected_revision,
                readiness_revision=request.readiness_revision,
                document_kind=request.document_kind,
            ),
        )

    return router


def build_preparation_review_router(
    *, service: PreparationReviewService, security_runtime: ConsultationSecurityRuntime
) -> APIRouter:
    router = APIRouter(prefix="/api/v1/preparation", tags=["preparation-review"])

    @router.post("/{package_id}/response-coverage", response_model=ResponseCoverageProjection)
    def read_response_coverage(
        package_id: UUID,
        selection: SelectedResponseDraft,
        authorization: str | None = Header(default=None),
    ):
        return _coverage_read(service, security_runtime, package_id, selection, authorization)

    @router.get(
        "/{package_id}/reviews",
        response_model=PreparationReviewListResponse,
    )
    def read_reviews(
        package_id: UUID,
        authorization: str | None = Header(default=None),
    ) -> PreparationReviewListResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            reviews = service.read_reviews(
                actor=actor, package_id=package_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
                ) from error
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        return PreparationReviewListResponse(
            package_id=package_id,
            reviews=[
                PreparationReviewProjection(
                    review_id=review.review_id,
                    package_id=review.package_id,
                    target_document_id=review.target_document_id,
                    target_version=review.target_version,
                    target_draft_id=review.target_draft_id,
                    target_draft_version=review.target_draft_version,
                    target_content_sha256=review.target_content_sha256,
                    revision=review.revision,
                    state=review.state,
                    decision_code=review.decision_code,
                    decision_note=review.decision_note,
                    corrections=[
                        PreparationReviewCorrectionProjection(
                            correction_id=correction.id,
                            review_revision=correction.review_revision,
                            revision=correction.revision,
                            target_document_id=correction.target_document_id,
                            target_draft_id=correction.target_draft_id,
                            target_draft_version=correction.target_draft_version,
                            target_content_sha256=correction.target_content_sha256,
                            correction_code=correction.correction_code,
                            instruction=correction.instruction,
                            source_locator=correction.source_locator,
                        )
                        for correction in corrections
                    ],
                )
                for review, corrections in reviews
            ],
        )

    @router.get("/{package_id}/response-drafts/{draft_id}/versions/{version}/content")
    def review_response_content(
        package_id: UUID,
        draft_id: UUID,
        version: int,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        return _response_artifact_response(service, actor, package_id, draft_id, version)

    @router.post("/{package_id}/buyer-docx-inputs")
    def buyer_docx_inputs(
        package_id: UUID,
        request: BuyerDocxInputsRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        try:
            return service.read_buyer_docx_inputs(
                actor=actor,
                package_id=package_id,
                source_response=request.source_response,
                now=datetime.now(tz=UTC),
            )
        except PermissionError as error:
            raise HTTPException(
                status_code=404 if str(error) == "NOT_FOUND_OR_FORBIDDEN" else 403,
                detail="NOT_FOUND_OR_FORBIDDEN",
            ) from error
        except (CommandExecutionError, ValueError) as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @router.post(
        "/{package_id}/buyer-response-drafts",
        response_model=PreparationCommandResponse,
        status_code=201,
    )
    def create_buyer_docx(
        package_id: UUID,
        request: CreateBuyerDocxResponseDraftRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization, context_resolver=security_runtime.context_resolver
        )
        return _dispatch_review(
            service=service,
            actor=actor,
            command=CreateBuyerDocxResponseDraftCommand(
                **request.model_dump(), package_id=package_id
            ),
        )

    @router.get(
        "/{package_id}/response-drafts",
        response_model=PreparationResponseDraftListResponse,
    )
    def read_response_drafts(
        package_id: UUID,
        response: Response,
        authorization: str | None = Header(default=None),
    ) -> PreparationResponseDraftListResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            package_revision = service.read_response_drafts_package_revision(
                actor=actor, package_id=package_id, now=datetime.now(tz=UTC)
            )
            verified = service.read_verified_response_drafts(
                actor=actor, package_id=package_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
                ) from error
            if str(error) == "RESPONSE_DRAFT_UNKNOWN":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="RESPONSE_DRAFT_UNKNOWN",
                ) from error
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        response.headers["Cache-Control"] = "no-store"
        return PreparationResponseDraftListResponse(
            package_id=package_id,
            package_revision=package_revision,
            drafts=[
                TechnicalResponseDraftProjection(
                    draft_id=draft.draft_id,
                    version=draft.version,
                    state=draft.state,
                    section_codes=list(draft.section_codes_json),
                    source_refs=list(draft.source_refs_json),
                    responsible_role=draft.responsible_role,
                    content_sha256=draft.content_sha256,
                    content_format=getattr(draft, "content_format", "MARKDOWN"),
                    content_provenance=getattr(draft, "content_provenance_json", None),
                    response_plan_id=draft.response_plan_id,
                    response_plan_version=draft.response_plan_version,
                    content=content,
                )
                for draft, content in verified
            ],
        )

    @router.get(
        "/{package_id}/response-plans",
        response_model=PreparationResponsePlanListResponse,
    )
    def read_response_plans(
        package_id: UUID,
        response: Response,
        authorization: str | None = Header(default=None),
    ) -> PreparationResponsePlanListResponse:
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            plans = service.read_response_plans(
                actor=actor, package_id=package_id, now=datetime.now(tz=UTC)
            )
        except PermissionError as error:
            if str(error) == "NOT_FOUND_OR_FORBIDDEN":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
                ) from error
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN"
            ) from error
        response.headers["Cache-Control"] = "no-store"
        return PreparationResponsePlanListResponse(
            package_id=package_id,
            plans=[
                PreparationResponsePlanProjection(
                    plan_id=plan.plan_id,
                    version=plan.version,
                    package_id=plan.package_id,
                    dce_version_id=plan.dce_version_id,
                    state=plan.state,
                    plan_sha256=plan.plan_sha256,
                    content=plan.content_json,
                )
                for plan in plans
            ],
        )

    @router.post(
        "/{package_id}/response-plans",
        response_model=PreparationCommandResponse,
    )
    def create_response_plan(
        package_id: UUID,
        request: CreatePreparationResponsePlanRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch_review(
            service=service,
            actor=actor,
            command=CreatePreparationResponsePlanCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                package_id=package_id,
                plan_id=request.plan_id,
                expected_package_revision=request.expected_package_revision,
                items=[item.model_dump() for item in request.items],
            ),
        )

    @router.post("/{package_id}/reviews", response_model=PreparationCommandResponse)
    def request_review(
        package_id: UUID,
        request: RequestPreparationReviewRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch_review(
            service=service,
            actor=actor,
            command=RequestPreparationReviewCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                review_id=request.review_id,
                package_id=package_id,
                target_document_id=request.target_document_id,
                target_version=request.target_version,
                target_draft_id=request.target_draft_id,
                target_draft_version=request.target_draft_version,
                target_content_sha256=request.target_content_sha256,
                expected_package_revision=request.expected_package_revision,
            ),
        )

    @router.post(
        "/{package_id}/reviews/{review_id}/decision",
        response_model=PreparationCommandResponse,
    )
    def decide_review(
        package_id: UUID,
        review_id: UUID,
        request: DecidePreparationReviewRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        try:
            command = DecidePreparationReviewCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                review_id=review_id,
                package_id=package_id,
                target_document_id=request.target_document_id,
                target_draft_id=request.target_draft_id,
                target_draft_version=request.target_draft_version,
                target_content_sha256=request.target_content_sha256,
                expected_review_revision=request.expected_review_revision,
                decision_code=request.decision_code,
                decision_note=request.decision_note,
            )
        except ValidationError as error:
            raise HTTPException(
                status_code=422, detail="PREPARATION_REVIEW_INPUT_INVALID"
            ) from error
        return _dispatch_review(service=service, actor=actor, command=command)

    @router.post(
        "/{package_id}/reviews/{review_id}/corrections",
        response_model=PreparationCommandResponse,
    )
    def add_correction(
        package_id: UUID,
        review_id: UUID,
        request: AddPreparationCorrectionRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch_review(
            service=service,
            actor=actor,
            command=AddPreparationCorrectionCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                review_id=review_id,
                package_id=package_id,
                target_document_id=request.target_document_id,
                target_draft_id=request.target_draft_id,
                target_draft_version=request.target_draft_version,
                target_content_sha256=request.target_content_sha256,
                correction_code=request.correction_code,
                instruction=request.instruction,
                source_locator=request.source_locator,
                corrected_content=request.corrected_content,
            ),
        )

    @router.post("/{package_id}/response-drafts", response_model=PreparationCommandResponse)
    def create_response_draft(
        package_id: UUID,
        request: CreateTechnicalResponseDraftRequest,
        authorization: str | None = Header(default=None),
    ):
        actor = _resolve_context(
            authorization=authorization,
            context_resolver=security_runtime.context_resolver,
        )
        return _dispatch_review(
            service=service,
            actor=actor,
            command=CreateTechnicalResponseDraftCommand(
                command_id=request.command_id,
                idempotency_key=request.idempotency_key,
                correlation_id=request.correlation_id,
                draft_id=request.draft_id,
                package_id=package_id,
                source_document_id=request.source_document_id,
                expected_package_revision=request.expected_package_revision,
                section_codes=request.section_codes,
                source_refs=request.source_refs,
                contributions=request.contributions,
            ),
        )

    return router


def _dispatch_review(*, service: PreparationReviewService, actor, command):
    try:
        result = service.execute(actor=actor, command=command, now=datetime.now(tz=UTC))
    except PermissionError as error:
        if str(error) == "NOT_FOUND_OR_FORBIDDEN":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
            ) from error
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
    except IdempotencyKeyReusedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="IDEMPOTENCY_KEY_REUSED"
        ) from error
    except CommandInProgressError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="COMMAND_IN_PROGRESS"
        ) from error
    except CommandExecutionError as error:
        detail = str(error)
        code = (
            status.HTTP_404_NOT_FOUND
            if detail == "NOT_FOUND_OR_FORBIDDEN"
            else status.HTTP_409_CONFLICT
            if detail == "VERSION_CONFLICT"
            else status.HTTP_422_UNPROCESSABLE_CONTENT
        )
        raise HTTPException(status_code=code, detail=detail) from error
    response = PreparationCommandResponse(
        command_id=result.command_id,
        idempotency_key=result.idempotency_key,
        result_code=result.result_code,
        aggregate_refs=[PreparationAggregateReference(**ref) for ref in result.aggregate_refs],
        event_ids=list(result.event_ids),
        replayed=result.replayed,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )


def _readiness_revision(*, document, readiness) -> int:
    if readiness is not None and readiness.id == document.readiness_id:
        return readiness.revision
    return 0


def _dispatch(*, service: PreparationService, actor, command):
    try:
        result = service.execute(actor=actor, command=command, now=datetime.now(tz=UTC))
    except PermissionError as error:
        if str(error) == "NOT_FOUND_OR_FORBIDDEN":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="NOT_FOUND_OR_FORBIDDEN"
            ) from error
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
    except IdempotencyKeyReusedError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="IDEMPOTENCY_KEY_REUSED"
        ) from error
    except CommandInProgressError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="COMMAND_IN_PROGRESS"
        ) from error
    except CommandExecutionError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)
        ) from error
    response = PreparationCommandResponse(
        command_id=result.command_id,
        idempotency_key=result.idempotency_key,
        result_code=result.result_code,
        aggregate_refs=[PreparationAggregateReference(**ref) for ref in result.aggregate_refs],
        event_ids=list(result.event_ids),
        replayed=result.replayed,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED,
        content=response.model_dump(mode="json"),
    )


def _response_artifact_response(service, actor, package_id, draft_id, version):
    try:
        draft, content = service.read_response_draft_bytes(
            actor=actor,
            package_id=package_id,
            draft_id=draft_id,
            version=version,
            now=datetime.now(tz=UTC),
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=404 if str(error) == "NOT_FOUND_OR_FORBIDDEN" else 403,
            detail="NOT_FOUND_OR_FORBIDDEN",
        ) from error
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=503, detail="RESPONSE_DRAFT_UNKNOWN") from error
    docx = getattr(draft, "content_format", "MARKDOWN") == "DOCX"
    return StreamingResponse(
        iter((content,)),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if docx
        else "text/markdown",
        headers={
            "Content-Disposition": (
                f'attachment; filename="reponse-v{version}.{"docx" if docx else "md"}"'
            ),
            "Cache-Control": "no-store",
            "X-Content-SHA256": draft.content_sha256,
            "X-Content-Type-Options": "nosniff",
        },
    )


def _coverage_read(service, runtime, package_id, selection, authorization):
    actor = _resolve_context(authorization=authorization, context_resolver=runtime.context_resolver)
    try:
        result = service.read_response_coverage(
            actor=actor, package_id=package_id, selection=selection, now=datetime.now(tz=UTC)
        )
    except PermissionError as error:
        raise HTTPException(
            status_code=404 if str(error) == "NOT_FOUND_OR_FORBIDDEN" else 403,
            detail="NOT_FOUND_OR_FORBIDDEN"
            if str(error) == "NOT_FOUND_OR_FORBIDDEN"
            else "FORBIDDEN",
        ) from error
    except CommandExecutionError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return JSONResponse(
        content=result.model_dump(mode="json"), headers={"Cache-Control": "no-store"}
    )
