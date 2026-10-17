from personal_ai.core.audit import make_audit_event
from personal_ai.core.durable_audit import SQLiteAuditSink


def test_sqlite_audit_persists_events_after_reopen(tmp_path):
    database = tmp_path / "audit.sqlite3"
    event = make_audit_event(
        "action",
        "success",
        "test_tool",
        correlation_id="correlation-1",
    )

    SQLiteAuditSink(database).emit(event)

    reopened = SQLiteAuditSink(database)
    events = reopened.get_events()

    assert events == (event,)
    assert reopened.integrity_check() == "ok"


def test_sqlite_audit_stores_metadata_only(tmp_path):
    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")
    event = make_audit_event("generation", "success", "llm_generate")

    sink.emit(event)

    stored = sink.get_events()[0]
    assert stored.operation == "llm_generate"
    assert not hasattr(stored, "prompt")
    assert not hasattr(stored, "arguments")


def test_sqlite_audit_rejects_non_event(tmp_path):
    import pytest

    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")

    with pytest.raises(TypeError):
        sink.emit({"prompt": "must not be stored"})


def test_unresolved_action_intent_survives_database_reopen(tmp_path):
    database = tmp_path / "audit.sqlite3"
    sink = SQLiteAuditSink(database)
    intent = make_audit_event("action", "intent", "test_tool", correlation_id="recovery-1")
    sink.emit(intent)

    reopened = SQLiteAuditSink(database)

    assert reopened.get_unresolved_actions() == (intent,)


def test_resolved_action_intent_is_not_unresolved(tmp_path):
    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")
    intent = make_audit_event("action", "intent", "test_tool", correlation_id="recovery-2")
    terminal = make_audit_event("action", "success", "test_tool", correlation_id="recovery-2")
    sink.emit(intent)
    sink.emit(terminal)

    assert sink.get_unresolved_actions() == ()


def test_recovery_requires_explicit_confirmation(tmp_path):
    import pytest

    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")
    intent = make_audit_event(
        "action", "intent", "test_tool", correlation_id="recovery-confirmation"
    )
    sink.emit(intent)

    with pytest.raises(ValueError, match="confirm_recovery=True"):
        sink.mark_unresolved_actions_indeterminate()

    assert sink.get_unresolved_actions() == (intent,)
    assert sink.get_events() == (intent,)


def test_recovery_marks_intent_indeterminate_without_replaying(tmp_path):
    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")
    intent = make_audit_event("action", "intent", "test_tool", correlation_id="recovery-3")
    sink.emit(intent)

    recovered = sink.mark_unresolved_actions_indeterminate(confirm_recovery=True)

    assert recovered == (intent,)
    assert sink.get_unresolved_actions() == ()

    events = sink.get_events()
    terminal_events = [
        event
        for event in events
        if event.correlation_id == "recovery-3" and event.outcome == "indeterminate"
    ]
    assert len(terminal_events) == 1
    assert terminal_events[0].event_type == "action"
    assert terminal_events[0].operation == "test_tool"

    # Recovery only updates audit metadata; it does not execute any tool.
    assert len(events) == 2
    assert events[0] == intent


def test_sqlite_audit_backup_restore_preserves_events(tmp_path):
    import sqlite3

    database = tmp_path / "audit.sqlite3"
    backup_database = tmp_path / "audit-backup.sqlite3"
    restored_database = tmp_path / "audit-restored.sqlite3"

    sink = SQLiteAuditSink(database)
    intent = make_audit_event("action", "intent", "test_tool", correlation_id="backup-restore-1")
    terminal = make_audit_event("action", "success", "test_tool", correlation_id="backup-restore-1")
    sink.emit(intent)
    sink.emit(terminal)

    # Use SQLite's online backup API rather than copying a live database file.
    with sqlite3.connect(database) as source, sqlite3.connect(backup_database) as destination:
        source.backup(destination)

    with (
        sqlite3.connect(backup_database) as source,
        sqlite3.connect(restored_database) as destination,
    ):
        source.backup(destination)

    restored = SQLiteAuditSink(restored_database)
    assert restored.get_events() == (intent, terminal)
    assert restored.integrity_check() == "ok"
    assert restored.get_unresolved_actions() == ()


def test_recovery_skips_action_when_ownership_lock_is_busy(tmp_path, monkeypatch):
    import pytest

    from personal_ai.core.action_ownership import ActionAlreadyOwnedError

    sink = SQLiteAuditSink(tmp_path / "audit.sqlite3")
    intent = make_audit_event(
        "action",
        "intent",
        "test_tool",
        correlation_id="recovery-active-lock",
    )
    sink.emit(intent)

    class BusyLock:
        def acquire(self):
            raise ActionAlreadyOwnedError("test lock is busy")

        def release(self):
            pytest.fail("Recovery must not release a lock it did not acquire")

    monkeypatch.setattr(sink, "action_lock", lambda correlation_id: BusyLock())

    recovered = sink.mark_unresolved_actions_indeterminate(confirm_recovery=True)

    assert recovered == ()
    assert sink.get_unresolved_actions() == (intent,)
    assert not any(
        event.correlation_id == "recovery-active-lock"
        and event.outcome == "indeterminate"
        for event in sink.get_events()
    )