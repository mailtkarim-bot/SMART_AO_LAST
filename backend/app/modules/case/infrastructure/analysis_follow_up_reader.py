"""Exact native relations only; never infer a responsible or a lot from prose."""

from __future__ import annotations

import sqlalchemy as sa

from app.modules.decision.infrastructure.models.risk_requirement import (
    DecisionRiskRequirementLinkRecord as Link,
)
from app.modules.patron_action.infrastructure.models import PatronActionRecord as Action
from app.modules.patron_action.infrastructure.models import (
    PatronActionTransitionRecord as Transition,
)


def attach_analysis_follow_ups(session, *, tenant_id, case_id, version, requirements, risks):
    current_items = [i for i in (*requirements, *risks) if i["source_state"] == "CURRENT_SOURCE"]
    for item in current_items:
        item["follow_ups"] = []
    if not current_items:
        return False
    requirements_by_id = {
        i["item_id"]: i
        for i in requirements
        if i["source_state"] == "CURRENT_SOURCE" and i["native_state"] == "CONFIRMED"
    }
    risks_by_id = {i["item_id"]: i for i in risks if i["source_state"] == "CURRENT_SOURCE"}
    keys = {f"decision-risk:{rid}": (None, rid, None) for rid in risks_by_id}
    links = session.scalars(
        sa.select(Link)
        .where(Link.tenant_id == tenant_id, Link.case_id == case_id, Link.dce_version_id == version)
        .order_by(Link.id)
        .limit(301)
    ).all()
    for link in links[:300]:
        if link.risk_id in risks_by_id and link.requirement_id in requirements_by_id:
            keys[f"decision-risk-requirement:{link.id}"] = (
                link.id,
                link.risk_id,
                link.requirement_id,
            )
    actions = (
        session.scalars(
            sa.select(Action)
            .where(
                Action.tenant_id == tenant_id,
                Action.case_id == case_id,
                Action.functional_key.in_(keys),
            )
            .order_by(Action.id)
            .limit(301)
        ).all()
        if keys
        else []
    )
    for action in actions[:300]:
        relation, risk, requirement = keys[action.functional_key]
        expected = {f"decision-risk:{risk}"}
        if requirement is not None:
            expected.update(
                {f"dce-requirement:{requirement}", f"decision-risk-requirement-link:{relation}"}
            )
        if set(action.source_refs_json) != expected:
            continue
        transition = session.scalar(
            sa.select(Transition)
            .where(Transition.tenant_id == tenant_id, Transition.action_id == action.id)
            .order_by(Transition.aggregate_revision.desc())
            .limit(1)
        )
        record = dict(
            kind="ACTION",
            record_id=action.id,
            revision=transition.aggregate_revision if transition else action.aggregate_revision,
            state=transition.to_state if transition else action.state,
            relation_id=relation,
            risk_id=risk,
            requirement_id=requirement,
            description=action.recommended_action,
            consequence=action.impact,
            responsible_actor_id=None,
            due_at=action.due_at,
            scope="EXACT_RECORDED_RELATION",
        )
        risks_by_id[risk]["follow_ups"].append(record)
        if requirement is not None:
            requirements_by_id[requirement]["follow_ups"].append(record)
    contract_truncated = attach_contract_follow_ups(
        session, tenant_id=tenant_id, case_id=case_id, requirements=requirements
    )
    for link in links[:300]:
        if link.risk_id in risks_by_id and link.requirement_id in requirements_by_id:
            for follow_up in requirements_by_id[link.requirement_id]["follow_ups"]:
                if follow_up["kind"] != "ACTION":
                    risks_by_id[link.risk_id]["follow_ups"].append(
                        dict(
                            follow_up,
                            risk_id=link.risk_id,
                            risk_requirement_link_id=link.id,
                        )
                    )
    return len(links) > 300 or len(actions) > 300 or contract_truncated


def attach_contract_follow_ups(session, *, tenant_id, case_id, requirements):
    from app.modules.dce.infrastructure.models.contract_baseline import (
        ContractBaselineDeviationImpactRecord as Impact,
    )
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationCurrentRecord as Current,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import (
        DceRequirementRecord as Requirement,
    )

    items = {
        i["item_id"]: i
        for i in requirements
        if i["source_state"] == "CURRENT_SOURCE" and i["native_state"] == "CONFIRMED"
    }
    if not items:
        return False
    newer = sa.orm.aliased(Impact)
    rows = session.execute(
        sa.select(Impact, Current, Requirement)
        .join(
            Current,
            sa.and_(
                Current.tenant_id == tenant_id,
                Current.requirement_id == Impact.dce_requirement_id,
                Current.revision == Impact.dce_requirement_revision,
                Current.outcome == "CONFIRMED",
            ),
        )
        .join(
            Requirement,
            sa.and_(
                Requirement.tenant_id == tenant_id,
                Requirement.id == Impact.dce_requirement_id,
                Requirement.source_observation_id == Impact.baseline_observation_id,
            ),
        )
        .where(
            Impact.tenant_id == tenant_id,
            Impact.case_id == case_id,
            Impact.dce_requirement_id.in_(items),
            ~sa.exists(
                sa.select(newer.id).where(
                    newer.tenant_id == tenant_id,
                    newer.case_id == case_id,
                    newer.baseline_observation_id == Impact.baseline_observation_id,
                    newer.proof_revision > Impact.proof_revision,
                )
            ),
        )
        .order_by(Impact.id)
        .limit(301)
    ).all()
    qualified = {}
    for impact, current, requirement in rows[:300]:
        if (
            impact.status not in {"HUMAN_REVIEW_REQUIRED", "CONFIRMED"}
            or f"DCE_REQUIREMENT:{requirement.id}@{current.revision}"
            not in impact.baseline_source_refs_json
        ):
            continue
        qualified[impact.id] = impact
        items[requirement.id]["follow_ups"].append(
            dict(
                kind="CONTRACT_IMPACT",
                record_id=impact.id,
                revision=impact.proof_revision,
                state=impact.status,
                relation_id=None,
                risk_id=None,
                requirement_id=requirement.id,
                description=impact.deviation_statement or impact.baseline_statement,
                consequence=impact.impact_statement,
                responsible_actor_id=None,
                due_at=None,
                scope="EXACT_RECORDED_RELATION",
            )
        )
    conditions_truncated = attach_condition_follow_ups(
        session, tenant_id=tenant_id, case_id=case_id, items=items, impacts=qualified
    )
    return len(rows) > 300 or conditions_truncated


def attach_condition_follow_ups(session, *, tenant_id, case_id, items, impacts):
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.decision.infrastructure.models.decision import (
        DecisionConditionContractEvidenceLinkRecord as Evidence,
    )
    from app.modules.decision.infrastructure.models.decision import (
        DecisionConditionRecord as Condition,
    )
    from app.modules.decision.infrastructure.models.decision import (
        DecisionContextRecord as Context,
    )
    from app.modules.decision.infrastructure.models.decision import (
        DecisionContextReferenceRecord as Reference,
    )
    from app.modules.decision.infrastructure.models.decision import (
        DecisionRecord as Decision,
    )
    from app.modules.decision.infrastructure.repositories import (
        SqlAlchemyDecisionLifecycleRepository,
    )

    if not impacts:
        return False
    rows = session.execute(
        sa.select(Evidence, Condition, Decision)
        .join(
            Condition,
            sa.and_(
                Condition.tenant_id == tenant_id,
                Condition.id == Evidence.condition_id,
                Condition.decision_id == Evidence.decision_id,
            ),
        )
        .join(
            Decision,
            sa.and_(
                Decision.tenant_id == tenant_id,
                Decision.id == Evidence.decision_id,
                Decision.case_id == case_id,
                Decision.validity == "CURRENT",
                Decision.decision_type == "GO_NO_GO",
                Decision.context_status == "FROZEN",
                Decision.lifecycle == "FINALIZED",
                Decision.outcome == "CONDITIONAL_GO",
                Decision.selected_final_context_id == Evidence.context_id,
            ),
        )
        .join(
            Context,
            sa.and_(
                Context.tenant_id == tenant_id,
                Context.id == Evidence.context_id,
                Context.decision_id == Decision.id,
                Context.context_state == "FROZEN",
            ),
        )
        .join(
            CaseRecord,
            sa.and_(
                CaseRecord.tenant_id == tenant_id,
                CaseRecord.id == case_id,
                CaseRecord.scope_fingerprint == Decision.scope_fingerprint,
            ),
        )
        .where(Evidence.tenant_id == tenant_id, Evidence.contract_impact_id.in_(impacts))
        .order_by(Evidence.id)
        .limit(301)
    ).all()
    repository = SqlAlchemyDecisionLifecycleRepository()
    for evidence, condition, decision in rows[:300]:
        impact = impacts[evidence.contract_impact_id]
        if (
            evidence.proof_revision != impact.proof_revision
            or evidence.dce_requirement_id != impact.dce_requirement_id
            or evidence.dce_requirement_revision != impact.dce_requirement_revision
        ):
            continue
        refs = session.scalars(
            sa.select(Reference).where(
                Reference.tenant_id == tenant_id,
                Reference.decision_context_id == evidence.context_id,
            )
        ).all()
        actual = {
            (r.aggregate_type, r.aggregate_id, r.aggregate_revision, r.content_hash) for r in refs
        }
        expected = {
            (
                "DCE_REQUIREMENT",
                evidence.dce_requirement_id,
                evidence.dce_requirement_revision,
                None,
            ),
            ("CONTRACT_BASELINE_IMPACT", impact.id, impact.proof_revision, None),
            (
                "BUSINESS_METHOD_PROFILE",
                evidence.profile_version_id,
                evidence.profile_version,
                evidence.profile_content_sha256,
            ),
        }
        if not expected.issubset(actual):
            continue
        if not all(
            repository.context_reference_is_valid(
                session=session,
                tenant_id=tenant_id,
                case_id=case_id,
                aggregate_type=kind,
                aggregate_id=rid,
                aggregate_revision=revision,
                content_hash=content_hash,
            )
            for kind, rid, revision, content_hash in actual
        ):
            continue
        items[impact.dce_requirement_id]["follow_ups"].append(
            dict(
                kind="CONDITION",
                contract_impact_id=impact.id,
                contract_impact_revision=impact.proof_revision,
                decision_id=decision.id,
                context_id=evidence.context_id,
                record_id=condition.id,
                revision=decision.aggregate_revision,
                state=condition.status,
                relation_id=evidence.id,
                risk_id=None,
                requirement_id=evidence.dce_requirement_id,
                description=condition.label,
                consequence=condition.failure_consequence,
                responsible_actor_id=condition.owner_actor_id,
                due_at=condition.due_at,
                scope="EXACT_RECORDED_RELATION",
            )
        )
    return len(rows) > 300
