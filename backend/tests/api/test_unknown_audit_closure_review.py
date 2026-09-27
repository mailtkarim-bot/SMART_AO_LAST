from uuid import uuid4
from app.modules.dce.domain.unknown_audit_closure_review import UnknownAuditClosureReview

def test_closure_review_api_contract_keeps_public_go_forbidden() -> None:
    review = UnknownAuditClosureReview(uuid4(), 2, True, False, "Vérification locale")
    review.validate()
    assert review.public_go is False
