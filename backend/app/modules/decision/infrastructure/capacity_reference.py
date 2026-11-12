"""Revalidate a selected immutable capacity hypothesis, never its business suitability."""

import sqlalchemy as sa

from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.optimization.infrastructure.dated_service import read_dated_capacity_in_session


def capacity_reference_is_current(
    session, *, tenant_id, case_id, aggregate_id, aggregate_revision, content_hash
):
    if not content_hash or aggregate_revision < 1:
        return False
    try:
        with session.begin_nested():
            case = session.scalar(
                sa.select(CaseRecord)
                .where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
                .execution_options(populate_existing=True)
                .with_for_update(nowait=True)
            )
            if case is None or case.lifecycle != "ACTIVE" or case.dce_freshness != "CURRENT":
                return False
            current = read_dated_capacity_in_session(session, tenant_id=tenant_id, case_id=case_id)[
                "current"
            ]
            return bool(
                current
                and current["run_id"] == str(aggregate_id)
                and current["revision"] == aggregate_revision
                and current["input_sha256"] == content_hash.lower()
            )
    except sa.exc.OperationalError:
        return False
