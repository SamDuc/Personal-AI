from datetime import datetime

from personal_ai.core.memory import Memory, MemoryMetadata
from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus
from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)
from personal_ai.core.memory_provenance_model import MemoryProvenance
from personal_ai.core.memory_types import MemoryType


class MemoryValidationError(ValueError):
    """Raised when a Memory violates the validation contract."""


def _raise(field_name: str, message: str) -> None:
    raise MemoryValidationError(f"{field_name}: {message}")


def validate_memory(memory: Memory) -> None:
    """Validate a canonical Memory object without mutating it."""
    if not isinstance(memory, Memory):
        _raise("memory", "must be a Memory instance")

    if not isinstance(memory.id, str) or not memory.id:
        _raise("id", "must be a non-empty string")

    if not isinstance(memory.memory_type, MemoryType):
        _raise("memory_type", "must be a MemoryType value")

    if not isinstance(memory.content, str):
        _raise("content", "must be a string")

    provenance = memory.provenance
    if not isinstance(provenance, MemoryProvenance):
        _raise("provenance", "must be a MemoryProvenance instance")

    if not isinstance(provenance.source, MemorySource):
        _raise("provenance.source", "must be a MemorySource value")

    if not isinstance(provenance.source_ref, str):
        _raise("provenance.source_ref", "must be a string")

    if not isinstance(provenance.method, MemoryProvenanceMethod):
        _raise("provenance.method", "must be a MemoryProvenanceMethod value")

    if not isinstance(provenance.confidence, MemoryConfidence):
        _raise("provenance.confidence", "must be a MemoryConfidence value")

    if not isinstance(provenance.recorded_at, datetime):
        _raise("provenance.recorded_at", "must be a datetime")

    for field_name in ("created_at", "updated_at", "expires_at"):
        value = getattr(memory, field_name)
        if value is not None and not isinstance(value, datetime):
            _raise(field_name, "must be a datetime or None")

    if not isinstance(memory.status, MemoryLifecycleStatus):
        _raise("status", "must be a MemoryLifecycleStatus value")

    valid_sensitivities = {
        "normal",
        "private",
        "sensitive",
        "restricted",
    }
    if memory.sensitivity not in valid_sensitivities:
        _raise("sensitivity", "has an invalid value")

    if memory.metadata is not None and not isinstance(memory.metadata, MemoryMetadata):
        _raise("metadata", "must be a MemoryMetadata instance or None")
