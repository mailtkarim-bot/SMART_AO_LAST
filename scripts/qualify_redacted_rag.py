"""Run a temporary metadata-aware RAG qualification over a redacted corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

import numpy as np
import torch
from sentence_transformers import SentenceTransformer


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--max-chunks-per-document", type=int, default=12)
    args = parser.parse_args()
    if args.max_chunks_per_document < 1:
        raise SystemExit("--max-chunks-per-document must be positive")

    chunks: list[dict[str, object]] = []
    for path in sorted(args.corpus_root.glob("*.txt")):
        for index, start in enumerate(range(0, min(len(path.read_text(errors="replace")), 12_000), 1_000)):
            text = path.read_text(errors="replace")[start : start + 1_000].strip()
            if text:
                chunks.append(
                    {
                        "source": path.name,
                        "chunk": index,
                        "text": text,
                        # Metadata is embedded for retrieval only; source text is unchanged.
                        "embedding_text": f"Document source: {path.stem}\n{text}",
                    }
                )
            if index >= args.max_chunks_per_document:
                break
    if not chunks:
        raise SystemExit("redacted corpus is empty")

    queries = (
        ("deadline", "Quelle est la date limite de réception des offres ?", "RC"),
        ("common_requirements", "Quelles sont les prescriptions techniques communes du marché ?", "CCTC"),
        ("schedule", "Quel est le calendrier prévisionnel des travaux ?", "Planning"),
    )
    torch.set_num_threads(1)
    started = perf_counter()
    model = SentenceTransformer(str(args.model_path), device="cpu", local_files_only=True)
    vectors = model.encode(
        [chunk["embedding_text"] for chunk in chunks] + [query for _, query, _ in queries],
        batch_size=2,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    corpus = vectors[: len(chunks)]
    results = []
    for (label, query, expected), query_vector in zip(queries, vectors[len(chunks) :], strict=True):
        scores = corpus @ query_vector
        order = np.argsort(-scores)[:3]
        top = [
            {
                "source": chunks[int(index)]["source"],
                "chunk": chunks[int(index)]["chunk"],
                "score": round(float(scores[int(index)]), 4),
            }
            for index in order
        ]
        results.append(
            {
                "label": label,
                "expected_source": expected,
                "top": top,
                "expected_found_in_top3": any(expected.lower() in item["source"].lower() for item in top),
            }
        )
    output = {
        "status": "ok",
        "chunks": len(chunks),
        "queries": len(queries),
        "embedding_dimension": int(vectors.shape[-1]),
        "elapsed_ms": round((perf_counter() - started) * 1000, 2),
        "persistent_index": False,
        "database_writes": 0,
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if all(item["expected_found_in_top3"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
