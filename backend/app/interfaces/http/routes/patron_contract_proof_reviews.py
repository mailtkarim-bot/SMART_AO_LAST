# ruff: noqa: E501
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, status

from app.interfaces.http.dependencies.auth import resolve_bearer_context
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.dce.application.contract_review_handler import ContractProofReviewReadService
from app.modules.dce.public.contracts import (
    ContractProofReviewPageResponse,
    ContractProofReviewResponse,
)


def build_patron_contract_proof_review_router(*, service: ContractProofReviewReadService, security_runtime: ConsultationSecurityRuntime) -> APIRouter:
    router = APIRouter(prefix="/api/v1/patron", tags=["patron-contract-proof-reviews"])
    @router.get("/cases/{case_id}/contract-proof-reviews", response_model=ContractProofReviewPageResponse)
    def list_reviews(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            rows = service.list_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return ContractProofReviewPageResponse(case_id=case_id, items=[ContractProofReviewResponse(review_id=row.id, proof_id=row.proof_id, reviewer_id=row.reviewer_id, reviewed_revision=row.reviewed_revision, decision=row.decision, rationale=row.rationale) for row in rows])

    @router.get("/cases/{case_id}/contract-proof-reviews/latest", response_model=ContractProofReviewPageResponse)
    def list_latest_reviews(case_id: UUID, authorization: str | None = Header(default=None)):
        actor = resolve_bearer_context(authorization=authorization, context_resolver=security_runtime.context_resolver)
        try:
            rows = service.latest_for_case(actor=actor, case_id=case_id, now=datetime.now(tz=UTC))
        except PermissionError as error:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN") from error
        return ContractProofReviewPageResponse(case_id=case_id, items=[ContractProofReviewResponse(review_id=row.id, proof_id=row.proof_id, reviewer_id=row.reviewer_id, reviewed_revision=row.reviewed_revision, decision=row.decision, rationale=row.rationale) for row in rows])
    return router
