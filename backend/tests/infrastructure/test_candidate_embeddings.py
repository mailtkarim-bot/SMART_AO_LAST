import hashlib
import json
from dataclasses import replace
from types import SimpleNamespace

import pytest
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile


def fixture(tmp_path):
    root = tmp_path / "model"
    root.mkdir()
    contents = {
        "config.json": "{}",
        "modules.json": json.dumps(
            [
                {"type": "sentence_transformers.models.Transformer", "path": ""},
                {"type": "sentence_transformers.models.Pooling", "path": "1_Pooling"},
                {"type": "sentence_transformers.models.Normalize", "path": "2_Normalize"},
            ]
        ),
        "model.safetensors": "synthetic-test-weights",
    }
    files = []
    for name, text in contents.items():
        (root / name).write_text(text)
        files.append(
            {
                "file": name,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "bytes": len(text.encode()),
            }
        )
    manifest = root / "qualification-manifest.json"
    manifest.write_text(
        json.dumps(
            {"repository": "intfloat/multilingual-e5-small", "revision": "a" * 40, "files": files}
        )
    )
    runtime = tmp_path / "runtime.json"
    runtime.write_text(
        json.dumps({"torch": "2.13.0+cpu", "torchvision": {"version": "0.28.0+cpu"}})
    )
    profile = CandidateRetrievalProfile(
        revision="a" * 40,
        model_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),
        runtime_manifest_sha256=hashlib.sha256(runtime.read_bytes()).hexdigest(),
    )
    return root, runtime, profile


def test_manifest_and_every_local_file_are_verified(tmp_path):
    from app.modules.knowledge.infrastructure.candidate_embeddings import verify_candidate_files

    root, runtime, p = fixture(tmp_path)
    verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)
    (root / "model.safetensors").write_text("tampered")
    with pytest.raises(ValueError):
        verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)


def test_manifest_path_escape_is_refused(tmp_path):
    from app.modules.knowledge.infrastructure.candidate_embeddings import verify_candidate_files

    root, runtime, p = fixture(tmp_path)
    path = root / "qualification-manifest.json"
    d = json.loads(path.read_text())
    d["files"][0]["file"] = "../outside"
    path.write_text(json.dumps(d))
    p = replace(p, model_manifest_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):
        verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)


def test_cpu_encoder_has_distinct_prefixes_and_refuses_truncation(tmp_path, monkeypatch):
    import app.modules.knowledge.infrastructure.candidate_embeddings as module

    root, runtime, p = fixture(tmp_path)
    calls = []

    class Model:
        max_seq_length = 512

        def tokenizer(self, text, **kwargs):
            return {"input_ids": list(range(513 if "overflow" in text else 12))}

        def encode(self, texts, **kwargs):
            calls.append((texts, kwargs))
            return [[1.0] + [0.0] * 383 for _ in texts]

    encoder = module.CpuCandidateEncoder(profile=p, model_dir=root, runtime_manifest=runtime)
    monkeypatch.setattr(encoder, "_load_model", lambda: Model())
    encoder.encode_passages(["texte"])
    encoder.encode_query("question")
    assert calls[0][0] == ["passage: texte"] and calls[1][0] == ["query: question"]
    assert all(kwargs["normalize_embeddings"] for _, kwargs in calls)
    with pytest.raises(ValueError, match="TOKEN_TRUNCATION_REFUSED"):
        encoder.encode_query("overflow")
    assert len(calls) == 2


def test_module_path_outside_verified_model_is_refused(tmp_path):
    from app.modules.knowledge.infrastructure.candidate_embeddings import verify_candidate_files

    root, runtime, p = fixture(tmp_path)
    path = root / "modules.json"
    modules = json.loads(path.read_text())
    modules[0]["path"] = "../outside"
    path.write_text(json.dumps(modules))
    manifest = root / "qualification-manifest.json"
    data = json.loads(manifest.read_text())
    entry = next(e for e in data["files"] if e["file"] == "modules.json")
    entry["bytes"] = path.stat().st_size
    entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    p = replace(p, model_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    with pytest.raises(ValueError):
        verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)


def test_unlisted_tokenizer_asset_is_not_silently_loaded(tmp_path):
    from app.modules.knowledge.infrastructure.candidate_embeddings import verify_candidate_files

    root, runtime, p = fixture(tmp_path)
    (root / "added_tokens.json").write_text("{}")
    with pytest.raises(ValueError):
        verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)


def test_weights_changed_during_loading_never_receive_verified_identity(tmp_path, monkeypatch):
    import sys

    import app.modules.knowledge.infrastructure.candidate_embeddings as module

    root, runtime, p = fixture(tmp_path)
    versions = {
        "torch": "2.13.0+cpu",
        "torchvision": "0.28.0+cpu",
        "sentence-transformers": p.sentence_transformers_version,
        "transformers": p.transformers_version,
        "tokenizers": p.tokenizers_version,
        "numpy": p.numpy_version,
        "safetensors": p.safetensors_version,
    }
    monkeypatch.setattr(module, "version", lambda name: versions[name])

    class Model:
        def __init__(self, *args, **kwargs):
            (root / "model.safetensors").write_text("changed-during-construction")

        def get_sentence_embedding_dimension(self):
            return 384

        def parameters(self):
            return iter([SimpleNamespace(dtype="FP32")])

        def tokenizer(self, *args, **kwargs):
            return {"input_ids": [1, 2]}

        def encode(self, *args, **kwargs):
            return [[1.0] + [0.0] * 383]

    monkeypatch.setitem(
        sys.modules, "torch", SimpleNamespace(set_num_threads=lambda n: None, float32="FP32")
    )
    monkeypatch.setitem(
        sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=Model)
    )
    encoder = module.CpuCandidateEncoder(profile=p, model_dir=root, runtime_manifest=runtime)
    with pytest.raises(ValueError):
        encoder.encode_query("question")
    assert encoder._model is None


def test_manifest_is_parsed_from_the_bytes_whose_hash_was_checked(tmp_path, monkeypatch):
    from pathlib import Path

    from app.modules.knowledge.infrastructure.candidate_embeddings import verify_candidate_files

    root, runtime, p = fixture(tmp_path)
    manifest = root / "qualification-manifest.json"
    forged = json.loads(manifest.read_text())
    weights = root / "model.safetensors"
    weights.write_text("forged-weights")
    record = next(r for r in forged["files"] if r["file"] == "model.safetensors")
    record["bytes"] = weights.stat().st_size
    record["sha256"] = hashlib.sha256(weights.read_bytes()).hexdigest()
    original = Path.read_text
    monkeypatch.setattr(
        Path,
        "read_text",
        lambda self, *a, **kw: json.dumps(forged) if self == manifest else original(self, *a, **kw),
    )
    with pytest.raises(ValueError):
        verify_candidate_files(profile=p, model_dir=root, runtime_manifest=runtime)
