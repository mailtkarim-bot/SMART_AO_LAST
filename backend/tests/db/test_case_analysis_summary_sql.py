from dataclasses import replace
from datetime import timedelta
from hashlib import sha256
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.interfaces.http.routes.case_analysis_summary import build_case_analysis_summary_router
from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
from app.modules.case.infrastructure.analysis_summary_reader import (
    SqlAlchemyCaseAnalysisSummaryReader,
)
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord as Fragment,
)
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionRecord as Extraction,
)
from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
from app.modules.decision.infrastructure.models.risk import (
    DecisionRiskRecord,
    DecisionRiskTreatmentTransitionRecord,
)
from app.platform.security.authorization import AuthorizationPolicy
from app.platform.security.capabilities import capabilities_for
from app.platform.security.context import ActorKind
from fastapi import FastAPI
from fastapi.testclient import TestClient
from tests.api.test_case_dce_reading_routes import _Resolver
from tests.db.test_candidate_retrieval_sql import _clone
from tests.db.test_knowledge_source_freshness import NOW, seed_indexed_source


@pytest.fixture
def dossier(session_factory):
    seed = list(seed_indexed_source(session_factory))
    with session_factory.begin() as s:
        old = s.get(Extraction, seed[4])
        fragment = s.get(Fragment, seed[5])
        e, f = uuid4(), uuid4()
        s.add(
            _clone(old, id=e, extractor_version="l04-proof", created_at=NOW + timedelta(seconds=1))
        )
        s.flush()
        s.add(
            _clone(fragment, id=f, extraction_id=e, locator_json={"kind": "pdf_page", "page": 42})
        )
        s.flush()
        seed[4:6] = [e, f]
        risk = uuid4()
        text = fragment.text
        s.add(
            DecisionRiskRecord(
                id=risk,
                tenant_id=seed[0],
                case_id=seed[1],
                dce_version_id=seed[2],
                source_fragment_id=f,
                functional_key=str(risk),
                category="CCTP",
                risk_code="SYNTHETIC_ACCESS",
                title="Accès à revoir",
                statement="Déclaration synthétique",
                severity="HIGH",
                likelihood="POSSIBLE",
                treatment="OPEN",
                source_excerpt=text,
                source_locator_json={"kind": "pdf_page", "page": 42},
                start_byte_offset=0,
                end_byte_offset=len(text.encode()),
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
    return seed, risk


def read(factory, seed):
    with factory() as s:
        return SqlAlchemyCaseAnalysisSummaryReader(s).get(tenant_id=seed[0], case_id=seed[1])


def risk_items(result):
    return [i for a in result["axes"] for i in a["items"] if i["kind"] == "RISK"]


def test_current_risk_has_exact_origin_and_repeat_is_read_only(session_factory, dossier):
    seed, risk = dossier
    result = read(session_factory, seed)
    item = risk_items(result)[0]
    assert len(result["axes"]) == 12 and not result["analysis_complete"]
    assert item["item_id"] == risk and item["source_state"] == "CURRENT_SOURCE"
    assert item["source_anchor"]["source_anchor_id"] == seed[5]
    assert item["source_anchor"]["dce_version_id"] == seed[2]
    assert item["source_anchor"]["source_sha256"] == seed[6]
    assert item["source_anchor"]["locator"]["coordinates"]["page"] == 42
    assert item["applicability"] == item["lot_state"] == "UNKNOWN" and item["lot_numbers"] == []
    assert item["start_byte_offset"] == 0 and item["end_byte_offset"] > 0
    assert read(session_factory, seed) == result
    with session_factory() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(DecisionRiskRecord)
                .where(DecisionRiskRecord.id == risk)
            )
            == 1
        )


@pytest.mark.parametrize(
    "status", ["REVIEW_REQUIRED", "FAILED_SAFE", "UNSUPPORTED", "REJECTED_LIMIT"]
)
def test_new_refused_extraction_never_transfers_old_risk_proof(session_factory, dossier, status):
    seed, risk = dossier
    with session_factory.begin() as s:
        old = s.get(Extraction, seed[4])
        s.add(
            _clone(
                old,
                id=uuid4(),
                created_at=NOW + timedelta(seconds=2),
                extractor_version=str(uuid4()),
                status=status,
                failure_code="SYNTHETIC_REFUSAL",
                fragment_count=0,
                extracted_char_count=0,
            )
        )
    result = read(session_factory, seed)
    item = risk_items(result)[0]
    assert item["item_id"] == risk and item["source_state"] == "UNKNOWN"
    assert item["source_anchor"] is None and item["title"] is None
    assert item["source_excerpt"] is None and item["severity"] == "UNKNOWN"
    assert item["source_excerpt_state"] == "UNKNOWN"
    assert result["coverage"]["unread_documents"] == 1
    with session_factory() as s:
        assert s.get(Fragment, seed[5]) is not None


@pytest.mark.parametrize("corruption", ["fragment", "input"])
def test_hash_discordance_is_unknown_without_source_details(session_factory, dossier, corruption):
    seed, risk = dossier
    with session_factory.begin() as s:
        old = s.get(Extraction, seed[4])
        f = s.get(Fragment, seed[5])
        new = uuid4()
        frag = uuid4()
        s.add(
            _clone(
                old,
                id=new,
                created_at=NOW + timedelta(seconds=2),
                extractor_version=str(uuid4()),
                input_sha256="0" * 64 if corruption == "input" else old.input_sha256,
            )
        )
        s.flush()
        s.add(
            _clone(
                f,
                id=frag,
                extraction_id=new,
                text_sha256="0" * 64 if corruption == "fragment" else f.text_sha256,
            )
        )
        # A new synthetic risk deliberately claims the discordant current fragment.
        r = s.get(DecisionRiskRecord, risk)
        s.add(
            _clone(
                r,
                id=uuid4(),
                functional_key=str(uuid4()),
                source_fragment_id=frag,
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
    assert all(
        i["source_state"] == "UNKNOWN" and i["source_anchor"] is None
        for i in risk_items(read(session_factory, seed))
    )


def test_tenant_affaire_and_replaced_version_do_not_reuse_risks(session_factory, dossier):
    seed, risk = dossier
    with session_factory() as s:
        assert (
            SqlAlchemyCaseAnalysisSummaryReader(s).get(tenant_id=uuid4(), case_id=seed[1]) is None
        )
    with session_factory.begin() as s:
        old = s.get(CaseRecord, seed[1])
        other = uuid4()
        s.add(
            _clone(old, id=other, functional_identity_hash=sha256(str(other).encode()).hexdigest())
        )
    other_seed = list(seed)
    other_seed[1] = other
    assert not risk_items(read(session_factory, other_seed))
    with session_factory.begin() as s:
        v = s.get(DceVersionRecord, seed[2])
        new = uuid4()
        s.add(_clone(v, id=new, corpus_hash=sha256(str(new).encode()).hexdigest()))
        s.flush()
        s.execute(
            sa.update(CaseRecord)
            .where(CaseRecord.id == seed[1])
            .values(applicable_dce_version_id=new, dce_freshness="REVIEW_REQUIRED")
        )
    result = read(session_factory, seed)
    assert result["dce_version_id"] == new and not risk_items(result)
    with session_factory() as s:
        assert s.get(DecisionRiskRecord, risk) is not None


@pytest.mark.parametrize("treatment", ["ACCEPTED", "MITIGATED"])
def test_native_treatment_comes_from_latest_transition(session_factory, dossier, treatment):
    seed, risk = dossier
    with session_factory.begin() as s:
        s.add(
            DecisionRiskTreatmentTransitionRecord(
                id=uuid4(),
                tenant_id=seed[0],
                risk_id=risk,
                from_treatment="OPEN",
                to_treatment=treatment,
                evidence_excerpt="preuve synthétique",
                evidence_locator_json={"page": 42},
                evidence_start_byte_offset=0,
                evidence_end_byte_offset=1,
                rationale="Revue synthétique",
                aggregate_revision=2,
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
    item = risk_items(read(session_factory, seed))[0]
    assert item["native_state"] == treatment
    assert item["expected_evidence"] == item["residual_risk"] == "UNKNOWN"


def test_http_sql_with_real_policy_refuses_foreign_role_and_missing_capability(
    session_factory, dossier
):
    seed, risk = dossier
    base = replace(
        _Resolver().resolve(access_token="test-token"),
        tenant_id=seed[0],
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
    )
    current = [base]

    def owner(**kw):
        with session_factory() as s:
            return s.scalar(sa.select(CaseRecord.tenant_id).where(CaseRecord.id == kw["case_id"]))

    def summary(**kw):
        with session_factory() as s:
            s.connection(execution_options={"isolation_level": "REPEATABLE READ"})
            return SqlAlchemyCaseAnalysisSummaryReader(s).get(**kw)

    runtime = SimpleNamespace(get_case_tenant_id=owner, get_case_analysis_summary=summary)
    security = ConsultationSecurityRuntime(
        context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kw: current[0])),
        policy=AuthorizationPolicy(),
    )
    app = FastAPI()
    app.include_router(
        build_case_analysis_summary_router(runtime=runtime, security_runtime=security)
    )
    c = TestClient(app)
    url = f"/api/v1/cases/{seed[1]}/analysis-summary"
    headers = {"Authorization": "Bearer test-token"}
    assert c.get(url, headers=headers).status_code == 200
    from app.platform.security.capabilities import Capability

    for capability in (
        Capability.CASE_DCE_READ,
        Capability.DECISION_RISK_READ,
        Capability.PATRON_ACTION_READ,
        Capability.DECISION_FINALIZE,
        Capability.PRICING_READ,
        Capability.FINANCIAL_REPORT_READ,
    ):
        current[0] = replace(base, capabilities=base.capabilities - {capability})
        denied = c.get(url, headers=headers)
        assert denied.status_code == 403 and denied.json() == {"detail": "FORBIDDEN"}
    for actor, status in [
        (replace(base, tenant_id=uuid4()), 404),
        (replace(base, actor_kind=ActorKind.COLLABORATEUR), 403),
        (replace(base, capabilities=frozenset()), 403),
        (replace(base, mfa_verified_at=None), 403),
    ]:
        current[0] = actor
        response = c.get(url, headers=headers)
        assert response.status_code == status and "axes" not in response.json()


@pytest.fixture
def requirements_dossier(
    session_factory, tmp_path, source_bytes=b"Lot 6 : le DC1 est obligatoire.", family="RC"
):
    from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
    from app.modules.dce.application.requirements import DceRequirementsService
    from app.modules.dce.infrastructure.models.dce_version import DceDocumentClassificationRecord
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
    from app.platform.events.dispatcher import CommandDispatcher
    from tests.application.test_dce_rc_analysis import (
        _extract_then_analyze,
        _seed_admitted_document,
    )

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, doc, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=source_bytes
    )
    with session_factory.begin() as s:
        s.add(
            DceDocumentClassificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_document_id=doc,
                classification=family,
                rationale=None,
                source="SYNTHETIC",
                previous_classification_id=None,
                is_current=True,
                created_by_actor_id=None,
            )
        )
    analysis = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant,
        document_id=doc,
        dce_version_id=version,
    )
    DceRequirementsService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementMaterializationRun": (
                    RecordDceRequirementMaterializationRunHandler()
                )
            },
        ),
    ).materialize(
        tenant_id=tenant,
        dce_version_id=version,
        dce_rc_analysis_id=UUID(analysis.aggregate_refs[0]["aggregate_id"]),
        now=NOW,
    )
    with session_factory.begin() as s:
        v = s.get(DceVersionRecord, version)
        case = uuid4()
        s.add(
            CaseRecord(
                id=case,
                tenant_id=tenant,
                consultation_id=v.consultation_id,
                applicable_dce_version_id=version,
                functional_identity_hash=sha256(str(case).encode()).hexdigest(),
                title="Synthèse RC",
                business_origin="MANUAL",
                origin_rationale="Fixture synthétique",
                scope_kind="SINGLE_LOT",
                scope_json={"lot": "6"},
                scope_fingerprint="d" * 64,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
            )
        )
    return [tenant, case, version]


@pytest.mark.parametrize("change", ["analysis", "materialization", "offsets"])
def test_requirement_proof_must_remain_current_and_exact(
    session_factory, requirements_dossier, change
):
    from app.modules.dce.infrastructure.models.dce_rc_analysis import DceRcAnalysisRunRecord
    from app.modules.dce.infrastructure.models.dce_requirements import (
        DceRequirementMaterializationRunRecord,
        DceRequirementRecord,
        DceRequirementSourceRecord,
    )

    seed = requirements_dossier
    before = read(session_factory, seed)
    items = [i for a in before["axes"] for i in a["items"]]
    assert items and items[0]["source_state"] == "CURRENT_SOURCE"
    with session_factory.begin() as s:
        req = s.scalar(
            sa.select(DceRequirementRecord).where(DceRequirementRecord.tenant_id == seed[0])
        )
        run = s.get(DceRequirementMaterializationRunRecord, req.requirements_run_id)
        if change == "analysis":
            old = s.get(DceRcAnalysisRunRecord, run.dce_rc_analysis_id)
            s.add(
                _clone(
                    old,
                    id=uuid4(),
                    analyzer_version=str(uuid4()),
                    created_at=old.created_at + timedelta(seconds=2),
                )
            )
        else:
            new = uuid4()
            s.add(
                _clone(
                    run,
                    id=new,
                    materializer_version=str(uuid4()),
                    created_at=run.created_at + timedelta(seconds=2),
                )
            )
            s.flush()
            if change == "offsets":
                bad = uuid4()
                source = s.scalar(
                    sa.select(DceRequirementSourceRecord).where(
                        DceRequirementSourceRecord.requirement_id == req.id
                    )
                )
                s.add(_clone(req, id=bad, requirements_run_id=new))
                s.flush()
                s.add(
                    _clone(
                        source,
                        id=uuid4(),
                        requirement_id=bad,
                        start_byte_offset=source.start_byte_offset + 1,
                    )
                )
    result = read(session_factory, seed)
    items = [i for a in result["axes"] for i in a["items"]]
    assert items and all(
        i["source_state"] == "UNKNOWN" and i["source_anchor"] is None for i in items
    )


@pytest.mark.parametrize(
    "field,value",
    [("freshness", "REVIEW_REQUIRED"), ("integrity", "PARTIAL"), ("lifecycle", "WITHDRAWN")],
)
def test_unreviewed_or_withdrawn_context_cannot_claim_current_risk_proof(
    session_factory, dossier, field, value
):
    seed, _ = dossier
    with session_factory.begin() as s:
        model = CaseRecord if field == "freshness" else DceVersionRecord
        column = (
            CaseRecord.dce_freshness if field == "freshness" else getattr(DceVersionRecord, field)
        )
        key = seed[1] if field == "freshness" else seed[2]
        values = {column: value}
        if field == "lifecycle":
            values.update(
                {
                    DceVersionRecord.withdrawal_source: "SYNTHETIC",
                    DceVersionRecord.withdrawal_reason: "Test withdrawal",
                }
            )
        s.execute(sa.update(model).where(model.id == key).values(values))
    assert all(i["source_state"] == "UNKNOWN" for i in risk_items(read(session_factory, seed)))


@pytest.mark.parametrize("bad", [None, "case", "refs", "source"])
def test_follow_up_direct_action_exact_case_refs_and_current_source(session_factory, dossier, bad):
    from app.modules.patron_action.infrastructure.models import (
        PatronActionRecord,
        PatronActionTransitionRecord,
    )

    seed, risk = dossier
    other = uuid4()
    with session_factory.begin() as s:
        action = PatronActionRecord(
            id=uuid4(),
            tenant_id=seed[0],
            case_id=other if bad == "case" else seed[1],
            functional_key=f"decision-risk:{risk}",
            action_type="DECIDE_GO_NO_GO",
            severity="BLOCKING",
            state="OPEN",
            title="Revoir",
            why_now="Source synthétique",
            impact="Conséquence déclarée",
            recommended_action="Vérifier accès",
            due_at=NOW,
            source_refs_json=[] if bad == "refs" else [f"decision-risk:{risk}"],
            aggregate_revision=1,
            actor_id=uuid4(),
            membership_id=uuid4(),
            command_id=uuid4(),
            idempotency_key=uuid4(),
        )
        s.add(action)
        s.flush()
        s.add(
            PatronActionTransitionRecord(
                id=uuid4(),
                tenant_id=seed[0],
                action_id=action.id,
                from_state="OPEN",
                to_state="IN_PROGRESS",
                reason_code="SYNTHETIC",
                aggregate_revision=2,
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
        if bad == "source":
            old = s.get(Extraction, seed[4])
            s.add(
                _clone(
                    old,
                    id=uuid4(),
                    extractor_version=str(uuid4()),
                    created_at=NOW + timedelta(seconds=4),
                    status="REVIEW_REQUIRED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC",
                )
            )
    item = risk_items(read(session_factory, seed))[0]
    if bad:
        assert item["follow_ups"] == [] and item["follow_up_state"] == "UNKNOWN"
    else:
        assert item["follow_up_state"] == "RECORDED"
        f = item["follow_ups"][0]
        assert f["record_id"] == action.id and f["revision"] == 2 and f["state"] == "IN_PROGRESS"
        assert f["consequence"] == "Conséquence déclarée" and f["responsible_actor_id"] is None
        assert f["description"] == "Vérifier accès" and f["risk_id"] == risk


@pytest.mark.parametrize("change", [None, "revision", "superseded", "unconfirmed", "case"])
def test_contract_consequences_require_exact_current_requirement_proof(
    session_factory, requirements_dossier, change
):
    from app.modules.dce.infrastructure.models.contract_baseline import (
        ContractBaselineDeviationImpactRecord as Impact,
    )
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationCurrentRecord as Current,
    )
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationRecord as Confirmation,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord

    seed = requirements_dossier
    with session_factory.begin() as s:
        req = s.scalar(
            sa.select(DceRequirementRecord).where(DceRequirementRecord.tenant_id == seed[0])
        )
        confirmation = uuid4()
        s.add(
            Confirmation(
                id=confirmation,
                tenant_id=seed[0],
                requirement_id=req.id,
                revision=1,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
                confirmed_by_actor_id=uuid4(),
            )
        )
        s.flush()
        s.add(
            Current(
                tenant_id=seed[0],
                requirement_id=req.id,
                confirmation_id=confirmation,
                revision=1,
                outcome="REVIEW_REQUIRED" if change == "unconfirmed" else "CONFIRMED",
            )
        )
        impact = Impact(
            id=uuid4(),
            tenant_id=seed[0],
            case_id=seed[1],
            baseline_observation_id=req.source_observation_id,
            dce_requirement_id=req.id,
            dce_requirement_revision=2 if change == "revision" else 1,
            proof_revision=1,
            baseline_source_refs_json=[f"DCE_REQUIREMENT:{req.id}@1"],
            baseline_statement="Source déclarée",
            impact_statement="Délai déclaré de deux jours",
            status="HUMAN_REVIEW_REQUIRED",
        )
        s.add(impact)
        s.flush()
        if change == "superseded":
            s.add(_clone(impact, id=uuid4(), proof_revision=2, status="SUPERSEDED"))
    actual_seed = list(seed)
    if change == "case":
        with session_factory.begin() as s:
            original = s.get(CaseRecord, seed[1])
            new = uuid4()
            s.add(
                _clone(
                    original, id=new, functional_identity_hash=sha256(str(new).encode()).hexdigest()
                )
            )
        actual_seed[1] = new
    items = [i for a in read(session_factory, actual_seed)["axes"] for i in a["items"]]
    follows = [f for i in items for f in i["follow_ups"] if f["kind"] == "CONTRACT_IMPACT"]
    if change:
        assert follows == []
    else:
        assert len(follows) == 1 and follows[0]["record_id"] == impact.id
        assert follows[0]["consequence"] == "Délai déclaré de deux jours"
        assert follows[0]["responsible_actor_id"] is None


@pytest.mark.parametrize("confirmed", [True, False])
def test_exact_link_projects_action_and_declared_impact_on_both_endpoints(
    session_factory, requirements_dossier, confirmed
):
    from app.modules.dce.infrastructure.models.contract_baseline import (
        ContractBaselineDeviationImpactRecord as Impact,
    )
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationCurrentRecord as Current,
    )
    from app.modules.dce.infrastructure.models.dce_requirement_confirmations import (
        DceRequirementConfirmationRecord as Confirmation,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
    from app.modules.decision.infrastructure.models.risk_requirement import (
        DecisionRiskRequirementLinkRecord as Link,
    )
    from app.modules.patron_action.infrastructure.models import PatronActionRecord as Action

    seed = requirements_dossier
    before = read(session_factory, seed)
    req_item = next(i for a in before["axes"] for i in a["items"])
    with session_factory.begin() as s:
        req = s.get(DceRequirementRecord, req_item["item_id"])
        fragment = s.get(Fragment, req_item["source_anchor"]["source_anchor_id"])
        confirmation = uuid4()
        risk = uuid4()
        link = uuid4()
        s.add(
            Confirmation(
                id=confirmation,
                tenant_id=seed[0],
                requirement_id=req.id,
                revision=1,
                outcome="CONFIRMED",
                reason_code="SOURCE_REVIEWED",
                confirmed_by_actor_id=uuid4(),
            )
        )
        s.flush()
        s.add(
            Current(
                tenant_id=seed[0],
                requirement_id=req.id,
                confirmation_id=confirmation,
                revision=1,
                outcome="CONFIRMED" if confirmed else "REVIEW_REQUIRED",
            )
        )
        s.add(
            DecisionRiskRecord(
                id=risk,
                tenant_id=seed[0],
                case_id=seed[1],
                dce_version_id=seed[2],
                source_fragment_id=fragment.id,
                functional_key=str(risk),
                category="CCAP",
                risk_code="SYNTHETIC",
                title="Risque lié",
                statement="À vérifier",
                severity="HIGH",
                likelihood="POSSIBLE",
                treatment="OPEN",
                source_excerpt=fragment.text,
                source_locator_json={"kind": "pdf_page", "page": 1},
                start_byte_offset=0,
                end_byte_offset=len(fragment.text.encode()),
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
        s.flush()
        s.add(
            Link(
                id=link,
                tenant_id=seed[0],
                case_id=seed[1],
                dce_version_id=seed[2],
                risk_id=risk,
                requirement_id=req.id,
                functional_key=str(link),
                relationship="IMPACTS",
                rationale="Lien synthétique explicite",
                source_refs_json=[],
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
        s.flush()
        s.add(
            Action(
                id=uuid4(),
                tenant_id=seed[0],
                case_id=seed[1],
                functional_key=f"decision-risk-requirement:{link}",
                action_type="DECIDE_GO_NO_GO",
                severity="BLOCKING",
                state="OPEN",
                title="Revoir",
                why_now="À vérifier",
                impact="Impact déclaré de revue",
                recommended_action="Revoir le couple",
                source_refs_json=[
                    f"decision-risk:{risk}",
                    f"dce-requirement:{req.id}",
                    f"decision-risk-requirement-link:{link}",
                ],
                aggregate_revision=1,
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
            )
        )
        s.add(
            Impact(
                id=uuid4(),
                tenant_id=seed[0],
                case_id=seed[1],
                baseline_observation_id=req.source_observation_id,
                dce_requirement_id=req.id,
                dce_requirement_revision=1,
                proof_revision=1,
                baseline_source_refs_json=[f"DCE_REQUIREMENT:{req.id}@1"],
                baseline_statement="Déclaration",
                impact_statement="Conséquence liée",
                status="HUMAN_REVIEW_REQUIRED",
            )
        )
    items = [i for a in read(session_factory, seed)["axes"] for i in a["items"]]
    for item in items:
        if confirmed:
            assert {f["kind"] for f in item["follow_ups"]} == {"ACTION", "CONTRACT_IMPACT"}
            if item["kind"] == "RISK":
                impact = next(f for f in item["follow_ups"] if f["kind"] == "CONTRACT_IMPACT")
                assert (
                    impact["risk_requirement_link_id"] == link
                    and impact["requirement_id"] == req.id
                )
        else:
            assert item["follow_ups"] == []


def test_anatomy_exact_risk_quote_severity_and_unknown_unrecorded_fields(session_factory, dossier):
    seed, risk = dossier
    item = risk_items(read(session_factory, seed))[0]
    with session_factory() as s:
        registered = s.get(DecisionRiskRecord, risk)
        fragment = s.get(Fragment, seed[5])
        expected = fragment.text.encode()[
            registered.start_byte_offset : registered.end_byte_offset
        ].decode()
    assert item["source_excerpt"] == expected == registered.source_excerpt
    assert item["source_excerpt_state"] == "EXACT_SOURCE"
    assert item["severity"] == "HIGH"
    assert item["expected_evidence"] == item["residual_risk"] == "UNKNOWN"


def test_anatomy_requirement_quote_keeps_utf8_source_region_and_no_inferred_severity(
    session_factory, requirements_dossier
):
    items = [i for a in read(session_factory, requirements_dossier)["axes"] for i in a["items"]]
    assert items
    for item in items:
        with session_factory() as s:
            fragment = s.get(Fragment, item["source_anchor"]["source_anchor_id"])
        assert (
            item["source_excerpt"]
            == fragment.text.encode()[item["start_byte_offset"] : item["end_byte_offset"]].decode()
        )
        assert item["source_excerpt_state"] == "EXACT_SOURCE" and item["severity"] == "UNKNOWN"
        assert item["expected_evidence"] == item["residual_risk"] == "UNKNOWN"


@pytest.mark.parametrize("corruption", ["quote_length", "unknown_quote", "unknown_severity"])
def test_anatomy_response_refuses_unproved_or_discordant_fields(
    session_factory, dossier, corruption
):
    from app.modules.case.public.analysis_summary_contracts import CaseAnalysisSummaryResponse
    from pydantic import ValidationError

    seed, _ = dossier
    result = read(session_factory, seed)
    item = risk_items(result)[0]
    if corruption == "quote_length":
        item["source_excerpt"] += "X"
    else:
        item.update(
            source_state="UNKNOWN",
            source_anchor=None,
            title=None,
            start_byte_offset=None,
            end_byte_offset=None,
        )
        if corruption == "unknown_severity":
            item.update(source_excerpt=None, source_excerpt_state="UNKNOWN")
    with pytest.raises(ValidationError):
        CaseAnalysisSummaryResponse.model_validate(result)


def test_runtime_price_axis_reads_exact_native_scenario_and_masks_stale_basis(
    session_factory, dossier
):
    from app.bootstrap.application import AppRuntime
    from app.modules.pricing.infrastructure.models import (
        FinancialReportLineRecord,
        FinancialReportSnapshotRecord,
        PricingScenarioRecord,
    )
    from tests.application.test_pricing_scenarios import _declare_base_lines

    seed, risk = dossier
    snapshot_id, scenario_id = uuid4(), uuid4()
    with session_factory.begin() as s:
        case = s.get(CaseRecord, seed[1])
        snapshot = FinancialReportSnapshotRecord(
            id=snapshot_id,
            tenant_id=seed[0],
            case_id=case.id,
            state="DRAFT",
            currency_code="EUR",
            ruleset_version=1,
            aggregate_revision=2,
            calculated_at=NOW,
            published_at=None,
            sales_total_minor=100000,
            direct_cost_total_minor=60000,
            overhead_total_minor=10000,
            subcontracting_total_minor=5000,
            contingency_total_minor=5000,
            gross_margin_minor=20000,
            gross_margin_rate_bps=2000,
            forecast_cashflow_minor=10000,
        )
        s.add(snapshot)
        s.flush()
        _declare_base_lines(s, snapshot)
        s.add(
            FinancialReportLineRecord(
                id=uuid4(),
                tenant_id=seed[0],
                snapshot_id=snapshot_id,
                category="FORECAST_CASHFLOW",
                label="Déclaration cash synthétique",
                quantity_decimal="1",
                unit="forfait",
                amount_minor=10000,
            )
        )
        snapshot.state = "PUBLISHED"
        snapshot.published_at = NOW
        s.flush()
        s.add(
            PricingScenarioRecord(
                id=scenario_id,
                tenant_id=seed[0],
                case_id=case.id,
                source_snapshot_id=snapshot_id,
                source_snapshot_revision=2,
                scenario_key="Prudent synthétique",
                scenario_type="PRUDENT",
                version=1,
                state="DRAFT",
                assumptions_json={"origine": "estimation utilisateur"},
                sales_total_minor=100000,
                total_cost_minor=80000,
                gross_margin_minor=20000,
                gross_margin_rate_bps=2000,
                retention_reserve_minor=2000,
                guarantee_reserve_minor=3000,
                actor_id=uuid4(),
                membership_id=uuid4(),
                command_id=uuid4(),
                idempotency_key=uuid4(),
                correlation_id=uuid4(),
            )
        )
    runtime = SimpleNamespace(session_factory=session_factory)

    def read():
        return AppRuntime.get_case_analysis_summary(
            cast(Any, runtime), tenant_id=seed[0], case_id=seed[1]
        )

    result = read()
    price = next(a for a in result["axes"] if a["code"] == "PRICE")
    item = price["pricing_scenarios"][0]
    assert item["details"]["source_snapshot_id"] == snapshot_id
    assert item["details"]["assumptions"] == {"origine": "estimation utilisateur"}
    assert item["dce_applicability"] == "UNKNOWN" and result["analysis_complete"] is False
    cash = next(a for a in result["axes"] if a["code"] == "CASH")
    assert cash["cash_reports"][0]["details"]["forecast_cashflow_minor"] == 10000
    assert cash["cash_reports"][0]["report_id"] == snapshot_id
    assert cash["cash_reports"][0]["revision"] == 2
    assert cash["cash_reports"][0]["funding_peak_state"] == "UNKNOWN"
    assert cash["pricing_scenarios"][0]["details"]["retention_reserve_minor"] == 2000
    from app.modules.case.public.analysis_summary_contracts import CaseAnalysisSummaryResponse

    CaseAnalysisSummaryResponse.model_validate(result)
    runtime.get_case_analysis_summary = lambda **kw: AppRuntime.get_case_analysis_summary(
        cast(Any, runtime), **kw
    )
    runtime.get_case_tenant_id = lambda **kw: seed[0] if kw["case_id"] == seed[1] else None
    base = replace(
        _Resolver().resolve(access_token="test-token"),
        tenant_id=seed[0],
        actor_kind=ActorKind.PATRON_ADMIN,
        capabilities=capabilities_for(ActorKind.PATRON_ADMIN),
    )
    actor = [base]
    security = ConsultationSecurityRuntime(
        context_resolver=cast(Any, SimpleNamespace(resolve=lambda **kw: actor[0])),
        policy=AuthorizationPolicy(),
    )
    app = FastAPI()
    app.include_router(
        build_case_analysis_summary_router(runtime=runtime, security_runtime=security)
    )
    client = TestClient(app)
    url = f"/api/v1/cases/{seed[1]}/analysis-summary"
    headers = {"Authorization": "Bearer test-token"}
    allowed = client.get(url, headers=headers)
    assert allowed.status_code == 200 and str(snapshot_id) in allowed.text
    assert allowed.headers.get("cache-control") == "no-store"
    from app.platform.security.capabilities import Capability

    for context, status in [
        (replace(base, tenant_id=uuid4()), 404),
        (replace(base, actor_kind=ActorKind.COLLABORATEUR), 403),
        (replace(base, capabilities=base.capabilities - {Capability.PRICING_READ}), 403),
        (replace(base, capabilities=base.capabilities - {Capability.FINANCIAL_REPORT_READ}), 403),
        (replace(base, mfa_verified_at=None), 403),
    ]:
        actor[0] = context
        denied = client.get(url, headers=headers)
        assert denied.status_code == status
        assert str(snapshot_id) not in denied.text and "estimation utilisateur" not in denied.text
    assert (
        AppRuntime.get_case_analysis_summary(cast(Any, runtime), tenant_id=uuid4(), case_id=seed[1])
        is None
    )
    with session_factory.begin() as s:
        s.execute(sa.text("SET session_replication_role = replica"))
        s.get(PricingScenarioRecord, scenario_id).source_snapshot_revision = 99
    item = next(a for a in read()["axes"] if a["code"] == "PRICE")["pricing_scenarios"][0]
    assert item["state"] == "UNKNOWN" and item["details"] is None

    with session_factory.begin() as s:
        s.get(CaseRecord, seed[1]).dce_freshness = "REVIEW_REQUIRED"
    cash = next(a for a in read()["axes"] if a["code"] == "CASH")
    assert cash["cash_reports"][0]["state"] == "UNKNOWN"
    assert cash["cash_reports"][0]["details"] is None
    assert cash["pricing_scenarios"][0]["details"] is None
    with session_factory.begin() as s:
        s.execute(sa.text("SET session_replication_role = replica"))
        s.get(FinancialReportSnapshotRecord, snapshot_id).state = "DRAFT"
        s.get(FinancialReportSnapshotRecord, snapshot_id).published_at = None
    assert next(a for a in read()["axes"] if a["code"] == "CASH")["cash_reports"] == []
