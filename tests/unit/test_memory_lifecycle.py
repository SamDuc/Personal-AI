import pytest

from personal_ai.core.memory_lifecycle import MemoryLifecycleStatus


def test_memory_lifecycle_status_values():
    assert {status.value for status in MemoryLifecycleStatus} == {
        "candidate",
        "active",
        "superseded",
        "archived",
        "expired",
    }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("candidate", MemoryLifecycleStatus.CANDIDATE),
        ("active", MemoryLifecycleStatus.ACTIVE),
        ("superseded", MemoryLifecycleStatus.SUPERSEDED),
        ("archived", MemoryLifecycleStatus.ARCHIVED),
        ("expired", MemoryLifecycleStatus.EXPIRED),
    ],
)
def test_memory_lifecycle_status_from_string(value, expected):
    assert MemoryLifecycleStatus(value) is expected


def test_memory_lifecycle_status_is_string_compatible():
    assert MemoryLifecycleStatus.CANDIDATE == "candidate"
    assert MemoryLifecycleStatus.ACTIVE == "active"
    assert MemoryLifecycleStatus.SUPERSEDED == "superseded"
    assert MemoryLifecycleStatus.ARCHIVED == "archived"
    assert MemoryLifecycleStatus.EXPIRED == "expired"


def test_invalid_memory_lifecycle_status_is_rejected():
    with pytest.raises(ValueError):
        MemoryLifecycleStatus("invalid")