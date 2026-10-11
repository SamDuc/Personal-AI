import json
import os
from collections.abc import Callable
from urllib import error, request

from personal_ai.core.llm import LLMProvider, LLMRequest, LLMResponse, LLMToolCall


class OpenAICompatibleProvider(LLMProvider):
    def __init__(
        self,
        base_url: str,
        model: str,
        api_key_env: str | None = None,
        timeout: float = 60.0,
        urlopen: Callable[..., object] | None = None,
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
        self._urlopen = request.urlopen if urlopen is None else urlopen

    @staticmethod
    def _serialize_message(message) -> dict[str, object]:
        result: dict[str, object] = {
            "role": message.role,
            "content": message.content,
        }

        if message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                }
                for call in message.tool_calls
            ]

        if message.tool_call_id is not None:
            result["tool_call_id"] = message.tool_call_id

        return result

    def generate(self, req: LLMRequest) -> LLMResponse:
        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                self._serialize_message(message)
                for message in req.messages
            ],
        }

        if req.tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                for tool in req.tools
            ]

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "personal-ai/0.1.0",
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
        except error.HTTPError as exc:
            raise RuntimeError(
                f"OpenAI-compatible provider request failed with HTTP {exc.code}"
            ) from exc
        except error.URLError as exc:
            raise RuntimeError(
                "OpenAI-compatible provider request failed"
            ) from exc

        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                "OpenAI-compatible provider returned invalid JSON"
            ) from exc

        try:
            message = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                "OpenAI-compatible provider returned an invalid response"
            ) from exc

        if not isinstance(message, dict):
            raise RuntimeError(
                "OpenAI-compatible provider returned an invalid response"
            )

        text = message.get("content")
        if text is None:
            text = ""
        elif not isinstance(text, str):
            raise RuntimeError(
                "OpenAI-compatible provider response content must be text"
            )

        raw_tool_calls = message.get("tool_calls", [])
        if not isinstance(raw_tool_calls, list):
            raise RuntimeError(
                "OpenAI-compatible provider tool_calls must be a list"
            )

        tool_calls = []
        for item in raw_tool_calls:
            if not isinstance(item, dict):
                raise RuntimeError(
                    "OpenAI-compatible provider returned a malformed tool call"
                )

            function = item.get("function")
            if not isinstance(function, dict):
                raise RuntimeError(
                    "OpenAI-compatible provider returned a malformed tool call"
                )

            call_id = item.get("id")
            name = function.get("name")
            arguments = function.get("arguments")

            if (
                not isinstance(call_id, str)
                or not call_id
                or not isinstance(name, str)
                or not name
                or not isinstance(arguments, str)
            ):
                raise RuntimeError(
                    "OpenAI-compatible provider returned a malformed tool call"
                )

            tool_calls.append(
                LLMToolCall(
                    id=call_id,
                    name=name,
                    arguments=arguments,
                )
            )

        if not text and not tool_calls:
            raise RuntimeError(
                "OpenAI-compatible provider response contained no text or tool calls"
            )

        return LLMResponse(text=text, tool_calls=tuple(tool_calls))
