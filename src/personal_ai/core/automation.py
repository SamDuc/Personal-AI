from dataclasses import dataclass

SUPPORTED_AUTOMATION_VERSION = 1


@dataclass(frozen=True)
class AutomationDefinition:
    """Immutable definition of an automation trigger."""

    automation_id: str
    request: str
    route_id: str
    interval_seconds: int
    enabled: bool = True
    version: int = SUPPORTED_AUTOMATION_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.automation_id, str) or not self.automation_id:
            raise ValueError("automation_id must be a non-empty string")

        if not isinstance(self.request, str) or not self.request:
            raise ValueError("request must be a non-empty string")

        if not isinstance(self.route_id, str) or not self.route_id:
            raise ValueError("route_id must be a non-empty string")

        if (
            isinstance(self.interval_seconds, bool)
            or not isinstance(self.interval_seconds, int)
            or self.interval_seconds <= 0
        ):
            raise ValueError("interval_seconds must be a positive integer")

        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")

        if self.version != SUPPORTED_AUTOMATION_VERSION:
            raise ValueError("unsupported automation version")
