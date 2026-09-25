from datetime import UTC, datetime

from personal_ai.core.memory import Memory, MemoryMetadata
from personal_ai.core.memory_types import MemoryType


def test_memory_can_be_created():
    memory = Memory(
        id="memory-001",
        memory_type=MemoryType.SEMANTIC,
        content="Python is a programming language.",
    )

    assert memory.id == "memory-001"
    assert memory.memory_type is MemoryType.SEMANTIC
    assert memory.content == "Python is a programming language."


def test_memory_defaults_match_contract():
    memory = Memory(
        id="memory-001",
        memory_type=MemoryType.EPISODIC,
        content="A task was completed.",
    )

    assert memory.source == "user"
    assert memory.confidence == "explicit"
    assert memory.status == "candidate"
    assert memory.sensitivity == "normal"
    assert memory.created_at is None
    assert memory.updated_at is None
    assert memory.expires_at is None


def test_memory_supports_timestamps():
    timestamp = datetime.now(UTC)

    memory = Memory(
        id="memory-001",
        memory_type=MemoryType.WORKING,
        content="Current task context.",
        created_at=timestamp,
        updated_at=timestamp,
        expires_at=timestamp,
    )

    assert memory.created_at == timestamp
    assert memory.updated_at == timestamp
    assert memory.expires_at == timestamp


def test_memory_supports_metadata():
    metadata = MemoryMetadata(
        source="trusted_system",
        confidence="verified",
        sensitivity="private",
    )

    memory = Memory(
        id="memory-001",
        memory_type=MemoryType.PROCEDURAL,
        content="A known workflow.",
        metadata=metadata,
    )

    assert memory.metadata is metadata
    assert memory.metadata.source == "trusted_system"
    assert memory.metadata.confidence == "verified"
    assert memory.metadata.sensitivity == "private"


def test_memory_type_is_explicit():
    memory = Memory(
        id="memory-001",
        memory_type=MemoryType.SEMANTIC,
        content="Known information.",
    )

    assert isinstance(memory.memory_type, MemoryType)
    assert memory.memory_type.value == "semantic"
