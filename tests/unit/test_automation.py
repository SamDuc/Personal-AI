import pytest

from personal_ai.core.automation import (
    SUPPORTED_AUTOMATION_VERSION,
    AutomationDefinition,
)


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


def test_automation_preserves_definition_fields():
    automation = make_automation()

    assert automation.automation_id == "daily-summary"
    assert automation.request == "Summarize my latest work."
    assert automation.route_id == "general"
    assert automation.interval_seconds == 3600
    assert automation.enabled is True
    assert automation.version == SUPPORTED_AUTOMATION_VERSION


@pytest.mark.parametrize("field", ["automation_id", "request", "route_id"])
def test_automation_rejects_empty_identity_fields(field):
    with pytest.raises(ValueError):
        make_automation(**{field: ""})


@pytest.mark.parametrize("field", ["automation_id", "request", "route_id"])
def test_automation_rejects_non_string_identity_fields(field):
    with pytest.raises(ValueError):
        make_automation(**{field: 123})


@pytest.mark.parametrize("interval", [0, -1, -60, True, False, 1.5, "3600"])
def test_automation_rejects_invalid_interval(interval):
    with pytest.raises(ValueError):
        make_automation(interval_seconds=interval)


@pytest.mark.parametrize("enabled", [0, 1, "true", None, []])
def test_automation_requires_boolean_enabled(enabled):
    with pytest.raises(ValueError):
        make_automation(enabled=enabled)


def test_automation_rejects_unsupported_version():
    with pytest.raises(ValueError):
        make_automation(version=SUPPORTED_AUTOMATION_VERSION + 1)


def test_automation_is_immutable():
    automation = make_automation()

    with pytest.raises(AttributeError):
        automation.enabled = False
