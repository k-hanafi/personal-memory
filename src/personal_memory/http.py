"""Hosted MCP: a client pastes a URL and a key.

The seven verbs stay the ones `make_server` already registers. Until Postgres
(order 13), the store is a markdown folder (or an empty temp folder).
"""

from __future__ import annotations

import hmac
import os
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from personal_memory.mcp import make_server

API_KEY_ENV = "PERSONAL_MEMORY_API_KEY"
MCP_PATH = "/mcp"


def resolve_api_key(cli_key: str | None = None) -> str:
    """Return the shared secret from `--key` or the env var. Empty is refused."""
    key = (cli_key or os.environ.get(API_KEY_ENV) or "").strip()
    if not key:
        raise ValueError(
            f"hosted MCP needs a key: pass --key or set {API_KEY_ENV}"
        )
    return key


def make_http_app(
    brain: Path,
    api_key: str,
    *,
    sources: str = "sources",
    host: str = "127.0.0.1",
) -> ASGIApp:
    """ASGI app at `/mcp`, gated by `Authorization: Bearer <key>`.

    `/health` is the one unauthenticated route (a process ping).
    """
    key = api_key.strip()
    if not key:
        raise ValueError("hosted MCP needs a non-empty key")
    server = make_server(brain, sources)

    @server.custom_route("/health", methods=["GET"])
    async def health(_request: Request) -> JSONResponse:
        return JSONResponse({"ok": True})

    inner = server.streamable_http_app(
        streamable_http_path=MCP_PATH,
        stateless_http=True,
        json_response=True,
        host=host,
    )
    return _ApiKeyGate(inner, key, _keep=server)


def serve_http(
    brain: Path,
    api_key: str,
    *,
    sources: str = "sources",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    """Block on the hosted MCP server. Callers print the URL themselves."""
    import uvicorn

    app = make_http_app(brain, api_key, sources=sources, host=host)
    uvicorn.run(app, host=host, port=port)


class _ApiKeyGate:
    """Pure ASGI wrapper so streaming MCP responses are not buffered."""

    def __init__(self, app: ASGIApp, api_key: str, *, _keep: object) -> None:
        self.app = app
        self._api_key = api_key
        self._keep = _keep

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope.get("path", "")
        if path.rstrip("/") == "/health":
            await self.app(scope, receive, send)
            return
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        token = _bearer_token(headers.get("authorization", ""))
        if token is None or not _keys_match(token, self._api_key):
            response = JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="personal-memory"'},
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _bearer_token(header: str) -> str | None:
    prefix = "bearer "
    if not header.lower().startswith(prefix):
        return None
    token = header[len(prefix) :].strip()
    return token or None


def _keys_match(provided: str, expected: str) -> bool:
    left = provided.encode("utf-8")
    right = expected.encode("utf-8")
    if len(left) != len(right):
        return False
    return hmac.compare_digest(left, right)
