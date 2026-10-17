"""In-memory audit boundary for agent operations.

Events contain metadata only; prompts, file contents, credentials, and
tool arguments must not be included.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    outcome: str
    operation: str
    timestamp: str
    correlation_id: str | None = None


class AuditSink(Protocol):
    def emit(self, event: AuditEvent) -> None:
        """Accept one metadata-only audit event."""
        ...


class InMemoryAuditSink:
    """Non-persistent sink suitable for the initial implementation."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def emit(self, event: AuditEvent) -> None:
        if not isinstance(event, AuditEvent):
            raise TypeError("event must be an AuditEvent")
        self._events.append(event)

    def get_events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)


def make_audit_event(
    event_type: str,
    outcome: str,
    operation: str,
    correlation_id: str | None = None,
) -> AuditEvent:
    allowed_types = {"generation", "retrieval", "action"}
    allowed_outcomes = {"intent", "success", "failure", "indeterminate"}

    if not isinstance(event_type, str) or event_type not in allowed_types:
        raise ValueError("Unsupported audit event type")
    if not isinstance(outcome, str) or outcome not in allowed_outcomes:
        raise ValueError("Unsupported audit outcome")
    if outcome in {"intent", "indeterminate"} and event_type != "action":
        raise ValueError("intent and indeterminate outcomes are only valid for action events")
    if not isinstance(operation, str) or not operation.strip():
        raise ValueError("operation must be a non-empty string")
    if correlation_id is not None and (
        not isinstance(correlation_id, str) or not correlation_id.strip()
    ):
        raise ValueError("correlation_id must be a non-empty string or None")

    return AuditEvent(
        event_type=event_type,
        outcome=outcome,
        operation=operation,
        timestamp=datetime.now(UTC).isoformat(),
        correlation_id=correlation_id,
    )
