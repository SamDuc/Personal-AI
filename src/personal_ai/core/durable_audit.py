"""Durable SQLite-backed audit event storage."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from personal_ai.core.action_ownership import ActionAlreadyOwnedError, ActionOwnershipLock
from personal_ai.core.audit import AuditEvent, make_audit_event


class SQLiteAuditSink:
    """Append-only metadata audit sink backed by SQLite."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path).expanduser().resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def action_lock(self, correlation_id: str) -> ActionOwnershipLock:
        """Return the OS-level ownership lock for an action."""
        return ActionOwnershipLock(
            self.database_path.parent / "action-locks",
            correlation_id,
        )


    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path, timeout=10.0)
        try:
            connection.execute("PRAGMA synchronous = FULL")
            yield connection
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    correlation_id TEXT
                )
                """
            )

    def emit(self, event: AuditEvent) -> None:
        if not isinstance(event, AuditEvent):
            raise TypeError("event must be an AuditEvent")

        with self._connection() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    event_type, outcome, operation, timestamp, correlation_id
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event.event_type,
                    event.outcome,
                    event.operation,
                    event.timestamp,
                    event.correlation_id,
                ),
            )

    def get_events(self) -> tuple[AuditEvent, ...]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT event_type, outcome, operation, timestamp, correlation_id
                FROM audit_events
                ORDER BY id
                """
            ).fetchall()

        return tuple(AuditEvent(*row) for row in rows)

    def get_unresolved_actions(self) -> tuple[AuditEvent, ...]:
        """Return action intents without a terminal event for the same ID.

        This method only detects unresolved actions. It never replays tools or
        changes audit records.
        """
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT intent.event_type,
                       intent.outcome,
                       intent.operation,
                       intent.timestamp,
                       intent.correlation_id
                FROM audit_events AS intent
                WHERE intent.event_type = 'action'
                  AND intent.outcome = 'intent'
                  AND intent.correlation_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM audit_events AS terminal
                      WHERE terminal.event_type = 'action'
                        AND terminal.outcome IN (
                            'success', 'failure', 'indeterminate'
                        )
                        AND terminal.correlation_id = intent.correlation_id
                  )
                ORDER BY intent.id
                """
            ).fetchall()

        return tuple(AuditEvent(*row) for row in rows)

    def mark_unresolved_actions_indeterminate(
        self, *, confirm_recovery: bool = False
    ) -> tuple[AuditEvent, ...]:
        """Mark abandoned actions indeterminate without replaying them.

        Active actions are skipped when another process owns their lock.
        No SQLite write transaction is held while attempting to acquire locks.
        """
        if confirm_recovery is not True:
            raise ValueError("Recovery requires explicit confirm_recovery=True")

        candidates = self.get_unresolved_actions()
        marked: list[AuditEvent] = []

        for intent in candidates:
            correlation_id = intent.correlation_id
            if correlation_id is None:
                continue

            ownership = self.action_lock(correlation_id)
            try:
                ownership.acquire()
            except ActionAlreadyOwnedError:
                continue

            try:
                with self._connection() as connection:
                    connection.execute("BEGIN IMMEDIATE")
                    still_unresolved = connection.execute(
                        """
                        SELECT 1
                        FROM audit_events AS intent
                        WHERE intent.event_type = 'action'
                          AND intent.outcome = 'intent'
                          AND intent.correlation_id = ?
                          AND NOT EXISTS (
                              SELECT 1
                              FROM audit_events AS terminal
                              WHERE terminal.event_type = 'action'
                                AND terminal.outcome IN (
                                    'success', 'failure', 'indeterminate'
                                )
                                AND terminal.correlation_id =
                                    intent.correlation_id
                          )
                        LIMIT 1
                        """,
                        (correlation_id,),
                    ).fetchone()

                    if still_unresolved is None:
                        continue

                    terminal = make_audit_event(
                        event_type="action",
                        outcome="indeterminate",
                        operation=intent.operation,
                        correlation_id=correlation_id,
                    )
                    connection.execute(
                        """
                        INSERT INTO audit_events (
                            event_type, outcome, operation, timestamp,
                            correlation_id
                        ) VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            terminal.event_type,
                            terminal.outcome,
                            terminal.operation,
                            terminal.timestamp,
                            terminal.correlation_id,
                        ),
                    )
                    marked.append(intent)
            finally:
                ownership.release()

        return tuple(marked)

    def integrity_check(self) -> str:
        with self._connection() as connection:
            row = connection.execute("PRAGMA integrity_check").fetchone()

        if row is None:
            raise RuntimeError("SQLite integrity check returned no result")
        return str(row[0])
