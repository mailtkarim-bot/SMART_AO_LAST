from uuid import uuid4
import pytest
from app.modules.dce.domain.unknown_audit_closure_review import UnknownAuditClosureReview

def test_closure_review_requires_evidence_docs_and_no_public_go() -> None:
    UnknownAuditClosureReview(uuid4(), 3, True, False, "Cycle local vérifié").validate()

@pytest.mark.parametrize("kwargs, error", [({"evidence_count": 0}, "CLOSURE_EVIDENCE_REQUIRED"), ({"documentation_synced": False}, "DOCUMENTATION_SYNC_REQUIRED"), ({"public_go": True}, "PUBLIC_GO_FORBIDDEN")])
def test_closure_review_rejects_invalid_state(kwargs, error) -> None:
    values = {"reviewer_id": uuid4(), "evidence_count": 1, "documentation_synced": True, "public_go": False, "rationale": "ok"}
    values.update(kwargs)
    with pytest.raises(ValueError, match=error):
        UnknownAuditClosureReview(**values).validate()
