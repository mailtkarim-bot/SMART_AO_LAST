"""Adverse source cases for technical preparation eligibility; no corpus admission."""

from datetime import timedelta
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceVersionRecord,
)
from app.modules.dce.infrastructure.preparation_readiness import current_preparation_readiness
from app.modules.preparation.infrastructure.dce_preparation_reader import (
    SqlAlchemyPreparationDceReader,
)
from tests.db.test_transversal_affaire_workflow import affaire  # noqa: F401


@pytest.mark.parametrize("fault", ["failed_extraction", "unclassified", "foreign_tenant"])
def test_native_readiness_rejects_replaced_or_unproven_inputs(session_factory, affaire, fault):  # noqa: F811
    w = affaire
    with session_factory() as session:
        version = session.get(DceVersionRecord, w.seed[2])
        state, proof = current_preparation_readiness(session, version=version)
        assert state == "READY_FOR_ANALYSIS" and len(proof) == 64
    if fault == "foreign_tenant":
        with session_factory() as session:
            assert (
                SqlAlchemyPreparationDceReader().read(
                    session=session, tenant_id=uuid4(), dce_version_id=w.seed[2], as_of=w.now
                )
                is None
            )
        return
    with session_factory.begin() as session:
        document = w.seed[3]["rc.txt"]
        if fault == "failed_extraction":
            previous = session.scalar(
                sa.select(DceDocumentExtractionRecord).where(
                    DceDocumentExtractionRecord.tenant_id == w.actor.tenant_id,
                    DceDocumentExtractionRecord.dce_document_id == document,
                )
            )
            session.add(
                DceDocumentExtractionRecord(
                    id=uuid4(),
                    tenant_id=w.actor.tenant_id,
                    dce_version_id=w.seed[2],
                    dce_document_id=document,
                    input_sha256=previous.input_sha256,
                    extractor_id=previous.extractor_id,
                    extractor_version="synthetic-adverse-v2",
                    status="FAILED_SAFE",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC_UNREADABLE",
                    created_at=previous.created_at + timedelta(seconds=1),
                )
            )
        else:
            current = session.scalar(
                sa.select(DceDocumentClassificationRecord).where(
                    DceDocumentClassificationRecord.tenant_id == w.actor.tenant_id,
                    DceDocumentClassificationRecord.dce_document_id == document,
                    DceDocumentClassificationRecord.is_current.is_(True),
                )
            )
            current.is_current = False
    with session_factory() as session:
        version = session.get(DceVersionRecord, w.seed[2])
        state, proof = current_preparation_readiness(session, version=version, lock=True)
        assert state != "READY_FOR_ANALYSIS" and proof is None
