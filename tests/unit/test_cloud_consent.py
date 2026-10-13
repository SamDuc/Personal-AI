import pytest

from personal_ai.core.cloud_consent import (
    CLICloudConsentProvider,
    CloudConsentDecision,
    CloudConsentDeniedError,
    CloudConsentPendingError,
    CloudConsentProvider,
    CloudConsentRequest,
    ConsentGuardedProvider,
    DenyCloudConsentProvider,
)
from personal_ai.core.llm import (
    ChatMessage,
    LLMProvider,
    LLMRequest,
    LLMResponse,
)


def make_request(request_id="req-1", provider_id="cloud-a"):
    return CloudConsentRequest(
        request_id=request_id,
        provider_id=provider_id,
        reason="Local processing was insufficient",
        data_summary="A short user prompt",
    )


def test_cli_approves_only_explicit_yes():
    provider = CLICloudConsentProvider(input_fn=lambda _: "yes")
    assert provider.request_consent(make_request()) is CloudConsentDecision.APPROVED


def test_cli_denies_explicit_no():
    provider = CLICloudConsentProvider(input_fn=lambda _: "no")
    assert provider.request_consent(make_request()) is CloudConsentDecision.DENIED


@pytest.mark.parametrize("answer", ["", "y", "YES PLEASE", "approve", "maybe", "  "])
def test_cli_denies_invalid_or_ambiguous_input(answer):
    provider = CLICloudConsentProvider(input_fn=lambda _: answer)
    assert provider.request_consent(make_request()) is CloudConsentDecision.DENIED


@pytest.mark.parametrize("error", [EOFError(), OSError("stdin unavailable")])
def test_cli_denies_when_input_raises(error):
    def broken_input(_):
        raise error

    provider = CLICloudConsentProvider(input_fn=broken_input)
    assert provider.request_consent(make_request()) is CloudConsentDecision.DENIED


def test_cli_displays_provider_and_data_summary(capsys):
    provider = CLICloudConsentProvider(input_fn=lambda _: "no")
    request = make_request(provider_id="provider-x")

    provider.request_consent(request)

    output = capsys.readouterr().out
    assert request.request_id in output
    assert "provider-x" in output
    assert request.data_summary in output


def test_default_provider_denies_without_interactive_channel():
    provider = DenyCloudConsentProvider()
    assert provider.request_consent(make_request()) is CloudConsentDecision.DENIED


def test_api_compatible_contract_can_return_pending():
    class PendingProvider:
        def request_consent(self, request):
            assert request.request_id == "req-api"
            return CloudConsentDecision.PENDING

    provider: CloudConsentProvider = PendingProvider()
    assert provider.request_consent(make_request("req-api")) is CloudConsentDecision.PENDING


def test_contract_accepts_cli_and_default_implementations():
    assert isinstance(CLICloudConsentProvider(input_fn=lambda _: "no"), CloudConsentProvider)
    assert isinstance(DenyCloudConsentProvider(), CloudConsentProvider)


def test_approval_is_not_reused_for_another_request_or_provider():
    answers = iter(["yes", "no"])
    provider = CLICloudConsentProvider(input_fn=lambda _: next(answers))

    first = make_request("req-1", "cloud-a")
    second = make_request("req-2", "cloud-b")

    assert provider.request_consent(first) is CloudConsentDecision.APPROVED
    assert provider.request_consent(second) is CloudConsentDecision.DENIED


def test_request_is_immutable():
    request = make_request()

    with pytest.raises((AttributeError, TypeError)):
        request.provider_id = "other-provider"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("request_id", ""),
        ("provider_id", "  "),
        ("reason", ""),
        ("data_summary", ""),
    ],
)
def test_request_rejects_missing_required_fields(field, value):
    values = {
        "request_id": "req-1",
        "provider_id": "cloud-a",
        "reason": "reason",
        "data_summary": "summary",
    }
    values[field] = value

    with pytest.raises(ValueError):
        CloudConsentRequest(**values)


def make_llm_request():
    return LLMRequest(
        messages=[
            ChatMessage(role="user", content="Private test content"),
        ],
    )


class SpyLLMProvider(LLMProvider):
    def __init__(self):
        self.calls = 0

    def generate(self, request):
        self.calls += 1
        return LLMResponse(text="provider response")


class FixedConsentProvider:
    def __init__(self, decision):
        self.decision = decision
        self.requests = []

    def request_consent(self, request):
        self.requests.append(request)
        return self.decision


def test_guard_calls_cloud_provider_after_approval():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider(CloudConsentDecision.APPROVED)
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    response = guarded.generate(make_llm_request())

    assert response.text == "provider response"
    assert cloud.calls == 1
    assert len(consent.requests) == 1


def test_guard_blocks_cloud_provider_when_denied():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider(CloudConsentDecision.DENIED)
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    with pytest.raises(CloudConsentDeniedError):
        guarded.generate(make_llm_request())

    assert cloud.calls == 0


def test_guard_blocks_cloud_provider_when_pending():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider(CloudConsentDecision.PENDING)
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    with pytest.raises(CloudConsentPendingError):
        guarded.generate(make_llm_request())

    assert cloud.calls == 0


def test_guard_fails_closed_for_unknown_decision():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider("unexpected")
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    with pytest.raises(CloudConsentDeniedError):
        guarded.generate(make_llm_request())

    assert cloud.calls == 0


def test_guard_summary_does_not_include_message_content():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider(CloudConsentDecision.DENIED)
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    with pytest.raises(CloudConsentDeniedError):
        guarded.generate(make_llm_request())

    assert "Private test content" not in consent.requests[0].data_summary


def test_guard_creates_new_request_id_for_each_attempt():
    cloud = SpyLLMProvider()
    consent = FixedConsentProvider(CloudConsentDecision.DENIED)
    guarded = ConsentGuardedProvider(cloud, "cloud-a", consent)

    for _ in range(2):
        with pytest.raises(CloudConsentDeniedError):
            guarded.generate(make_llm_request())

    ids = [item.request_id for item in consent.requests]
    assert len(ids) == 2
    assert len(set(ids)) == 2
