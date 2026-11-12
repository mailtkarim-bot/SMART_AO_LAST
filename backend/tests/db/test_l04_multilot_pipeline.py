"""Real text originals -> extraction -> active rules -> requirements -> L04, no gold injection."""

from __future__ import annotations

import asyncio
import json
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.case.infrastructure.analysis_dossier_reader import read_analysis_dossier
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.case.public.analysis_summary_contracts import CaseAnalysisSummaryResponse
from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
from app.modules.dce.application.requirements import DceRequirementsService
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceDocumentRecord,
)
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.platform.events.dispatcher import CommandDispatcher
from tests.application.test_dce_rc_analysis import (
    NOW,
    _analysis_service,
    _extraction_service,
    _seed_admitted_document,
    _stream,
)
from tests.db.test_candidate_retrieval_sql import _clone

FIXTURES = Path(__file__).parents[1] / "fixtures"
# Independent expectations at the public materialization/synthesis boundary.
EXPECTED_PROJECTIONS = {
    "RC_DOCUMENT_CANDIDATURE": ("CANDIDATURE_DOCUMENT", "CANDIDATURE"),
    "RC_SITE_VISIT": ("SITE_VISIT", "CANDIDATURE"),
    "RC_CONTENT_OFFER": ("OFFER_DOCUMENT", "DOCUMENTS"),
    "RC_SUBMISSION_DEADLINE": ("SUBMISSION_DEADLINE_SIGNAL", "DOCUMENTS"),
    "RC_RESPONSE_CHANNEL": ("SUBMISSION_CHANNEL", "DOCUMENTS"),
    "RC_FILE_CONSTRAINT": ("FILE_CONSTRAINT", "DOCUMENTS"),
    "RC_AWARD_CRITERION": ("AWARD_CRITERION_SIGNAL", "COMMERCIAL"),
    "RC_NEGOTIATION": ("NEGOTIATION_SIGNAL", "COMMERCIAL"),
    "RC_OFFER_VALIDITY": ("OFFER_VALIDITY_SIGNAL", "DOCUMENTS"),
    "CCAP_PENALTIES": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCAP_RETENTION_GUARANTEE": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCAP_GUARANTEE": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCAP_INSURANCE": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCAP_SUBCONTRACTING": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCAP_QUALIFICATIONS": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
    "CCTP_VARIANTS": ("CONTRACT_RISK_SIGNAL", "CONTRACT"),
}


@pytest.fixture(params=["dce_l04_multilot", "dce_l04_multilot_holdout_v2"])
def complete_dossier(session_factory, tmp_path, request):
    corpus = FIXTURES / request.param
    manifest = json.loads((corpus / "manifest.json").read_text())
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    first = manifest["documents"][0]
    if first.get("media_type"):
        from tests.application.test_dce_document_extraction import (
            _seed_admitted_document as seed_typed,
        )

        tenant, first_id, version = seed_typed(
            session_factory,
            storage=storage,
            source_bytes=(corpus / first["file"]).read_bytes(),
            media_type=first["media_type"],
        )
    else:
        tenant, first_id, version = _seed_admitted_document(
            session_factory, storage=storage, source_bytes=(corpus / first["file"]).read_bytes()
        )
    ids = {first["file"]: first_id}
    for doc in manifest["documents"]:
        raw = (corpus / doc["file"]).read_bytes()
        assert sha256(raw).hexdigest() == doc["sha256"]
        if doc is not first:
            doc_id, stage_id = uuid4(), uuid4()
            key = f"dce-staging/{tenant}/{stage_id}"
            asyncio.run(
                storage.write(storage_key=key, stream=_stream(raw), max_bytes=128 * 1024 * 1024)
            )
            with session_factory.begin() as s:
                original = s.get(DceDocumentRecord, first_id)
                stage = s.get(DceStagedObjectRecord, original.storage_object_id)
                s.add(
                    _clone(
                        stage,
                        id=stage_id,
                        storage_key=key,
                        original_filename=doc["file"],
                        media_type=doc.get("media_type", "text/plain"),
                        sha256=doc["sha256"],
                        expected_byte_size=len(raw),
                        actual_byte_size=len(raw),
                    )
                )
                s.flush()
                s.add(
                    _clone(
                        original,
                        id=doc_id,
                        storage_object_id=stage_id,
                        storage_key=key,
                        original_filename=doc["file"],
                        media_type=doc.get("media_type", "text/plain"),
                        sha256=doc["sha256"],
                        byte_size=len(raw),
                    )
                )
            ids[doc["file"]] = doc_id
        with session_factory.begin() as s:
            s.add(
                DceDocumentClassificationRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    dce_document_id=ids[doc["file"]],
                    classification=doc["family"],
                    source="SYNTHETIC",
                    rationale=None,
                    previous_classification_id=None,
                    is_current=True,
                    created_by_actor_id=None,
                )
            )
        asyncio.run(
            _extraction_service(session_factory=session_factory, storage=storage).extract(
                tenant_id=tenant, dce_document_id=ids[doc["file"]], now=NOW
            )
        )
    analysis = _analysis_service(session_factory=session_factory).analyze(
        tenant_id=tenant, dce_version_id=version, now=NOW
    )
    materializer = DceRequirementsService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementMaterializationRun": (
                    RecordDceRequirementMaterializationRunHandler()
                )
            },
        ),
    )
    args = dict(
        tenant_id=tenant,
        dce_version_id=version,
        dce_rc_analysis_id=UUID(analysis.aggregate_refs[0]["aggregate_id"]),
        now=NOW,
    )
    materializer.materialize(**args)
    assert materializer.materialize(**args).replayed
    case_id = uuid4()
    with session_factory.begin() as s:
        from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord

        v = s.get(DceVersionRecord, version)
        s.add(
            CaseRecord(
                id=case_id,
                tenant_id=tenant,
                consultation_id=v.consultation_id,
                applicable_dce_version_id=version,
                functional_identity_hash=sha256(str(case_id).encode()).hexdigest(),
                title="École synthétique - lots 1 et 2",
                business_origin="MANUAL",
                origin_rationale="Qualification locale",
                scope_kind="MULTI_LOT",
                scope_json={"lots": [str(lot) for lot in manifest["lots"]]},
                scope_fingerprint="d" * 64,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
            )
        )
    return tenant, case_id, version, ids, manifest


def read(factory, seed):
    with factory() as s:
        s.connection(execution_options={"isolation_level": "REPEATABLE READ"})
        return read_analysis_dossier(s, session_factory=factory, tenant_id=seed[0], case_id=seed[1])


def test_complete_multilot_sources_reach_dossier_without_invented_coverage(
    session_factory, complete_dossier
):
    seed = complete_dossier
    summary = read(session_factory, seed)
    CaseAnalysisSummaryResponse.model_validate(summary)
    assert len(summary["axes"]) == 12 and not summary["analysis_complete"]
    assert summary["source_context_state"] == "CURRENT"
    items = [i for axis in summary["axes"] for i in axis["items"]]
    assert items and all(i["source_state"] == "CURRENT_SOURCE" for i in items)
    # These original gold annotations predate execution-signal support. Keep their
    # RC/contract expectations independent; execution coverage has its own test.
    items = [
        i
        for i in items
        if i["native_type"]
        not in {
            "TECHNICAL_PRESCRIPTION",
            "LOGISTICS_CONSTRAINT",
            "SCHEDULE_CONSTRAINT",
            "HSE_CONSTRAINT",
            "PAYMENT_TERM_SIGNAL",
            "ACCEPTANCE_TERM_SIGNAL",
        }
    ]

    expected = [f for d in seed[4]["documents"] for f in d["facts"] if f["expected_kind"]]
    assert len(items) == len(expected)
    for doc in seed[4]["documents"]:
        for fact in doc["facts"]:
            matches = [
                i
                for i in items
                if i["source_excerpt"] == fact["quote"]
                and i["source_anchor"]["dce_document_id"] == seed[3][doc["file"]]
            ]
            if fact["expected_kind"]:
                assert len(matches) == 1, (doc["file"], fact, matches)
                item = matches[0]
                expected_type, expected_axis = EXPECTED_PROJECTIONS[fact["expected_kind"]]
                assert item["native_type"] == expected_type
                assert any(
                    item in a["items"] for a in summary["axes"] if a["code"] == expected_axis
                )
                anchor = item["source_anchor"]
                assert anchor["dce_version_id"] == seed[2]
                assert anchor["source_sha256"] == doc["sha256"]
                assert anchor["fragment_sha256"] == sha256(fact["quote"].encode()).hexdigest()
                assert anchor["locator"]["kind"] == "text_line"
                assert anchor["locator"]["coordinates"]["line"] == fact["line"]
                assert item["start_byte_offset"] == 0
                assert item["end_byte_offset"] == len(fact["quote"].encode())
            else:
                assert not matches  # Semantic gaps stay measured; no fabricated requirement.
    visits = [i for i in items if i["native_type"] == "SITE_VISIT"]
    assert len(visits) == 3
    positive = [i for i in visits if "ne sont pas" not in i["source_excerpt"]]
    assert {tuple(i["lot_numbers"]) for i in positive} == {
        (seed[4]["lots"][0],),
        (seed[4]["lots"][1],),
    }
    negative = next(i for i in visits if "ne sont pas" in i["source_excerpt"])
    assert negative["lot_numbers"] == [] and negative["lot_state"] == "UNKNOWN"
    assert all(i["applicability"] == "UNKNOWN" for i in items)
    assert summary["coverage"]["unread_documents"] == 0
    # Reading all originals is not equivalent to analysing all their business facts.
    assert any(not a["items"] and a["status"] == "NON_EVALUATED" for a in summary["axes"])
    with session_factory() as s:
        assert (
            read_analysis_dossier(
                s, session_factory=session_factory, tenant_id=uuid4(), case_id=seed[1]
            )
            is None
        )


def test_new_incomplete_extraction_invalidates_old_proofs(session_factory, complete_dossier):
    from datetime import timedelta

    from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord

    seed = complete_dossier
    before = read(session_factory, seed)
    doc_id = seed[3]["rc.txt"]
    with session_factory.begin() as s:
        old = s.scalar(
            sa.select(DceDocumentExtractionRecord).where(
                DceDocumentExtractionRecord.dce_document_id == doc_id
            )
        )
        s.add(
            _clone(
                old,
                id=uuid4(),
                extractor_version="synthetic-incomplete",
                status="REVIEW_REQUIRED",
                failure_code="SYNTHETIC_INCOMPLETE",
                created_at=old.created_at + timedelta(seconds=1),
            )
        )
    after = read(session_factory, seed)
    assert after["dossier_sha256"] != before["dossier_sha256"]
    assert not after["analysis_complete"]
    assert not any(
        i["source_state"] == "CURRENT_SOURCE" and i["source_anchor"]["dce_document_id"] == doc_id
        for a in after["axes"]
        for i in a["items"]
    )
