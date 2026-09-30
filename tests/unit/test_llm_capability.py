from personal_ai.core.llm_capability import (
    LLMCapability,
    LLMCapabilitySet,
)


def test_capability_values_are_stable() -> None:
    assert LLMCapability.TEXT_INPUT.value == "text_input"
    assert LLMCapability.TEXT_OUTPUT.value == "text_output"


def test_capability_set_is_immutable() -> None:
    capabilities = LLMCapabilitySet(
        capabilities=frozenset(
            {
                LLMCapability.TEXT_INPUT,
                LLMCapability.TEXT_OUTPUT,
            }
        )
    )

    assert capabilities.supports(LLMCapability.TEXT_INPUT)
    assert capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_capability_set_rejects_unsupported_capability() -> None:
    capabilities = LLMCapabilitySet(
        capabilities=frozenset({LLMCapability.TEXT_INPUT})
    )

    assert capabilities.supports(LLMCapability.TEXT_INPUT)
    assert not capabilities.supports(LLMCapability.TEXT_OUTPUT)


def test_capability_set_does_not_expose_mutable_state() -> None:
    capabilities = LLMCapabilitySet(
        capabilities=frozenset({LLMCapability.TEXT_INPUT})
    )

    assert isinstance(capabilities.capabilities, frozenset)
