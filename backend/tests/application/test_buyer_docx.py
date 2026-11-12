"""A buyer frame is filled at exact regions, not rebuilt from its visible text."""

import io
import zipfile
from hashlib import sha256

import pytest
from app.modules.preparation.infrastructure.buyer_docx import (
    DocxFill,
    fill_template,
    inspect_template,
)
from docx import Document


def frame():
    document = Document()
    document.add_heading("Mémoire technique — cadre synthétique", 0)
    document.add_paragraph("Question acheteur : conserver ce texte et ce style.", style="Heading 2")
    paragraph = document.add_paragraph()
    paragraph.add_run("[[REPONSE:").bold = True
    paragraph.add_run("METHODE]]").bold = True
    table = document.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Rubrique acheteur"
    table.cell(0, 1).text = "Réponse entreprise"
    table.cell(1, 0).text = "Précautions par lot"
    table.cell(1, 1).text = "[[REPONSE:RISQUES]]"
    document.add_paragraph("[[REPONSE:INCONNU]]")
    result = io.BytesIO()
    document.save(result)
    return result.getvalue()


def test_fill_preserves_parts_static_content_and_explicit_unknown():
    original = frame()
    regions = inspect_template(original)
    assert {r.locator for r in regions} == {"p:3", "t:1/r:2/c:2/p:1", "p:4"}
    chosen = {r.locator: r for r in regions}
    text = "Ne pas intervenir sans validation.\nSi le lot 1 est retenu, vérifier la pièce."
    result = fill_template(
        original,
        (
            DocxFill("p:3", chosen["p:3"].xml_sha256, text),
            DocxFill(
                "t:1/r:2/c:2/p:1",
                chosen["t:1/r:2/c:2/p:1"].xml_sha256,
                "Aucun délai certain déduit.",
            ),
        ),
    )
    with (
        zipfile.ZipFile(io.BytesIO(original)) as before,
        zipfile.ZipFile(io.BytesIO(result.content)) as after,
    ):
        assert before.namelist() == after.namelist()
        assert all(
            before.read(p) == after.read(p) for p in before.namelist() if p != "word/document.xml"
        )
    document = Document(io.BytesIO(result.content))
    assert document.paragraphs[1].text == "Question acheteur : conserver ce texte et ce style."
    assert document.paragraphs[2].text == text
    assert document.paragraphs[2].runs[0].bold
    assert document.paragraphs[3].text.startswith("UNKNOWN")
    assert document.tables[0].cell(1, 0).text == "Précautions par lot"
    assert document.tables[0].cell(1, 1).text == "Aucun délai certain déduit."
    assert next(r for r in result.regions if r.locator == "p:4").state == "UNKNOWN"
    assert (
        result.content
        == fill_template(
            original,
            (
                DocxFill("p:3", chosen["p:3"].xml_sha256, text),
                DocxFill(
                    "t:1/r:2/c:2/p:1",
                    chosen["t:1/r:2/c:2/p:1"].xml_sha256,
                    "Aucun délai certain déduit.",
                ),
            ),
        ).content
    )


def test_changed_region_and_duplicate_fill_are_refused():
    original = frame()
    region = inspect_template(original)[0]
    with pytest.raises(ValueError, match="REGION_CHANGED"):
        fill_template(original, (DocxFill(region.locator, "0" * 64, "texte"),))
    fill = DocxFill(region.locator, region.xml_sha256, "texte")
    with pytest.raises(ValueError, match="DUPLICATE"):
        fill_template(original, (fill, fill))


@pytest.mark.parametrize(
    "fault", ["external", "traversal", "merge", "tracked", "mixed_style", "header_field"]
)
def test_ambiguous_or_active_frame_is_refused(fault):
    from app.modules.preparation.infrastructure.buyer_docx import NS, W
    from lxml import etree

    original = frame()
    with zipfile.ZipFile(io.BytesIO(original)) as archive:
        parts = {n: archive.read(n) for n in archive.namelist()}
    if fault == "external":
        root = etree.fromstring(parts["word/_rels/document.xml.rels"])
        etree.SubElement(
            root,
            "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship",
            Id="unsafe",
            Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
            Target="https://example.invalid/",
            TargetMode="External",
        )
        parts["word/_rels/document.xml.rels"] = etree.tostring(root)
    elif fault == "header_field":
        parts["word/header1.xml"] = (
            f'<w:hdr xmlns:w="{W}"><w:p><w:fldSimple w:instr="DDEAUTO"/></w:p></w:hdr>'
        ).encode()
    elif fault == "traversal":
        parts["word/../escaped.xml"] = b"<x/>"
    else:
        root = etree.fromstring(parts["word/document.xml"])
        paragraph = root.find("w:body", NS).findall("w:p", NS)[2]
        if fault == "merge":
            table = root.find(".//w:tbl", NS)
            cell = table.findall("w:tr", NS)[1].findall("w:tc", NS)[1]
            etree.SubElement(cell.find("w:tcPr", NS), f"{{{W}}}gridSpan").set(f"{{{W}}}val", "2")
        elif fault == "tracked":
            etree.SubElement(paragraph, f"{{{W}}}ins")
        else:
            etree.SubElement(paragraph.findall("w:r", NS)[1].find("w:rPr", NS), f"{{{W}}}i")
        parts["word/document.xml"] = etree.tostring(root)
    result = io.BytesIO()
    with zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in parts.items():
            archive.writestr(name, content)
    with pytest.raises(ValueError, match="REVIEW_REQUIRED|UNSAFE_PART"):
        inspect_template(result.getvalue())


def test_artifact_models_have_explicit_legacy_format_and_docx_provenance():
    from app.modules.preparation.infrastructure.models import (
        GeneratedTechnicalDocumentRecord,
        TechnicalResponseDraftRecord,
    )

    assert "content_format" in GeneratedTechnicalDocumentRecord.__table__.c
    assert "content_format" in TechnicalResponseDraftRecord.__table__.c
    assert "content_provenance_json" in TechnicalResponseDraftRecord.__table__.c


def test_source_contributions_keep_exact_byte_anchors_and_missing_status():
    from uuid import uuid4

    from app.modules.preparation.application.document_content import (
        ResponsePlanDraftItem,
        build_response_plan_draft,
    )
    from app.modules.preparation.infrastructure.response_artifact import source_contributions
    from app.modules.preparation.public.contracts import ResponseContribution

    requirement = uuid4()
    content = "Ne pas supprimer la négation.\nSi le lot 1 est retenu, confirmer l’accès."
    text = build_response_plan_draft(
        plan_version=1,
        draft_version=1,
        items=(ResponsePlanDraftItem(requirement, "METHOD", "Méthode", "Titre", 1, 1, "{}"),),
        contributions=(
            ResponseContribution(
                requirement_id=requirement,
                section_code="METHOD",
                content=content,
                missing="Échéance UNKNOWN",
            ),
        ),
    )
    raw = text.encode()
    parts = source_contributions(raw)
    source = parts[(str(requirement), "METHOD")]
    assert source.text == content
    assert sha256(raw[source.start_byte : source.end_byte]).hexdigest() == source.raw_sha256
    assert raw[source.start_byte : source.end_byte].decode().startswith("> Ne pas")


def test_text_correction_cannot_reinterpret_a_binary_docx(monkeypatch, tmp_path):
    from datetime import UTC, datetime
    from types import SimpleNamespace
    from uuid import uuid4

    from app.modules.preparation.application.review import PreparationReviewHandler
    from app.modules.preparation.application.review_commands import AddPreparationCorrectionCommand
    from app.modules.preparation.infrastructure.document_storage import (
        LocalGeneratedDocumentStorage,
    )
    from app.platform.events.dispatcher import CommandContext, CommandExecutionError

    draft_id = uuid4()
    draft = SimpleNamespace(content_format="DOCX")
    package = SimpleNamespace(id=uuid4())
    review = SimpleNamespace(
        package_id=package.id,
        target_document_id=None,
        target_draft_id=draft_id,
        target_draft_version=1,
        target_content_sha256="a" * 64,
        state="RETURNED_WITH_CORRECTIONS",
    )
    handler = PreparationReviewHandler(storage=LocalGeneratedDocumentStorage(root=tmp_path))
    monkeypatch.setattr(handler, "_package", lambda **_: package)
    monkeypatch.setattr(handler, "_latest_review", lambda **_: review)
    monkeypatch.setattr(handler, "_exact_response_draft", lambda **_: draft)
    command = AddPreparationCorrectionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        correction_code="WORDING_UNCLEAR",
        instruction="Revoir le cadre synthétique.",
        package_id=package.id,
        review_id=uuid4(),
        target_document_id=None,
        target_draft_id=draft_id,
        target_draft_version=1,
        target_content_sha256="a" * 64,
        corrected_content="A text box cannot stand in for the buyer DOCX.",
    )
    with pytest.raises(CommandExecutionError, match="BUYER_DOCX_REFILL_REQUIRED"):
        handler._correction(
            session=None,
            command=command,
            context=CommandContext(
                tenant_id=uuid4(),
                actor_id=uuid4(),
                actor_kind="PATRON_ADMIN",
                received_at=datetime.now(UTC),
            ),
        )


def test_private_wording_in_static_header_is_not_omitted_from_safety_check():
    from types import SimpleNamespace

    from app.modules.preparation.infrastructure.response_artifact import read_response_artifact

    original = Document(io.BytesIO(frame()))
    original.sections[0].header.paragraphs[0].text = "Marge financière interne à ne pas publier"
    output = io.BytesIO()
    original.save(output)
    raw = output.getvalue()
    storage = SimpleNamespace(read=lambda **_: raw)
    draft = SimpleNamespace(
        storage_key="synthetic.docx", content_format="DOCX", content_sha256=sha256(raw).hexdigest()
    )
    with pytest.raises(ValueError, match="FINANCIAL_DATA_FORBIDDEN"):
        read_response_artifact(storage, draft)
