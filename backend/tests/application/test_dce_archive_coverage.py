# ruff: noqa: F401, F811
from __future__ import annotations

import asyncio
import sys
from dataclasses import asdict
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4
from zipfile import ZipFile

import pytest
import sqlalchemy as sa
from app.modules.dce.application.extraction import DceDocumentExtractionService
from app.modules.dce.application.handlers import RecordDceDocumentExtractionHandler
from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionFragmentRecord
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentIssueRecord,
    DceMissingDocumentDeclarationRecord,
)
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.platform.events.dispatcher import CommandDispatcher

sys.path.append(str(Path(__file__).parent))
from test_dce_document_extraction import NOW, _seed_admitted_document, isolate_extraction_records


def test_archive_entries_and_missing_declarations_are_visible_without_source_promotion(
    session_factory,
    tmp_path,
):
    content = BytesIO()
    with ZipFile(content, "w") as archive:
        archive.writestr("../private-path.txt", "private body")
        archive.writestr("valid.txt", "no automatic admission")
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=content.getvalue(),
        media_type="application/zip",
    )
    service = DceDocumentExtractionService(
        session_factory=session_factory,
        storage=storage,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDceDocumentExtraction": RecordDceDocumentExtractionHandler()},
        ),
    )
    first = asyncio.run(service.extract(tenant_id=tenant, dce_document_id=document, now=NOW))
    replay = asyncio.run(service.extract(tenant_id=tenant, dce_document_id=document, now=NOW))
    assert replay.replayed
    assert first.aggregate_refs == replay.aggregate_refs
    declaration_id = uuid4()
    with session_factory.begin() as session:
        session.add(
            DceMissingDocumentDeclarationRecord(
                id=declaration_id,
                tenant_id=tenant,
                dce_version_id=version,
                expected_document_family="CCAP",
                expectation_source_kind="PRIVATE_UNVERIFIED",
                expectation_source_id="private source reference",
                reason="private justification",
                created_by_actor_id=None,
            )
        )
    with session_factory() as session:
        reader = SqlAlchemyCaseDceReadingReader(session)
        coverage = reader._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="SINGLE_LOT"
        )
        assert len(coverage.exceptions) == 3
        archives = [item for item in coverage.exceptions if item.kind == "ARCHIVE_ENTRY"]
        assert [item.state for item in archives] == ["EXCLUDED_UNSAFE", "NOT_EXTRACTED"]
        assert all(
            item.document_id == document and item.source_state == "RESOLVED" for item in archives
        )
        missing = next(item for item in coverage.exceptions if item.kind == "DECLARED_MISSING")
        assert missing.observation_id == declaration_id
        assert missing.document_family == "CCAP"
        assert missing.source_state == missing.lot_applicability == missing.criticality == "UNKNOWN"
        assert coverage.analysis_complete is False
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(DceDocumentExtractionFragmentRecord)
            )
            == 0
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(DceDocumentIssueRecord)) == 2
        text = str(asdict(coverage))
        for private in [
            "private body",
            "private-path",
            "private source reference",
            "private justification",
        ]:
            assert private not in text
        for t, v in [(uuid4(), version), (tenant, uuid4())]:
            assert (
                reader._read_coverage(
                    tenant_id=t, dce_version_id=v, case_scope_kind="CUSTOM"
                ).exceptions
                == ()
            )


def test_archive_anchor_cannot_be_resolved_with_a_discordant_extraction_hash(
    session_factory,
    tmp_path,
):
    from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord
    from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=b"synthetic archive",
        media_type="application/zip",
    )
    extraction = uuid4()
    with session_factory.begin() as session:
        source = session.get(DceDocumentRecord, document)
        session.add(
            DceDocumentExtractionRecord(
                id=extraction,
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                input_sha256="0" * 64,
                extractor_id="smart-ao-archive-inventory",
                extractor_version="1",
                status="UNSUPPORTED",
                fragment_count=0,
                extracted_char_count=0,
                failure_code="ARCHIVE_MEMBERS_NOT_ADMITTED",
                created_at=NOW,
            )
        )
        session.flush()
        session.add(
            DceDocumentIssueRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_version_id=version,
                dce_document_id=document,
                issue_kind="ARCHIVE_ENTRY_NOT_ADMITTED",
                impact="REVIEW_REQUIRED",
                reason="synthetic",
                locator_json={
                    "kind": "archive_entry",
                    "extraction_id": str(extraction),
                    "source_sha256": source.sha256,
                    "entry_path": [1],
                    "state": "NOT_EXTRACTED",
                },
                created_by_actor_id=None,
            )
        )
    with session_factory() as session:
        coverage = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant,
            dce_version_id=version,
            case_scope_kind="CUSTOM",
        )
        assert len(coverage.exceptions) == 1
        assert coverage.exceptions[0].source_state == "UNKNOWN"
        assert coverage.exceptions[0].state == "UNREADABLE"
        assert not coverage.analysis_complete


def test_archive_issues_and_extraction_roll_back_together_then_retry_once(
    session_factory,
    tmp_path,
    monkeypatch,
):
    from app.modules.dce.application import handlers as module
    from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord
    from app.platform.events.dispatcher import CommandExecutionError

    source = BytesIO()
    with ZipFile(source, "w") as archive:
        archive.writestr("first", b"one")
        archive.writestr("second", b"two")
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=source.getvalue(),
        media_type="application/zip",
    )
    service = DceDocumentExtractionService(
        session_factory=session_factory,
        storage=storage,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDceDocumentExtraction": RecordDceDocumentExtractionHandler()},
        ),
    )
    original = module.DceDocumentIssueRecord
    calls = 0

    def fail_second(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise ValueError("synthetic persistence refusal")
        return original(**kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(module, "DceDocumentIssueRecord", fail_second)
        with pytest.raises(CommandExecutionError):
            asyncio.run(service.extract(tenant_id=tenant, dce_document_id=document, now=NOW))
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(DceDocumentExtractionRecord)) == 0
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(DceDocumentIssueRecord)) == 0
    asyncio.run(service.extract(tenant_id=tenant, dce_document_id=document, now=NOW))
    assert asyncio.run(
        service.extract(tenant_id=tenant, dce_document_id=document, now=NOW)
    ).replayed
    with session_factory() as session:
        assert (
            session.scalar(sa.select(sa.func.count()).select_from(DceDocumentExtractionRecord)) == 1
        )
        assert session.scalar(sa.select(sa.func.count()).select_from(DceDocumentIssueRecord)) == 2


def test_historical_archive_inventory_is_preserved_but_not_projected_as_current(
    session_factory,
    tmp_path,
):
    from datetime import timedelta

    from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord
    from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=b"synthetic",
        media_type="application/zip",
    )
    old, current = uuid4(), uuid4()
    with session_factory.begin() as session:
        source = session.get(DceDocumentRecord, document)
        for run, extractor_version, date in [
            (old, "0", NOW),
            (current, "1", NOW + timedelta(seconds=1)),
        ]:
            session.add(
                DceDocumentExtractionRecord(
                    id=run,
                    tenant_id=tenant,
                    dce_version_id=version,
                    dce_document_id=document,
                    input_sha256=source.sha256,
                    extractor_id="smart-ao-archive-inventory",
                    extractor_version=extractor_version,
                    status="UNSUPPORTED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="ARCHIVE_MEMBERS_NOT_ADMITTED",
                    created_at=date,
                )
            )
        session.flush()
        for run, path in [(old, [1]), (current, [2])]:
            session.add(
                DceDocumentIssueRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    dce_version_id=version,
                    dce_document_id=document,
                    issue_kind="ARCHIVE_ENTRY_NOT_ADMITTED",
                    impact="REVIEW_REQUIRED",
                    reason="synthetic",
                    locator_json={
                        "kind": "archive_entry",
                        "extraction_id": str(run),
                        "source_sha256": source.sha256,
                        "entry_path": path,
                        "state": "NOT_EXTRACTED",
                    },
                    created_by_actor_id=None,
                )
            )
    with session_factory() as session:
        coverage = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant,
            dce_version_id=version,
            case_scope_kind="CUSTOM",
        )
        assert len(coverage.exceptions) == 1
        assert coverage.exceptions[0].extraction_id == current
        assert coverage.exceptions[0].entry_path == (2,)
        assert session.scalar(sa.select(sa.func.count()).select_from(DceDocumentIssueRecord)) == 2
