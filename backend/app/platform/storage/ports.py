"""Framework-neutral ports owned by the platform shared kernel."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class GeneratedDocumentStorage(Protocol):
    """Port for private generated-document bytes."""

    def write(self, *, storage_key: str, content: bytes) -> str:
        """Persist bytes at a private key and return their SHA-256 digest."""
        ...

    def read(self, *, storage_key: str) -> bytes:
        """Read bytes from a private key."""
        ...


@runtime_checkable
class BoundedPrivateStorage(Protocol):
    """Read one private artifact without allocating beyond the caller's byte limit."""

    def read_bounded(self, *, storage_key: str, max_bytes: int) -> bytes: ...
