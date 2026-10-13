"""Request-scoped consent contracts for sending data to cloud providers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, runtime_checkable
from uuid import uuid4

from personal_ai.core.llm import LLMProvider, LLMRequest, LLMResponse


@dataclass(frozen=True)
class CloudConsentRequest:
    """Describe a proposed cloud transfer without carrying the payload itself."""

    request_id: str
    provider_id: str
    reason: str
    data_summary: str

    def __post_init__(self) -> None:
        for name in ("request_id", "provider_id", "reason", "data_summary"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")


class CloudConsentDecision(str, Enum):
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


@runtime_checkable
class CloudConsentProvider(Protocol):
    """Transport-independent contract for obtaining consent."""

    def request_consent(
        self, request: CloudConsentRequest
    ) -> CloudConsentDecision:
        """Return a decision for this specific request."""
        ...


class DenyCloudConsentProvider:
    """Safe default when no interactive consent channel is configured."""

    def request_consent(
        self, request: CloudConsentRequest
    ) -> CloudConsentDecision:
        del request
        return CloudConsentDecision.DENIED


class CLICloudConsentProvider:
    """Ask for explicit, request-scoped consent through an injectable input."""

    def __init__(
        self,
        input_fn: Callable[[str], str] | None = None,
        output_fn: Callable[[str], object] | None = None,
    ) -> None:
        self._input_fn = input if input_fn is None else input_fn
        self._output_fn = print if output_fn is None else output_fn

    def request_consent(
        self, request: CloudConsentRequest
    ) -> CloudConsentDecision:
        self._output_fn("Cloud transfer requires your explicit consent.")
        self._output_fn(f"Request ID: {request.request_id}")
        self._output_fn(f"Provider: {request.provider_id}")
        self._output_fn(f"Reason: {request.reason}")
        self._output_fn(f"Data to be sent: {request.data_summary}")
        self._output_fn("Allow this request only? Enter yes or no.")

        try:
            answer = self._input_fn("Consent [yes/no]: ")
        except (EOFError, OSError):
            # EOF and unavailable stdin must never grant consent.
            return CloudConsentDecision.DENIED

        if not isinstance(answer, str):
            return CloudConsentDecision.DENIED

        normalized = answer.strip().casefold()
        if normalized == "yes":
            return CloudConsentDecision.APPROVED
        if normalized == "no":
            return CloudConsentDecision.DENIED
        return CloudConsentDecision.DENIED


class CloudConsentError(RuntimeError):
    """Base exception for a cloud request blocked by consent."""

    def __init__(self, provider_id: str, message: str) -> None:
        self.provider_id = provider_id
        super().__init__(message)


class CloudConsentDeniedError(CloudConsentError):
    """Raised when cloud transfer consent is denied."""

    def __init__(self, provider_id: str) -> None:
        super().__init__(
            provider_id,
            f"Cloud transfer to '{provider_id}' was denied. "
            "No data was sent by this request.",
        )


class CloudConsentPendingError(CloudConsentError):
    """Raised while cloud transfer consent is pending."""

    def __init__(self, provider_id: str) -> None:
        super().__init__(
            provider_id,
            f"Cloud transfer to '{provider_id}' is awaiting consent. "
            "No data was sent by this request.",
        )


class ConsentGuardedProvider(LLMProvider):
    """Require fresh consent before forwarding each cloud LLM request."""

    def __init__(
        self,
        provider: LLMProvider,
        provider_id: str,
        consent_provider: CloudConsentProvider,
    ) -> None:
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise ValueError("provider_id must be a non-empty string")

        self._provider = provider
        self._provider_id = provider_id
        self._consent_provider = consent_provider

    def generate(self, request: LLMRequest) -> LLMResponse:
        consent_request = CloudConsentRequest(
            request_id=str(uuid4()),
            provider_id=self._provider_id,
            reason="The configured cloud LLM will process this request.",
            data_summary=(
                f"{len(request.messages)} conversation message(s) and "
                f"{len(request.tools)} tool definition(s); "
                "message contents are not included in this summary."
            ),
        )

        decision = self._consent_provider.request_consent(consent_request)

        if decision is CloudConsentDecision.APPROVED:
            return self._provider.generate(request)

        if decision is CloudConsentDecision.PENDING:
            raise CloudConsentPendingError(self._provider_id)

        # DENIED and unknown decisions both fail closed.
        raise CloudConsentDeniedError(self._provider_id)
