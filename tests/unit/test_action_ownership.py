import multiprocessing
from pathlib import Path

import pytest

from personal_ai.core.action_ownership import (
    ActionAlreadyOwnedError,
    ActionOwnershipLock,
)


def _hold_action_lock(lock_directory, correlation_id, ready, release):
    """Child process holds the lock until the parent signals release."""
    with ActionOwnershipLock(Path(lock_directory), correlation_id):
        ready.set()
        release.wait(timeout=15)


def test_action_lock_excludes_another_process_and_can_be_reacquired(tmp_path):
    context = multiprocessing.get_context("spawn")
    ready = context.Event()
    release = context.Event()
    correlation_id = "cross-process-ownership-regression"

    process = context.Process(
        target=_hold_action_lock,
        args=(str(tmp_path / "locks"), correlation_id, ready, release),
    )
    process.start()

    try:
        assert ready.wait(timeout=10), "Child process did not acquire the lock"
        assert process.is_alive(), "Child process exited before contention check"

        contender = ActionOwnershipLock(
            tmp_path / "locks",
            correlation_id,
        )
        with pytest.raises(ActionAlreadyOwnedError):
            contender.acquire()
    finally:
        release.set()
        process.join(timeout=10)
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)

    assert process.exitcode == 0

    # Once the owner exits and releases the lock, another owner can acquire it.
    with ActionOwnershipLock(tmp_path / "locks", correlation_id):
        pass


def test_action_lock_rejects_empty_correlation_id(tmp_path):
    with pytest.raises(ValueError, match="correlation_id"):
        ActionOwnershipLock(tmp_path, "")

def test_windows_lock_error_classification(monkeypatch, tmp_path):
    import sys
    import types

    import personal_ai.core.action_ownership as ownership_module
    fake_msvcrt = types.SimpleNamespace(LK_NBLCK=1, LK_UNLCK=0)

    def raise_permission_error(*args):
        error = OSError(5, "I/O error")
        error.winerror = 1117
        raise error

    fake_msvcrt.locking = raise_permission_error
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(
        ownership_module,
        "os",
        types.SimpleNamespace(
            name="nt",
            SEEK_END=ownership_module.os.SEEK_END,
        ),
    )

    lock = ownership_module.ActionOwnershipLock(tmp_path, "permission-error")
    with pytest.raises(OSError) as captured:
        lock.acquire()

    assert not isinstance(captured.value, ActionAlreadyOwnedError)
    assert lock._file is None

def test_windows_lock_contention_errno_13(monkeypatch, tmp_path):
    import sys
    import types

    import personal_ai.core.action_ownership as ownership_module

    fake_msvcrt = types.SimpleNamespace(LK_NBLCK=1, LK_UNLCK=0)

    def raise_lock_contention(*args):
        raise PermissionError(13, "Permission denied")

    fake_msvcrt.locking = raise_lock_contention
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(
        ownership_module,
        "os",
        types.SimpleNamespace(
            name="nt",
            SEEK_END=ownership_module.os.SEEK_END,
        ),
    )

    lock = ownership_module.ActionOwnershipLock(tmp_path, "busy-lock")
    with pytest.raises(ActionAlreadyOwnedError):
        lock.acquire()

    assert lock._file is None