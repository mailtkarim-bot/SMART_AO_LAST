"""Full development dossier transformed to actual binaries; no gold observations seeded."""

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest
from docx import Document
from openpyxl import Workbook
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from tests.db.test_l04_execution_pipeline import (
    EXPECTED_GAPS,
)
from tests.db.test_l04_execution_pipeline import (
    test_every_execution_point_can_be_treated_then_exact_dossier_reviewed as qualify_review,
)
from tests.db.test_l04_multiformat_rectification import (
    DOCX,
    XLSX,
)
from tests.db.test_l04_multiformat_rectification import (
    test_rectificatif_invalidates_review_and_restarts_treatments as qualify_rectification,
)
from tests.db.test_l04_multilot_pipeline import EXPECTED_PROJECTIONS, complete_dossier, read

DEVELOPMENT = Path(__file__).parents[1] / "fixtures/dce_l04_multilot"


def full_originals(root, revision):
    root.mkdir()
    manifest = deepcopy(json.loads((DEVELOPMENT / "manifest.json").read_text()))
    manifest.update(purpose="MULTIFORMAT_DEVELOPMENT_ONLY", expected_point_count=34)
    for doc in manifest["documents"]:
        old = doc["file"]
        lines = (DEVELOPMENT / old).read_text().splitlines()
        for fact in doc["facts"]:
            fact["expected_type"] = (
                EXPECTED_PROJECTIONS[fact["expected_kind"]][0]
                if fact["expected_kind"]
                else EXPECTED_GAPS[(old, fact["line"])]
            )
        if old == "cctp-lot-1.txt":
            quote = "Le titulaire doit fournir les plans pour le lot 1."
            lines.append(quote)
            doc["facts"].append(
                dict(line=len(lines), quote=quote, expected_type="TECHNICAL_PRESCRIPTION")
            )
        if old == "planning.txt":
            quote = (
                f"Le délai d'exécution est de {6 if revision == 1 else 9} semaines pour le lot 2."
            )
            lines.append(quote)
            doc["facts"].append(
                dict(line=len(lines), quote=quote, expected_type="SCHEDULE_CONSTRAINT")
            )
        if old == "rc.txt":
            doc["file"], doc["media_type"] = "rc.pdf", "application/pdf"
            writer = PdfWriter()
            page = writer.add_blank_page(width=612, height=792)
            font = DictionaryObject(
                {
                    NameObject("/Type"): NameObject("/Font"),
                    NameObject("/Subtype"): NameObject("/Type1"),
                    NameObject("/BaseFont"): NameObject("/Helvetica"),
                    NameObject("/Encoding"): NameObject("/WinAnsiEncoding"),
                }
            )
            page[NameObject("/Resources")] = DictionaryObject(
                {
                    NameObject("/Font"): DictionaryObject(
                        {NameObject("/F1"): writer._add_object(font)}
                    )
                }
            )
            instructions = [b"BT /F1 10 Tf 42 750 Td"]
            for n, line in enumerate(lines):
                raw = (
                    line.encode("cp1252")
                    .replace(b"\\", b"\\\\")
                    .replace(b"(", b"\\(")
                    .replace(b")", b"\\)")
                )
                if n:
                    instructions.append(b"0 -18 Td")
                instructions.append(b"(" + raw + b") Tj")
            instructions.append(b"ET")
            stream = DecodedStreamObject()
            stream.set_data(b"\n".join(instructions))
            page[NameObject("/Contents")] = writer._add_object(stream)
            writer.write(root / doc["file"])
        elif old.startswith("cctp") or old == "ccap.txt":
            doc["file"], doc["media_type"] = Path(old).with_suffix(".docx").name, DOCX
            document = Document()
            for line in lines:
                document.add_paragraph(line)
            document.save(root / doc["file"])
        elif old == "planning.txt":
            doc["file"], doc["media_type"] = "planning.xlsx", XLSX
            book = Workbook()
            book.active.title = "Planning"
            for n, line in enumerate(lines, 1):
                book.active[f"B{n}"] = line
            book.save(root / doc["file"])
        else:
            doc["media_type"] = "text/plain"
            (root / doc["file"]).write_text("\n".join(lines) + "\n")
        doc["sha256"] = sha256((root / doc["file"]).read_bytes()).hexdigest()
    document = Document()
    document.add_paragraph("Annexe de sécurité à relire.")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).merge(table.cell(0, 1)).text = "Ne pas intervenir sans consignation."
    document.save(root / "annexe-non-lue.docx")
    manifest["documents"].append(
        dict(
            file="annexe-non-lue.docx",
            media_type=DOCX,
            family="PGC",
            facts=[],
            sha256=sha256((root / "annexe-non-lue.docx").read_bytes()).hexdigest(),
        )
    )
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False))
    return manifest


@pytest.fixture
def full_dossier(session_factory, tmp_path):
    corpus = tmp_path / "v1"
    full_originals(corpus, 1)
    seed = complete_dossier.__wrapped__(
        session_factory, tmp_path / "storage", SimpleNamespace(param=str(corpus))
    )
    return seed, tmp_path


def test_all_34_development_points_reach_review_with_exact_multiformat_provenance(
    session_factory, full_dossier
):
    seed, _ = full_dossier
    summary = read(session_factory, seed)
    points = [p for a in summary["axes"] for p in a["items"]]
    assert len(points) == 34
    assert summary["coverage"]["unread_documents"] == 1
    assert not summary["analysis_complete"]
    for doc in seed[4]["documents"]:
        for fact in doc["facts"]:
            matching = [p for p in points if p["source_excerpt"] == fact["quote"]]
            assert len(matching) == 1, (doc["file"], fact["quote"])
            p = matching[0]
            anchor = p["source_anchor"]
            locator = anchor["locator"]
            assert p["native_type"] == fact["expected_type"]
            assert anchor["dce_document_id"] == seed[3][doc["file"]]
            assert anchor["dce_version_id"] == seed[2]
            assert anchor["source_sha256"] == doc["sha256"]
            assert p["source_state"] == "CURRENT_SOURCE"
            assert p["applicability"] == "UNKNOWN"
            suffix = Path(doc["file"]).suffix
            if suffix == ".pdf":
                assert locator["kind"] == "pdf_page" and locator["coordinates"]["page"] == 1
            elif suffix == ".docx":
                assert locator["kind"] == "docx_paragraph"
                assert locator["coordinates"]["paragraph"] == fact["line"]
            elif suffix == ".xlsx":
                assert locator["coordinates"] == dict(
                    sheet="Planning", cell=f"B{fact['line']}", part=1
                )
            else:
                assert locator["coordinates"]["line"] == fact["line"]
    for quote, lot, axis in [
        ("Le titulaire doit fournir les plans pour le lot 1.", 1, "TECHNICAL"),
        ("Le délai d'exécution est de 6 semaines pour le lot 2.", 2, "CAPACITY"),
    ]:
        p = next(p for p in points if p["source_excerpt"] == quote)
        assert p["lot_numbers"] == [lot] and p["lot_state"] == "CANDIDATE"
        assert p in next(a for a in summary["axes"] if a["code"] == axis)["items"]
    qualify_review(session_factory, seed)


def test_full_rectificatif_requires_fresh_treatment_and_keeps_history(
    session_factory, full_dossier
):
    qualify_rectification(
        session_factory, full_dossier, corpus_builder=full_originals, expected_points=34
    )
    seed, _ = full_dossier
    summary = read(session_factory, seed)
    quotes = [p["source_excerpt"] for a in summary["axes"] for p in a["items"]]
    assert "Le délai d'exécution est de 9 semaines pour le lot 2." in quotes
    assert "Le délai d'exécution est de 6 semaines pour le lot 2." not in quotes
