"""Actual mixed originals, native pipeline and immutable human review across versions."""

from __future__ import annotations

import asyncio
import json
from hashlib import sha256
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import pytest
from app.modules.case.application.commands import LinkCaseDceVersionCommand
from app.modules.case.application.link_dce_version_handler import LinkCaseDceVersionHandler
from app.modules.case.infrastructure.models.case import CaseRecord
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceDocumentRecord,
    DceVersionRecord,
)
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.platform.events.dispatcher import CommandDispatcher
from docx import Document
from openpyxl import Workbook
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from tests.application.test_dce_rc_analysis import (
    NOW,
    _analysis_service,
    _extraction_service,
    _stream,
)
from tests.db.test_analysis_assessment_sql import context
from tests.db.test_candidate_retrieval_sql import _clone
from tests.db.test_l04_execution_pipeline import (
    test_every_execution_point_can_be_treated_then_exact_dossier_reviewed as qualify_review,
)
from tests.db.test_l04_multilot_pipeline import complete_dossier, read

DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def originals(root, revision):
    root.mkdir()
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): writer._add_object(font)})}
    )
    quote = f"Le DC{revision} est obligatoire pour le lot 2."
    stream = DecodedStreamObject()
    stream.set_data(f"BT /F1 12 Tf 72 720 Td ({quote}) Tj ET".encode())
    page[NameObject("/Contents")] = writer._add_object(stream)
    writer.write(root / "rc.pdf")
    document = Document()
    document.add_paragraph("Installer des clapets coupe-feu pour le lot 2.")
    document.save(root / "cctp.docx")
    book = Workbook()
    book.active.title = "Planning"
    book.active["B3"] = "Les travaux du lot 7 seront exécutés du 3 mai au 28 mai 2027."
    book.save(root / "planning.xlsx")
    document = Document()
    document.add_paragraph("Annexe de sécurité à relire intégralement.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).merge(table.cell(0, 1)).text = "Ne pas intervenir sans consignation."
    document.save(root / "annexe.docx")
    documents = []
    for filename, family, media in [
        ("rc.pdf", "RC", "application/pdf"),
        ("cctp.docx", "CCTP", DOCX),
        ("planning.xlsx", "PLANNING", XLSX),
        ("annexe.docx", "PGC", DOCX),
    ]:
        documents.append(
            dict(
                file=filename,
                family=family,
                media_type=media,
                sha256=sha256((root / filename).read_bytes()).hexdigest(),
                facts=[],
            )
        )
    manifest = dict(lots=[2, 7], documents=documents, expected_point_count=3)
    (root / "manifest.json").write_text(json.dumps(manifest))
    return manifest


@pytest.fixture
def mixed(session_factory, tmp_path):
    corpus = tmp_path / "v1"
    originals(corpus, 1)
    seed = complete_dossier.__wrapped__(
        session_factory, tmp_path / "storage", SimpleNamespace(param=str(corpus))
    )
    return seed, tmp_path


def test_mixed_originals_keep_exact_anchors_and_unread_table(session_factory, mixed):
    seed, _ = mixed
    summary = read(session_factory, seed)
    points = [p for a in summary["axes"] for p in a["items"]]
    assert len(points) == 3
    assert summary["coverage"]["unread_documents"] == 1
    assert not summary["analysis_complete"]
    expected_kinds = {"pdf_page", "docx_paragraph", "xlsx_cell"}
    assert {p["source_anchor"]["locator"]["kind"] for p in points} == expected_kinds
    for point in points:
        anchor = point["source_anchor"]
        assert anchor["dce_version_id"] == seed[2]
        assert anchor["dce_document_id"] in seed[3].values()
        assert anchor["source_sha256"] in {d["sha256"] for d in seed[4]["documents"]}
        assert point["applicability"] == "UNKNOWN"
        assert point["source_state"] == "CURRENT_SOURCE"
        assert point["lot_state"] == "CANDIDATE"
        locator = anchor["locator"]
        expected = {
            "pdf_page": ({"page": 1, "part": 1}, [2], "Le DC1 est obligatoire pour le lot 2."),
            "docx_paragraph": (
                {"paragraph": 1, "part": 1},
                [2],
                "Installer des clapets coupe-feu pour le lot 2.",
            ),
            "xlsx_cell": (
                {"sheet": "Planning", "cell": "B3", "part": 1},
                [7],
                "Les travaux du lot 7 seront exécutés du 3 mai au 28 mai 2027.",
            ),
        }[locator["kind"]]
        assert locator["coordinates"] == expected[0]
        assert point["lot_numbers"] == expected[1]
        assert point["source_excerpt"] == expected[2]
    qualify_review(session_factory, seed)


def test_rectificatif_invalidates_review_and_restarts_treatments(
    session_factory, mixed, *, corpus_builder=originals, expected_points=3
):
    from app.modules.case.infrastructure.analysis_dossier_reader import (
        read_analysis_dossier_history,
    )
    from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
    from app.modules.dce.application.requirements import DceRequirementsService

    seed, root = mixed
    qualify_review(session_factory, seed)
    before = read(session_factory, seed)
    with session_factory() as s:
        history_before = read_analysis_dossier_history(
            s, tenant_id=seed[0], case_id=seed[1], before_revision=None
        )
    corpus = root / "v2"
    manifest = corpus_builder(corpus, 2)
    new_version = uuid4()
    with session_factory.begin() as s:
        old = s.get(DceVersionRecord, seed[2])
        s.add(_clone(old, id=new_version, predecessor_dce_version_id=old.id, corpus_hash="c" * 64))
    storage = LocalQuarantineStorageAdapter(root=root / "storage")
    ids = {}
    for doc in manifest["documents"]:
        doc_id, stage_id = uuid4(), uuid4()
        raw = (corpus / doc["file"]).read_bytes()
        key = f"dce-staging/{seed[0]}/{stage_id}"
        asyncio.run(
            storage.write(storage_key=key, stream=_stream(raw), max_bytes=128 * 1024 * 1024)
        )
        with session_factory.begin() as s:
            original = s.get(DceDocumentRecord, seed[3][doc["file"]])
            stage = s.get(DceStagedObjectRecord, original.storage_object_id)
            s.add(
                _clone(
                    stage,
                    id=stage_id,
                    storage_key=key,
                    sha256=doc["sha256"],
                    expected_byte_size=len(raw),
                    actual_byte_size=len(raw),
                    consumed_by_dce_version_id=new_version,
                )
            )
            s.flush()
            s.add(
                _clone(
                    original,
                    id=doc_id,
                    dce_version_id=new_version,
                    storage_object_id=stage_id,
                    storage_key=key,
                    sha256=doc["sha256"],
                    byte_size=len(raw),
                )
            )
            s.flush()
            s.add(
                DceDocumentClassificationRecord(
                    id=uuid4(),
                    tenant_id=seed[0],
                    dce_document_id=doc_id,
                    classification=doc["family"],
                    source="SYNTHETIC",
                    is_current=True,
                )
            )
        ids[doc["file"]] = doc_id
        asyncio.run(
            _extraction_service(session_factory=session_factory, storage=storage).extract(
                tenant_id=seed[0], dce_document_id=doc_id, now=NOW
            )
        )
    dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={
            "LinkCaseDceVersion": LinkCaseDceVersionHandler(),
            "RecordDceRequirementMaterializationRun": (
                RecordDceRequirementMaterializationRunHandler()
            ),
        },
    )
    with session_factory() as s:
        revision = s.get(CaseRecord, seed[1]).aggregate_revision
    cmd = LinkCaseDceVersionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        case_id=seed[1],
        dce_version_id=new_version,
        expected_case_revision=revision,
        reason="Rectificatif synthétique",
    )
    actor = context(seed)
    dispatcher.dispatch(command=cmd, context=actor)
    assert dispatcher.dispatch(command=cmd, context=actor).replayed
    intermediate = read(session_factory, seed)
    assert intermediate["dossier_review"]["state"] == "REVIEW_REQUIRED"
    from app.modules.case.application.analysis_assessment import RecordAnalysisAssessmentCommand
    from app.modules.case.infrastructure.analysis_assessment_handler import (
        RecordAnalysisAssessmentHandler,
    )
    from app.platform.events.dispatcher import CommandExecutionError
    from tests.application.test_analysis_assessment import fields

    point = next(p for a in before["axes"] for p in a["items"])
    stale_payload = fields()
    stale_payload.update(
        case_id=seed[1],
        point_kind="REQUIREMENT",
        point_id=point["item_id"],
        expected_revision=1,
        source_context_sha256=point["source_context_sha256"],
    )
    assessment_dispatcher = CommandDispatcher(
        session_factory=session_factory,
        handlers={"RecordAnalysisAssessment": RecordAnalysisAssessmentHandler()},
    )
    with pytest.raises(CommandExecutionError, match="STALE_SOURCE_CONTEXT"):
        assessment_dispatcher.dispatch(
            command=RecordAnalysisAssessmentCommand(**stale_payload),
            context=actor,
        )
    analysis = _analysis_service(session_factory=session_factory).analyze(
        tenant_id=seed[0], dce_version_id=new_version, now=NOW
    )
    DceRequirementsService(session_factory=session_factory, dispatcher=dispatcher).materialize(
        tenant_id=seed[0],
        dce_version_id=new_version,
        dce_rc_analysis_id=UUID(cast(str, analysis.aggregate_refs[0]["aggregate_id"])),
        now=NOW,
    )
    successor = seed[0], seed[1], new_version, ids, manifest
    after = read(session_factory, successor)
    points = [p for a in after["axes"] for p in a["items"]]
    assert len(points) == expected_points and after["coverage"]["unread_documents"] == 1
    assert before["dossier_sha256"] != after["dossier_sha256"]
    assert all(p["human_assessment"] is None for p in points)
    assert all(p["source_anchor"]["dce_version_id"] == new_version for p in points)
    with session_factory() as s:
        history = read_analysis_dossier_history(
            s, tenant_id=seed[0], case_id=seed[1], before_revision=None
        )
    assert history == history_before
    assert history["entries"][0]["snapshot"]["dce_version_id"] == str(seed[2])

    qualify_review(session_factory, successor, initial_revision=3)
    final = read(session_factory, successor)
    assert final["dossier_review"]["state"] == "CURRENT"
    assert final["dossier_review"]["revision"] == 6
    with session_factory() as s:
        prior = read_analysis_dossier_history(
            s, tenant_id=seed[0], case_id=seed[1], before_revision=4
        )
    assert prior == history_before


def test_fresh_extraction_can_be_rematerialized_without_ghost_points(
    session_factory, mixed, monkeypatch
):
    from dataclasses import replace
    from datetime import timedelta

    import app.modules.dce.application.extraction as module
    from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
    from app.modules.dce.application.requirements import DceRequirementsService

    seed, root = mixed
    before = read(session_factory, seed)
    original = module._project_document

    def fresh(**kwargs):
        return replace(original(**kwargs), extractor_version="synthetic-new-recipe")

    monkeypatch.setattr(module, "_project_document", fresh)
    storage = LocalQuarantineStorageAdapter(root=root / "storage")
    for document in seed[3].values():
        asyncio.run(
            _extraction_service(session_factory=session_factory, storage=storage).extract(
                tenant_id=seed[0], dce_document_id=document, now=NOW + timedelta(seconds=1)
            )
        )
    stale = read(session_factory, seed)
    assert all(p["source_state"] == "UNKNOWN" for a in stale["axes"] for p in a["items"])
    analysis = _analysis_service(session_factory=session_factory).analyze(
        tenant_id=seed[0], dce_version_id=seed[2], now=NOW + timedelta(seconds=2)
    )
    service = DceRequirementsService(
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
    service.materialize(
        tenant_id=seed[0],
        dce_version_id=seed[2],
        dce_rc_analysis_id=UUID(cast(str, analysis.aggregate_refs[0]["aggregate_id"])),
        now=NOW + timedelta(seconds=3),
    )
    current = read(session_factory, seed)
    points = [p for a in current["axes"] for p in a["items"]]
    assert len(points) == 3
    assert all(p["source_state"] == "CURRENT_SOURCE" for p in points)
    assert before["dossier_sha256"] != current["dossier_sha256"]
    qualify_review(session_factory, seed)

    import sqlalchemy as sa
    from app.modules.dce.infrastructure.models.dce_requirements import (
        DceRequirementMaterializationRunRecord as Run,
    )
    from app.modules.dce.infrastructure.models.dce_requirements import (
        DceRequirementRecord,
    )

    with session_factory.begin() as s:
        assert (
            s.scalar(
                sa.select(sa.func.count())
                .select_from(DceRequirementRecord)
                .where(DceRequirementRecord.tenant_id == seed[0])
            )
            == 6
        )
        latest = s.scalar(
            sa.select(Run).where(Run.tenant_id == seed[0]).order_by(Run.created_at.desc()).limit(1)
        )
        s.add(
            _clone(
                latest,
                id=uuid4(),
                input_manifest_sha256="e" * 64,
                status="FAILED_SAFE",
                failure_code="SYNTHETIC_FAILURE",
                created_at=latest.created_at + timedelta(seconds=1),
            )
        )
    failed = read(session_factory, seed)
    remaining = [p for a in failed["axes"] for p in a["items"]]
    assert len(remaining) == 3
    assert all(p["source_state"] == "UNKNOWN" for p in remaining)
    assert failed["dossier_review"]["state"] == "REVIEW_REQUIRED"
