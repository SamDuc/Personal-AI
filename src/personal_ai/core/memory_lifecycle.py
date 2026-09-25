from enum import StrEnum


class MemoryLifecycleStatus(StrEnum):
    """Lifecycle status defined by the memory contract."""

    CANDIDATE = "candidate"
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"
    EXPIRED = "expired"