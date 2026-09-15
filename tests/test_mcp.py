import inspect
import shutil
from pathlib import Path

import pytest

from personal_memory.filing import QUEUE_DIR
from personal_memory.get import get_note
from personal_memory.mcp import make_server

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"

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


def _tools(brain: Path, sources: str = "sources"):
    return {tool.name: tool.fn for tool in make_server(brain, sources)._tool_manager.list_tools()}


def test_mcp_cli_exposes_sources(capsys, _cli) -> None:
    assert _cli(["mcp", "--help"]) == 0
    assert "--sources" in capsys.readouterr().out


def test_tool_names_are_the_seven_human_verbs() -> None:
    fns = _tools(DEMO)
    assert tuple(fns) == (
        "remember",
        "revisit",
        "inbox",
        "draft",
        "pending",
        "file",
        "note",
    )
    assert "title" not in inspect.signature(fns["note"]).parameters
    draft = inspect.signature(fns["draft"]).parameters
    assert tuple(draft) == (
        "kind",
        "provenance",
        "confidence",
        "as_of",
        "path",
        "id",
        "type",
        "title",
        "body",
        "aliases",
        "source",
        "supersedes",
        "target",
        "claim",
    )


def test_inbox_lists_unfiled_sources(brain: Path) -> None:
    result = _tools(brain)["inbox"]()
    assert "sources/dean-email.md" in result["unfiled"]


def test_inbox_uses_named_sources_dir(tmp_path: Path) -> None:
    (tmp_path / "70-sources").mkdir()
    (tmp_path / "70-sources" / "x.md").write_text("x\n", encoding="utf-8")
    result = _tools(tmp_path, sources="70-sources")["inbox"]()
    assert result["unfiled"] == ["70-sources/x.md"]


def test_draft_queues_and_writes_nothing(brain: Path) -> None:
    result = _tools(brain)["draft"](**CREATE)
    assert result["status"] == "queued"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()


def test_pending_lists_waiting_drafts(brain: Path) -> None:
    fns = _tools(brain)
    fns["draft"](**CREATE)
    result = fns["pending"]()
    assert len(result["items"]) == 1
    assert result["items"][0]["proposal"]["id"] == "dana-whitfield"


def test_file_without_id_skips_low_confidence(brain: Path) -> None:
    low = dict(CREATE, provenance="agent:cursor, 2026-09-10")
    del low["source"]
    fns = _tools(brain)
    queued = fns["draft"](**low)
    assert queued["confidence"] == "medium"
    result = fns["file"]()
    assert result["outcomes"][0]["status"] == "queued"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()


def test_file_and_note_leave_sources_untouched(brain: Path) -> None:
    source = brain / "sources" / "dean-email.md"
    before = source.read_text(encoding="utf-8")
    fns = _tools(brain)
    fns["draft"](**CREATE)
    fns["file"]()
    fns["note"](
        claim="Samir will draft the first case.",
        provenance="user, 2026-09-10",
        target="samir-okonkwo",
        as_of="2026-09-10",
    )
    assert source.read_text(encoding="utf-8") == before


def test_note_without_provenance_is_blocked_outcome(brain: Path) -> None:
    result = _tools(brain)["note"](claim="A fact.", target="alex-rivera")
    assert result["status"] == "blocked"
    assert "provenance" in (result["reason"] or "")
    assert "A fact." not in get_note(brain, "alex-rivera").text


def test_note_empty_claim_is_blocked_outcome(brain: Path) -> None:
    result = _tools(brain)["note"](claim="", provenance="user", target="alex-rivera")
    assert result["status"] == "blocked"
    assert "claim" in (result["reason"] or "")
    assert get_note(brain, "alex-rivera").text


def test_draft_bad_payload_is_blocked_outcome(brain: Path) -> None:
    fns = _tools(brain)
    empty = fns["draft"]()
    assert empty["status"] == "blocked"
    assert empty["reason"]
    assert list((brain / QUEUE_DIR).glob("*.json")) == []

    partial = fns["draft"](kind="create", provenance="user, 2026-09-10")
    assert partial["status"] == "blocked"
    assert "as_of" in (partial["reason"] or "")
