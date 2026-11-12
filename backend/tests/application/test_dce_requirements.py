# ruff: noqa: F401, F811
from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID, uuid4

import pytest
import sqlalchemy as sa
from app.modules.dce.application.handlers import RecordDceRequirementMaterializationRunHandler
from app.modules.dce.application.requirements import (
    DceRequirementsService,
    project_requirements,
    recording_command,
)
from app.modules.dce.infrastructure.models.dce_requirements import (
    DceRequirementMaterializationRunRecord,
    DceRequirementRecord,
)
from app.platform.events.dispatcher import (
    CommandContext,
    CommandDispatcher,
    CommandExecutionError,
)

sys.path.append(str(Path(__file__).parent))

from test_dce_rc_analysis import (
    NOW,
    _extract_then_analyze,
    _seed_admitted_document,
    isolate_rc_analysis_records,
)


@pytest.mark.db
@pytest.mark.integration
def test_materialization_handler_rejects_preconditions_manifest_projection_and_mapping(
    session_factory, tmp_path: Path
) -> None:
    from app.modules.dce.infrastructure.models.dce_version import DceVersionRecord
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant_id, document_id, dce_version_id = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=(
            "Le DC1 est obligatoire. Le mémoire technique est obligatoire. "
            "Le dépôt électronique se fait sur le profil d'acheteur."
        ).encode(),
    )
    analysis = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant_id,
        document_id=document_id,
        dce_version_id=dce_version_id,
    )
    analysis_id = UUID(analysis.aggregate_refs[0]["aggregate_id"])
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
    signals = service._load_signals(  # noqa: SLF001
        tenant_id=tenant_id,
        dce_version_id=dce_version_id,
        dce_rc_analysis_id=analysis_id,
    )
    command = recording_command(
        dce_version_id=dce_version_id,
        dce_rc_analysis_id=analysis_id,
        projection=project_requirements(signals=signals),
    )
    dispatcher = service._dispatcher  # noqa: SLF001

    with pytest.raises(CommandExecutionError) as actor_failure:
        dispatcher.dispatch(
            command=command,
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="USER", received_at=NOW
            ),
        )
    assert str(actor_failure.value.__cause__) == "DCE_REQUIREMENT_SYSTEM_ACTOR_REQUIRED"

    with session_factory.begin() as session:
        version = session.get(DceVersionRecord, dce_version_id)
        assert version is not None
        version.integrity = "PARTIAL"
    with pytest.raises(CommandExecutionError) as version_failure:
        dispatcher.dispatch(
            command=command.model_copy(update={"command_id": uuid4(), "idempotency_key": uuid4()}),
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
            ),
        )
    assert str(version_failure.value.__cause__) == "DCE_VERSION_NOT_REQUIREMENTS_READY"
    with session_factory.begin() as session:
        version = session.get(DceVersionRecord, dce_version_id)
        assert version is not None
        version.integrity = "VERIFIED"

    with pytest.raises(CommandExecutionError) as analysis_failure:
        dispatcher.dispatch(
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "dce_rc_analysis_id": uuid4(),
                }
            ),
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
            ),
        )
    assert str(analysis_failure.value.__cause__) == "DCE_RC_ANALYSIS_COMPLETED_REQUIRED"

    with pytest.raises(CommandExecutionError) as manifest_failure:
        dispatcher.dispatch(
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "input_manifest_sha256": "f" * 64,
                }
            ),
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
            ),
        )
    assert str(manifest_failure.value.__cause__) == "DCE_REQUIREMENT_INPUT_MANIFEST_REQUIRED"

    with pytest.raises(CommandExecutionError) as count_failure:
        dispatcher.dispatch(
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "source_observation_count": command.source_observation_count + 1,
                }
            ),
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
            ),
        )
    assert str(count_failure.value.__cause__) == "DCE_REQUIREMENT_SOURCE_COUNT_REQUIRED"

    wrong_type = (
        "SITE_VISIT"
        if command.requirements[0].requirement_type != "SITE_VISIT"
        else "NEGOTIATION_SIGNAL"
    )
    mapped = command.requirements[0].model_copy(update={"requirement_type": wrong_type})
    with pytest.raises(CommandExecutionError) as mapping_failure:
        dispatcher.dispatch(
            command=command.model_copy(
                update={
                    "command_id": uuid4(),
                    "idempotency_key": uuid4(),
                    "requirements": [mapped, *command.requirements[1:]],
                }
            ),
            context=CommandContext(
                tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
            ),
        )
    assert str(mapping_failure.value.__cause__) == "DCE_REQUIREMENT_MAPPING_REQUIRED"

    first = dispatcher.dispatch(
        command=command,
        context=CommandContext(
            tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
        ),
    )
    replay = dispatcher.dispatch(
        command=command.model_copy(
            update={
                "command_id": uuid4(),
                "idempotency_key": uuid4(),
                "requirements_run_id": uuid4(),
            }
        ),
        context=CommandContext(
            tenant_id=tenant_id, actor_id=uuid4(), actor_kind="SYSTEM", received_at=NOW
        ),
    )
    assert first.result_code == "DCE_REQUIREMENTS_MATERIALIZED"
    assert replay.result_code == "DCE_REQUIREMENTS_ALREADY_MATERIALIZED"


@pytest.mark.db
@pytest.mark.integration
def test_requirements_are_atomic_sourced_immutable_and_replayed(
    session_factory, tmp_path: Path
) -> None:
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant_id, document_id, dce_version_id = _seed_admitted_document(
        session_factory,
        storage=storage,
        source_bytes=(
            "Le DC1 est obligatoire. Le mémoire technique est obligatoire. "
            "Le dépôt électronique se fait sur le profil d'acheteur."
        ).encode(),
    )
    analysis = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant_id,
        document_id=document_id,
        dce_version_id=dce_version_id,
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

    first = service.materialize(
        tenant_id=tenant_id,
        dce_version_id=dce_version_id,
        dce_rc_analysis_id=analysis.aggregate_refs[0]["aggregate_id"],
        now=NOW,
    )
    replay = service.materialize(
        tenant_id=tenant_id,
        dce_version_id=dce_version_id,
        dce_rc_analysis_id=analysis.aggregate_refs[0]["aggregate_id"],
        now=NOW,
    )

    assert first.result_code == "DCE_REQUIREMENTS_MATERIALIZED"
    assert replay.result_code == "DCE_REQUIREMENTS_MATERIALIZED"
    with session_factory() as session:
        requirements = list(session.scalars(sa.select(DceRequirementRecord)))
        run = session.scalar(sa.select(DceRequirementMaterializationRunRecord))
    assert run is not None
    assert {item.requirement_type for item in requirements} == {
        "CANDIDATURE_DOCUMENT",
        "OFFER_DOCUMENT",
        "SUBMISSION_CHANNEL",
    }
    assert {item.confirmation_status for item in requirements} == {"PENDING_HUMAN_CONFIRMATION"}
    with pytest.raises(sa.exc.DBAPIError), session_factory.begin() as session:
        requirement = session.get(DceRequirementRecord, requirements[0].id)
        assert requirement is not None
        requirement.confirmation_status = "CONFIRMED"


@pytest.mark.parametrize(
    "case",
    json.loads(
        (Path(__file__).parents[1] / "fixtures/rc_requirements_holdout_v1.json").read_text()
    )["cases"],
    ids=lambda x: x["id"],
)
def test_rc_holdout_extraction_analysis_and_materialization_keep_every_clause(
    session_factory, tmp_path, case
):
    from collections import Counter
    from hashlib import sha256

    from app.modules.dce.infrastructure.models.dce_extraction import (
        DceDocumentExtractionFragmentRecord,
    )
    from app.modules.dce.infrastructure.models.dce_rc_analysis import (
        DceRcRequirementObservationRecord,
        DceRcRequirementSourceRecord,
    )
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=case["text"].encode()
    )
    analysis = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant,
        document_id=document,
        dce_version_id=version,
    )
    analysis_id = analysis.aggregate_refs[0]["aggregate_id"]
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
    first = service.materialize(
        tenant_id=tenant, dce_version_id=version, dce_rc_analysis_id=analysis_id, now=NOW
    )
    replay = service.materialize(
        tenant_id=tenant, dce_version_id=version, dce_rc_analysis_id=analysis_id, now=NOW
    )
    assert first.result_code == "DCE_REQUIREMENTS_MATERIALIZED" and replay.replayed
    with session_factory() as session:
        requirements = list(
            session.scalars(
                sa.select(DceRequirementRecord).where(DceRequirementRecord.tenant_id == tenant)
            )
        )
        actual = []
        for requirement in requirements:
            observation = session.get(
                DceRcRequirementObservationRecord, requirement.source_observation_id
            )
            source = session.scalar(
                sa.select(DceRcRequirementSourceRecord).where(
                    DceRcRequirementSourceRecord.observation_id == observation.id
                )
            )
            fragment = session.get(DceDocumentExtractionFragmentRecord, source.fragment_id)
            assert sha256(fragment.text.encode()).hexdigest() == fragment.text_sha256
            assert (
                fragment.text.encode()[source.start_byte_offset : source.end_byte_offset].decode()
                == observation.excerpt
            )
            assert requirement.confirmation_status == "PENDING_HUMAN_CONFIRMATION"
            assert requirement.uncertainty_status == "SOURCE_SIGNAL_ONLY"
            assert requirement.directive_signal == observation.directive
            assert observation.rule_version == "11"
            actual.append(
                (observation.requirement_kind, observation.directive, observation.excerpt.strip())
            )
        assert Counter(actual) == Counter(tuple(x) for x in case["expected"])
    with pytest.raises(ValueError, match="DCE_VERSION_NOT_REQUIREMENTS_READY"):
        service.materialize(
            tenant_id=uuid4(), dce_version_id=version, dce_rc_analysis_id=analysis_id, now=NOW
        )


@pytest.mark.parametrize(
    "text,status",
    [
        ("Si le lot 2 est retenu :\n- Le mémoire technique est obligatoire.", "FAILED_SAFE"),
        ("Si " + "contexte " * 160 + "le mémoire technique est obligatoire.", "REJECTED_LIMIT"),
    ],
)
def test_unproven_rc_context_never_materializes_partial_obligations(
    session_factory, tmp_path, text, status
):
    from app.modules.dce.infrastructure.models.dce_rc_analysis import DceRcAnalysisRunRecord
    from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter

    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    tenant, document, version = _seed_admitted_document(
        session_factory, storage=storage, source_bytes=text.encode()
    )
    result = _extract_then_analyze(
        session_factory=session_factory,
        storage=storage,
        tenant_id=tenant,
        document_id=document,
        dce_version_id=version,
    )
    analysis_id = result.aggregate_refs[0]["aggregate_id"]
    with session_factory() as session:
        run = session.get(DceRcAnalysisRunRecord, UUID(str(analysis_id)))
        assert run.status == status
        assert session.scalar(sa.select(sa.func.count()).select_from(DceRequirementRecord)) == 0
    service = DceRequirementsService(
        session_factory=session_factory,
        dispatcher=CommandDispatcher(session_factory=session_factory, handlers={}),
    )
    with pytest.raises(ValueError, match="DCE_RC_ANALYSIS_COMPLETED_REQUIRED"):
        service.materialize(
            tenant_id=tenant, dce_version_id=version, dce_rc_analysis_id=analysis_id, now=NOW
        )


def test_profile_url_survives_the_complete_rc_materialization_chain(session_factory, tmp_path):
    quote = (
        "Le dépôt électronique se fait via le profil d'acheteur "
        "https://plateforme.test/depot?lot=2."
    )
    test_rc_holdout_extraction_analysis_and_materialization_keep_every_clause(
        session_factory,
        tmp_path,
        {"text": quote, "expected": [["RC_RESPONSE_CHANNEL", "UNSPECIFIED", quote]]},
    )


def test_independent_negation_does_not_block_persisted_offer_requirement(session_factory, tmp_path):
    quote = "- Le mémoire technique est obligatoire."
    text = "Le candidat ne doit pas remettre de papier. Contenu de l'offre :\n" + quote
    test_rc_holdout_extraction_analysis_and_materialization_keep_every_clause(
        session_factory,
        tmp_path,
        {"text": text, "expected": [["RC_CONTENT_OFFER", "REQUIRED_SIGNAL", quote]]},
    )
