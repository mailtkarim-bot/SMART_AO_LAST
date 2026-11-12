"""One synthetic buyer frame is independently reviewed and exported as exact DOCX bytes."""

import io
import json
import shutil
from hashlib import sha256

import pytest
from docx import Document
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db import test_transversal_affaire_workflow as flow


@pytest.mark.parametrize("include_annexes", [False, True])
def test_buyer_docx_from_selected_sources_to_exact_authorized_zip(
    session_factory, tmp_path, monkeypatch, include_annexes
):
    development = tmp_path / "development"
    corpus = development / "dce_l04_multilot"
    shutil.copytree(pipeline.FIXTURES / "dce_l04_multilot", corpus)
    ccap = corpus / "ccap.txt"
    ccap.write_text(
        ccap.read_text() + "\nUne attestation d'assurance décennale est exigée pour le lot 1.\n"
    )
    manifest = json.loads((corpus / "manifest.json").read_text())
    next(d for d in manifest["documents"] if d["file"] == "ccap.txt")["sha256"] = sha256(
        ccap.read_bytes()
    ).hexdigest()
    document = Document()
    document.add_heading("Cadre acheteur synthétique — assurances", 0)
    document.add_paragraph("Engagement de couverture déclaré pour le lot 1, à relire.")
    document.add_paragraph("[[REPONSE:COUVERTURE]]")
    table = document.add_table(rows=2, cols=2)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Rubrique acheteur"
    table.cell(0, 1).text = "Réponse entreprise"
    table.cell(1, 0).text = "Pièces assurance lot 1"
    table.cell(1, 1).text = "[[REPONSE:ATTESTATION]]"
    document.add_paragraph("[[REPONSE:AUTRE]]")
    output = io.BytesIO()
    document.save(output)
    raw = output.getvalue()
    (corpus / "cadre.docx").write_bytes(raw)
    manifest["documents"].append(
        dict(
            file="cadre.docx",
            family="ANNEXE",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            sha256=sha256(raw).hexdigest(),
        )
    )
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    case = flow.affaire.__wrapped__(session_factory, tmp_path)
    case.response_assembly = True
    case.buyer_docx = True
    case.source_annexes = include_annexes
    case.docx_template_bytes = raw
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, case, tmp_path, monkeypatch
    )
    assert (
        Document(io.BytesIO(case.exported_docx)).tables[0].cell(1, 0).text
        == "Pièces assurance lot 1"
    )

    # Optional private evidence output: synthetic bytes only, never a production export.
    import os
    from pathlib import Path

    if root := os.environ.get("SMART_AO_DOCX_PROOF_DIR"):
        destination = Path(root)
        destination.mkdir(mode=0o700, parents=True, exist_ok=True)
        (destination / "buyer-template.docx").write_bytes(raw)
        (destination / "filled-response.docx").write_bytes(case.exported_docx)
        (destination / "region-provenance.json").write_text(
            json.dumps(case.docx_provenance, indent=2)
        )
