from enum import StrEnum


class MemorySource(StrEnum):
    """Origin category for a memory item."""

    USER = "user"
    TRUSTED_SYSTEM = "trusted_system"
    EXTERNAL_SOURCE = "external_source"


class MemoryProvenanceMethod(StrEnum):
    """Method by which a memory was recorded."""

    EXPLICIT = "explicit"
    IMPORTED = "imported"
    DERIVED = "derived"


class MemoryConfidence(StrEnum):
    """Confidence classification associated with a memory provenance."""

    EXPLICIT = "explicit"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"