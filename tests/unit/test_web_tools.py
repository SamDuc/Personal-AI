from __future__ import annotations

import pytest

from personal_ai.tools.web_common import (
    UnsafeURLError,
    VisibleTextParser,
    validate_public_https_url,
)
from personal_ai.tools.web_fetch import WebFetchTool
from personal_ai.tools.web_search import WebSearchTool


class _Permission:
    def __init__(self, decision: str = "allowed") -> None:
        self.decision = decision
        self.calls: list[tuple[str, str]] = []

    def evaluate(self, *, resource_category: str, operation: str) -> str:
        self.calls.append((resource_category, operation))
        return self.decision


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "file:///C:/Windows/win.ini",
        "https://127.0.0.1/",
        "https://10.0.0.5/",
        "https://localhost/",
        "https://user:password@example.com/",
        "https://example.com:8443/",
    ],
)
def test_validate_public_https_url_blocks_unsafe_urls(url: str) -> None:
    with pytest.raises(UnsafeURLError):
        validate_public_https_url(url)


def test_validate_public_https_url_accepts_public_https_ip() -> None:
    assert validate_public_https_url("https://1.1.1.1/") == "https://1.1.1.1/"


def test_visible_text_parser_omits_script_and_style_content() -> None:
    parser = VisibleTextParser()
    parser.feed(
        "<h1>Public title</h1><script>secret()</script>"
        "<style>.hidden{display:none}</style><p>Visible paragraph</p>"
    )
    text = parser.text()
    assert "Public title" in text
    assert "Visible paragraph" in text
    assert "secret()" not in text
    assert "display:none" not in text


@pytest.mark.parametrize("tool", [WebSearchTool(), WebFetchTool()])
def test_web_tools_do_not_make_requests_when_permission_denied(
    monkeypatch: pytest.MonkeyPatch, tool
) -> None:
    def unexpected_request(*args, **kwargs):
        raise AssertionError("network must not be accessed when permission is denied")

    monkeypatch.setattr("personal_ai.tools.web_common.fetch_bytes", unexpected_request)
    monkeypatch.setattr("personal_ai.tools.web_fetch.fetch_bytes", unexpected_request)

    permission = _Permission("denied")
    if isinstance(tool, WebSearchTool):
        result = tool.execute({"query": "Python release notes"}, permission)
    else:
        result = tool.execute({"url": "https://example.com/"}, permission)

    assert result.status == "denied"
    assert permission.calls == [("browser", "read")]


def test_web_search_rejects_invalid_input_before_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_request(*args, **kwargs):
        raise AssertionError("network must not be accessed for invalid input")

    result = WebSearchTool().execute({"query": "  "}, _Permission())
    assert result.status == "invalid_input"


def test_web_fetch_rejects_invalid_input_before_network(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unexpected_request(*args, **kwargs):
        raise AssertionError("network must not be accessed for invalid input")

    monkeypatch.setattr("personal_ai.tools.web_fetch.fetch_bytes", unexpected_request)
    result = WebFetchTool().execute({"url": "  "}, _Permission())
    assert result.status == "invalid_input"
def test_pinned_https_connection_rejects_private_dns_at_connect_time(monkeypatch):
    import socket
    from unittest.mock import Mock

    import pytest

    from personal_ai.tools.web_common import (
        UnsafeURLError,
        _PinnedHTTPSConnection,
    )

    monkeypatch.setattr(
        "personal_ai.tools.web_common.socket.getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP,
             "", ("127.0.0.1", 443))
        ],
    )
    socket_factory = Mock()
    monkeypatch.setattr(
        "personal_ai.tools.web_common.socket.socket", socket_factory
    )

    connection = _PinnedHTTPSConnection("example.com", timeout=1)

    with pytest.raises(UnsafeURLError, match="non-public"):
        connection.connect()

    socket_factory.assert_not_called()


def test_pinned_https_connection_uses_validated_ip_and_tls_hostname(monkeypatch):
    import socket
    from unittest.mock import Mock

    from personal_ai.tools.web_common import _PinnedHTTPSConnection

    validated_address = ("93.184.216.34", 443)
    monkeypatch.setattr(
        "personal_ai.tools.web_common.socket.getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP,
             "", validated_address)
        ],
    )

    raw_socket = Mock()
    tls_socket = Mock()
    ssl_context = Mock()
    ssl_context.wrap_socket.return_value = tls_socket
    socket_factory = Mock(return_value=raw_socket)
    monkeypatch.setattr(
        "personal_ai.tools.web_common.socket.socket", socket_factory
    )

    connection = _PinnedHTTPSConnection(
        "example.com", timeout=1, context=ssl_context
    )
    connection.connect()

    raw_socket.connect.assert_called_once_with(validated_address)
    ssl_context.wrap_socket.assert_called_once_with(
        raw_socket, server_hostname="example.com"
    )
    assert connection.sock is tls_socket


class _FailingSearchProvider:
    def search(self, query: str, max_results: int) -> list[dict[str, str]]:
        raise RuntimeError("Search provider returned an anti-bot challenge.")


class _EmptySearchProvider:
    def search(self, query: str, max_results: int) -> list[dict[str, str]]:
        return []


def test_web_search_reports_provider_failure() -> None:
    result = WebSearchTool(provider=_FailingSearchProvider()).execute(
        {"query": "Python urllib HTTPS"},
        _Permission(),
    )
    assert result.status == "execution_failure"
    assert "anti-bot challenge" in result.error.lower()


def test_web_search_does_not_report_success_without_results() -> None:
    result = WebSearchTool(provider=_EmptySearchProvider()).execute(
        {"query": "Python urllib HTTPS"},
        _Permission(),
    )
    assert result.status == "execution_failure"
    assert "no usable results" in result.error.lower()

def test_reject_redirect_handler_blocks_redirect() -> None:
    from urllib.error import HTTPError
    from urllib.request import Request

    from personal_ai.tools.web_common import RejectRedirectHandler

    request = Request("https://api.tavily.com/search", data=b"{}")
    with pytest.raises(HTTPError, match="Redirects are not permitted"):
        RejectRedirectHandler().redirect_request(
            request,
            None,
            302,
            "Found",
            {},
            "https://attacker.example/",
        )


def test_post_json_uses_redirect_rejection_handler(monkeypatch) -> None:
    from urllib.error import HTTPError

    from personal_ai.tools import web_common

    monkeypatch.setattr(
        web_common, "validate_public_https_url", lambda url: url
    )
    captured_handlers = []

    class FakeOpener:
        def open(self, request, timeout):
            raise HTTPError(
                request.full_url, 302, "Found", {}, None
            )

    def fake_build_opener(*handlers):
        captured_handlers.extend(handlers)
        return FakeOpener()

    monkeypatch.setattr(web_common, "build_opener", fake_build_opener)

    with pytest.raises(RuntimeError, match="HTTP 302"):
        web_common.post_json(
            "https://api.tavily.com/search",
            {"query": "test"},
            timeout_seconds=1,
        )

    assert any(
        isinstance(handler, web_common.RejectRedirectHandler)
        for handler in captured_handlers
    )


def test_post_json_converts_timeout_to_runtime_error(monkeypatch) -> None:
    from personal_ai.tools import web_common

    monkeypatch.setattr(
        web_common, "validate_public_https_url", lambda url: url
    )

    class TimeoutOpener:
        def open(self, request, timeout):
            raise TimeoutError("simulated timeout")

    monkeypatch.setattr(
        web_common, "build_opener", lambda *handlers: TimeoutOpener()
    )

    with pytest.raises(RuntimeError, match="timed out"):
        web_common.post_json(
            "https://api.tavily.com/search",
            {"query": "test"},
            timeout_seconds=1,
        )


def test_web_search_does_not_call_provider_when_denied() -> None:
    class SpyProvider:
        calls = 0

        def search(self, query: str, max_results: int) -> list[dict[str, str]]:
            self.calls += 1
            raise AssertionError("Provider must not be called when denied.")

    provider = SpyProvider()
    tool = WebSearchTool(provider=provider)
    permission = _Permission("denied")

    result = tool.execute({"query": "example query"}, permission)

    assert result.status == "denied"
    assert provider.calls == 0
    assert permission.calls == [("browser", "read")]
