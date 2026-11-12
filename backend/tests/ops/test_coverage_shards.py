import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

COMMIT = "a" * 40


def helper():
    spec = importlib.util.spec_from_file_location(
        "coverage_diagnostics",
        Path(__file__).parents[3] / "scripts/collect_coverage_diagnostics.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def modules(root):
    for name in ("test_a.py", "test_b.py", "nested/c_test.py", "nested/test_d.py", "support.py"):
        path = root / "backend/tests" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("")


def artifacts(root, folder):
    module = helper()
    for index in range(4):
        path = folder / f"coverage-shard-{index}"
        path.mkdir(parents=True)
        (path / "modules.json").write_text(json.dumps(module.shard_modules(root, index, 4)))
        (path / "environment.json").write_text(json.dumps({"git_commit": COMMIT}))
        (path / "pytest-exit-code.txt").write_text("0")
        (path / "coverage.data").write_bytes(b"placeholder")


def test_partitions_are_complete_disjoint_stable_and_keep_modules_whole(tmp_path):
    modules(tmp_path)
    groups = [helper().shard_modules(tmp_path, index, 4) for index in range(4)]
    flat = [name for group in groups for name in group]
    assert len(flat) == len(set(flat)) == 4
    assert sorted(flat) == sorted(
        str(p.relative_to(tmp_path))
        for p in (tmp_path / "backend/tests").rglob("*.py")
        if p.name != "support.py"
    )
    assert groups == [helper().shard_modules(tmp_path, index, 4) for index in range(4)]


@pytest.mark.parametrize("index,count", [(-1, 4), (4, 4), (0, 0), (0, 1)])
def test_invalid_or_empty_partition_is_refused(tmp_path, index, count):
    with pytest.raises(ValueError):
        helper().shard_modules(tmp_path, index, count)


@pytest.mark.parametrize("fault", ["missing", "duplicate", "failed", "source", "empty"])
def test_aggregation_refuses_incomplete_or_mixed_proof(tmp_path, fault):
    modules(tmp_path)
    folder = tmp_path / "artifacts"
    artifacts(tmp_path, folder)
    first = folder / "coverage-shard-0"
    if fault == "missing":
        (first / "modules.json").unlink()
    elif fault == "duplicate":
        (first / "modules.json").write_bytes(
            (folder / "coverage-shard-1/modules.json").read_bytes()
        )
    elif fault == "failed":
        (first / "pytest-exit-code.txt").write_text("1")
    elif fault == "source":
        (first / "environment.json").write_text(json.dumps({"git_commit": "previous-source"}))
    else:
        (first / "coverage.data").write_bytes(b"")
    with pytest.raises(ValueError):
        helper().validate_shards(tmp_path, folder, 4, COMMIT)


@pytest.mark.parametrize("commit", ["", "fatal: not a git repository"])
def test_unresolved_source_identity_is_never_accepted(tmp_path, commit):
    modules(tmp_path)
    folder = tmp_path / "artifacts"
    artifacts(tmp_path, folder)
    for path in folder.glob("*/environment.json"):
        path.write_text(json.dumps({"git_commit": commit}))
    with pytest.raises(ValueError):
        helper().validate_shards(tmp_path, folder, 4, commit)


@pytest.mark.parametrize("complete,expected", [(True, 0), (False, 2)])
def test_real_combination_enforces_global_threshold(tmp_path, monkeypatch, complete, expected):
    for key in list(os.environ):
        if key.startswith("COV_CORE_") or key == "COVERAGE_FILE":
            monkeypatch.delenv(key)
    modules(tmp_path)
    folder = tmp_path / "artifacts"
    artifacts(tmp_path, folder)
    app = tmp_path / "backend/app"
    app.mkdir()
    (app / "probe.py").write_text(
        'import os\nif os.environ["PROBE_BRANCH"] == "a":\n    a = 1\nelse:\n    b = 2\n'
    )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.coverage.run]\nbranch=true\nsource=["backend/app"]\n'
        "[tool.coverage.report]\nprecision=2\nfail_under=85.50\n"
    )
    for index in range(4):
        path = folder / f"coverage-shard-{index}/coverage.data"
        path.unlink()
        subprocess.run(
            [
                sys.executable,
                "-m",
                "coverage",
                "run",
                f"--data-file={path}",
                "backend/app/probe.py",
            ],
            cwd=tmp_path,
            env=dict(os.environ, PROBE_BRANCH="b" if complete and index % 2 else "a"),
            check=True,
        )
    module = helper()
    monkeypatch.setattr(module, "_git_value", lambda *args: COMMIT)
    assert module.combine_shards(tmp_path, folder, tmp_path / "combined", 4) == expected


def test_cli_runs_all_partitions_then_combines_their_real_data(tmp_path, monkeypatch):
    for key in list(os.environ):
        if key.startswith("COV_CORE_") or key == "COVERAGE_FILE":
            monkeypatch.delenv(key)
    modules(tmp_path)
    app = tmp_path / "backend/app"
    app.mkdir()
    (app / "__init__.py").write_text("")
    (app / "probe.py").write_text(
        "def choose(flag):\n    if flag:\n        return 1\n    return 2\n"
    )
    files = [name for index in range(4) for name in helper().shard_modules(tmp_path, index, 4)]
    for index, name in enumerate(files):
        (tmp_path / name).write_text(
            "from app.probe import choose\n"
            "def test_branch():\n"
            f"    assert choose({index % 2 == 0}) == {1 if index % 2 == 0 else 2}\n"
        )
    (tmp_path / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\npythonpath=["backend"]\n'
        '[tool.coverage.run]\nbranch=true\nsource=["backend/app"]\n'
        "[tool.coverage.report]\nprecision=2\nfail_under=85.50\n"
    )
    (tmp_path / "uv.lock").write_text("synthetic CLI proof")
    script = tmp_path / "scripts/collect_coverage_diagnostics.py"
    script.parent.mkdir()
    shutil.copyfile(Path(__file__).parents[3] / "scripts/collect_coverage_diagnostics.py", script)
    for args in (
        ["git", "init", "-q"],
        ["git", "add", "."],
        [
            "git",
            "-c",
            "user.name=CI",
            "-c",
            "user.email=ci@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
    ):
        subprocess.run(args, cwd=tmp_path, check=True, capture_output=True)
    for index in range(4):
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--output-dir",
                str(tmp_path / f"artifacts/coverage-shard-{index}"),
                "--shard-index",
                str(index),
            ],
            cwd=tmp_path,
            check=True,
            capture_output=True,
        )
    subprocess.run(
        [
            sys.executable,
            str(script),
            "--output-dir",
            str(tmp_path / "combined"),
            "--combine-shards",
            str(tmp_path / "artifacts"),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    report = json.loads((tmp_path / "combined/coverage.json").read_text())
    assert report["totals"]["percent_covered"] == 100
