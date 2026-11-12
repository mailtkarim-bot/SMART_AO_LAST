import stat
from io import BytesIO
from zipfile import ZipFile, ZipInfo

import pytest
from app.modules.dce.application.extraction import _project_document


def zip_bytes(entries):
    out = BytesIO()
    with ZipFile(out, "w") as archive:
        for name, data in entries:
            archive.writestr(name, data)
    return out.getvalue()


def test_nested_archive_is_inventoried_without_admission_or_rag_fragments():
    source = zip_bytes([("same.txt", b"one"), ("nested.zip", zip_bytes([("inner.txt", b"two")]))])
    projection = _project_document(media_type="application/zip", source_bytes=source)
    assert projection.fragments == ()
    assert projection.status == "UNSUPPORTED"
    assert projection.failure_code == "ARCHIVE_MEMBERS_NOT_ADMITTED"
    entries = projection.archive_entries
    assert [tuple(x.entry_path) for x in entries] == [(1,), (2,), (2, 1)]
    assert [x.state for x in entries] == ["NOT_EXTRACTED", "NESTED_ARCHIVE", "NOT_EXTRACTED"]
    assert all(x.entry_sha256 for x in entries)


def test_archive_unsafe_and_symlink_entries_stay_excluded():
    link = ZipInfo("link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    projection = _project_document(
        media_type="application/zip",
        source_bytes=zip_bytes(
            [("../outside.txt", b"secret"), (link, b"target"), ("C:\\danger.txt", b"secret")]
        ),
    )
    assert [x.state for x in projection.archive_entries] == [
        "EXCLUDED_UNSAFE",
        "EXCLUDED_SYMLINK",
        "EXCLUDED_UNSAFE",
    ]
    assert not projection.fragments
    assert all(x.entry_sha256 is None for x in projection.archive_entries)


def test_archive_corruption_and_limits_never_disappear(monkeypatch):
    import app.modules.dce.application.archive_inventory as module

    broken = _project_document(media_type="application/zip", source_bytes=b"not a zip")
    assert broken.archive_entries[0].state == "UNREADABLE"
    monkeypatch.setattr(module, "MAX_ARCHIVE_ENTRIES", 1)
    projection = _project_document(
        media_type="application/zip", source_bytes=zip_bytes([("a.txt", b"a"), ("b.txt", b"b")])
    )
    assert projection.archive_entries[-1].state == "INVENTORY_LIMIT"
    assert len(projection.archive_entries) <= 2
    assert not projection.fragments


@pytest.mark.parametrize("name", ["a.zip", "a.ZIP"])
def test_nested_depth_limit_is_explicit(monkeypatch, name):
    import app.modules.dce.application.archive_inventory as module

    monkeypatch.setattr(module, "MAX_ARCHIVE_DEPTH", 0)
    result = _project_document(
        media_type="application/zip",
        source_bytes=zip_bytes([(name, zip_bytes([("hidden.txt", b"x")]))]),
    )
    assert result.archive_entries[0].state == "EXCLUDED_LIMIT"


def test_archive_anchor_rejects_boolean_ordinals():
    from app.modules.dce.application.commands import DceArchiveEntryInput
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        DceArchiveEntryInput(entry_path=[True], state="NOT_EXTRACTED")


def test_nested_failures_cannot_overflow_inventory_budget(monkeypatch):
    import app.modules.dce.application.archive_inventory as module

    monkeypatch.setattr(module, "MAX_ARCHIVE_ENTRIES", 1)
    result = _project_document(
        media_type="application/zip",
        source_bytes=zip_bytes([("bad.zip", b"bad"), ("another.txt", b"x")]),
    )
    assert len(result.archive_entries) <= 2
    assert result.archive_entries[-1].state == "INVENTORY_LIMIT"


def test_legacy_extraction_request_hash_does_not_change_when_inventory_is_absent():
    from types import SimpleNamespace
    from uuid import uuid4

    from app.modules.dce.application.commands import RecordDceDocumentExtractionCommand
    from app.platform.events.dispatcher import canonical_request_hash

    command = RecordDceDocumentExtractionCommand(
        command_id=uuid4(),
        idempotency_key=uuid4(),
        extraction_id=uuid4(),
        dce_document_id=uuid4(),
        input_sha256="a" * 64,
        extractor_id="smart-ao-deterministic",
        extractor_version="2",
        status="UNSUPPORTED",
        extracted_char_count=0,
        failure_code="MEDIA_TYPE_UNSUPPORTED",
    )
    payload = command.model_dump(mode="json")
    payload.pop("archive_entries", None)
    legacy = SimpleNamespace(command_type=command.command_type, model_dump=lambda **kwargs: payload)
    assert canonical_request_hash(command) == canonical_request_hash(legacy)
    assert "archive_entries" not in command.model_dump(mode="json")


def test_corrupt_member_still_consumes_the_read_budget(monkeypatch):
    import app.modules.dce.application.archive_inventory as module

    monkeypatch.setattr(module, "MAX_ARCHIVE_EXPANDED_BYTES", 8, raising=False)
    source = zip_bytes([("bad.txt", b"12345678"), ("good.txt", b"abcdefgh")])
    result = _project_document(
        media_type="application/zip",
        source_bytes=source.replace(b"12345678", b"87654321", 1),
    )
    assert result.archive_entries[0].state == "UNREADABLE"
    assert result.archive_entries[1].state == "EXCLUDED_LIMIT"


def test_encrypted_and_corrupt_members_are_not_read_or_promoted():
    import struct

    source = bytearray(zip_bytes([("private.txt", b"body")]))
    struct.pack_into("<H", source, 6, 1)
    central = source.index(b"PK\x01\x02")
    struct.pack_into("<H", source, central + 8, 1)
    result = _project_document(media_type="application/zip", source_bytes=bytes(source))
    assert result.archive_entries[0].state == "EXCLUDED_ENCRYPTED"
    assert result.archive_entries[0].entry_sha256 is None
    assert not result.fragments


@pytest.mark.parametrize("method", [8, 12, 14])
def test_forged_uncompressed_sizes_cannot_bypass_actual_output_limits(method, monkeypatch):
    import struct

    import app.modules.dce.application.archive_inventory as module

    out = BytesIO()
    with ZipFile(out, "w", compression=method) as archive:
        archive.writestr("hostile.txt", b"A" * (2 * 1024 * 1024))
    data = bytearray(out.getvalue())
    central = data.index(b"PK\x01\x02")
    import zlib

    crc = zlib.crc32(b"A")
    struct.pack_into("<I", data, 14, crc)
    struct.pack_into("<I", data, 22, 1)
    struct.pack_into("<I", data, central + 16, crc)
    struct.pack_into("<I", data, central + 24, 1)
    monkeypatch.setattr(module, "MAX_ARCHIVE_MEMBER_BYTES", 4096)
    result = _project_document(media_type="application/zip", source_bytes=bytes(data))
    assert result.archive_entries[0].state in {
        "EXCLUDED_LIMIT",
        "EXCLUDED_COMPRESSION",
        "UNREADABLE",
    }
    assert result.archive_entries[0].entry_sha256 is None
    assert not result.fragments


def test_central_directory_is_bounded_before_zipinfo_allocation(monkeypatch):
    import app.modules.dce.application.archive_inventory as module

    source = zip_bytes([("a", b"a"), ("b", b"b")])
    monkeypatch.setattr(module, "MAX_ARCHIVE_ENTRIES", 1)

    def forbidden(*args, **kwargs):
        raise AssertionError("ZipFile must not allocate oversized central directory")

    monkeypatch.setattr(module, "ZipFile", forbidden)
    result = _project_document(media_type="application/zip", source_bytes=source)
    assert result.archive_entries[0].state == "INVENTORY_LIMIT"


def test_decoder_error_is_charged_conservatively_to_the_work_budget(monkeypatch):
    import zlib

    import app.modules.dce.application.archive_inventory as module

    out = BytesIO()
    with ZipFile(out, "w", compression=8) as archive:
        archive.writestr("first", b"A")
        archive.writestr("second", b"B")
    monkeypatch.setattr(module, "MAX_ARCHIVE_EXPANDED_BYTES", 128)
    monkeypatch.setattr(module, "MAX_ARCHIVE_MEMBER_BYTES", 128)

    class FailedDecoder:
        def decompress(self, *args):
            raise zlib.error("synthetic decoder failure")

    monkeypatch.setattr(module.zlib, "decompressobj", lambda *args: FailedDecoder())
    result = _project_document(media_type="application/zip", source_bytes=out.getvalue())
    assert [entry.state for entry in result.archive_entries] == ["UNREADABLE", "EXCLUDED_LIMIT"]


def test_zip64_locator_is_refused_before_stdlib_directory_override(monkeypatch):
    import app.modules.dce.application.archive_inventory as module

    info = ZipInfo("entry")
    info.comment = b"PK\x06\x07" + b"\x00" * 16
    source = zip_bytes([(info, b"one")])

    def forbidden(*args, **kwargs):
        raise AssertionError("ZIP64 locator must be refused before ZipFile")

    monkeypatch.setattr(module, "ZipFile", forbidden)
    result = _project_document(media_type="application/zip", source_bytes=source)
    assert result.archive_entries[0].state == "INVENTORY_LIMIT"
