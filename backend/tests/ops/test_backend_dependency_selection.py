from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[3]
FLAGS = {
    "rag": "SMART_AO_INSTALL_RAG",
    "document-advanced": "SMART_AO_INSTALL_DOCUMENT_ADVANCED",
    "document-ocr": "SMART_AO_INSTALL_DOCUMENT_OCR",
    "object-storage": "SMART_AO_INSTALL_OBJECT_STORAGE",
    "connectors": "SMART_AO_INSTALL_CONNECTORS",
    "notifications": "SMART_AO_INSTALL_NOTIFICATIONS",
    "calendar": "SMART_AO_INSTALL_CALENDAR",
}


@pytest.mark.parametrize(
    "extras",
    [
        (),
        ("rag", "document-advanced"),
        ("document-ocr",),
        ("document-advanced", "document-ocr"),
        tuple(FLAGS),
    ],
)
def test_backend_build_synchronizes_the_union_of_requested_extras_once(
    tmp_path: Path,
    extras: tuple[str, ...],
) -> None:
    dockerfile = (ROOT / "ops/docker/backend.Dockerfile").read_text()
    block = re.search(r"^RUN python .*?(?=\n\nUSER)", dockerfile, re.M | re.S)
    assert block is not None
    # Exercise the real build shell; only external installer/ownership commands are replaced.
    tools = tmp_path / "bin"
    tools.mkdir()
    for name in ("python", "chown"):
        path = tools / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o700)
    uv = tools / "uv"
    uv.write_text(
        f"#!{sys.executable}\n"
        "import json, os, sys\n"
        "with open(os.environ['SMART_AO_SYNC_PROOF_OUTPUT'], 'a') as output:\n"
        "    output.write(json.dumps(sys.argv[1:]) + '\\n')\n"
    )
    uv.chmod(0o700)
    output = tmp_path / "calls.jsonl"
    env = {
        **os.environ,
        **{flag: "1" if extra in extras else "0" for extra, flag in FLAGS.items()},
        "PATH": f"{tools}:{os.environ['PATH']}",
        "SMART_AO_SYNC_PROOF_OUTPUT": str(output),
    }
    # Docker's absolute interpreter must never invoke the host installer.
    shell = block.group()[4:].replace("\\\n", " ")
    shell = shell.replace("/usr/local/bin/python", shlex.quote(str(tools / "python")))
    result = subprocess.run(
        ["/bin/sh", "-c", shell],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    calls = [json.loads(line) for line in output.read_text().splitlines()]
    assert calls == [
        [
            "sync",
            "--frozen",
            "--no-dev",
            "--no-editable",
            *(argument for extra in extras for argument in ("--extra", extra)),
        ]
    ]


def test_pdf_ocr_extra_declares_its_existing_renderer_dependency() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    names = {
        Requirement(value).name.lower()
        for value in project["project"]["optional-dependencies"]["document-ocr"]
    }
    assert "pymupdf" in names
