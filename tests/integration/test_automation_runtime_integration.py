from datetime import UTC, datetime
from pathlib import Path

from personal_ai.application.bootstrap import bootstrap
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.automation import AutomationDefinition


def test_bootstrap_integrates_scheduler_with_agent_router(tmp_path) -> None:
    application = bootstrap(
        ApplicationPaths(
            config_dir=Path("config"),
            data_dir=tmp_path / "data",
        )
    )

    application.automation_scheduler.register(
        AutomationDefinition(
            automation_id="integration-test",
            request="Run automation integration test",
            route_id="general",
            interval_seconds=60,
        )
    )

    results = application.automation_scheduler.run_due(
        datetime(2026, 1, 1, tzinfo=UTC)
    )

    assert len(results) == 1
    assert isinstance(results[0], str)
    assert results[0]
