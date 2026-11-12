"""Database tests must never infer a connection to the operator's local database."""

import importlib
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest
import sqlalchemy as sa


def test_missing_explicit_database_url_has_no_local_fallback() -> None:
    environment = os.environ.copy()
    environment.pop("SMART_AO_TEST_DATABASE_URL", None)
    environment["PYTHONPATH"] = str(Path(__file__).resolve().parents[2])
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from tests.support.database import DATABASE_URL; print(repr(DATABASE_URL))",
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.strip() == "''"


@pytest.mark.parametrize("flag", [None, "0"])
def test_destructive_benchmark_requires_disposable_opt_in(monkeypatch, flag) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3]))
    benchmark = importlib.import_module("scripts.benchmark_assignment_change_journal")
    monkeypatch.setattr(benchmark, "DATABASE_URL", "postgresql+psycopg://fixture@127.0.0.1/test")
    if flag is None:
        monkeypatch.delenv("SMART_AO_TEST_DISPOSABLE_DATABASE", raising=False)
    else:
        monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", flag)
    engine = cast(sa.Engine, SimpleNamespace(url=sa.make_url(benchmark.DATABASE_URL)))
    with pytest.raises(RuntimeError, match="disposable"):
        benchmark.measure(engine)


def test_destructive_benchmark_refuses_another_engine(monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3]))
    benchmark = importlib.import_module("scripts.benchmark_assignment_change_journal")
    monkeypatch.setattr(benchmark, "DATABASE_URL", "postgresql+psycopg://fixture@127.0.0.1/test")
    monkeypatch.setenv("SMART_AO_TEST_DISPOSABLE_DATABASE", "1")
    engine = cast(sa.Engine, SimpleNamespace(url=sa.make_url("postgresql+psycopg://fixture/other")))
    with pytest.raises(RuntimeError, match="disposable"):
        benchmark.measure(engine)


def test_openapi_export_uses_no_network_database(monkeypatch, tmp_path) -> None:
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[3]))
    exporter = importlib.import_module("scripts.export_assignment_openapi")
    monkeypatch.setattr(exporter, "__file__", str(tmp_path / "scripts" / "export.py"))
    (tmp_path / "docs" / "reference").mkdir(parents=True)
    create_engine = sa.create_engine
    destinations = []

    def local_engine(url):
        destinations.append(url)
        assert url == "sqlite://"
        return create_engine(url)

    monkeypatch.setattr(exporter.sa, "create_engine", local_engine)
    exporter.main()
    assert destinations == ["sqlite://"]
    assert (tmp_path / "docs" / "reference" / "SMART_AO_V8_ASSIGNMENT_OPENAPI.json").exists()
