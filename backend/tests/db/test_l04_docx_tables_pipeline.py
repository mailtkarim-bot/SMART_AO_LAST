"""Complete mixed dossier with cell-level prescriptions, still no automatic context admission."""

import json
from hashlib import sha256
from types import SimpleNamespace

import pytest
from app.modules.knowledge.infrastructure.dce_source import SqlAlchemyDceRetrievalSource
from docx import Document
from tests.db.test_l04_execution_pipeline import (
    test_every_execution_point_can_be_treated_then_exact_dossier_reviewed as qualify_review,
)
from tests.db.test_l04_fullformats_duration import full_originals
from tests.db.test_l04_multiformat_rectification import DOCX
from tests.db.test_l04_multiformat_rectification import (
    test_rectificatif_invalidates_review_and_restarts_treatments as qualify_rectification,
)
from tests.db.test_l04_multilot_pipeline import complete_dossier, read


def table_originals(root, revision):
    manifest = full_originals(root, revision)
    target = next(d for d in manifest["documents"] if d["file"] == "cctp-lot-1.docx")
    document = Document(root / target["file"])
    t = document.add_table(rows=3, cols=2)
    t.cell(0, 0).text = "Portée"
    t.cell(0, 1).text = "Prescription"
    t.cell(1, 0).text = "Lot 2"
    deliverable = "notes de calcul" if revision == 1 else "plans"
    quote = f"Le titulaire doit fournir les {deliverable}."
    t.cell(1, 1).text = quote
    t.cell(2, 0).text = "Si le support est accepté"
    second = "Les fiches techniques doivent être fournies pour le lot 1."
    t.cell(2, 1).text = second
    document.save(root / target["file"])
    target["sha256"] = sha256((root / target["file"]).read_bytes()).hexdigest()
    target["facts"].extend(
        [
            dict(
                quote=quote,
                expected_type="TECHNICAL_PRESCRIPTION",
                table=1,
                row=2,
                column=2,
                paragraph=1,
            ),
            dict(
                quote=second,
                expected_type="TECHNICAL_PRESCRIPTION",
                table=1,
                row=3,
                column=2,
                paragraph=1,
            ),
        ]
    )
    d = Document()
    t = d.add_table(rows=1, cols=1)
    hse = "Ne pas intervenir sans consignation pour le lot 2."
    t.cell(0, 0).text = hse
    d.save(root / "prescriptions-hse.docx")
    manifest["documents"].append(
        dict(
            file="prescriptions-hse.docx",
            family="PGC",
            media_type=DOCX,
            sha256=sha256((root / "prescriptions-hse.docx").read_bytes()).hexdigest(),
            facts=[
                dict(
                    quote=hse, expected_type="HSE_CONSTRAINT", table=1, row=1, column=1, paragraph=1
                )
            ],
        )
    )
    manifest["expected_point_count"] = 37
    (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False))
    return manifest


@pytest.fixture
def table_dossier(session_factory, tmp_path):
    root = tmp_path / "v1"
    table_originals(root, 1)
    seed = complete_dossier.__wrapped__(
        session_factory, tmp_path / "storage", SimpleNamespace(param=str(root))
    )
    return seed, tmp_path


def test_cell_prescriptions_have_exact_anchors_unknown_context_and_full_human_review(
    session_factory, table_dossier
):
    seed, _ = table_dossier
    summary = read(session_factory, seed)
    points = [p for a in summary["axes"] for p in a["items"]]
    assert len(points) == 37 and summary["coverage"]["unread_documents"] == 1
    cells = []
    for doc in seed[4]["documents"]:
        for fact in doc["facts"]:
            matching = [p for p in points if p["source_excerpt"] == fact["quote"]]
            assert len(matching) == 1, (doc["file"], fact["quote"])
            p = matching[0]
            anchor = p["source_anchor"]
            assert p["source_state"] == "CURRENT_SOURCE"
            assert anchor["dce_document_id"] == seed[3][doc["file"]]
            assert anchor["dce_version_id"] == seed[2] and anchor["source_sha256"] == doc["sha256"]
            assert p["applicability"] == "UNKNOWN"
            if "table" not in fact:
                continue
            assert anchor["locator"]["kind"] == "docx_table_cell"
            assert anchor["locator"]["coordinates"] == dict(
                table=fact["table"],
                row=fact["row"],
                column=fact["column"],
                paragraph=fact["paragraph"],
                part=1,
            )
            assert p["native_type"] == fact["expected_type"]
            cells.append(p)
    assert len(cells) == 3
    first = next(p for p in cells if "notes de calcul" in p["source_excerpt"])
    assert first["lot_numbers"] == [] and first["lot_state"] == "UNKNOWN"
    context = first.get("table_context")
    assert context is not None and context["state"] == "EXACT_SOURCE"
    assert context["applicability"] == "UNKNOWN"
    assert [c["text"] for c in context["cells"]] == [
        "Portée",
        "Prescription",
        "Lot 2",
        "Le titulaire doit fournir les notes de calcul.",
        "Si le support est accepté",
        "Les fiches techniques doivent être fournies pour le lot 1.",
    ]
    for cell in context["cells"]:
        a = cell["source_anchor"]
        assert a["dce_document_id"] == first["source_anchor"]["dce_document_id"]
        assert a["extraction_id"] == first["source_anchor"]["extraction_id"]
        assert a["fragment_sha256"] == sha256(cell["text"].encode()).hexdigest()
    hse = next(p for p in cells if p["native_type"] == "HSE_CONSTRAINT")
    assert (
        hse["table_context"]["cells"][0]["text"]
        == "Ne pas intervenir sans consignation pour le lot 2."
    )
    chunks = SqlAlchemyDceRetrievalSource(session_factory=session_factory).read_chunks(
        tenant_id=seed[0], case_id=seed[1], dce_version_id=seed[2]
    )
    assert chunks and not any(c.locator.get("kind") == "docx_table_cell" for c in chunks)
    qualify_review(session_factory, seed)
    assert not read(session_factory, seed)["analysis_complete"]


def test_cell_rectificatif_requires_new_acts_and_keeps_prior_snapshots(
    session_factory, table_dossier
):
    qualify_rectification(
        session_factory, table_dossier, corpus_builder=table_originals, expected_points=37
    )
    seed, _ = table_dossier
    final = read(session_factory, seed)
    quotes = [p["source_excerpt"] for a in final["axes"] for p in a["items"]]
    assert "Le titulaire doit fournir les notes de calcul." not in quotes
    assert "Le titulaire doit fournir les plans." in quotes


def context_originals(root, revision):
    manifest = table_originals(root, 1)
    if revision == 2:
        target = next(d for d in manifest["documents"] if d["file"] == "cctp-lot-1.docx")
        document = Document(root / target["file"])
        document.tables[0].cell(1, 0).text = "Lot 3 — ne pas appliquer sans accord"
        document.tables[0].cell(2, 0).text = "Si le support est refusé"
        document.save(root / target["file"])
        target["sha256"] = sha256((root / target["file"]).read_bytes()).hexdigest()
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False))
    return manifest


def test_context_only_rectificatif_keeps_text_but_requires_fresh_treatment_and_review(
    session_factory, table_dossier
):
    qualify_rectification(
        session_factory, table_dossier, corpus_builder=context_originals, expected_points=37
    )
    summary = read(session_factory, table_dossier[0])
    item = next(
        p
        for a in summary["axes"]
        for p in a["items"]
        if "notes de calcul" in (p["source_excerpt"] or "")
    )
    assert item["human_assessment"]["state"] == "CURRENT"
    texts = [c["text"] for c in item["table_context"]["cells"]]
    assert "Lot 3 — ne pas appliquer sans accord" in texts
    assert "Si le support est refusé" in texts
    assert "Lot 2" not in texts
    assert item["lot_state"] == item["applicability"] == "UNKNOWN"


def test_context_budget_invalidates_cell_treatments_without_erasing_history(
    session_factory, table_dossier, monkeypatch
):
    import app.modules.case.infrastructure.analysis_table_context as context

    seed = table_dossier[0]
    qualify_review(session_factory, seed)
    before = read(session_factory, seed)
    monkeypatch.setattr(context, "MAX_TABLE_BYTES", 1)
    after = read(session_factory, seed)
    assert after["dossier_sha256"] != before["dossier_sha256"]
    assert after["dossier_review"]["state"] == "REVIEW_REQUIRED"
    for item in [p for a in after["axes"] for p in a["items"] if p.get("table_context")]:
        assert item["table_context"]["state"] == "UNKNOWN"
        assert item["table_context"]["cells"] == []
        assert item["table_context"]["unknown_reason"] == "READ_BUDGET_EXCEEDED"
        assert item["human_assessment"]["state"] == "REVIEW_REQUIRED"
        assert item["human_assessment"]["treatment"] is None


@pytest.mark.parametrize("fault", ["missing", "hash", "document", "version", "locator"])
def test_context_refuses_discordant_sibling_proof(
    session_factory, table_dossier, monkeypatch, fault
):
    from dataclasses import replace
    from uuid import uuid4

    import app.modules.case.infrastructure.analysis_table_context as context

    original = context.SqlAlchemyDceSourceAnchorReader

    class DiscordantReader(original):
        def get_many(self, **kwargs):
            anchors = super().get_many(**kwargs)
            first = next(iter(anchors))
            a = anchors[first]
            if fault == "missing":
                del anchors[first]
            else:
                change = {
                    "hash": dict(fragment_sha256="0" * 64),
                    "document": dict(dce_document_id=uuid4()),
                    "version": dict(dce_version_id=uuid4()),
                    "locator": dict(locator=None),
                }[fault]
                anchors[first] = replace(a, **change)
            return anchors

    monkeypatch.setattr(context, "SqlAlchemyDceSourceAnchorReader", DiscordantReader)
    summary = read(session_factory, table_dossier[0])
    cells = [p for a in summary["axes"] for p in a["items"] if p.get("table_context")]
    assert len(cells) == 3
    assert all(p["source_state"] == "CURRENT_SOURCE" for p in cells)
    assert all(
        p["table_context"]["state"] == "UNKNOWN" and not p["table_context"]["cells"] for p in cells
    )
