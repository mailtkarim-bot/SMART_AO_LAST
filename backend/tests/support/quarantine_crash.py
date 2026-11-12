from __future__ import annotations

import os
import select
import signal
import subprocess
import sys
from pathlib import Path

_WRITER = r"""
import asyncio
import os
import sys
import time
from pathlib import Path

from app.modules.dce.infrastructure.quarantine import LocalQuarantineStorageAdapter

root, storage_key, signal_fd, phase = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]

async def content():
    yield b"%PDF-1.7\ncrash-recovery fixture\n"
    if phase == "during-write":
        os.write(signal_fd, b"R")
        await asyncio.Event().wait()

async def main():
    storage = LocalQuarantineStorageAdapter(root=Path(root))
    await storage.write(storage_key=storage_key, stream=content(), max_bytes=4096)

asyncio.run(main())
if phase == "after-rename":
    os.write(signal_fd, b"R")
    while True:
        time.sleep(1)
"""


def kill_local_quarantine_write(*, root: Path, storage_key: str, after_rename: bool) -> None:
    """SIGKILL a writer after a partial write or after its atomic rename."""

    read_fd, write_fd = os.pipe()
    repo_root = Path(__file__).resolve().parents[3]
    environment = os.environ.copy()
    backend_path = str(repo_root / "backend")
    environment["PYTHONPATH"] = os.pathsep.join(
        filter(None, (backend_path, environment.get("PYTHONPATH")))
    )
    phase = "after-rename" if after_rename else "during-write"
    process = subprocess.Popen(
        [sys.executable, "-c", _WRITER, str(root), storage_key, str(write_fd), phase],
        cwd=repo_root,
        env=environment,
        pass_fds=(write_fd,),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    os.close(write_fd)
    ready, _, _ = select.select([read_fd], [], [], 15)
    try:
        if not ready or os.read(read_fd, 1) != b"R":
            process.kill()
            _, stderr = process.communicate(timeout=10)
            raise AssertionError(f"crash writer did not reach {phase}: {stderr!r}")
        process.send_signal(signal.SIGKILL)
        process.wait(timeout=10)
    finally:
        os.close(read_fd)
        if process.poll() is None:
            process.kill()
            process.wait(timeout=10)
