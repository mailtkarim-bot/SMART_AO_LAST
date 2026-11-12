"""Source cell identity must survive extraction; ambiguous structures stay unadmitted."""

from hashlib import sha256
from io import BytesIO
from uuid import uuid4

import pytest
from app.modules.dce.application import extraction as module
from app.modules.dce.application.analysis import (
    RcAnalysisSourceFragment,
    _project_rc_requirements,
    is_valid_rc_observation,
)
from app.modules.dce.application.source_anchor_projection import resolve_dce_source_locator
from docx import Document
from docx.oxml import OxmlElement

MEDIA = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def project(document):
    buffer = BytesIO()
    document.save(buffer)
    return module._project_document(media_type=MEDIA, source_bytes=buffer.getvalue())


def test_rectangular_table_preserves_document_order_exact_cell_paragraphs_and_empty_positions():
    d = Document()
    d.add_paragraph("Avant.")
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 1).text = "Fournir les plans."
    t.cell(1, 0).text = "Ne pas intervenir sans consignation."
    t.cell(1, 0).add_paragraph("Pour le lot 2.")
    t.cell(1, 1).text = "Après réception."
    d.add_paragraph("Fin.")
    r = project(d)
    assert r.status == "COMPLETED"
    assert [f.text for f in r.fragments] == [
        "Avant.",
        "Fournir les plans.",
        "Ne pas intervenir sans consignation.",
        "Pour le lot 2.",
        "Après réception.",
        "Fin.",
    ]
    assert r.fragments[1].locator_json == dict(
        kind="docx_table_cell", table=1, row=1, column=2, paragraph=1, part=1
    )
    assert r.fragments[3].locator_json == dict(
        kind="docx_table_cell", table=1, row=2, column=1, paragraph=2, part=1
    )
    assert r.fragments[-1].locator_json == dict(kind="docx_paragraph", paragraph=2, part=1)
    assert all(resolve_dce_source_locator(f.locator_json) is not None for f in r.fragments)


@pytest.mark.parametrize(
    "shape", ["horizontal_merge", "vertical_merge", "nested", "omitted", "revision", "drawing"]
)
def test_ambiguous_table_cannot_become_completed(shape):
    d = Document()
    d.add_paragraph("Corps conservé.")
    t = d.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "Installer une vanne."
    if shape == "horizontal_merge":
        t.cell(0, 0).merge(t.cell(0, 1))
    elif shape == "vertical_merge":
        t.cell(0, 0).merge(t.cell(1, 0))
    elif shape == "nested":
        t.cell(0, 0).add_table(rows=1, cols=1).cell(0, 0).text = "Ne pas installer."
    elif shape == "omitted":
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:gridBefore"))
    elif shape == "revision":
        parent = t._tbl.getparent()
        parent.remove(t._tbl)
        wrapper = OxmlElement("w:ins")
        wrapper.append(t._tbl)
        parent.insert(1, wrapper)
    else:
        t.cell(0, 0).paragraphs[0].add_run()._r.append(OxmlElement("w:drawing"))
    r = project(d)
    assert r.status == "REVIEW_REQUIRED" and r.failure_code == "DOCX_TABLE_CONTENT_REVIEW_REQUIRED"
    assert any(f.text == "Corps conservé." for f in r.fragments)


def test_cell_limit_is_enforced(monkeypatch):
    monkeypatch.setattr(module, "MAX_DOCX_TABLE_CELLS", 1, raising=False)
    d = Document()
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text = "Installer une vanne."
    assert project(d).status == "REJECTED_LIMIT"


@pytest.mark.parametrize(
    "field,value",
    [("table", 0), ("row", True), ("column", -1), ("paragraph", "1"), ("part", False)],
)
def test_invalid_cell_coordinate_stays_unknown(field, value):
    loc = dict(kind="docx_table_cell", table=1, row=2, column=3, paragraph=1, part=1)
    assert resolve_dce_source_locator(loc) is not None
    assert resolve_dce_source_locator(dict(loc, **{field: value})) is None
    assert resolve_dce_source_locator(dict(loc, header="Lot 3")) is None


def test_cell_signal_cannot_inherit_required_certainty_from_its_text_alone():
    text = "Les fiches techniques doivent être fournies pour le lot 1."
    source = RcAnalysisSourceFragment(
        uuid4(),
        uuid4(),
        uuid4(),
        1,
        text,
        sha256(text.encode()).hexdigest(),
        "CCTP",
        source_locator_kind="docx_table_cell",
    )
    obs = _project_rc_requirements(sources=(source,)).observations
    assert len(obs) == 1 and obs[0].directive == "UNSPECIFIED"
    args = dict(
        requirement_kind=obs[0].requirement_kind,
        rule_id=obs[0].rule_id,
        excerpt=text,
        rule_version="9",
        source_locator_kind="docx_table_cell",
    )
    assert is_valid_rc_observation(**args, directive="UNSPECIFIED")
    assert not is_valid_rc_observation(**args, directive="REQUIRED_SIGNAL")


def test_consignation_negation_becomes_source_only_hse_signal():
    text = "Ne pas intervenir sans consignation pour le lot 2."
    source = RcAnalysisSourceFragment(
        uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), "PGC"
    )
    obs = _project_rc_requirements(sources=(source,)).observations
    assert len(obs) == 1 and obs[0].requirement_kind == "DCE_HSE_CONSTRAINT"
    assert obs[0].excerpt == text and obs[0].directive == "UNSPECIFIED"


def test_financial_consignation_is_not_an_hse_prescription():
    text = "La consignation d'un acompte est prévue."
    source = RcAnalysisSourceFragment(
        uuid4(), uuid4(), uuid4(), 1, text, sha256(text.encode()).hexdigest(), "OTHER"
    )
    assert not any(
        o.requirement_kind == "DCE_HSE_CONSTRAINT"
        for o in _project_rc_requirements(sources=(source,)).observations
    )


def test_header_content_outside_body_remains_unread():
    d = Document()
    d.add_paragraph("Installer une vanne.")
    d.sections[0].header.paragraphs[0].text = "Ne pas intervenir sans consignation."
    assert project(d).status == "REVIEW_REQUIRED"


def test_cell_proof_cannot_reuse_a_pre_cell_analysis_recipe():
    assert not is_valid_rc_observation(
        requirement_kind="DCE_TECHNICAL_PRESCRIPTION",
        rule_id="TECHNICAL_DELIVERABLE_V8",
        excerpt="Les fiches techniques doivent être fournies.",
        directive="REQUIRED_SIGNAL",
        rule_version="8",
        source_locator_kind="docx_table_cell",
    )


@pytest.mark.parametrize(
    "wrapper,inside_paragraph",
    [
        ("customXml", False),
        ("customXml", True),
        ("smartTag", True),
        ("AlternateContent", False),
        ("sym", True),
        ("oMath", True),
    ],
)
def test_unvisited_wrapped_or_mixed_text_cannot_claim_complete_extraction(
    wrapper, inside_paragraph
):
    d = Document()
    d.add_paragraph("Corps conservé.")
    t = d.add_table(rows=1, cols=1)
    cell = t.cell(0, 0)
    cell.text = "Installer une vanne."
    if wrapper == "AlternateContent":
        from lxml import etree

        node = etree.Element(
            "{http://schemas.openxmlformats.org/markup-compatibility/2006}AlternateContent"
        )
    elif wrapper == "oMath":
        from lxml import etree

        node = etree.Element("{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath")
    else:
        node = OxmlElement("w:" + wrapper)
    if wrapper not in {"sym", "oMath"}:
        run = OxmlElement("w:r")
        text = OxmlElement("w:t")
        text.text = "Ne pas installer cette vanne."
        run.append(text)
        if inside_paragraph:
            node.append(run)
        else:
            p = OxmlElement("w:p")
            p.append(run)
            node.append(p)
    if inside_paragraph:
        cell.paragraphs[0]._p.append(node)
    else:
        cell._tc.append(node)
    result = project(d)
    assert result.status == "REVIEW_REQUIRED"
