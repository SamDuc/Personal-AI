from datetime import UTC, datetime, timedelta

import pytest

from personal_ai.core.automation import AutomationDefinition
from personal_ai.core.automation_scheduler import AutomationScheduler


def make_automation(**overrides):
    values = {
        "automation_id": "daily-summary",
        "request": "Summarize my latest work.",
        "route_id": "general",
        "interval_seconds": 3600,
        "enabled": True,
    }
    values.update(overrides)
    return AutomationDefinition(**values)


def test_scheduler_registers_automation():
    scheduler = AutomationScheduler(lambda route_id, request: (route_id, request))
    automation = make_automation()

    scheduler.register(automation)

    assert scheduler.automation_ids == ("daily-summary",)


def test_scheduler_rejects_duplicate_automation():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    automation = make_automation()
    scheduler.register(automation)

    with pytest.raises(ValueError, match="duplicate automation"):
        scheduler.register(automation)


def test_disabled_automation_is_not_due():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    scheduler.register(make_automation(enabled=False))

    now = datetime(2026, 1, 1, tzinfo=UTC)

    assert scheduler.is_due("daily-summary", now) is False
    assert scheduler.run_due(now) == []


def test_new_enabled_automation_is_due():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    scheduler.register(make_automation())

    now = datetime(2026, 1, 1, tzinfo=UTC)

    assert scheduler.is_due("daily-summary", now) is True


def test_due_automation_dispatches_once():
    calls = []

    def dispatcher(route_id, request):
        calls.append((route_id, request))
        return "dispatched"

    scheduler = AutomationScheduler(dispatcher)
    scheduler.register(make_automation())

    now = datetime(2026, 1, 1, tzinfo=UTC)

    assert scheduler.run_due(now) == ["dispatched"]
    assert calls == [("general", "Summarize my latest work.")]

    assert scheduler.run_due(now) == []
    assert calls == [("general", "Summarize my latest work.")]


def test_automation_becomes_due_after_interval():
    calls = []

    scheduler = AutomationScheduler(
        lambda route_id, request: calls.append((route_id, request))
    )
    scheduler.register(make_automation(interval_seconds=60))

    start = datetime(2026, 1, 1, tzinfo=UTC)

    scheduler.run_due(start)
    assert scheduler.run_due(start + timedelta(seconds=59)) == []
    assert scheduler.run_due(start + timedelta(seconds=60)) == [
        None
    ]
    assert len(calls) == 2


def test_scheduler_preserves_route_and_request():
    calls = []

    scheduler = AutomationScheduler(
        lambda route_id, request: calls.append((route_id, request))
    )
    scheduler.register(
        make_automation(
            route_id="research",
            request="Find my recent research notes.",
        )
    )

    now = datetime(2026, 1, 1, tzinfo=UTC)

    scheduler.run_due(now)

    assert calls == [
        ("research", "Find my recent research notes.")
    ]


def test_scheduler_supports_multiple_automations():
    calls = []

    scheduler = AutomationScheduler(
        lambda route_id, request: calls.append((route_id, request))
    )
    scheduler.register(make_automation())
    scheduler.register(
        make_automation(
            automation_id="weekly-report",
            request="Prepare weekly report.",
            route_id="general",
            interval_seconds=604800,
        )
    )

    now = datetime(2026, 1, 1, tzinfo=UTC)

    scheduler.run_due(now)

    assert calls == [
        ("general", "Summarize my latest work."),
        ("general", "Prepare weekly report."),
    ]


def test_scheduler_rejects_unknown_automation():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    now = datetime(2026, 1, 1, tzinfo=UTC)

    with pytest.raises(ValueError, match="unknown automation"):
        scheduler.is_due("missing", now)


def test_scheduler_rejects_invalid_now():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    scheduler.register(make_automation())

    with pytest.raises(ValueError, match="now must be a datetime"):
        scheduler.run_due("2026-01-01")


def test_unregister_removes_automation():
    scheduler = AutomationScheduler(lambda route_id, request: None)
    scheduler.register(make_automation())

    scheduler.unregister("daily-summary")

    assert scheduler.automation_ids == ()


def test_unregister_unknown_automation_is_safe():
    scheduler = AutomationScheduler(lambda route_id, request: None)

    scheduler.unregister("missing")

    assert scheduler.automation_ids == ()
