from collections.abc import Callable
from datetime import datetime, timedelta

from personal_ai.core.automation import AutomationDefinition

AutomationDispatcher = Callable[[str, str], object]


class AutomationScheduler:
    """Deterministic in-memory scheduler for automation definitions."""

    def __init__(self, dispatcher: AutomationDispatcher) -> None:
        if not callable(dispatcher):
            raise ValueError("dispatcher must be callable")
        self._dispatcher = dispatcher
        self._automations: dict[str, AutomationDefinition] = {}
        self._last_run: dict[str, datetime] = {}

    @property
    def automation_ids(self) -> tuple[str, ...]:
        return tuple(self._automations)

    def register(self, automation: AutomationDefinition) -> None:
        if not isinstance(automation, AutomationDefinition):
            raise ValueError("automation must be an AutomationDefinition")
        if automation.automation_id in self._automations:
            raise ValueError(
                f"duplicate automation: {automation.automation_id}"
            )
        self._automations[automation.automation_id] = automation

    def unregister(self, automation_id: str) -> None:
        if not isinstance(automation_id, str) or not automation_id:
            raise ValueError("automation_id must be a non-empty string")
        self._automations.pop(automation_id, None)
        self._last_run.pop(automation_id, None)

    def is_due(self, automation_id: str, now: datetime) -> bool:
        automation = self._resolve(automation_id)
        self._validate_now(now)

        if not automation.enabled:
            return False

        last_run = self._last_run.get(automation_id)
        if last_run is None:
            return True

        return now >= last_run + timedelta(
            seconds=automation.interval_seconds
        )

    def run_due(self, now: datetime) -> list[object]:
        self._validate_now(now)
        results: list[object] = []

        for automation_id, automation in self._automations.items():
            if not automation.enabled:
                continue

            if not self.is_due(automation_id, now):
                continue

            result = self._dispatcher(
                automation.route_id,
                automation.request,
            )
            self._last_run[automation_id] = now
            results.append(result)

        return results

    def _resolve(self, automation_id: str) -> AutomationDefinition:
        if not isinstance(automation_id, str) or not automation_id:
            raise ValueError("automation_id must be a non-empty string")
        try:
            return self._automations[automation_id]
        except KeyError as exc:
            raise ValueError(
                f"unknown automation: {automation_id}"
            ) from exc

    @staticmethod
    def _validate_now(now: datetime) -> None:
        if not isinstance(now, datetime):
            raise ValueError("now must be a datetime")
