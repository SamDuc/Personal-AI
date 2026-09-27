import json
import os
from collections.abc import Callable
from urllib import error, request

from personal_ai.core.llm import LLMProvider, LLMRequest, LLMResponse


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key_env: str | None = None,
        timeout: float = 60.0,
        urlopen: Callable[..., object] = request.urlopen,
    ) -> None:
        if not base_url.strip():
            raise ValueError("base_url must be non-empty")
        if not model.strip():
            raise ValueError("model must be non-empty")
        if api_key_env is not None and not api_key_env.strip():
            raise ValueError("api_key_env must be non-empty when provided")
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        self._base_url = base_url.rstrip("/")
        self._model = model
        self._api_key_env = api_key_env
        self._timeout = timeout
        self._urlopen = urlopen

    def generate(self, req: LLMRequest) -> LLMResponse:
        payload = {
            "model": self._model,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in req.messages
            ],
        }

        headers = {
            "Content-Type": "application/json",
        }

        if self._api_key_env is not None:
            api_key = os.environ.get(self._api_key_env)
            if not api_key:
                raise RuntimeError(
                    f"API key environment variable is not set: {self._api_key_env}"
                )
            headers["Authorization"] = f"Bearer {api_key}"

        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self._base_url}/chat/completions",
            data=body,
            headers=headers,
            method="POST",
        )

        try:
            with self._urlopen(http_request, timeout=self._timeout) as response:
                raw = response.read()
        except error.URLError as exc:
            raise RuntimeError("OpenAI-compatible provider request failed") from exc

        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("OpenAI-compatible provider returned invalid JSON") from exc

        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "OpenAI-compatible provider returned an invalid response"
            ) from exc

        if not isinstance(text, str):
            raise RuntimeError(
                "OpenAI-compatible provider response content must be text"
            )

        return LLMResponse(text=text)

