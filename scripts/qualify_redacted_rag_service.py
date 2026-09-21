"""Qualify the redacted corpus through the real retrieval service, in memory only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from uuid import NAMESPACE_URL, uuid5

from app.modules.knowledge.application.retrieval import (
    FinancialRetrievalQueryRejected,
    InMemoryVectorIndex,
    RagRetrievalService,
)
from app.modules.knowledge.domain.retrieval import DataClassification, RetrievalChunk, RetrievalScope
from app.modules.knowledge.infrastructure.bge_embeddings import BgeEmbeddingProvider


TENANT_ID = uuid5(NAMESPACE_URL, "smartao:redacted:tenant")
CASE_ID = uuid5(NAMESPACE_URL, "smartao:redacted:case")
VERSION_ID = uuid5(NAMESPACE_URL, "smartao:redacted:version")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--max-chunks-per-document", type=int, default=12)
    args = parser.parse_args()
    chunks: list[RetrievalChunk] = []
    for path in sorted(args.corpus_root.glob("*.txt")):
        text = path.read_text(errors="replace")
        for ordinal, start in enumerate(range(0, min(len(text), 12_000), 1_000), start=1):
            source_text = text[start : start + 1_000].strip()
            if not source_text:
                continue
            chunk_id = uuid5(NAMESPACE_URL, f"{path.name}:{ordinal}")
            chunks.append(
                RetrievalChunk(
                    chunk_id=chunk_id,
                    tenant_id=TENANT_ID,
                    case_id=CASE_ID,
                    dce_version_id=VERSION_ID,
                    source_fragment_id=chunk_id,
                    ordinal=len(chunks) + 1,
                    text=f"Document source: {path.stem}\n{source_text}",
                    locator={"source": path.name, "chunk": ordinal},
                    classification=DataClassification.INTERNAL_OPERATIONAL,
                )
            )
            if ordinal >= args.max_chunks_per_document:
                break

    provider = BgeEmbeddingProvider(cache_dir=args.cache_dir, local_files_only=True, batch_size=2)
    retrieval = RagRetrievalService(embedding_provider=provider, index=InMemoryVectorIndex())
    scope = RetrievalScope(tenant_id=TENANT_ID, case_id=CASE_ID, dce_version_id=VERSION_ID)
    started = perf_counter()
    retrieval.index(chunks=chunks)
    checks = [
        ("deadline", "Quelle est la date limite de réception des offres ?", "RC"),
        ("common_requirements", "Quelles sont les prescriptions techniques communes du marché ?", "CCTC"),
        ("schedule", "Quel est le calendrier prévisionnel des travaux ?", "Planning"),
    ]
    results = []
    sensitive_markers = ("€", "BPU", "DPGF", "IBAN", "SIRET", "marge")
    for label, query, expected in checks:
        found = retrieval.retrieve(query=query, scope=scope, top_k=3)
        sources = [str(result.chunk.locator["source"]) for result in found]
        locators_complete = all(
            "source" in result.chunk.locator and "chunk" in result.chunk.locator
            for result in found
        )
        financial_marker_leak = any(
            marker.lower() in result.chunk.text.lower()
            for result in found
            for marker in sensitive_markers
        )
        results.append(
            {
                "label": label,
                "sources": sources,
                "expected_found": any(expected in source for source in sources),
                "locators_complete": locators_complete,
                "financial_marker_leak": financial_marker_leak,
            }
        )
    try:
        retrieval.retrieve(query="Quel est le montant du BPU et la marge ?", scope=scope, top_k=3)
    except FinancialRetrievalQueryRejected as error:
        refusal = {"status": "REFUSED", "code": str(error)}
    else:
        refusal = {"status": "ERROR", "code": "financial query was not refused"}
    entries_before_cleanup = len(retrieval._index._entries)  # in-memory qualification index only
    retrieval._index._entries.clear()
    entries_after_cleanup = len(retrieval._index._entries)
    output = {
        "status": "ok"
        if all(
            item["expected_found"]
            and item["locators_complete"]
            and not item["financial_marker_leak"]
            for item in results
        )
        and refusal["status"] == "REFUSED"
        and entries_after_cleanup == 0
        else "FAILED",
        "chunks": len(chunks),
        "queries": results,
        "financial_refusal": refusal,
        "entries_before_cleanup": entries_before_cleanup,
        "entries_after_cleanup": entries_after_cleanup,
        "elapsed_ms": round((perf_counter() - started) * 1000, 2),
        "persistent_index": False,
        "database_writes": 0,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
