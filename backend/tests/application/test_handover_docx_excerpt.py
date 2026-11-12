"""DOCX source text is located in bounded body XML, never raw ZIP byte offsets."""

import io
import zipfile
from hashlib import sha256

import pytest
from docx import Document
from docx.oxml import OxmlElement


def proof(content, excerpt):
    from app.modules.patron_action.infrastructure.operational_handover import docx_excerpt_proof

    return docx_excerpt_proof(content, excerpt.encode())


def raw(document):
    output = io.BytesIO()
    document.save(output)
    return output.getvalue()


def test_docx_split_runs_have_exact_text_offsets_and_part_hash_not_zip_offsets():
    document = Document()
    p = document.add_paragraph()
    p.add_run("Préfixe. Le KBIS ")
    p.add_run("reste UNKNOWN.").bold = True
    content = raw(document)
    result = proof(content, "Le KBIS reste UNKNOWN.")
    assert result["state"] == "EXACT_DOCX_TEXT_MATCH"
    assert result["start_byte_offset"] is result["end_byte_offset"] is None
    assert result["locator"].startswith("word/document.xml:")
    assert result["text_start_byte_offset"] == len("Préfixe. ".encode())
    assert result["text_end_byte_offset"] == len("Préfixe. Le KBIS reste UNKNOWN.".encode())
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        assert result["part_sha256"] == sha256(z.read("word/document.xml")).hexdigest()
    assert result["text_sha256"] == sha256("Préfixe. Le KBIS reste UNKNOWN.".encode()).hexdigest()


def test_simple_table_cell_is_located_in_exported_document_body():
    document = Document()
    document.add_table(rows=1, cols=1).cell(0, 0).text = "Attestation à obtenir."
    result = proof(raw(document), "Attestation à obtenir.")
    assert result["state"] == "EXACT_DOCX_TEXT_MATCH" and "w:tbl" in result["locator"]


@pytest.mark.parametrize("same_paragraph", [False, True])
def test_duplicate_text_is_ambiguous(same_paragraph):
    document = Document()
    document.add_paragraph(
        "Pièce à relire. Pièce à relire." if same_paragraph else "Pièce à relire."
    )
    if not same_paragraph:
        document.add_paragraph("Pièce à relire.")
    assert proof(raw(document), "Pièce à relire.")["state"] == "AMBIGUOUS"


def test_header_text_cannot_prove_an_engagement_in_the_document_body():
    document = Document()
    document.sections[0].header.paragraphs[0].text = "Texte source non publié."
    document.add_paragraph("Autre texte.")
    assert proof(raw(document), "Texte source non publié.")["state"] == "UNKNOWN"


def test_hidden_run_is_not_promoted_into_a_known_body_source():
    document = Document()
    run = document.add_paragraph().add_run("Texte caché.")
    run._r.get_or_add_rPr().append(OxmlElement("w:vanish"))
    assert proof(raw(document), "Texte caché.")["state"] == "UNKNOWN"


def test_excerpt_is_never_joined_across_paragraphs():
    document = Document()
    document.add_paragraph("Première partie.")
    document.add_paragraph("Deuxième partie.")
    assert proof(raw(document), "Première partie.Deuxième partie.")["state"] == "UNKNOWN"


def test_invalid_docx_is_unknown_and_does_not_escape_parser_exception():
    assert proof(b"not a DOCX", "Phrase")["state"] == "UNKNOWN"


def test_complex_content_control_is_not_promoted_to_a_simple_body_paragraph():
    document = Document()
    p = document.add_paragraph("Texte sous contrôle.")._p
    body = p.getparent()
    index = body.index(p)
    body.remove(p)
    wrapper = OxmlElement("w:sdt")
    container = OxmlElement("w:sdtContent")
    container.append(p)
    wrapper.append(container)
    body.insert(index, wrapper)
    assert proof(raw(document), "Texte sous contrôle.")["state"] == "UNKNOWN"


@pytest.mark.parametrize("scope", ["inherited_style", "doc_defaults"])
def test_hidden_style_or_document_defaults_are_unknown(scope):
    from docx.enum.style import WD_STYLE_TYPE

    document = Document()
    paragraph = document.add_paragraph("Texte masqué par style.")
    if scope == "inherited_style":
        style = document.styles.add_style("SyntheticHidden", WD_STYLE_TYPE.CHARACTER)
        style.font.hidden = True
        paragraph.runs[0].style = style
    else:
        defaults = document.styles.element.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}docDefaults"
        )
        properties = OxmlElement("w:rPr")
        properties.append(OxmlElement("w:vanish"))
        defaults.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPrDefault"
        ).append(properties)
    assert proof(raw(document), "Texte masqué par style.")["state"] == "UNKNOWN"
