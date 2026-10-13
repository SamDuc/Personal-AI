from pathlib import Path

from personal_ai.application.bootstrap import bootstrap
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.cloud_consent import (
    CloudConsentDecision,
    ConsentGuardedProvider,
)
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.core.llm import LLMProvider, LLMRequest, LLMResponse


class SpyCloudProvider(LLMProvider):
    def __init__(self) -> None:
        self.calls = 0

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return LLMResponse(text="unexpected cloud response")


class DenyConsent:
    def request_consent(self, request):
        return CloudConsentDecision.DENIED
class PendingConsent:
    def request_consent(self, request):
        return CloudConsentDecision.PENDING


def test_bootstrapped_agent_denial_never_calls_cloud_provider(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PERSONAL_AI_LLM_PROVIDER", "my_llm")

    config_dir = tmp_path / "config"
    (config_dir / "permissions").mkdir(parents=True)
    (config_dir / "sources").mkdir(parents=True)

    source_config = Path("config/llm.yaml").read_text(encoding="utf-8")
    cloud_config = source_config.replace(
        "  my_llm:\n    enabled: true\n    type: local",
        "  my_llm:\n    enabled: true\n    type: cloud",
    )
    (config_dir / "llm.yaml").write_text(cloud_config, encoding="utf-8")

    for relative_path in (
        Path("config/permissions/permissions.yaml"),
        Path("config/sources/sources.yaml"),
        Path("config/filesystem.yaml"),
    ):
        target = config_dir / relative_path.relative_to("config")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(relative_path.read_bytes())

    application = bootstrap(
        ApplicationPaths(config_dir=config_dir, data_dir=tmp_path / "data")
    )

    guarded = application.agent.integration.runtime.provider
    assert isinstance(guarded, ConsentGuardedProvider)

    spy = SpyCloudProvider()
    guarded._provider = spy
    guarded._consent_provider = DenyConsent()

    session = ConversationSession()
    answer = application.agent.run("Summarize my private notes", session)

    assert answer == (
        "Cloud transfer to 'my_llm' was denied. "
        "No data was sent by this request."
    )
    assert spy.calls == 0
    assert [message.role for message in session.get_messages()] == ["user"]


def test_bootstrapped_agent_pending_never_calls_cloud_provider(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("PERSONAL_AI_LLM_PROVIDER", "my_llm")

    config_dir = tmp_path / "config"
    (config_dir / "permissions").mkdir(parents=True)
    (config_dir / "sources").mkdir(parents=True)

    source_config = Path("config/llm.yaml").read_text(encoding="utf-8")
    cloud_config = source_config.replace(
        "  my_llm:\n    enabled: true\n    type: local",
        "  my_llm:\n    enabled: true\n    type: cloud",
    )
    (config_dir / "llm.yaml").write_text(cloud_config, encoding="utf-8")

    for relative_path in (
        Path("config/permissions/permissions.yaml"),
        Path("config/sources/sources.yaml"),
        Path("config/filesystem.yaml"),
    ):
        target = config_dir / relative_path.relative_to("config")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(relative_path.read_bytes())

    application = bootstrap(
        ApplicationPaths(config_dir=config_dir, data_dir=tmp_path / "data")
    )

    guarded = application.agent.integration.runtime.provider
    assert isinstance(guarded, ConsentGuardedProvider)

    spy = SpyCloudProvider()
    guarded._provider = spy
    guarded._consent_provider = PendingConsent()

    session = ConversationSession()
    answer = application.agent.run("Summarize my private notes", session)

    assert answer == (
        "Cloud transfer to 'my_llm' is awaiting consent. "
        "No data was sent by this request."
    )
    assert spy.calls == 0
    assert [message.role for message in session.get_messages()] == ["user"]
