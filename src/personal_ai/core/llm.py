from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class LLMRequest:
    messages: list[ChatMessage]


@dataclass(frozen=True)
class LLMResponse:
    text: str


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate a response for the given request."""
        raise NotImplementedError
