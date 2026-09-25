from copy import deepcopy
from datetime import UTC, datetime

import pytest

from personal_ai.core.memory import Memory, MemoryMetadata
from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus
from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)
from personal_ai.core.memory_provenance_model import MemoryProvenance
from personal_ai.core.memory_types import MemoryType
from personal_ai.core.memory_validation import (
    MemoryValidationError,
    validate_memory,
)


def create_test_memory() -> Memory:
    timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
    return Memory(
        id="memory:test:001",
        memory_type=MemoryType.SEMANTIC,
        content="Test memory",
        provenance=MemoryProvenance(
            source=MemorySource.USER,
            source_ref="test:user_input",
            method=MemoryProvenanceMethod.EXPLICIT,
            confidence=MemoryConfidence.EXPLICIT,
            recorded_at=timestamp,
        ),
        created_at=timestamp,
        updated_at=timestamp,
        expires_at=None,
        status=MemoryLifecycleStatus.ACTIVE,
        sensitivity="normal",
        metadata=MemoryMetadata(),
    )


def test_valid_memory_returns_none():
    memory = create_test_memory()
    assert validate_memory(memory) is None


@pytest.mark.parametrize("memory_type", list(MemoryType))
def test_all_memory_types_are_valid(memory_type):
    memory = create_test_memory()
    memory.memory_type = memory_type
    assert validate_memory(memory) is None


def test_empty_id_is_rejected():
    memory = create_test_memory()
    memory.id = ""
    with pytest.raises(MemoryValidationError, match="id"):
        validate_memory(memory)


def test_non_string_id_is_rejected():
    memory = create_test_memory()
    memory.id = 123
    with pytest.raises(MemoryValidationError, match="id"):
        validate_memory(memory)


def test_invalid_memory_type_is_rejected():
    memory = create_test_memory()
    memory.memory_type = "invalid"
    with pytest.raises(MemoryValidationError, match="memory_type"):
        validate_memory(memory)


def test_non_string_content_is_rejected():
    memory = create_test_memory()
    memory.content = 123
    with pytest.raises(MemoryValidationError, match="content"):
        validate_memory(memory)


def test_invalid_provenance_is_rejected():
    memory = create_test_memory()
    memory.provenance = None
    with pytest.raises(MemoryValidationError, match="provenance"):
        validate_memory(memory)


def test_invalid_provenance_source_is_rejected():
    memory = create_test_memory()
    memory.provenance.source = "invalid"
    with pytest.raises(MemoryValidationError, match="provenance.source"):
        validate_memory(memory)


def test_invalid_source_ref_is_rejected():
    memory = create_test_memory()
    memory.provenance.source_ref = 123
    with pytest.raises(MemoryValidationError, match="source_ref"):
        validate_memory(memory)


def test_invalid_provenance_method_is_rejected():
    memory = create_test_memory()
    memory.provenance.method = "invalid"
    with pytest.raises(MemoryValidationError, match="provenance.method"):
        validate_memory(memory)


def test_invalid_provenance_confidence_is_rejected():
    memory = create_test_memory()
    memory.provenance.confidence = "invalid"
    with pytest.raises(MemoryValidationError, match="provenance.confidence"):
        validate_memory(memory)


def test_invalid_recorded_at_is_rejected():
    memory = create_test_memory()
    memory.provenance.recorded_at = "invalid"
    with pytest.raises(MemoryValidationError, match="recorded_at"):
        validate_memory(memory)


@pytest.mark.parametrize("field", ["created_at", "updated_at", "expires_at"])
def test_invalid_timestamp_is_rejected(field):
    memory = create_test_memory()
    setattr(memory, field, "invalid")
    with pytest.raises(MemoryValidationError, match=field):
        validate_memory(memory)


def test_invalid_lifecycle_status_is_rejected():
    memory = create_test_memory()
    memory.status = "invalid"
    with pytest.raises(MemoryValidationError, match="status"):
        validate_memory(memory)


def test_invalid_sensitivity_is_rejected():
    memory = create_test_memory()
    memory.sensitivity = "invalid"
    with pytest.raises(MemoryValidationError, match="sensitivity"):
        validate_memory(memory)


def test_invalid_metadata_is_rejected():
    memory = create_test_memory()
    memory.metadata = "invalid"
    with pytest.raises(MemoryValidationError, match="metadata"):
        validate_memory(memory)


def test_validation_does_not_mutate_memory():
    memory = create_test_memory()
    before = deepcopy(memory)

    validate_memory(memory)

    assert memory == before


def test_validation_error_is_value_error():
    assert issubclass(MemoryValidationError, ValueError)
