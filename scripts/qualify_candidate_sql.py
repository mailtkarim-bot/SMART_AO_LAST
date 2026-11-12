"""Offline synthetic PostgreSQL + pinned E5 qualification; never an active factory."""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid5

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
import sqlalchemy as sa  # noqa: E402
from app.modules.case.infrastructure.models.case import CaseRecord  # noqa: E402
from app.modules.dce.infrastructure.models.consultation import ConsultationRecord  # noqa: E402
from app.modules.dce.infrastructure.models.dce_extraction import (  # noqa: E402
    DceDocumentExtractionFragmentRecord,
    DceDocumentExtractionRecord,
)
from app.modules.dce.infrastructure.models.dce_staging import DceStagedObjectRecord  # noqa: E402
from app.modules.dce.infrastructure.models.dce_version import (  # noqa: E402
    DceDocumentRecord,
    DceVersionRecord,
)
from app.modules.knowledge.application.candidate_retrieval import (
    CandidateRetrievalService,  # noqa: E402
)
from app.modules.knowledge.domain.embedding_profile import CandidateRetrievalProfile  # noqa: E402
from app.modules.knowledge.domain.retrieval import RetrievalScope  # noqa: E402
from app.modules.knowledge.infrastructure.candidate_embeddings import (
    CpuCandidateEncoder,  # noqa: E402
)
from app.modules.knowledge.infrastructure.dce_source import (
    SqlAlchemyDceRetrievalSource,  # noqa: E402
)
from app.platform.persistence.models import TenantRecord  # noqa: E402
from qualify_candidate_retrieval import main as qualify  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

NOW = datetime(2026, 10, 18, 12, tzinfo=UTC)


def seed_fixture(data, factory):
    if (
        data.get("synthetic") is not True
        or data.get("held_out") is not True
        or data.get("schema_version") != 1
        or any(d["classification"] != "INTERNAL_OPERATIONAL" for d in data["documents"])
    ):
        raise ValueError("synthetic internal SQL fixture required")
    documents = data["documents"]
    with factory.begin() as s:
        if s.scalar(sa.select(sa.func.count()).select_from(TenantRecord)):
            raise ValueError("empty disposable database required")
        for tenant in sorted({d["tenant_id"] for d in documents}):
            s.add(TenantRecord(id=UUID(tenant), slug=f"e5-sql-{tenant}", lifecycle="ACTIVE"))
        s.flush()
        for tenant, version in sorted({(d["tenant_id"], d["version_id"]) for d in documents}):
            consultation = uuid5(UUID(version), "consultation")
            s.add(
                ConsultationRecord(
                    id=consultation,
                    tenant_id=UUID(tenant),
                    functional_identity_hash=sha256(str(consultation).encode()).hexdigest(),
                    buyer_legal_name="Acheteur synthétique",
                    object_label="Essai E5 SQL",
                    source_channel="MANUAL_UPLOAD",
                    source_received_at=NOW,
                    lifecycle="OPEN",
                    freshness="CURRENT",
                )
            )
            s.flush()
            s.add(
                DceVersionRecord(
                    id=UUID(version),
                    tenant_id=UUID(tenant),
                    consultation_id=consultation,
                    corpus_hash=sha256(version.encode()).hexdigest(),
                    provenance_channel="MANUAL_UPLOAD",
                    source_received_at=NOW,
                    lifecycle="ADMITTED",
                    integrity="VERIFIED",
                    classification_readiness="UNCLASSIFIED",
                    analysis_readiness="NOT_READY",
                )
            )
        s.flush()
        for tenant, case in sorted({(d["tenant_id"], d["case_id"]) for d in documents}):
            current = {
                d["version_id"]
                for d in documents
                if d["tenant_id"] == tenant and d["case_id"] == case and d["current"]
            }
            if len(current) != 1:
                raise ValueError("exact current version required")
            version = UUID(current.pop())
            s.add(
                CaseRecord(
                    id=UUID(case),
                    tenant_id=UUID(tenant),
                    consultation_id=uuid5(version, "consultation"),
                    applicable_dce_version_id=version,
                    functional_identity_hash=sha256(case.encode()).hexdigest(),
                    title="Affaire synthétique E5 SQL",
                    business_origin="MANUAL",
                    origin_rationale="Banc synthétique",
                    scope_kind="SINGLE_LOT",
                    scope_json={"lot": "synthetic"},
                    scope_fingerprint=sha256(case.encode()).hexdigest(),
                    lifecycle="ACTIVE",
                    commercial_stage="ANALYSIS",
                    decision_readiness="NOT_READY",
                    dce_freshness="CURRENT",
                    responsibility_status="UNASSIGNED",
                )
            )
        s.flush()
        for i, d in enumerate(documents):
            fragment, tenant, version = UUID(d["id"]), UUID(d["tenant_id"]), UUID(d["version_id"])
            staged, document, extraction = (
                uuid5(fragment, k) for k in ("staged", "document", "extraction")
            )
            text = d["text"]
            digest = sha256(text.encode()).hexdigest()
            key = f"synthetic/e5-sql/{staged}"
            s.add(
                DceStagedObjectRecord(
                    id=staged,
                    tenant_id=tenant,
                    consultation_id=uuid5(version, "consultation"),
                    storage_key=key,
                    original_filename="synthetic.txt",
                    expected_byte_size=len(text.encode()),
                    actual_byte_size=len(text.encode()),
                    sha256=digest,
                    media_type="text/plain",
                    source_channel="MANUAL_UPLOAD",
                    state="CONSUMED",
                    scan_verdict="CLEAN",
                    expires_at=NOW + timedelta(days=1),
                    consumed_by_dce_version_id=version,
                    consumed_at=NOW,
                )
            )
            s.flush()
            s.add(
                DceDocumentRecord(
                    id=document,
                    tenant_id=tenant,
                    dce_version_id=version,
                    storage_object_id=staged,
                    storage_key=key,
                    original_filename="synthetic.txt",
                    media_type="text/plain",
                    byte_size=len(text.encode()),
                    sha256=digest,
                    received_from="MANUAL_UPLOAD",
                )
            )
            s.flush()
            s.add(
                DceDocumentExtractionRecord(
                    id=extraction,
                    tenant_id=tenant,
                    dce_version_id=version,
                    dce_document_id=document,
                    input_sha256=digest,
                    extractor_id="synthetic-e5-sql",
                    extractor_version="1",
                    status=d["extraction_status"],
                    fragment_count=1,
                    extracted_char_count=len(text),
                    failure_code=None
                    if d["extraction_status"] == "COMPLETED"
                    else "SYNTHETIC_INCOMPLETE",
                    created_at=NOW,
                )
            )
            s.flush()
            s.add(
                DceDocumentExtractionFragmentRecord(
                    id=fragment,
                    tenant_id=tenant,
                    extraction_id=extraction,
                    ordinal=i + 1,
                    text=text,
                    text_sha256=digest,
                    locator_json={"kind": "synthetic_page", "page": d["page"]},
                )
            )


def validate_runtime(data, factory, profile, encoder):
    source = SqlAlchemyDceRetrievalSource(session_factory=factory)
    scope = RetrievalScope(
        tenant_id=UUID(data["tenant_id"]),
        case_id=UUID(data["case_id"]),
        dce_version_id=UUID(data["version_id"]),
    )
    query = next(
        q
        for q in data["queries"]
        if len(q["expected"]) == 1
        and q.get("expected_visit_subject") == "VISIT_SITE"
        and q.get("expected_query_lot") is not None
    )
    fragment = UUID(query["expected"][0])

    class Probe:
        def __init__(self):
            self.profile_id = profile.profile_id
            self.after_query: Callable[[], None] = lambda: None

        def encode_passages(self, texts):
            return encoder.encode_passages(texts)

        def encode_query(self, text):
            vector = encoder.encode_query(text)
            self.after_query()
            return vector

    probe = Probe()
    service = CandidateRetrievalService(profile=profile, source=source, encoder=probe)
    warm = service.retrieve(query=query["text"], scope=scope)

    def refusal():
        with factory.begin() as s:
            s.add(
                DceDocumentExtractionRecord(
                    id=uuid5(fragment, "refusal"),
                    tenant_id=scope.tenant_id,
                    dce_version_id=scope.dce_version_id,
                    dce_document_id=uuid5(fragment, "document"),
                    input_sha256=sha256(
                        next(
                            d["text"] for d in data["documents"] if d["id"] == str(fragment)
                        ).encode()
                    ).hexdigest(),
                    extractor_id="synthetic-e5-sql-refusal",
                    extractor_version="1",
                    status="REVIEW_REQUIRED",
                    fragment_count=0,
                    extracted_char_count=0,
                    failure_code="SYNTHETIC_INCOMPLETE",
                    created_at=NOW + timedelta(seconds=1),
                )
            )

    probe.after_query = refusal
    invalid = service.retrieve(query=query["text"], scope=scope)
    probe.after_query = lambda: None
    later = service.retrieve(query=query["text"], scope=scope)

    def unlink():
        with factory.begin() as s:
            s.execute(
                sa.update(CaseRecord)
                .where(CaseRecord.id == scope.case_id)
                .values(applicable_dce_version_id=None)
            )

    probe.after_query = unlink
    changed = service.retrieve(query=query["text"], scope=scope)
    probe.after_query = lambda: None
    empty = service.retrieve(query=query["text"], scope=scope)
    return dict(
        initial_expected=fragment in {h.result.chunk.source_fragment_id for h in warm.hits},
        extraction_changed=invalid.reason == "SOURCE_CHANGED"
        and not invalid.hits
        and not invalid.score_trace
        and not invalid.visit_type_evidence,
        old_fragment_absent=fragment not in {t.source_fragment_id for t in later.score_trace}
        and not later.hits,
        version_dereferenced=changed.reason == "SOURCE_CHANGED"
        and not changed.hits
        and not changed.score_trace
        and not changed.visit_type_evidence,
        no_current_source=empty.reason == "NO_CURRENT_SOURCE" and not empty.hits,
        historical_fragment_preserved=_fragment_exists(factory, fragment),
    )


def _fragment_exists(factory, fragment):
    with factory() as s:
        return s.get(DceDocumentExtractionFragmentRecord, fragment) is not None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["fixture", "profile", "model-dir", "runtime-manifest", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    url = sa.engine.make_url(os.environ.get("SMART_AO_TEST_DATABASE_URL", ""))
    if (
        os.environ.get("SMART_AO_TEST_DISPOSABLE_DATABASE") != "1"
        or url.database != "smartao_e5_sql"
        or url.host is not None
        or url.drivername != "postgresql+psycopg"
        or url.username != "proof"
        or url.port is not None
        or dict(url.query) != {"host": "/socket"}
        or any(k in os.environ for k in ("PGHOSTADDR", "PGSERVICE", "PGSERVICEFILE"))
    ):
        raise ValueError("dedicated disposable Unix socket database required")
    engine = sa.create_engine(url)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    try:
        data = json.loads(args.fixture.read_text())
        seed_fixture(data, factory)
        profile = CandidateRetrievalProfile(**json.loads(args.profile.read_text()))
        encoder = CpuCandidateEncoder(
            profile=profile, model_dir=args.model_dir, runtime_manifest=args.runtime_manifest
        )
        source = SqlAlchemyDceRetrievalSource(session_factory=factory)
        counter = {"statements": 0}

        def count(*unused):
            counter["statements"] += 1

        sa.event.listen(engine, "before_cursor_execute", count)
        forwarded = [
            value
            for name in ["fixture", "profile", "model-dir", "runtime-manifest", "output"]
            for value in ["--" + name, str(getattr(args, name.replace("-", "_")))]
        ]
        qualify(forwarded, source_override=source, encoder_override=encoder)
        measured_count = counter["statements"]
        start = time.perf_counter()
        validations = validate_runtime(data, factory, profile, encoder)
        report = json.loads(args.output.read_text())
        report["sql_transport"] = {
            "statements_measured": measured_count,
            "validation_statements": counter["statements"] - measured_count,
            "validation_ms": (time.perf_counter() - start) * 1000,
            "validations": validations,
            "peak_rss_after_validation_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        }
        report["admitted"] = False
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
