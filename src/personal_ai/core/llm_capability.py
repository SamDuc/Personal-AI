from dataclasses import dataclass
from enum import Enum


class LLMCapability(str, Enum):
    TEXT_INPUT = "text_input"
    TEXT_OUTPUT = "text_output"


@dataclass(frozen=True)
class LLMCapabilitySet:
    capabilities: frozenset[LLMCapability]

    def supports(self, capability: LLMCapability) -> bool:
        return capability in self.capabilities
