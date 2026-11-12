import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.patron_action.infrastructure.models.rex import CaseRexRecord


def execution_reuse_context_state(session, tenant_id, record):
    """Revalidate an execution decision without rewriting its historical declaration."""
    from app.modules.patron_action.infrastructure.models.case_interview import CaseInterviewRecord
    from app.modules.pricing.infrastructure.case_closure_reader import (
        case_source_identity,
        source_context_state,
    )

    snapshot = record.source_snapshot_json
    reuse = snapshot.get("execution_reuse")
    if not reuse:
        return "UNKNOWN"
    interview = session.scalar(
        sa.select(CaseInterviewRecord).where(
            CaseInterviewRecord.tenant_id == tenant_id,
            CaseInterviewRecord.id == record.source_interview_id,
        )
    )
    rex = session.scalar(
        sa.select(CaseRexRecord).where(
            CaseRexRecord.tenant_id == tenant_id, CaseRexRecord.id == record.source_rex_id
        )
    )
    target = session.scalar(
        sa.select(CaseRecord).where(
            CaseRecord.tenant_id == tenant_id, CaseRecord.id == record.target_case_id
        )
    )
    source = (
        session.scalar(
            sa.select(CaseRecord).where(
                CaseRecord.tenant_id == tenant_id, CaseRecord.id == interview.case_id
            )
        )
        if interview
        else None
    )
    if not all((target, source, rex)) or not rex.execution_source_json:
        return "REVIEW_REQUIRED"
    states = (
        source_context_state(
            reuse.get("target_case_source"), case_source_identity(session, target)
        ),
        source_context_state(
            rex.execution_source_json.get("case_source"), case_source_identity(session, source)
        ),
    )
    return (
        "REVIEW_REQUIRED"
        if "REVIEW_REQUIRED" in states
        else "UNKNOWN"
        if "UNKNOWN" in states
        else "CURRENT"
    )
