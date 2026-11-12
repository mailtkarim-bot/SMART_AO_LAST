# ruff: noqa: F401,F811
from __future__ import annotations

import asyncio
import sys
from dataclasses import asdict
from datetime import timedelta
from hashlib import sha256
from io import BytesIO
from pathlib import Path
from uuid import uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.application.extraction import (
    EXTRACTOR_ID,
    EXTRACTOR_VERSION,
    DceDocumentExtractionService,
)
from app.modules.dce.application.handlers import RecordDceDocumentExtractionHandler
from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.dce.infrastructure.models.dce_extraction import (
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_version import (
    DceDocumentClassificationRecord,
    DceDocumentRecord,
)
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.platform.events.dispatcher import CommandDispatcher
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

sys.path.append(str(Path(__file__).parent))
from test_dce_document_extraction import NOW, _seed_admitted_document, isolate_extraction_records


def _source(session_factory, tmp_path, pages=None, *, extract=True):
    writer = PdfWriter()
    for text in pages or [
        b"Le DCE comprend : RC, CCAP pour le lot 2.",
        b"Le CCAP n'est pas joint pour le lot 2.",
    ]:
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
        stream = DecodedStreamObject()
        lines = [
            line.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
            for line in text.split(b"\n")
        ]
        stream.set_data(
            b"BT /F1 6 Tf 8 TL 72 720 Td "
            + b" ".join(b"(" + line + b") Tj T*" for line in lines)
            + b" ET"
        )
        page[NameObject("/Contents")] = writer._add_object(stream)
    data = BytesIO()
    writer.write(data)
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=data.getvalue(), media_type="application/pdf"
    )
    service = DceDocumentExtractionService(
        session_factory=session_factory,
        storage=storage,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={"RecordDceDocumentExtraction": RecordDceDocumentExtractionHandler()},
        ),
    )
    if extract:
        asyncio.run(service.extract(tenant_id=tenant, dce_document_id=document, now=NOW))
    with session_factory.begin() as session:
        session.add(
            DceDocumentClassificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_document_id=document,
                classification="RC",
                rationale=None,
                source="SYNTHETIC_TEST",
                previous_classification_id=None,
                is_current=True,
                created_by_actor_id=None,
            )
        )
    return tenant, document, version


def test_candidate_announcements_use_exact_pdf_pages_without_declaring_missing_pieces(
    session_factory, tmp_path
):
    tenant, document, version = _source(session_factory, tmp_path)
    with session_factory() as session:
        reader = SqlAlchemyCaseDceReadingReader(session)
        result = reader._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="SINGLE_LOT"
        )
        assert result.announcement_scan_state == "CANDIDATES_ONLY"
        assert len(result.announcements) == 3
        own_rc = next(item for item in result.announcements if item.document_family == "RC")
        assert own_rc.family_candidate_document_ids == (document,)
        ccap = [item for item in result.announcements if item.document_family == "CCAP"]
        assert {item.conflict_state for item in ccap} == {"CONFLICTING_CANDIDATES"}
        assert {item.source_locator_label for item in ccap} == {"RC · page 1", "RC · page 2"}
        for item in result.announcements:
            assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"
            assert item.source_document_id == document
            fragment = session.get(DceDocumentExtractionFragmentRecord, item.source_fragment_id)
            assert fragment.text.encode()[item.start_byte_offset : item.end_byte_offset]
            assert (
                item.family_candidate_document_ids == () if item.document_family == "CCAP" else True
            )
        assert not result.analysis_complete
        payload = str(asdict(result))
        assert "Le DCE comprend" not in payload
        assert "sha256" not in payload
        assert result == reader._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="SINGLE_LOT"
        )
        for t, v in [(uuid4(), version), (tenant, uuid4())]:
            assert (
                reader._read_coverage(
                    tenant_id=t, dce_version_id=v, case_scope_kind="CUSTOM"
                ).announcements
                == ()
            )


@pytest.mark.parametrize("fault", ["new_refusal", "fragment_hash", "input_hash"])
def test_old_or_discordant_sources_never_produce_current_announcements(
    session_factory, tmp_path, fault
):
    tenant, document, version = _source(session_factory, tmp_path)
    with session_factory.begin() as session:
        old = session.scalar(
            sa.select(DceDocumentExtractionRecord).where(
                DceDocumentExtractionRecord.dce_document_id == document
            )
        )
        source = session.get(DceDocumentRecord, document)
        run = uuid4()
        text = "Le dossier comprend le CCAP."
        session.add(
            DceDocumentExtractionRecord(
                id=run,
                tenant_id=tenant,
                dce_document_id=document,
                dce_version_id=version,
                input_sha256="0" * 64 if fault == "input_hash" else source.sha256,
                extractor_id="synthetic",
                extractor_version="fresh",
                status="FAILED_SAFE" if fault == "new_refusal" else "COMPLETED",
                fragment_count=0 if fault == "new_refusal" else 1,
                extracted_char_count=0 if fault == "new_refusal" else len(text),
                failure_code="SYNTHETIC" if fault == "new_refusal" else None,
                created_at=old.created_at + timedelta(seconds=1),
            )
        )
        session.flush()
        if fault != "new_refusal":
            session.add(
                DceDocumentExtractionFragmentRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    extraction_id=run,
                    ordinal=1,
                    locator_json={"kind": "pdf_page", "page": 1},
                    text=text,
                    text_sha256="0" * 64
                    if fault == "fragment_hash"
                    else sha256(text.encode()).hexdigest(),
                )
            )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert result.announcements == ()
        assert result.announcement_scan_state == "REVIEW_REQUIRED"
        assert not result.analysis_complete


@pytest.mark.parametrize(
    "constant",
    [
        "_MAX_ANNOUNCEMENT_SOURCE_FRAGMENTS",
        "_MAX_ANNOUNCEMENT_SOURCE_CHARS",
        "_MAX_ANNOUNCEMENT_CANDIDATES",
    ],
)
def test_announcement_limits_are_visible_without_partial_completeness(
    session_factory,
    tmp_path,
    monkeypatch,
    constant,
):
    from app.modules.dce.infrastructure import case_dce_reading_reader as module

    tenant, document, version = _source(session_factory, tmp_path)
    monkeypatch.setattr(module, constant, 1)
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant,
            dce_version_id=version,
            case_scope_kind="CUSTOM",
        )
        assert result.announcement_scan_state == "REJECTED_LIMIT"
        assert result.announcements == ()
        assert not result.analysis_complete


def test_reading_announcements_does_not_create_requirements_or_missing_declarations(
    session_factory, tmp_path
):
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
    from app.modules.dce.infrastructure.models.dce_version import (
        DceMissingDocumentDeclarationRecord,
    )

    tenant, document, version = _source(session_factory, tmp_path)
    with session_factory() as session:
        reader = SqlAlchemyCaseDceReadingReader(session)
        reader._read_coverage(tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM")
        session.flush()
        assert session.scalar(sa.select(sa.func.count()).select_from(DceRequirementRecord)) == 0
        assert (
            session.scalar(
                sa.select(sa.func.count()).select_from(DceMissingDocumentDeclarationRecord)
            )
            == 0
        )


def test_consecutive_pdf_list_keeps_both_fragment_anchors(session_factory, tmp_path):
    tenant, document, version = _source(
        session_factory,
        tmp_path,
        [
            b"Le DCE comprend :",
            b"- CCAP\n- CCTP",
        ],
    )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert {item.document_family for item in result.announcements} == {"CCAP", "CCTP"}
        for item in result.announcements:
            assert item.context_fragment_id != item.source_fragment_id
            assert item.context_locator_label == "RC · page 1"
            assert item.source_locator_label == "RC · page 2"
            heading = session.get(DceDocumentExtractionFragmentRecord, item.context_fragment_id)
            source = session.get(DceDocumentExtractionFragmentRecord, item.source_fragment_id)
            assert heading.extraction_id == source.extraction_id == item.source_extraction_id
            assert (
                heading.text.encode()[item.context_start_byte_offset : item.context_end_byte_offset]
                .decode()
                .endswith(":")
            )
            assert (
                source.text.encode()[item.start_byte_offset : item.end_byte_offset].decode()
                == item.document_family
            )
            assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"


@pytest.mark.parametrize(
    "fault",
    [
        "skipped_page",
        "previous_part",
        "skipped_ordinal",
        "hash",
        "part",
        "kind",
        "heading_replaced",
        "extraction",
    ],
)
def test_continuation_refuses_unproven_source_link(session_factory, tmp_path, fault):
    tenant, document, version = _source(
        session_factory,
        tmp_path,
        [
            b"Le DCE comprend :",
            b"- CCAP\n- CCTP",
        ],
        extract=False,
    )
    with session_factory.begin() as session:
        old_id = uuid4()
        parent = session.get(DceDocumentRecord, document)
        run = uuid4()
        session.add(
            DceDocumentExtractionRecord(
                id=run,
                tenant_id=tenant,
                dce_document_id=document,
                dce_version_id=version,
                input_sha256=parent.sha256,
                extractor_id=EXTRACTOR_ID,
                extractor_version=EXTRACTOR_VERSION,
                status="COMPLETED",
                fragment_count=2,
                extracted_char_count=50,
                failure_code=None,
                created_at=NOW + timedelta(seconds=1),
            )
        )
        if fault == "extraction":
            session.add(
                DceDocumentExtractionRecord(
                    id=old_id,
                    tenant_id=tenant,
                    dce_document_id=document,
                    dce_version_id=version,
                    input_sha256=parent.sha256,
                    extractor_id="synthetic-old",
                    extractor_version="1",
                    status="COMPLETED",
                    fragment_count=1,
                    extracted_char_count=17,
                    failure_code=None,
                    created_at=NOW,
                )
            )
        session.flush()
        for index, text in enumerate(["Le DCE comprend :", "- CCAP\n- CCTP"], 1):
            locator = {"kind": "pdf_page", "page": index, "part": 1}
            if index == 1 and fault == "previous_part":
                locator.pop("part")
            if index == 2 and fault == "skipped_page":
                locator["page"] = 3
            if index == 2 and fault == "part":
                locator["part"] = 2
            if index == 2 and fault == "kind":
                locator = {"kind": "text_line", "line": 2}
            if index == 1 and fault == "heading_replaced":
                text = "Autre section"
            session.add(
                DceDocumentExtractionFragmentRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    extraction_id=old_id if index == 1 and fault == "extraction" else run,
                    ordinal=3
                    if index == 2 and fault == "skipped_ordinal"
                    else (3 if index == 1 and fault == "extraction" else index),
                    locator_json=locator,
                    text=text,
                    text_sha256="0" * 64
                    if index == 1 and fault == "hash"
                    else sha256(text.encode()).hexdigest(),
                )
            )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert result.announcements == ()
        assert not result.analysis_complete


@pytest.mark.parametrize(
    "mode", ["three_pages", "two_pages_extended", "same_page", "word_split", "heading_split"]
)
def test_long_list_has_verifiable_region_chain(session_factory, tmp_path, mode):
    if mode == "three_pages":
        pages = [b"Le DCE comprend :", b"- CCAP", b"- CCTP"]
    elif mode == "two_pages_extended":
        pages = [b"Le DCE comprend :\n- CCAP", b"- CCTP"]
    else:
        # Visible short filler lines place the requested boundary at the real 8000-char chunk.
        target = {
            "same_page": "\n- CCTP",
            "word_split": "AP\n- CCTP",
            "heading_split": "prend :\n- CCAP\n- CCTP",
        }[mode]
        suffix = {
            "same_page": "Le DCE comprend :\n- CCAP",
            "word_split": "Le DCE comprend :\n- CC",
            "heading_split": "Le DCE com",
        }[mode]
        length = 8000 - len(suffix)
        filler = (("Texte neutre de qualification. " * 4 + "\n") * 100)[: length - 1] + "\n"
        pages = [(filler + suffix + target).encode()]
    tenant, document, version = _source(session_factory, tmp_path, pages)
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert {x.document_family for x in result.announcements} == {"CCAP", "CCTP"}
        cctp = next(x for x in result.announcements if x.document_family == "CCTP")
        assert len({a.fragment_id for a in cctp.anchor_chain}) == (
            3 if mode == "three_pages" else 2
        )
        if mode == "two_pages_extended":
            assert cctp.rule_version == "3"
        for item in result.announcements:
            if item.anchor_chain:
                for anchor in item.anchor_chain:
                    original = session.get(DceDocumentExtractionFragmentRecord, anchor.fragment_id)
                    assert (
                        original.tenant_id == tenant
                        and original.extraction_id == item.source_extraction_id
                    )
                    assert original.ordinal == anchor.fragment_ordinal
                    assert original.locator_json["part"] == anchor.part
                    assert original.text.encode()[anchor.start_byte_offset : anchor.end_byte_offset]
            assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"
        assert not result.analysis_complete


def test_chain_refuses_an_unqualified_parser_contract(session_factory, tmp_path):
    suffix = "Le DCE comprend :"
    length = 8000 - len(suffix)
    filler = (("Texte neutre de qualification. " * 4 + "\n") * 100)[: length - 1] + "\n"
    tenant, document, version = _source(
        session_factory, tmp_path, [(filler + suffix + "\n- CCAP\n- CCTP").encode()]
    )
    with session_factory.begin() as session:
        old = session.scalar(
            sa.select(DceDocumentExtractionRecord).where(
                DceDocumentExtractionRecord.dce_document_id == document
            )
        )
        fragments = list(
            session.scalars(
                sa.select(DceDocumentExtractionFragmentRecord).where(
                    DceDocumentExtractionFragmentRecord.extraction_id == old.id
                )
            )
        )
        run = uuid4()
        session.add(
            DceDocumentExtractionRecord(
                id=run,
                tenant_id=tenant,
                dce_document_id=document,
                dce_version_id=version,
                input_sha256=old.input_sha256,
                extractor_id="UNQUALIFIED_SYNTHETIC",
                extractor_version="unknown",
                status="COMPLETED",
                fragment_count=len(fragments),
                extracted_char_count=sum(len(x.text) for x in fragments),
                failure_code=None,
                created_at=old.created_at + timedelta(seconds=1),
            )
        )
        session.flush()
        for x in fragments:
            session.add(
                DceDocumentExtractionFragmentRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    extraction_id=run,
                    ordinal=x.ordinal,
                    text=x.text,
                    text_sha256=x.text_sha256,
                    locator_json=x.locator_json,
                )
            )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert result.announcements == ()
        assert not result.analysis_complete


@pytest.mark.parametrize(
    "heading,line,claim,end",
    [
        ("Le DCE comprend :", "- CCAP fourni", "PROVIDED_SIGNAL", 13),
        ("Le DCE comprend :", "- CCAP non fourni", "NOT_PROVIDED_SIGNAL", 17),
        ("Documents fournis pour le lot 2 :", "- CCAP fourni", "PROVIDED_SIGNAL", 13),
    ],
)
def test_autonomous_announcements_keep_legacy_identity_and_scope(
    session_factory, tmp_path, heading, line, claim, end
):
    from uuid import uuid5

    tenant, document, version = _source(
        session_factory, tmp_path, [heading.encode(), line.encode()]
    )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert len(result.announcements) == 1
        item = result.announcements[0]
        assert item.candidate_id == uuid5(
            item.source_fragment_id, f"announcement:1:CCAP:2:{end}:None"
        )
        assert item.rule_version == "1" and item.context_fragment_id is None
        assert item.context_start_byte_offset is None and item.anchor_chain == ()
        assert item.claim == claim and item.lot_numbers == ()


@pytest.mark.parametrize(
    "body", ["CCAP fourni\n- CCTP fourni", "Documents fournis :\n- CCAP\n- CCTP fourni"]
)
def test_missing_chunk_prefix_cannot_promote_a_partial_first_line(session_factory, tmp_path, body):
    from app.modules.dce.application.extraction import _extract_pdf

    suffix = "non "
    length = 8000 - len(suffix)
    filler = (("Texte neutre de qualification. " * 4 + "\n") * 100)[: length - 1] + "\n"
    tenant, document, version = _source(
        session_factory,
        tmp_path,
        [(filler + suffix + body).encode()],
        extract=False,
    )
    with session_factory.begin() as session:
        parent = session.get(DceDocumentRecord, document)
        storage = LocalQuarantineStorageAdapter(root=tmp_path)
        data = asyncio.run(
            storage.read_bytes(storage_key=parent.storage_key, max_bytes=128 * 1024 * 1024)
        )
        fragments = _extract_pdf(source_bytes=data)
        assert len(fragments) == 2
        run = uuid4()
        session.add(
            DceDocumentExtractionRecord(
                id=run,
                tenant_id=tenant,
                dce_document_id=document,
                dce_version_id=version,
                input_sha256=parent.sha256,
                extractor_id=EXTRACTOR_ID,
                extractor_version=EXTRACTOR_VERSION,
                status="COMPLETED",
                fragment_count=2,
                extracted_char_count=sum(len(x.text) for x in fragments),
                failure_code=None,
                created_at=NOW,
            )
        )
        session.flush()
        for x in fragments:
            session.add(
                DceDocumentExtractionFragmentRecord(
                    id=uuid4(),
                    tenant_id=tenant,
                    extraction_id=run,
                    ordinal=x.ordinal,
                    text=x.text,
                    locator_json=x.locator_json,
                    text_sha256="0" * 64 if x.ordinal == 1 else sha256(x.text.encode()).hexdigest(),
                )
            )
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        ccap = next(x for x in result.announcements if x.document_family == "CCAP")
        assert ccap.claim == "AMBIGUOUS" and ccap.lot_numbers == ()
        assert ccap.anchor_chain == ()
        cctp = next(x for x in result.announcements if x.document_family == "CCTP")
        assert cctp.claim == ("AMBIGUOUS" if body.startswith("Documents") else "PROVIDED_SIGNAL")
        assert result.announcement_scan_state == "REVIEW_REQUIRED" and not result.analysis_complete


def test_new_long_heading_never_reuses_legacy_rule_two(session_factory, tmp_path):
    heading = "Documents fournis " + " " * 1000 + ":"
    tenant, document, version = _source(session_factory, tmp_path, [heading.encode(), b"- CCAP"])
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert len(result.announcements) == 1
        assert result.announcements[0].rule_version == "3"


def test_total_chain_limit_rejects_without_partial_candidates(
    session_factory, tmp_path, monkeypatch
):
    from app.modules.dce.infrastructure import case_dce_reading_reader as module

    tenant, document, version = _source(
        session_factory, tmp_path, [b"Le DCE comprend :", b"- CCAP", b"- CCTP"]
    )
    monkeypatch.setattr(module, "_MAX_ANNOUNCEMENT_CHAIN_ANCHORS", 1)
    with session_factory() as session:
        result = SqlAlchemyCaseDceReadingReader(session)._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert result.announcement_scan_state == "REJECTED_LIMIT" and result.announcements == ()
        assert not result.analysis_complete


@pytest.mark.parametrize(
    "pages,expected,lots",
    [
        ([b"Le DCE comprend :", b"| CCAP | CCTP |"], ("CCAP", "CCTP"), ()),
        (
            [b"Le DCE comprend :", b"Composition du dossier - suite\n- CCAP", b"- CCTP"],
            ("CCAP", "CCTP"),
            (),
        ),
        ([b"Le DCE comprend pour le lot 2 :", b"- CCAP"], ("CCAP",), (2,)),
        ([b"Le DCE comprend pour le lot 2 :", b"- CCAP pour le lot 3"], ("CCAP",), ()),
        ([b"Le DCE comprend :", b"| CCAP | non fourni |\n- CCTP"], (), ()),
        ([b"Le DCE comprend :", b"Composition du dossier - suite pour le lot 3\n- CCAP"], (), ()),
    ],
)
def test_residual_layouts_through_native_pdf_keep_scoped_hashed_regions(
    session_factory, tmp_path, pages, expected, lots
):
    tenant, document, version = _source(session_factory, tmp_path, pages)
    with session_factory() as session:
        reader = SqlAlchemyCaseDceReadingReader(session)
        result = reader._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert tuple(x.document_family for x in result.announcements) == expected
        for item in result.announcements:
            assert item.source_document_id == document and item.lot_numbers == lots
            assert item.presence_status == item.applicability == item.criticality == "UNKNOWN"
            assert item.anchor_chain and item.context_fragment_id is not None
            for anchor in item.anchor_chain:
                fragment = session.get(DceDocumentExtractionFragmentRecord, anchor.fragment_id)
                run = session.get(DceDocumentExtractionRecord, fragment.extraction_id)
                parent = session.get(DceDocumentRecord, document)
                assert fragment.tenant_id == run.tenant_id == tenant
                assert run.dce_document_id == document and run.dce_version_id == version
                assert run.input_sha256 == parent.sha256
                assert sha256(fragment.text.encode()).hexdigest() == fragment.text_sha256
                assert (
                    0
                    <= anchor.start_byte_offset
                    < anchor.end_byte_offset
                    <= len(fragment.text.encode())
                )
                assert anchor.locator_label == f"RC · page {fragment.locator_json['page']}"
            source = session.get(DceDocumentExtractionFragmentRecord, item.source_fragment_id)
            raw = source.text.encode()[item.start_byte_offset : item.end_byte_offset].decode()
            if pages[1].startswith(b"|"):
                assert raw == item.document_family
            if b"lot 3" in pages[1]:
                assert (
                    item.claim == "AMBIGUOUS"
                    and result.announcement_scan_state == "REVIEW_REQUIRED"
                )
        assert not result.analysis_complete
        assert result == reader._read_coverage(
            tenant_id=tenant, dce_version_id=version, case_scope_kind="CUSTOM"
        )
        assert (
            reader._read_coverage(
                tenant_id=uuid4(), dce_version_id=version, case_scope_kind="CUSTOM"
            ).announcements
            == ()
        )
        assert "Le DCE comprend" not in str(asdict(result))
