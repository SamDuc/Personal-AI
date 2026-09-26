from personal_ai.core.llm import (
    LLMProvider,
    LLMRequest,
    LLMResponse,
)


class LLMRuntime:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self.provider.generate(request)
