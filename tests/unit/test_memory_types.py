import pytest

from personal_ai.core.memory_types import MemoryType


def test_memory_types_match_contract():
    assert {item.value for item in MemoryType} == {
        "semantic",
        "episodic",
        "working",
        "procedural",
    }


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("SEMANTIC", "semantic"),
        ("EPISODIC", "episodic"),
        ("WORKING", "working"),
        ("PROCEDURAL", "procedural"),
    ],
)
def test_memory_type_values(name, value):
    assert getattr(MemoryType, name) == value


def test_memory_type_is_str_compatible():
    assert isinstance(MemoryType.SEMANTIC, str)


def test_invalid_memory_type_is_rejected():
    with pytest.raises(ValueError):
        MemoryType("invalid")
