import os
from pathlib import Path

from personal_ai.application.bootstrap import bootstrap
from personal_ai.application.paths import ApplicationPaths
from personal_ai.core.conversation_session import ConversationSession
from personal_ai.i18n import (
    DEFAULT_LANGUAGE,
    Translator,
    resolve_language,
)

DATA_DIR = Path("demo_runtime_data")


def create_application():
    config_dir = Path(os.environ.get("PERSONAL_AI_CONFIG_DIR", "config"))

    paths = ApplicationPaths(
        config_dir=config_dir,
        data_dir=DATA_DIR,
    )
    return bootstrap(paths)


def normalize_command(value: str) -> str:
    command = value.strip().lower()

    command = command.removeprefix("/")

    aliases = {
        "h": "help",
        "?": "help",
        "q": "exit",
        "quit": "exit",
        "lang": "language",
    }

    return aliases.get(command, command)


def _provider_name(application) -> str:
    return type(application.agent.integration.runtime.provider).__name__


def _provider_id() -> str:
    return os.environ.get("PERSONAL_AI_LLM_PROVIDER", "fake")


def print_banner(translator: Translator, application) -> None:
    print()
    print("=" * 64)
    print(f" {translator('title')}")
    print("=" * 64)
    print(f" {translator('provider')}: {_provider_name(application)}")
    print(f" {translator('security')}: {translator('deny_by_default')}")
    print()
    print(f" {translator('commands')}")
    print(f"   /help       {translator('help')}")
    print(f"   /security   {translator('security_command')}")
    print(f"   /config     {translator('config')}")
    print(f"   /session    {translator('session')}")
    print(f"   /clear      {translator('clear')}")
    print(f"   /self-test  {translator('self_test')}")
    print(f"   /language   {translator('language')}")
    print(f"   /exit       {translator('exit')}")
    print()
    print(f" {translator('input_hint')}")
    print("=" * 64)
    print()


def show_config(application, translator: Translator) -> None:
    provider_id = _provider_id()

    print()
    print(translator("runtime_configuration"))
    print("-" * 32)
    print(f"{translator('provider_mode')}: {provider_id}")
    print(f"{translator('provider')}: {_provider_name(application)}")
    print()


def show_security(application, translator: Translator) -> None:
    permission = application.permission_evaluator.evaluate(
        "local_filesystem",
        "read",
    )

    print()
    print(translator("security_boundary"))
    print("-" * 32)
    print(f"{translator('filesystem_read')}: {permission}")
    print()

    if permission == "denied":
        print(f"{translator('pass')}: {translator('filesystem_denied')}")
    else:
        print(f"{translator('warning')}: {translator('filesystem_not_denied')}")
    print()


def show_session(session, translator: Translator) -> None:
    print()
    print(translator("conversation_session"))
    print("-" * 32)

    if not session.messages:
        print(translator("empty"))
        print()
        return

    for index, message in enumerate(session.messages, start=1):
        print(f"[{index}] {message.role}: {message.content}")

    print()


def run_self_test(application, translator: Translator) -> bool:
    print()
    print("=" * 64)
    print(f" {translator('self_test')}")
    print("=" * 64)

    checks = []

    provider = application.agent.integration.runtime.provider
    checks.append(
        (
            translator("provider"),
            provider is not None,
        )
    )

    permission = application.permission_evaluator.evaluate(
        "local_filesystem",
        "read",
    )
    checks.append(
        (
            translator("check_filesystem"),
            permission == "denied",
        )
    )

    session = ConversationSession()
    result = application.agent.run(
        "Run a safe release smoke test.",
        session,
    )

    checks.append(
        (
            translator("check_agent_response"),
            isinstance(result, str) and bool(result.strip()),
        )
    )

    checks.append(
        (
            translator("check_assistant_message"),
            bool(session.messages)
            and session.messages[-1].role == "assistant",
        )
    )

    checks.append(
        (
            translator("check_data_isolation"),
            not DATA_DIR.exists(),
        )
    )

    print()

    all_passed = True

    for name, passed in checks:
        status = translator("pass") if passed else translator("fail")
        print(f"[{status}] {name}")
        all_passed = all_passed and passed

    print()

    if not all_passed:
        print(f"{translator('self_test_result')}: {translator('fail')}")
        print("=" * 64)
        return False

    print(f"{translator('self_test_result')}: {translator('pass')}")
    print("=" * 64)
    print()

    return True


def show_language(translator: Translator) -> None:
    print()
    print(translator("language_selection"))
    print("-" * 32)
    print("vi  - Tiếng Việt")
    print("en  - English")
    print("zh  - 中文")
    print()


def main() -> int:
    application = create_application()
    session = ConversationSession()

    language = DEFAULT_LANGUAGE
    translator = Translator(language)

    print_banner(translator, application)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print(translator("goodbye"))
            return 0

        if not user_input:
            continue

        command = normalize_command(user_input)

        if command == "exit":
            print(translator("goodbye"))
            return 0

        if command == "help":
            print_banner(translator, application)
            continue

        if command == "security":
            show_security(application, translator)
            continue

        if command == "config":
            show_config(application, translator)
            continue

        if command == "session":
            show_session(session, translator)
            continue

        if command == "clear":
            session = ConversationSession()
            print(translator("session_cleared"))
            print()
            continue

        if command == "self-test":
            run_self_test(application, translator)
            continue

        if command == "language":
            parts = user_input.strip().split(maxsplit=1)

            if len(parts) == 1:
                show_language(translator)
                continue

            try:
                language = resolve_language(parts[1])
            except ValueError:
                print()
                print(translator("unsupported_language"))
                print()
                continue

            translator = Translator(language)

            print()
            print(translator("language_changed"))
            print_banner(translator, application)
            continue

        try:
            result = application.agent.run(
                user_input,
                session,
            )

            print(f"AI: {result}")
            print()

        except Exception as exc:  # noqa: BLE001
            print()
            print(f"{translator('error')}: {type(exc).__name__}: {exc}")
            print()


if __name__ == "__main__":
    raise SystemExit(main())
