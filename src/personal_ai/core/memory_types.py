from enum import StrEnum


class MemoryType(StrEnum):
    """Initial memory classification defined by the memory contract."""

    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    WORKING = "working"
    PROCEDURAL = "procedural"
