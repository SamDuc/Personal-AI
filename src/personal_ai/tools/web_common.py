from __future__ import annotations

import http.client
import ipaddress
import json
import socket
from html.parser import HTMLParser
from typing import ClassVar
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

USER_AGENT = "PersonalAI-WebResearch/0.1"
TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 1_000_000


class UnsafeURLError(ValueError):
    pass


def validate_public_https_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise UnsafeURLError("URL must be a non-empty string.")
    try:
        parsed = urlsplit(url.strip())
        port = parsed.port
    except ValueError as exc:
        raise UnsafeURLError("URL is malformed.") from exc
    if parsed.scheme.lower() != "https":
        raise UnsafeURLError("Only HTTPS URLs are allowed.")
    if not parsed.hostname or parsed.username or parsed.password:
        raise UnsafeURLError("URL must have a hostname and no embedded credentials.")
    if port not in (None, 443):
        raise UnsafeURLError("Only the standard HTTPS port is allowed.")

    host = parsed.hostname.rstrip(".")
    if host.lower() == "localhost" or host.lower().endswith(".localhost"):
        raise UnsafeURLError("Localhost URLs are blocked.")
    try:
        literal_ip = ipaddress.ip_address(host)
    except ValueError:
        literal_ip = None
    if literal_ip is not None:
        if not literal_ip.is_global:
            raise UnsafeURLError("Non-public IP addresses are blocked.")
    else:
        try:
            addresses = {
                item[4][0]
                for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
            }
        except OSError as exc:
            raise UnsafeURLError("Hostname could not be resolved.") from exc
        if not addresses:
            raise UnsafeURLError("Hostname did not resolve to an address.")
        for address in addresses:
            try:
                ip = ipaddress.ip_address(address)
            except ValueError as exc:
                raise UnsafeURLError("Hostname resolved to an invalid IP address.") from exc
            if not ip.is_global:
                raise UnsafeURLError("Hostname resolves to a non-public IP address.")
    return parsed.geturl()



class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to a validated public IP while preserving TLS hostname checks."""

    def connect(self) -> None:
        if self._tunnel_host:
            raise UnsafeURLError("HTTPS proxy tunneling is not permitted.")

        try:
            addresses = socket.getaddrinfo(
                self.host, self.port, type=socket.SOCK_STREAM
            )
        except OSError as exc:
            raise UnsafeURLError(
                "Hostname could not be resolved at connection time."
            ) from exc

        if not addresses:
            raise UnsafeURLError("Hostname did not resolve to an address.")

        # Reject the entire hostname if ANY answer is non-public.
        for family, socktype, proto, _canonname, sockaddr in addresses:
            try:
                ip = ipaddress.ip_address(sockaddr[0])
            except ValueError as exc:
                raise UnsafeURLError(
                    "Hostname resolved to an invalid IP address."
                ) from exc
            if not ip.is_global:
                raise UnsafeURLError(
                    "Hostname resolves to a non-public IP address."
                )

        last_error = None
        for family, socktype, proto, _canonname, sockaddr in addresses:
            sock = socket.socket(family, socktype, proto)
            try:
                sock.settimeout(self.timeout)
                if self.source_address:
                    sock.bind(self.source_address)
                # Connect to the exact sockaddr returned by the validated lookup.
                sock.connect(sockaddr)
                self.sock = self._context.wrap_socket(
                    sock, server_hostname=self.host
                )
                return
            except OSError as exc:
                last_error = exc
                sock.close()

        raise OSError(
            "Could not connect to any validated public address."
        ) from last_error


class PinnedHTTPSHandler(HTTPSHandler):
    def https_open(self, req):
        return self.do_open(
            _PinnedHTTPSConnection,
            req,
            context=self._context,
            check_hostname=self._check_hostname,
        )


class SafeRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urljoin(req.full_url, newurl)
        validate_public_https_url(target)
        return super().redirect_request(req, fp, code, msg, headers, target)


class RejectRedirectHandler(HTTPRedirectHandler):
    """Reject redirects for requests carrying search API credentials."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(
            req.full_url,
            code,
            "Redirects are not permitted for search API requests.",
            headers,
            fp,
        )


def fetch_bytes(url: str) -> tuple[str, str, bytes]:
    safe_url = validate_public_https_url(url)
    request = Request(
        safe_url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html, text/plain;q=0.9"},
        method="GET",
    )
    opener = build_opener(ProxyHandler({}), SafeRedirectHandler(), PinnedHTTPSHandler())
    try:
        with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
            final_url = validate_public_https_url(response.geturl())
            content_type = response.headers.get_content_type()
            if content_type not in ("text/html", "text/plain", "application/xhtml+xml"):
                raise ValueError("Only HTML and plain-text pages can be read.")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise RuntimeError(f"Website returned HTTP {exc.code}.") from exc
    except TimeoutError as exc:
        raise RuntimeError("Website request timed out.") from exc
    except URLError as exc:
        raise RuntimeError("Website could not be reached.") from exc
    except OSError as exc:
        raise RuntimeError("Website request failed.") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("Website response exceeded the 1 MB limit.")
    return final_url, content_type, body


def post_json(
    url: str,
    payload: dict[str, object],
    *,
    timeout_seconds: int = TIMEOUT_SECONDS,
) -> bytes:
    """POST JSON over pinned, public HTTPS without inheriting system proxies."""
    safe_url = validate_public_https_url(url)
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    request = Request(
        safe_url,
        data=encoded,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    opener = build_opener(ProxyHandler({}), RejectRedirectHandler(), PinnedHTTPSHandler())
    try:
        with opener.open(request, timeout=timeout_seconds) as response:
            validate_public_https_url(response.geturl())
            content_type = response.headers.get_content_type().lower()
            if content_type != "application/json" and not content_type.endswith("+json"):
                raise ValueError("Search provider did not return JSON.")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise RuntimeError(f"Search provider returned HTTP {exc.code}.") from exc
    except TimeoutError as exc:
        raise RuntimeError("Search provider request timed out.") from exc
    except URLError as exc:
        if isinstance(exc.reason, TimeoutError):
            raise RuntimeError("Search provider request timed out.") from exc
        raise RuntimeError("Search provider could not be reached.") from exc
    except OSError as exc:
        raise RuntimeError("Search provider request failed.") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("Search provider response exceeded the 1 MB limit.")
    return body


class VisibleTextParser(HTMLParser):
    BLOCKED: ClassVar[set[str]] = {"script", "style", "noscript", "svg", "canvas", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.blocked_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag in self.BLOCKED:
            self.blocked_depth += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.BLOCKED and self.blocked_depth:
            self.blocked_depth -= 1
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.blocked_depth:
            cleaned = " ".join(data.split())
            if cleaned:
                self.parts.append(cleaned)

    def text(self) -> str:
        return "\n".join(part for part in self.parts if part).strip()
