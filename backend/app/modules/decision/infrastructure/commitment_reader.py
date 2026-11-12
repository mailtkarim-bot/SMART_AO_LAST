"""One tenant-scoped snapshot of the card and native decision history."""

import sqlalchemy as sa

from app.modules.case.application.analysis_summary import AXES
from app.modules.case.infrastructure.analysis_dossier_reader import read_analysis_dossier
from app.modules.case.infrastructure.models.analysis_assessment import AnalysisAssessmentRecord
from app.modules.case.infrastructure.models.business_method_profile_adoption import (
    CaseBusinessMethodProfileAdoptionRecord,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.case.public.analysis_summary_contracts import CaseAnalysisSummaryResponse
from app.modules.decision.application.commitment_card import project_commitment_points
from app.modules.decision.infrastructure.models.decision import (
    DecisionConditionRecord,
    DecisionConditionTransitionRecord,
    DecisionContextRecord,
    DecisionContextReferenceRecord,
    DecisionRecord,
)
from app.modules.decision.infrastructure.repositories import SqlAlchemyDecisionLifecycleRepository


def read_commitment_card(session, *, tenant_id, case_id, session_factory):
    case = session.scalar(
        sa.select(CaseRecord).where(CaseRecord.tenant_id == tenant_id, CaseRecord.id == case_id)
    )
    if case is None:
        raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
    try:
        summary = read_analysis_dossier(
            session, session_factory=session_factory, tenant_id=tenant_id, case_id=case_id
        )
    except ValueError:
        summary = None
    if summary:
        summary = CaseAnalysisSummaryResponse.model_validate(summary).model_dump(mode="json")
    points = project_commitment_points(summary) if summary else []
    repository = SqlAlchemyDecisionLifecycleRepository()
    references = [
        dict(
            aggregate_type="CASE",
            aggregate_id=str(case.id),
            aggregate_revision=case.aggregate_revision,
            reference_role="AFFAIRE",
            content_hash=None,
        )
    ]
    for row in points:
        point = row["point"]
        if point["source_state"] != "CURRENT_SOURCE":
            continue
        if point["kind"] == "REQUIREMENT" and point["native_state"] == "CONFIRMED":
            references.append(
                dict(
                    aggregate_type="DCE_REQUIREMENT",
                    aggregate_id=point["item_id"],
                    aggregate_revision=point["native_revision"],
                    content_hash=None,
                    reference_role="CLAUSE",
                )
            )
        act = point.get("human_assessment")
        if act and act["state"] == "CURRENT":
            references.append(
                dict(
                    aggregate_type="ANALYSIS_ASSESSMENT",
                    aggregate_id=act["assessment_id"],
                    aggregate_revision=act["revision"],
                    content_hash=act["source_context_sha256"],
                    reference_role="CRITICAL_POINT",
                )
            )
    if summary:
        for axis in summary["axes"]:
            for plan in axis.get("capacity_plans", []):
                if plan["state"] == "RECORDED" and plan["details"]:
                    references.append(
                        dict(
                            aggregate_type="CAPACITY_RUN",
                            aggregate_id=plan["run_id"],
                            aggregate_revision=plan["revision"],
                            content_hash=plan["input_sha256"],
                            reference_role="CAPACITY_HYPOTHESIS",
                        )
                    )
    adoption = session.scalar(
        sa.select(CaseBusinessMethodProfileAdoptionRecord)
        .where(
            CaseBusinessMethodProfileAdoptionRecord.tenant_id == tenant_id,
            CaseBusinessMethodProfileAdoptionRecord.case_id == case_id,
        )
        .order_by(CaseBusinessMethodProfileAdoptionRecord.adoption_revision.desc())
        .limit(1)
    )
    if adoption:
        profile = dict(
            aggregate_type="BUSINESS_METHOD_PROFILE",
            aggregate_id=str(adoption.profile_version_id),
            aggregate_revision=adoption.profile_version,
            content_hash=adoption.profile_content_sha256,
            reference_role="METHOD_PROFILE",
        )
        if repository.context_reference_is_valid(
            session=session,
            tenant_id=tenant_id,
            case_id=case_id,
            **{
                k: profile[k]
                for k in ["aggregate_type", "aggregate_id", "aggregate_revision", "content_hash"]
            },
        ):
            references.append(profile)
            for row in points:
                for relation in row["point"].get("follow_ups", []):
                    if relation["kind"] == "CONTRACT_IMPACT":
                        references.append(
                            dict(
                                aggregate_type="CONTRACT_BASELINE_IMPACT",
                                aggregate_id=relation["record_id"],
                                aggregate_revision=relation["revision"],
                                content_hash=None,
                                reference_role="CONTRACT_IMPACT",
                            )
                        )
    # The same native point/impact may be visible under several axes.
    references = list(
        {(r["aggregate_type"], str(r["aggregate_id"])): r for r in references}.values()
    )
    included_impacts = {
        str(ref["aggregate_id"])
        for ref in references
        if ref["aggregate_type"] == "CONTRACT_BASELINE_IMPACT"
    }
    unbound_impacts = sorted(
        {
            str(relation["record_id"])
            for row in points
            for relation in row["point"].get("follow_ups", [])
            if relation["kind"] == "CONTRACT_IMPACT"
        }
        - included_impacts
    )
    decisions, limited = read_commitment_decisions(session, tenant_id=tenant_id, case_id=case_id)
    current_id = session.scalar(
        sa.select(DecisionRecord.id)
        .where(
            DecisionRecord.tenant_id == tenant_id,
            DecisionRecord.case_id == case_id,
            DecisionRecord.scope_fingerprint == case.scope_fingerprint,
            DecisionRecord.validity == "CURRENT",
            DecisionRecord.decision_type == "GO_NO_GO",
            ~DecisionRecord.lifecycle.in_(("SUPERSEDED", "CANCELLED")),
        )
        .order_by(DecisionRecord.created_at.desc(), DecisionRecord.id.desc())
        .limit(1)
    )
    current = next((d for d in decisions if d["decision_id"] == str(current_id)), None)
    if current_id is not None and current is None:
        exact, _ = read_commitment_decisions(
            session, tenant_id=tenant_id, case_id=case_id, decision_id=current_id
        )
        current = exact[0] if exact else None
    for row in points:
        act = row["point"].get("human_assessment")
        row["condition_links"] = []
        if current and current["state"] == "CURRENT" and act and act["state"] == "CURRENT":
            row["condition_links"] = [
                link
                for link in current["assessment_links"]
                if link["assessment_id"] == str(act["assessment_id"])
                and link["assessment_revision"] == act["revision"]
                and link["source_context_sha256"] == act["source_context_sha256"]
            ]
        if row["condition_links"]:
            row["relations_state"] = "RECORDED"
    return dict(
        case_id=str(case_id),
        case_scope_fingerprint=case.scope_fingerprint,
        dce_version_id=str(case.applicable_dce_version_id)
        if case.applicable_dce_version_id
        else None,
        source_context_state=summary["source_context_state"] if summary else "UNKNOWN",
        axes=[{key: axis[key] for key in ("code", "label", "status")} for axis in summary["axes"]]
        if summary
        else [dict(code=code, label=label, status="UNKNOWN", items=[]) for code, label in AXES],
        points=points,
        coverage=summary["coverage"] if summary else None,
        dossier_review=summary.get("dossier_review") if summary else None,
        references=references[:500],
        unbound_contract_impacts=unbound_impacts,
        truncated=(summary["truncated"] if summary else False) or len(references) > 500,
        analysis_complete=False,
        gate_effect="NONE",
        current_decision=current,
        history=[d for d in decisions if d is not current],
        history_has_more=limited,
    )


def read_commitment_decisions(
    session, *, tenant_id, case_id, decision_id=None, before_decision_id=None
):
    from app.modules.decision.infrastructure.models.assessment_link import (
        DecisionConditionAssessmentLinkRecord as Link,
    )

    repository = SqlAlchemyDecisionLifecycleRepository()
    query = sa.select(DecisionRecord).where(
        DecisionRecord.tenant_id == tenant_id,
        DecisionRecord.case_id == case_id,
        DecisionRecord.decision_type == "GO_NO_GO",
    )
    if decision_id is not None:
        query = query.where(DecisionRecord.id == decision_id)
    if before_decision_id is not None:
        cursor = session.scalar(
            sa.select(DecisionRecord).where(
                DecisionRecord.tenant_id == tenant_id,
                DecisionRecord.case_id == case_id,
                DecisionRecord.id == before_decision_id,
            )
        )
        if cursor is None:
            raise PermissionError("NOT_FOUND_OR_FORBIDDEN")
        query = query.where(
            sa.or_(
                DecisionRecord.created_at < cursor.created_at,
                sa.and_(
                    DecisionRecord.created_at == cursor.created_at, DecisionRecord.id < cursor.id
                ),
            )
        )
    records = session.scalars(
        query.order_by(DecisionRecord.created_at.desc(), DecisionRecord.id.desc()).limit(21)
    ).all()
    result = []
    for record in records[:20]:
        contexts = session.scalars(
            sa.select(DecisionContextRecord)
            .where(
                DecisionContextRecord.tenant_id == tenant_id,
                DecisionContextRecord.decision_id == record.id,
            )
            .order_by(DecisionContextRecord.sequence_number.desc())
            .limit(21)
        ).all()
        context = next(
            (c for c in contexts if c.id == record.selected_final_context_id),
            contexts[0] if contexts else None,
        )
        refs = (
            session.scalars(
                sa.select(DecisionContextReferenceRecord)
                .where(
                    DecisionContextReferenceRecord.tenant_id == tenant_id,
                    DecisionContextReferenceRecord.decision_context_id == context.id,
                )
                .order_by(DecisionContextReferenceRecord.id)
                .limit(501)
            ).all()
            if context
            else []
        )
        valid = (
            bool(context and refs)
            and len(refs) <= 500
            and all(
                repository.context_reference_is_valid(
                    session=session,
                    tenant_id=tenant_id,
                    case_id=case_id,
                    aggregate_type=r.aggregate_type,
                    aggregate_id=r.aggregate_id,
                    aggregate_revision=r.aggregate_revision,
                    content_hash=r.content_hash,
                )
                for r in refs
            )
        )
        conditions = session.scalars(
            sa.select(DecisionConditionRecord)
            .where(
                DecisionConditionRecord.tenant_id == tenant_id,
                DecisionConditionRecord.decision_id == record.id,
            )
            .order_by(DecisionConditionRecord.id)
            .limit(33)
        ).all()
        transitions = session.scalars(
            sa.select(DecisionConditionTransitionRecord)
            .where(
                DecisionConditionTransitionRecord.tenant_id == tenant_id,
                DecisionConditionTransitionRecord.decision_id == record.id,
            )
            .order_by(DecisionConditionTransitionRecord.aggregate_revision)
            .limit(101)
        ).all()
        acts = []
        links = session.scalars(
            sa.select(Link)
            .where(
                Link.tenant_id == tenant_id, Link.case_id == case_id, Link.decision_id == record.id
            )
            .order_by(Link.created_at, Link.id)
            .limit(301)
        ).all()
        for ref in refs[:500]:
            if ref.aggregate_type != "ANALYSIS_ASSESSMENT":
                continue
            act = session.scalar(
                sa.select(AnalysisAssessmentRecord).where(
                    AnalysisAssessmentRecord.tenant_id == tenant_id,
                    AnalysisAssessmentRecord.case_id == case_id,
                    AnalysisAssessmentRecord.id == ref.aggregate_id,
                    AnalysisAssessmentRecord.revision == ref.aggregate_revision,
                    AnalysisAssessmentRecord.source_context_sha256 == ref.content_hash,
                )
            )
            if act:
                acts.append(
                    dict(
                        assessment_id=str(act.id),
                        point_id=str(act.point_id),
                        point_kind=act.point_kind,
                        revision=act.revision,
                        source=act.source_manifest_json,
                        treatment=act.treatment_json,
                        expected_evidence=act.expected_evidence,
                        residual_risk=act.residual_risk,
                        actor_id=str(act.actor_id),
                        created_at=act.created_at,
                        justification=act.justification,
                        state="HISTORICAL",
                    )
                )
        result.append(
            dict(
                decision_id=str(record.id),
                aggregate_revision=record.aggregate_revision,
                cycle_number=record.cycle_number,
                case_scope_fingerprint=record.scope_fingerprint,
                lifecycle=record.lifecycle,
                outcome=record.outcome,
                validity=record.validity,
                context_status=record.context_status,
                state="HISTORICAL"
                if record.validity != "CURRENT" or record.lifecycle in {"SUPERSEDED", "CANCELLED"}
                else "CURRENT"
                if valid
                else "REVIEW_REQUIRED"
                if context
                else "DRAFT",
                final_justification=record.final_justification,
                finalized_at=record.finalized_at,
                finalized_by_actor_id=str(record.finalized_by_actor_id)
                if record.finalized_by_actor_id
                else None,
                context_id=str(context.id) if context else None,
                context_fingerprint=context.context_fingerprint if context else None,
                rationale=context.rationale if context else None,
                unknowns=context.unknowns_json if context else [],
                references=[
                    dict(
                        aggregate_type=r.aggregate_type,
                        aggregate_id=str(r.aggregate_id),
                        aggregate_revision=r.aggregate_revision,
                        content_hash=r.content_hash,
                        reference_role=r.reference_role,
                    )
                    for r in refs[:500]
                ],
                assessment_snapshots=acts,
                assessment_links=[
                    dict(
                        link_id=str(link.id),
                        condition_id=str(link.condition_id),
                        context_id=str(link.context_id),
                        assessment_id=str(link.assessment_id),
                        assessment_revision=link.assessment_revision,
                        source_context_sha256=link.source_context_sha256,
                        justification=link.justification,
                        actor_id=str(link.actor_id),
                        created_at=link.created_at,
                    )
                    for link in links[:300]
                ],
                conditions=[
                    dict(
                        condition_id=str(c.id),
                        label=c.label,
                        status=c.status,
                        owner_actor_id=str(c.owner_actor_id) if c.owner_actor_id else None,
                        due_at=c.due_at,
                        due_date_absence_reason=c.due_date_absence_reason,
                        failure_consequence=c.failure_consequence,
                        satisfied_evidence=c.satisfied_evidence_ref_json,
                        failure_reason=c.failure_reason,
                    )
                    for c in conditions[:32]
                ],
                transitions=[
                    dict(
                        transition_id=str(t.id),
                        condition_id=str(t.condition_id),
                        from_status=t.from_status,
                        to_status=t.to_status,
                        evidence=t.satisfied_evidence_ref_json,
                        failure_reason=t.failure_reason,
                        actor_id=str(t.actor_id),
                        created_at=t.created_at,
                        revision=t.aggregate_revision,
                    )
                    for t in transitions[:100]
                ],
                truncated=len(links) > 300
                or len(contexts) > 20
                or len(refs) > 500
                or len(conditions) > 32
                or len(transitions) > 100,
            )
        )
    return result, len(records) > 20
