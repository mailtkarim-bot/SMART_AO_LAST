"""Revalidate an exact native human act without following downstream conditions."""

import sqlalchemy as sa

from app.modules.case.infrastructure.analysis_summary_reader import (
    SqlAlchemyCaseAnalysisSummaryReader,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord, DceVersionRecord
from app.modules.decision.infrastructure.models.risk import DecisionRiskRecord


def _clear_sources(session, *_):
    for key in list(session.info):
        if isinstance(key, tuple) and key and key[0] == "decision-assessment-sources":
            session.info.pop(key, None)


def _before_statement(state):
    if not state.is_select:
        _clear_sources(state.session)


def assessment_reference_is_current(
    session, *, tenant_id, case_id, aggregate_id, aggregate_revision, content_hash
):
    if not content_hash or aggregate_revision < 1:
        return False
    if not session.info.get("decision-source-events"):
        sa.event.listen(session, "after_flush", _clear_sources)
        sa.event.listen(session, "after_transaction_end", _clear_sources)
        sa.event.listen(session, "do_orm_execute", _before_statement)
        session.info["decision-source-events"] = True
    if session.new or session.dirty or session.deleted:
        session.flush()
    # Transaction-local only: never cache a source/tenant across requests.
    key = ("decision-assessment-sources", tenant_id, case_id)
    if key not in session.info:
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
                for model, condition, identity in [
                    (
                        DecisionRiskRecord,
                        DecisionRiskRecord.case_id == case_id,
                        DecisionRiskRecord.id,
                    ),
                    (
                        DceRequirementRecord,
                        DceRequirementRecord.dce_version_id == case.applicable_dce_version_id,
                        DceRequirementRecord.id,
                    ),
                    (
                        DceDocumentRecord,
                        DceDocumentRecord.dce_version_id == case.applicable_dce_version_id,
                        DceDocumentRecord.id,
                    ),
                    (
                        DceVersionRecord,
                        DceVersionRecord.id == case.applicable_dce_version_id,
                        DceVersionRecord.id,
                    ),
                ]:
                    session.scalars(
                        sa.select(model)
                        .where(model.tenant_id == tenant_id, condition)
                        .execution_options(populate_existing=True)
                        .order_by(identity)
                        .with_for_update(nowait=True)
                    ).all()
                summary = SqlAlchemyCaseAnalysisSummaryReader(session).get(
                    tenant_id=tenant_id, case_id=case_id, include_follow_ups=False
                )
            session.info[key] = summary
        except sa.exc.OperationalError as error:
            if getattr(error.orig, "sqlstate", None) in {"55P03", "40001"}:
                return False
            raise
        except ValueError:
            return False
    summary = session.info[key]
    if summary is None or summary["source_context_state"] != "CURRENT":
        return False
    for axis in summary["axes"]:
        for point in axis["items"]:
            act = point.get("human_assessment")
            if act and act["assessment_id"] == aggregate_id:
                return (
                    point["source_state"] == "CURRENT_SOURCE"
                    and act["state"] == "CURRENT"
                    and act["revision"] == aggregate_revision
                    and act["source_context_sha256"] == content_hash.lower()
                )
    return False
