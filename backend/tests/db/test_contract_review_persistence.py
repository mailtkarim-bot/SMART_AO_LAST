from types import SimpleNamespace
from uuid import uuid4

import sqlalchemy as sa

from app.modules.dce.application.contract_review_handler import ContractProofReviewReadService


def test_contract_review_table_is_append_only_and_revision_scoped(database_engine: sa.Engine) -> None:
    inspector = sa.inspect(database_engine)
    columns = {column["name"] for column in inspector.get_columns("contract_proof_reviews")}
    constraints = {item["name"] for item in inspector.get_unique_constraints("contract_proof_reviews")}
    checks = {item["name"] for item in inspector.get_check_constraints("contract_proof_reviews")}
    assert {"id", "tenant_id", "proof_id", "reviewer_id", "reviewed_revision", "decision", "rationale"} <= columns
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
