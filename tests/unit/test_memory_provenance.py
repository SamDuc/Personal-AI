from personal_ai.core.memory_provenance import (
    MemoryConfidence,
    MemoryProvenanceMethod,
    MemorySource,
)


def test_memory_sources_are_exact():
    assert set(MemorySource) == {
        MemorySource.USER,
        MemorySource.TRUSTED_SYSTEM,
        MemorySource.EXTERNAL_SOURCE,
    }


def test_memory_provenance_methods_are_exact():
    assert set(MemoryProvenanceMethod) == {
        MemoryProvenanceMethod.EXPLICIT,
        MemoryProvenanceMethod.IMPORTED,
        MemoryProvenanceMethod.DERIVED,
    }


def test_memory_confidence_values_are_exact():
    assert set(MemoryConfidence) == {
        MemoryConfidence.EXPLICIT,
        MemoryConfidence.HIGH,
        MemoryConfidence.MEDIUM,
        MemoryConfidence.LOW,
    }


def test_memory_source_is_string_compatible():
    assert MemorySource.USER == "user"


def test_memory_provenance_method_is_string_compatible():
    assert MemoryProvenanceMethod.DERIVED == "derived"


def test_memory_confidence_is_string_compatible():
    assert MemoryConfidence.HIGH == "high"


def test_invalid_memory_source_is_rejected():
    try:
        MemorySource("invalid")
    except ValueError:
        return

    raise AssertionError("Invalid memory source should be rejected")


def test_invalid_memory_provenance_method_is_rejected():
    try:
        MemoryProvenanceMethod("invalid")
    except ValueError:
        return

    raise AssertionError("Invalid provenance method should be rejected")


def test_invalid_memory_confidence_is_rejected():
    try:
        MemoryConfidence("invalid")
    except ValueError:
        return

    raise AssertionError("Invalid confidence should be rejected")