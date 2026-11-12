"""Two sourced contributions, a separate alternative and one exact synthetic offer."""

import json
import shutil
from hashlib import sha256

import pytest
from tests.db import test_l04_multilot_pipeline as pipeline
from tests.db import test_transversal_affaire_workflow as flow


@pytest.mark.parametrize("include_annexes", [False, True])
def test_selected_assembled_response_reaches_zip_and_handover(
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
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    monkeypatch.setattr(pipeline, "FIXTURES", development)
    case = flow.affaire.__wrapped__(session_factory, tmp_path)
    case.response_assembly = True
    case.source_annexes = include_annexes
    flow.test_shared_native_http_preserves_case_sources_and_denies_financial_access(
        session_factory, case, tmp_path, monkeypatch
    )
