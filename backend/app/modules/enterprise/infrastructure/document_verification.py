"""Current internal verification, from append-only human acts with legacy fallback."""

from uuid import UUID

import sqlalchemy as sa
from app.modules.enterprise.infrastructure.models import (
    EnterpriseDocumentRecord,
    EnterpriseDocumentVerificationRecord,
)
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement


def document_verification_status_expression() -> ColumnElement[str]:
    latest = (
        sa.select(EnterpriseDocumentVerificationRecord.outcome)
        .where(
            EnterpriseDocumentVerificationRecord.tenant_id == EnterpriseDocumentRecord.tenant_id,
            EnterpriseDocumentVerificationRecord.document_id == EnterpriseDocumentRecord.id,
        )
        .order_by(EnterpriseDocumentVerificationRecord.revision.desc())
        .limit(1)
        .correlate(EnterpriseDocumentRecord)
        .scalar_subquery()
    )
    return sa.func.coalesce(latest, EnterpriseDocumentRecord.verification_status)


def current_document_verification_status(
    session: Session, *, tenant_id: UUID | str, document_id: UUID
) -> str | None:
    return session.scalar(
        sa.select(document_verification_status_expression()).where(
            EnterpriseDocumentRecord.tenant_id == tenant_id,
            EnterpriseDocumentRecord.id == document_id,
        )
    )
