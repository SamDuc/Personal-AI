from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMToolCall:
    id: str
    name: str
    arguments: str


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str | None
    tool_calls: tuple[LLMToolCall, ...] = ()
    tool_call_id: str | None = None


@dataclass(frozen=True)
class LLMToolDefinition:
    name: str
    description: str
    parameters: dict[str, object]


@dataclass(frozen=True)
class LLMRequest:
    messages: list[ChatMessage]
    tools: tuple[LLMToolDefinition, ...] = ()


@dataclass(frozen=True)
class LLMResponse:
    text: str
    tool_calls: tuple[LLMToolCall, ...] = ()


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for the given request."""
        raise NotImplementedError
