# ruff: noqa: F401, F811
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
from app.modules.dce.application.requirements import DceRequirementsService
from app.modules.dce.infrastructure.case_dce_reading_reader import SqlAlchemyCaseDceReadingReader
from app.modules.dce.infrastructure.models.dce_version import DceDocumentClassificationRecord
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.platform.events.dispatcher import CommandDispatcher

sys.path.append(str(Path(__file__).parent))
from test_dce_rc_analysis import (
    NOW,
    _extract_then_analyze,
    _seed_admitted_document,
    isolate_rc_analysis_records,
)


def seed_values(session_factory, tmp_path, text):
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=text.encode()
    )
    with session_factory.begin() as session:
        session.add(
            DceDocumentClassificationRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_document_id=document,
                classification="RC",
                rationale=None,
                source="SYNTHETIC_TEST",
                previous_classification_id=None,
                is_current=True,
                created_by_actor_id=None,
            )
        )
    result = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant,
        document_id=document,
        dce_version_id=version,
    )
    service = DceRequirementsService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(
            session_factory=session_factory,
            handlers={
                "RecordDceRequirementMaterializationRun": (
                    RecordDceRequirementMaterializationRunHandler()
                )
            },
        ),
    )
    service.materialize(
        tenant_id=tenant,
        dce_version_id=version,
        dce_rc_analysis_id=UUID(result.aggregate_refs[0]["aggregate_id"]),
        now=NOW,
    )
    return tenant, document, version


def test_structured_rc_reading_has_source_values_without_effects(session_factory, tmp_path):
    tenant, document, version = seed_values(
        session_factory, tmp_path, "Le DC1 est obligatoire pour le lot 2."
    )
    with session_factory() as session:
        reader = SqlAlchemyCaseDceReadingReader(session)
        items = reader._read_requirements(tenant_id=tenant, dce_version_id=version)
        assert len(items) == 1
        candidate = getattr(items[0], "structured_candidate", None)
        assert candidate is not None
        assert candidate.documents == ("DC1",) and candidate.lot_numbers == (2,)
        assert candidate.applicability == "UNKNOWN" and candidate.date_state == "UNKNOWN"
        assert items[0].confirmation_outcome == "PENDING_HUMAN_CONFIRMATION"
        assert items == reader._read_requirements(tenant_id=tenant, dce_version_id=version)
        assert reader._read_requirements(tenant_id=uuid4(), dce_version_id=version) == ()


def test_ambiguous_rectification_never_selects_new_or_old_date(session_factory, tmp_path):
    tenant, _, version = seed_values(
        session_factory,
        tmp_path,
        "Rectificatif V2 : date limite de remise reportée au 25/11/2034. "
        "Ancienne date limite de remise : 20/11/2034.",
    )
    with session_factory() as session:
        rows = SqlAlchemyCaseDceReadingReader(session)._read_requirements(
            tenant_id=tenant, dce_version_id=version
        )
        assert len(rows) == 2
        assert all(x.structured_candidate.state == "REVIEW_REQUIRED" for x in rows)
        assert all(x.structured_candidate.date_iso is None for x in rows)


@pytest.mark.parametrize("second_lot,state", [(2, "REVIEW_REQUIRED"), (3, "CANDIDATES_ONLY")])
def test_conflicting_dates_are_not_chosen_for_the_same_scope(
    session_factory, tmp_path, second_lot, state
):
    tenant, _, version = seed_values(
        session_factory,
        tmp_path,
        "Date limite de remise pour le lot 2 : 21/11/2034. "
        f"Date limite de remise pour le lot {second_lot} : 22/11/2034.",
    )
    with session_factory() as session:
        rows = SqlAlchemyCaseDceReadingReader(session)._read_requirements(
            tenant_id=tenant, dce_version_id=version
        )
        assert len(rows) == 2
        assert {x.structured_candidate.state for x in rows} == {state}
        if state == "REVIEW_REQUIRED":
            assert all(x.structured_candidate.date_iso is None for x in rows)
        else:
            assert {x.structured_candidate.date_iso for x in rows} == {"2034-11-21", "2034-11-22"}


@pytest.mark.parametrize("same_time", [False, True])
def test_new_review_extraction_hides_previously_parsed_values(session_factory, tmp_path, same_time):
    from datetime import timedelta

    from app.modules.dce.infrastructure.models.dce_extraction import DceDocumentExtractionRecord
    from app.modules.dce.infrastructure.models.dce_version import DceDocumentRecord

    tenant, document, version = seed_values(
        session_factory, tmp_path, "Le DC1 est obligatoire pour le lot 2."
    )
    with session_factory.begin() as session:
        parent = session.get(DceDocumentRecord, document)
        previous = session.scalar(
            sa.select(DceDocumentExtractionRecord).where(
                DceDocumentExtractionRecord.dce_document_id == document,
                DceDocumentExtractionRecord.tenant_id == tenant,
            )
        )
        session.add(
            DceDocumentExtractionRecord(
                id=uuid4(),
                tenant_id=tenant,
                dce_document_id=document,
                dce_version_id=version,
                input_sha256=parent.sha256,
                extractor_id="synthetic-review",
                extractor_version="1",
                status="REVIEW_REQUIRED",
                fragment_count=0,
                extracted_char_count=0,
                failure_code="SYNTHETIC_REVIEW",
                created_at=previous.created_at + timedelta(seconds=0 if same_time else 1),
            )
        )
    with session_factory() as session:
        rows = SqlAlchemyCaseDceReadingReader(session)._read_requirements(
            tenant_id=tenant, dce_version_id=version
        )
        assert len(rows) == 1
        assert rows[0].structured_candidate.state == "UNKNOWN"
        assert rows[0].structured_candidate.reason_code == "STALE_SOURCE"
        assert (
            rows[0].structured_candidate.documents == rows[0].structured_candidate.lot_numbers == ()
        )


def test_structured_get_does_not_create_commands_events_or_requirements(session_factory, tmp_path):
    from app.modules.dce.infrastructure.models.dce_requirements import DceRequirementRecord
    from app.platform.persistence.models import DomainEventRecord, OutboxMessageRecord

    tenant, _, version = seed_values(
        session_factory, tmp_path, "Le DC1 est obligatoire pour le lot 2."
    )
    with session_factory() as session:
        models = (DceRequirementRecord, DomainEventRecord, OutboxMessageRecord)
        before = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(model)) for model in models
        )
        reader = SqlAlchemyCaseDceReadingReader(session)
        first = reader._read_requirements(tenant_id=tenant, dce_version_id=version)
        assert first == reader._read_requirements(tenant_id=tenant, dce_version_id=version)
        after = tuple(
            session.scalar(sa.select(sa.func.count()).select_from(model)) for model in models
        )
        assert before == after and not session.new and not session.dirty


def test_http_reads_structured_values_from_real_case_and_source_registers(
    session_factory, tmp_path
):
    from dataclasses import replace

    from app.interfaces.http.routes.case_dce_reading import build_case_dce_reading_router
    from app.interfaces.http.routes.consultations import ConsultationSecurityRuntime
    from app.modules.case.infrastructure.models.case import CaseRecord
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from tests.api.test_case_dce_reading_routes import _Decision, _headers, _Policy, _Resolver

    tenant, _, version = seed_values(
        session_factory, tmp_path, "Date limite de remise : 21/11/2034 à 10h30 pour le lot 2."
    )
    case_id = uuid4()
    with session_factory.begin() as session:
        dce = session.get(DceVersionRecord, version)
        session.add(
            CaseRecord(
                id=case_id,
                tenant_id=tenant,
                aggregate_revision=1,
                functional_identity_hash="c" * 64,
                title="Affaire synthétique RC",
                object_description=None,
                business_origin="OPPORTUNITY",
                origin_reference_id=None,
                origin_rationale=None,
                consultation_id=dce.consultation_id,
                scope_kind="CUSTOM",
                scope_json={},
                scope_fingerprint="d" * 64,
                applicable_dce_version_id=version,
                lifecycle="ACTIVE",
                commercial_stage="ANALYSIS",
                decision_readiness="NOT_ASSESSED",
                dce_freshness="CURRENT",
                responsibility_status="UNASSIGNED",
                created_by_actor_id=None,
                updated_by_actor_id=None,
            )
        )

    class Runtime:
        def get_case_tenant_id(self, *, case_id):
            with session_factory() as session:
                return session.scalar(
                    sa.select(CaseRecord.tenant_id).where(CaseRecord.id == case_id)
                )

        def get_case_dce_reading(self, *, tenant_id, case_id):
            with session_factory() as session:
                return SqlAlchemyCaseDceReadingReader(session).get(
                    tenant_id=tenant_id, case_id=case_id
                )

    def client_for(actor_tenant):
        class Resolver:
            def resolve(self, *, access_token):
                return replace(
                    _Resolver().resolve(access_token=access_token), tenant_id=actor_tenant
                )

        app = FastAPI()
        app.include_router(
            build_case_dce_reading_router(
                runtime=Runtime(),
                security_runtime=ConsultationSecurityRuntime(
                    context_resolver=Resolver(), policy=_Policy(_Decision(True))
                ),
            )
        )
        return TestClient(app, raise_server_exceptions=False)

    client = client_for(tenant)
    response = client.get(
        f"/api/v1/cases/{case_id}/dce-reading",
        headers=_headers(),
        params={"tenant_id": str(uuid4())},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["dce"]["dce_version_id"] == str(version)
    requirement = body["requirements"][0]
    candidate = requirement["structured_candidate"]
    assert candidate["date_iso"] == "2034-11-21" and candidate["time_local"] == "10:30"
    assert candidate["timezone_state"] == candidate["applicability"] == "UNKNOWN"
    assert candidate["lot_numbers"] == [2]
    assert candidate["source_fragment_id"] == requirement["source_anchor"]["source_anchor_id"]
    assert body["coverage"]["analysis_complete"] is False
    assert body == client.get(f"/api/v1/cases/{case_id}/dce-reading", headers=_headers()).json()
    foreign = client_for(uuid4()).get(f"/api/v1/cases/{case_id}/dce-reading", headers=_headers())
    assert foreign.status_code == 404 and foreign.json() == {"detail": "NOT_FOUND_OR_FORBIDDEN"}
