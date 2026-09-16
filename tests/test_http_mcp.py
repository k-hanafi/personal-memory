import asyncio
import json
import shutil
import socket
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import httpx2
import pytest
import uvicorn
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from personal_memory.http import API_KEY_ENV, MCP_PATH, make_http_app, resolve_api_key
from personal_memory.mcp import make_server

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"
KEY = "test-key-not-for-production"

CREATE = {
    "kind": "create",
    "provenance": "user, 2026-09-10",
    "confidence": "high",
    "as_of": "2026-09-10",
    "path": "50-people/dana-whitfield.md",
    "id": "dana-whitfield",
    "type": "person",
    "title": "Dana Whitfield",
    "body": "Department chair. Works with [[alex-rivera]].",
    "source": "sources/dean-email.md",
}


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    root = tmp_path / "brain"
    shutil.copytree(DEMO, root)
    (root / "sources").mkdir()
    (root / "sources" / "dean-email.md").write_text("Sabbatical approved.\n", encoding="utf-8")
    return root


@pytest.fixture
def http_mcp(brain: Path) -> Iterator[str]:
    app = make_http_app(brain, KEY)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(80):
        if server.started:
            break
        time.sleep(0.05)
    else:
        raise RuntimeError("hosted MCP did not start")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def _payload(result) -> dict:
    assert result.is_error is False
    return json.loads(result.content[0].text)


async def _with_key(base: str, key: str, fn):
    url = base + MCP_PATH
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {key}"},
        timeout=httpx2.Timeout(10.0, read=30.0),
    ) as http:
        async with Client(streamable_http_client(url, http_client=http)) as client:
            return await fn(client)


def test_stdio_server_still_exposes_the_seven_verbs() -> None:
    names = tuple(tool.name for tool in make_server(DEMO)._tool_manager.list_tools())
    assert names == (
        "remember",
        "revisit",
        "inbox",
        "draft",
        "pending",
        "file",
        "note",
    )


def test_serve_help_is_url_plus_key(capsys, _cli) -> None:
    assert _cli(["serve", "--help"]) == 0
    out = capsys.readouterr().out
    assert "--key" in out
    assert API_KEY_ENV in out
    assert "--brain" in out


def test_serve_without_key_exits_2(capsys, _cli, monkeypatch) -> None:
    monkeypatch.delenv(API_KEY_ENV, raising=False)
    assert _cli(["serve"]) == 2
    assert API_KEY_ENV in capsys.readouterr().err


def test_serve_missing_brain_dir_exits_2(tmp_path: Path, capsys, _cli, monkeypatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, KEY)
    missing = tmp_path / "nope"
    assert _cli(["serve", "--brain", str(missing)]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_resolve_api_key_prefers_flag_over_env(monkeypatch) -> None:
    monkeypatch.setenv(API_KEY_ENV, "from-env-aaaaaaaa")
    assert resolve_api_key("from-flag-bbbbbbbb") == "from-flag-bbbbbbbb"
    assert resolve_api_key(None) == "from-env-aaaaaaaa"
    monkeypatch.delenv(API_KEY_ENV)
    with pytest.raises(ValueError, match=API_KEY_ENV):
        resolve_api_key(None)


def test_health_does_not_need_a_key(http_mcp: str) -> None:
    response = httpx2.get(f"{http_mcp}/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_mcp_without_key_is_401(http_mcp: str) -> None:
    response = httpx2.post(f"{http_mcp}{MCP_PATH}", json={"jsonrpc": "2.0", "id": 1, "method": "ping"})
    assert response.status_code == 401
    assert response.json() == {"error": "unauthorized"}
    assert "Bearer" in response.headers.get("www-authenticate", "")


def test_mcp_wrong_key_is_401(http_mcp: str) -> None:
    response = httpx2.post(
        f"{http_mcp}{MCP_PATH}",
        headers={"Authorization": "Bearer wrong-key-not-the-one"},
        json={"jsonrpc": "2.0", "id": 1, "method": "ping"},
    )
    assert response.status_code == 401


def test_http_lists_the_same_seven_verbs(http_mcp: str) -> None:
    async def list_names(client: Client) -> list[str]:
        result = await client.list_tools()
        return [tool.name for tool in result.tools]

    names = asyncio.run(_with_key(http_mcp, KEY, list_names))
    assert names == [
        "remember",
        "revisit",
        "inbox",
        "draft",
        "pending",
        "file",
        "note",
    ]


def test_http_remember_returns_evidence_cards(http_mcp: str) -> None:
    async def remember(client: Client) -> dict:
        return _payload(await client.call_tool("remember", {"query": "alex rivera"}))

    payload = asyncio.run(_with_key(http_mcp, KEY, remember))
    paths = [card["path"] for card in payload["cards"]]
    assert "20-identity/alex-rivera.md" in paths
    card = next(c for c in payload["cards"] if c["path"].endswith("alex-rivera.md"))
    assert card["status"] == "current"
    assert card["start_line"] <= card["end_line"]


def test_http_write_verbs_use_the_folder_stub(http_mcp: str, brain: Path) -> None:
    async def write_path(client: Client) -> None:
        inbox = _payload(await client.call_tool("inbox", {}))
        assert "sources/dean-email.md" in inbox["unfiled"]
        queued = _payload(await client.call_tool("draft", CREATE))
        assert queued["status"] == "queued"
        pending = _payload(await client.call_tool("pending", {}))
        assert pending["items"][0]["proposal"]["id"] == "dana-whitfield"
        filed = _payload(await client.call_tool("file", {}))
        assert filed["outcomes"][0]["status"] == "inserted"
        noted = _payload(
            await client.call_tool(
                "note",
                {
                    "claim": "Samir will draft the first case.",
                    "provenance": "user, 2026-09-10",
                    "target": "samir-okonkwo",
                    "as_of": "2026-09-10",
                },
            )
        )
        assert noted["status"] == "inserted"
        opened = _payload(await client.call_tool("revisit", {"key": "dana-whitfield"}))
        assert opened["path"] == "50-people/dana-whitfield.md"
        assert "Dana Whitfield" in (opened["text"] or "")

    asyncio.run(_with_key(http_mcp, KEY, write_path))
    assert (brain / "50-people" / "dana-whitfield.md").exists()
    source = brain / "sources" / "dean-email.md"
    assert source.read_text(encoding="utf-8") == "Sabbatical approved.\n"
