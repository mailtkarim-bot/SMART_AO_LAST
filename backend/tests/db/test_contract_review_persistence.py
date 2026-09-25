# ruff: noqa: E501
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.application.contract_review_handler import ContractProofReviewReadService
from app.modules.dce.infrastructure.models.contract_baseline import (
    ContractBaselineDeviationImpactRecord,
)
from app.modules.dce.infrastructure.models.contract_review import ContractProofReviewRecord
from app.platform.persistence.models import TenantRecord
from sqlalchemy.orm import Session
from tests.db.test_regulatory_profile_persistence import _case


def test_contract_review_table_is_append_only_and_revision_scoped(
    database_engine: sa.Engine,
) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("contract_proof_reviews")}
    constraints = {
        item["name"] for item in inspector.get_unique_constraints("contract_proof_reviews")
    }
    checks = {item["name"] for item in inspector.get_check_constraints("contract_proof_reviews")}
    assert {
        "id",
        "tenant_id",
        "proof_id",
        "reviewer_id",
        "reviewed_revision",
        "decision",
        "rationale",
    } <= columns
    assert "uq_contract_proof_reviews__functional" in constraints
    assert any("contract_review_revision_positive" in check for check in checks)
    assert any("contract_review_decision_closed" in check for check in checks)


def test_latest_projection_keeps_one_act_per_proof_revision() -> None:
    proof_id = uuid4()
    rows = (
        SimpleNamespace(proof_id=proof_id, reviewed_revision=2, created_at=3),
        SimpleNamespace(proof_id=proof_id, reviewed_revision=2, created_at=2),
        SimpleNamespace(proof_id=proof_id, reviewed_revision=1, created_at=1),
    )

    class Reader(ContractProofReviewReadService):
        def __init__(self):
            pass

        def list_for_case(self, *, actor, case_id, now):
            return rows

    projected = Reader().latest_for_case(actor=None, case_id=uuid4(), now=None)
    assert len(projected) == 2
    assert {item.reviewed_revision for item in projected} == {1, 2}


def test_postgres_keeps_revision_2_append_only_and_rejects_duplicate_review(
    database_engine: sa.Engine,
) -> None:
    tenant_id, case_id, observation_id = uuid4(), uuid4(), uuid4()
    with Session(database_engine) as session:
        session.add(
            TenantRecord(id=tenant_id, slug=f"review-{tenant_id.hex[:12]}", lifecycle="ACTIVE")
        )
        session.flush()
        session.add(_case(tenant_id=tenant_id, case_id=case_id, marker="r"))
        session.flush()
        for revision in (1, 2):
            session.add(
                ContractBaselineDeviationImpactRecord(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    case_id=case_id,
                    baseline_observation_id=observation_id,
                    proof_revision=revision,
                    baseline_source_refs_json=["dce://ccap/p4"],
                    baseline_statement="Baseline",
                    deviation_statement=None,
                    impact_statement=None,
                    status="UNKNOWN",
                )
            )
        session.flush()
        review = ContractProofReviewRecord(
            id=uuid4(),
            tenant_id=tenant_id,
            proof_id=session.scalar(
                sa.select(ContractBaselineDeviationImpactRecord.id).where(
                    ContractBaselineDeviationImpactRecord.tenant_id == tenant_id,
                    ContractBaselineDeviationImpactRecord.proof_revision == 2,
                )
            ),
            reviewer_id=uuid4(),
            reviewed_revision=2,
            decision="NEEDS_CLARIFICATION",
            rationale="Révision requise",
        )
        session.add(review)
        session.commit()
        session.add(
            ContractProofReviewRecord(
                id=uuid4(),
                tenant_id=tenant_id,
                proof_id=review.proof_id,
                reviewer_id=uuid4(),
                reviewed_revision=2,
                decision="NEEDS_CLARIFICATION",
                rationale="Rejeu",
            )
        )
        with pytest.raises(sa.exc.IntegrityError):
            session.commit()


def test_superseded_proof_revision_requires_a_new_review_act() -> None:
    proof_id = uuid4()
    old = SimpleNamespace(proof_id=proof_id, reviewed_revision=1, decision="ACCEPTED")
    rectified = SimpleNamespace(proof_id=proof_id, reviewed_revision=2, decision=None)
    assert old.decision == "ACCEPTED"
    assert rectified.decision is None
    assert old.reviewed_revision != rectified.reviewed_revision
