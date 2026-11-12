"""Bounded ZIP inventory only: no filesystem extraction, content admission or RAG text."""

import stat
import struct
import zlib
from hashlib import sha256
from io import BytesIO
from pathlib import PurePosixPath
from zipfile import ZIP_DEFLATED, ZIP_STORED, BadZipFile, ZipFile, ZipInfo

from app.modules.dce.application.commands import DceArchiveEntryInput

MAX_ARCHIVE_BYTES = 16 * 1024 * 1024
MAX_ARCHIVE_EXPANDED_BYTES = 16 * 1024 * 1024
MAX_ARCHIVE_MEMBER_BYTES = 8 * 1024 * 1024
MAX_ARCHIVE_ENTRIES = 1000
MAX_ARCHIVE_DEPTH = 3
MAX_COMPRESSION_RATIO = 200


def _central_directory_start(data: bytes, remaining_entries: int) -> int:
    # PKWARE APPNOTE 4.3.12/4.3.16; reject unsupported ZIP64/multidisk layouts.
    end = data.rfind(b"PK\x05\x06", max(0, len(data) - 65557))
    if end < 0 or end + 22 > len(data):
        raise BadZipFile("invalid directory")
    disk, central_disk, disk_count, count, size, offset, comment = struct.unpack_from(
        "<4H2IH",
        data,
        end + 4,
    )
    if end + 22 + comment != len(data) or disk or central_disk or disk_count != count:
        raise BadZipFile("unsupported directory")
    if end >= 20 and data[end - 20 : end - 16] == b"PK\x06\x07":
        raise OverflowError("unsupported ZIP64 locator")
    if count == 65535 or size == 0xFFFFFFFF or offset == 0xFFFFFFFF:
        raise OverflowError("unsupported ZIP64")
    if count > remaining_entries or size > 1024 * 1024:
        raise OverflowError("directory limit")
    start = end - size
    if start < 0 or offset != start:
        raise BadZipFile("unsupported directory offset")
    cursor, actual = start, 0
    while cursor < end:
        if cursor + 46 > end or data[cursor : cursor + 4] != b"PK\x01\x02":
            raise BadZipFile("invalid directory record")
        name, extra, entry_comment = struct.unpack_from("<3H", data, cursor + 28)
        cursor += 46 + name + extra + entry_comment
        actual += 1
        if actual > remaining_entries:
            raise OverflowError("directory limit")
    if cursor != end or actual != count:
        raise BadZipFile("directory count mismatch")
    return start


def _read_member(
    data: bytes,
    info: ZipInfo,
    directory_start: int,
    budget: int,
) -> tuple[bytes | None, int, str]:
    """Count actual output before metadata truncation; never call ZipExtFile.read."""
    charge = info.compress_size
    try:
        header = info.header_offset
        if (
            header < 0
            or header + 30 > directory_start
            or data[header : header + 4] != b"PK\x03\x04"
        ):
            raise BadZipFile("invalid local header")
        flags, method = struct.unpack_from("<2H", data, header + 6)
        name_size, extra_size = struct.unpack_from("<2H", data, header + 26)
        start = header + 30 + name_size + extra_size
        end = start + info.compress_size
        if flags != info.flag_bits or method != info.compress_type or end > directory_start:
            raise BadZipFile("discordant local header")
        name = data[header + 30 : header + 30 + name_size].decode(
            "utf-8" if flags & 0x800 else "cp437",
        )
        if name != info.orig_filename:
            raise BadZipFile("discordant local name")
        compressed = data[start:end]
        if method == ZIP_STORED:
            member = compressed
        else:
            decoder = zlib.decompressobj(-15)
            member = decoder.decompress(compressed, budget + 1)
            charge = max(charge, len(member))
            if len(member) > budget or decoder.unconsumed_tail:
                return None, charge, "EXCLUDED_LIMIT"
            if not decoder.eof or decoder.unused_data:
                raise BadZipFile("incomplete compressed stream")
        charge = max(charge, len(member))
        if len(member) > budget:
            return None, charge, "EXCLUDED_LIMIT"
        if len(member) != info.file_size or zlib.crc32(member) != info.CRC:
            raise BadZipFile("discordant member size or CRC")
        return member, charge, "NOT_EXTRACTED"
    except zlib.error:
        # Output before an error is unavailable, so charge the full allowed attempt.
        return None, max(charge, budget), "UNREADABLE"
    except (ValueError, BadZipFile, UnicodeError, struct.error):
        return None, charge, "UNREADABLE"


def inventory_zip(source_bytes: bytes) -> tuple[DceArchiveEntryInput, ...]:
    rows: list[DceArchiveEntryInput] = []
    consumed = 0
    halted = False

    def record(row: DceArchiveEntryInput) -> None:
        nonlocal halted
        if halted:
            return
        if len(rows) >= MAX_ARCHIVE_ENTRIES:
            rows.append(DceArchiveEntryInput(entry_path=row.entry_path, state="INVENTORY_LIMIT"))
            halted = True
        else:
            rows.append(row)

    def visit(data: bytes, parent: list[int], depth: int) -> None:
        nonlocal consumed, halted
        if len(data) > MAX_ARCHIVE_BYTES:
            record(DceArchiveEntryInput(entry_path=parent, state="INVENTORY_LIMIT"))
            halted = True
            return
        try:
            directory_start = _central_directory_start(data, MAX_ARCHIVE_ENTRIES - len(rows))
            with ZipFile(BytesIO(data)) as archive:
                for ordinal, info in enumerate(archive.infolist(), 1):
                    if halted:
                        return
                    if len(rows) >= MAX_ARCHIVE_ENTRIES:
                        record(DceArchiveEntryInput(entry_path=parent, state="INVENTORY_LIMIT"))
                        halted = True
                        return
                    path = [*parent, ordinal]
                    name = info.orig_filename
                    name_hash = sha256(name.encode("utf-8", errors="surrogatepass")).hexdigest()
                    nested = name.lower().endswith(".zip")
                    state = "NOT_EXTRACTED"
                    if (
                        "\\" in name
                        or ":" in name
                        or "\x00" in name
                        or PurePosixPath(name).is_absolute()
                        or ".." in PurePosixPath(name).parts
                    ):
                        state = "EXCLUDED_UNSAFE"
                    elif stat.S_ISLNK(info.external_attr >> 16):
                        state = "EXCLUDED_SYMLINK"
                    elif info.flag_bits & 1:
                        state = "EXCLUDED_ENCRYPTED"
                    elif info.is_dir():
                        state = "DIRECTORY"
                    elif info.compress_type not in {ZIP_STORED, ZIP_DEFLATED}:
                        state = "EXCLUDED_COMPRESSION"
                    elif (
                        max(info.file_size, info.compress_size) > MAX_ARCHIVE_MEMBER_BYTES
                        or consumed + max(info.file_size, info.compress_size)
                        > MAX_ARCHIVE_EXPANDED_BYTES
                        or info.file_size > max(1, info.compress_size) * MAX_COMPRESSION_RATIO
                        or (nested and depth >= MAX_ARCHIVE_DEPTH)
                    ):
                        state = "EXCLUDED_LIMIT"
                    member = None
                    if state == "NOT_EXTRACTED":
                        remaining = min(
                            MAX_ARCHIVE_MEMBER_BYTES, MAX_ARCHIVE_EXPANDED_BYTES - consumed
                        )
                        member, charge, state = _read_member(data, info, directory_start, remaining)
                        consumed += charge
                    if member is not None and (nested or member.startswith(b"PK\x03\x04")):
                        state = "EXCLUDED_LIMIT" if depth >= MAX_ARCHIVE_DEPTH else "NESTED_ARCHIVE"
                    record(
                        DceArchiveEntryInput(
                            entry_path=path,
                            entry_name_sha256=name_hash,
                            entry_sha256=sha256(member).hexdigest() if member is not None else None,
                            state=state,
                        )
                    )
                    if state == "NESTED_ARCHIVE" and member is not None:
                        visit(member, path, depth + 1)
        except OverflowError:
            record(DceArchiveEntryInput(entry_path=parent, state="INVENTORY_LIMIT"))
            halted = True
        except (OSError, ValueError, BadZipFile, NotImplementedError, EOFError, struct.error):
            record(DceArchiveEntryInput(entry_path=parent, state="UNREADABLE"))

    visit(source_bytes, [], 0)
    # An empty archive is still not evidence of a complete DCE.
    if not rows:
        rows.append(DceArchiveEntryInput(entry_path=[], state="DIRECTORY"))
    return tuple(rows)
