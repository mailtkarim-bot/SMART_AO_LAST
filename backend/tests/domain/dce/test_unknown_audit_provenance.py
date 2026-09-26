from datetime import UTC, datetime
from uuid import uuid4
import pytest
from app.modules.dce.domain.unknown_audit_provenance import UnknownAuditProvenance, UnknownAuditSource

def test_unknown_provenance_requires_source_and_event() -> None:
    UnknownAuditProvenance(uuid4(), UnknownAuditSource.HUMAN_RESUMPTION, uuid4(), uuid4(), "BLOCKED", datetime.now(tz=UTC), "Action requise").validate()

def test_unknown_provenance_rejects_empty_status() -> None:
    with pytest.raises(ValueError, match="PROVENANCE_STATUS_REQUIRED"):
        UnknownAuditProvenance(uuid4(), UnknownAuditSource.VERIFICATION, uuid4(), uuid4(), "", datetime.now(tz=UTC), None).validate()
