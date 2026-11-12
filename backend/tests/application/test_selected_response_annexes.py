from uuid import uuid4

import pytest
from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter
from app.modules.preparation.application.transmission_commands import (
    CreatePreparationSnapshotCommand,
)
from app.modules.preparation.public.contracts import CreatePreparationSnapshotRequest
from pydantic import ValidationError


def _body():
    return dict(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        package_id=uuid4(),
        snapshot_id=uuid4(),
        expected_package_revision=1,
        selected_response_draft=dict(draft_id=uuid4(), version=1, content_sha256="a" * 64),
    )


def test_exact_annex_selection_is_preserved_in_the_command_and_not_in_legacy_hashes():
    body = _body()
    chosen = dict(requirement_id=uuid4(), document_id=uuid4(), sha256="b" * 64)
    request = CreatePreparationSnapshotRequest(
        **body, selected_annexes=[chosen], annex_justification="Pièce nécessaire à cette exigence."
    )
    command = CreatePreparationSnapshotCommand(**request.model_dump())
    assert command.model_dump(mode="json")["selected_annexes"][0]["document_id"] == str(
        chosen["document_id"]
    )
    assert "selected_annexes" not in CreatePreparationSnapshotCommand(**body).model_dump(
        mode="json"
    )
    assert "selected_annexes" not in CreatePreparationSnapshotCommand(
        **body, selected_annexes=[]
    ).model_dump(mode="json")


def test_annexes_require_a_response_and_unique_requirement_document_pairs():
    body = _body()
    chosen = dict(requirement_id=uuid4(), document_id=uuid4(), sha256="b" * 64)
    with pytest.raises(ValidationError):
        CreatePreparationSnapshotRequest(**body, selected_annexes=[chosen, chosen])
    body.pop("selected_response_draft")
    with pytest.raises(ValidationError):
        CreatePreparationSnapshotRequest(**body, selected_annexes=[chosen])


def test_private_binary_read_is_bounded_and_refuses_symlinks(tmp_path):
    storage = LocalQuarantineStorageAdapter(root=tmp_path)
    path = tmp_path / "proof.pdf"
    path.write_bytes(b"synthetic proof")
    assert hasattr(storage, "read_verified_bytes"), "Bounded source bytes are missing"
    assert storage.read_verified_bytes(storage_key="proof.pdf", max_bytes=16) == b"synthetic proof"
    with pytest.raises(ValueError):
        storage.read_verified_bytes(storage_key="proof.pdf", max_bytes=3)
    link = tmp_path / "link"
    link.symlink_to(path)
    with pytest.raises(ValueError):
        storage.read_verified_bytes(storage_key="link", max_bytes=16)
    with pytest.raises(ValueError):
        storage.read_verified_bytes(storage_key="../outside", max_bytes=16)


def test_annex_selection_requires_human_justification():
    with pytest.raises(ValidationError):
        CreatePreparationSnapshotRequest(
            **_body(),
            selected_annexes=[dict(requirement_id=uuid4(), document_id=uuid4(), sha256="b" * 64)],
        )


def test_annex_justification_does_not_import_financial_data_into_shared_preparation():
    with pytest.raises(ValidationError):
        CreatePreparationSnapshotRequest(
            **_body(),
            selected_annexes=[dict(requirement_id=uuid4(), document_id=uuid4(), sha256="b" * 64)],
            annex_justification="Budget et marge de 20 %.",
        )


def test_frozen_copy_is_read_with_a_bound_before_hash_validation():
    from hashlib import sha256
    from types import SimpleNamespace

    from app.modules.preparation.infrastructure.annexes import frozen_annex_bytes
    from app.platform.events.dispatcher import CommandExecutionError

    expected = b"PDF"
    item = dict(
        document_id=str(uuid4()),
        sha256=sha256(expected).hexdigest(),
        byte_size=3,
        media_type="application/pdf",
        signature="UNKNOWN",
    )
    item["archive_path"] = f"annexes/{item['document_id']}.pdf"
    seen = []

    def forbidden_read(**kwargs):
        pytest.fail("Unbounded private read")

    def bounded_read(*, storage_key, max_bytes):
        seen.append(max_bytes)
        return expected

    storage = SimpleNamespace(read=forbidden_read, read_bounded=bounded_read)
    assert (
        frozen_annex_bytes(
            storage, tenant_id=uuid4(), package_id=uuid4(), snapshot_id=uuid4(), item=item
        )
        == expected
    )
    assert seen == [3]
    item["byte_size"] = 150_000_001
    with pytest.raises(CommandExecutionError):
        frozen_annex_bytes(
            storage, tenant_id=uuid4(), package_id=uuid4(), snapshot_id=uuid4(), item=item
        )


def test_rib_citation_never_permits_reading_or_exporting_private_bytes(monkeypatch):
    from datetime import UTC, datetime
    from types import SimpleNamespace

    from app.modules.preparation.infrastructure import annexes
    from app.modules.preparation.public.contracts import SelectedResponseAnnex
    from app.platform.events.dispatcher import CommandExecutionError

    requirement, document, tenant, package = uuid4(), uuid4(), uuid4(), uuid4()
    selected = SelectedResponseAnnex(
        requirement_id=requirement, document_id=document, sha256="a" * 64
    )
    monkeypatch.setattr(
        annexes, "read_response_coverage", lambda *a, **k: SimpleNamespace(cited_annexes=[selected])
    )

    def no_bytes(**kwargs):
        pytest.fail("RIB bytes must not be read")

    review = SimpleNamespace(
        current_response_plan=lambda **k: (None, None),
        reread_response_plan_sources=lambda **k: None,
        read_source_document_bytes=no_bytes,
    )
    row = (
        SimpleNamespace(
            document_kind="RIB", verification_status="VALIDATED", sha256="a" * 64, expires_at=None
        ),
        SimpleNamespace(
            state="CLEAN", scan_verdict="CLEAN", media_type="application/pdf", sha256="a" * 64
        ),
    )
    session = SimpleNamespace(execute=lambda *a, **k: SimpleNamespace(one_or_none=lambda: row))
    with pytest.raises(CommandExecutionError, match="ANNEX_SOURCE_UNKNOWN"):
        annexes.selected_annex_manifest(
            session,
            package=SimpleNamespace(id=package, tenant_id=tenant),
            selections=[selected],
            response={},
            context=SimpleNamespace(received_at=datetime.now(UTC)),
            storage=object(),
            review=review,
        )
