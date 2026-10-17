"""Cross-process ownership locks for action execution and audit recovery."""

from __future__ import annotations

import errno
import hashlib
import os
from pathlib import Path
from typing import BinaryIO, Self


class ActionAlreadyOwnedError(RuntimeError):
    """Raised when another process currently owns an action lock."""


class ActionOwnershipLock:
    """Non-blocking OS-level lock for a single action correlation ID.

    Lock files are intentionally persistent. Deleting a lock file while
    another process has it open can create races between different inodes.
    """

    def __init__(self, lock_directory: Path, correlation_id: str) -> None:
        if not correlation_id or not correlation_id.strip():
            raise ValueError("correlation_id must not be empty")

        digest = hashlib.sha256(correlation_id.encode("utf-8")).hexdigest()
        self._path = Path(lock_directory) / f"action-{digest}.lock"
        self._file: BinaryIO | None = None

    @property
    def path(self) -> Path:
        return self._path

    def acquire(self) -> ActionOwnershipLock:
        if self._file is not None:
            raise RuntimeError("This lock instance is already acquired")

        self._path.parent.mkdir(parents=True, exist_ok=True)
        handle = self._path.open("a+b")

        try:
            # Windows byte-range locks require a byte to exist in the file.
            handle.seek(0, os.SEEK_END)
            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)

            if os.name == "nt":
                import msvcrt

                try:
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                except OSError as exc:
                    # Windows ERROR_LOCK_VIOLATION means another owner holds
                    # the byte range. Other OS errors must fail as themselves.
                    if exc.errno != errno.EACCES:
                        raise
                    raise ActionAlreadyOwnedError(
                        "Action is currently owned by another process"
                    ) from exc
            else:
                import fcntl

                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError as exc:
                    raise ActionAlreadyOwnedError(
                        "Action is currently owned by another process"
                    ) from exc

            self._file = handle
            return self
        except BaseException:
            handle.close()
            raise

    def release(self) -> None:
        handle = self._file
        if handle is None:
            return

        self._file = None
        try:
            handle.seek(0)
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        finally:
            handle.close()

    def __enter__(self) -> Self:
        return self.acquire()

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.release()
