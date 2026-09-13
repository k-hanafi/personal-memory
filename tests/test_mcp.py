import shutil
from pathlib import Path

import pytest

from personal_memory.get import get_note
from personal_memory.mcp import TOOL_NAMES, handle

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


def test_tool_names_are_the_seven_human_verbs() -> None:
    assert TOOL_NAMES == (
        "remember",
        "revisit",
        "inbox",
        "draft",
        "pending",
        "file",
        "note",
    )


def test_remember_cards_have_path_lines_and_freshness() -> None:
    result = handle("remember", DEMO, {"query": "teaching load"})
    cards = result["cards"]
    assert cards
    sept = next(card for card in cards if Path(card["path"]).name == "teaching-load-2026-09.md")
    assert sept["status"] == "current"
    assert sept["as_of"] == "2026-09-01"
    assert sept["confidence"]
    assert sept["claim"]
    assert sept["start_line"] >= 1
    assert sept["end_line"] >= sept["start_line"]
    names = {Path(card["path"]).name for card in cards}
    assert "teaching-load-2026-01.md" not in names


def test_remember_historical_includes_superseded() -> None:
    result = handle("remember", DEMO, {"query": "teaching load", "historical": True})
    by_name = {Path(card["path"]).name: card for card in result["cards"]}
    assert by_name["teaching-load-2026-01.md"]["status"] == "superseded"
    assert by_name["teaching-load-2026-09.md"]["status"] == "current"


def test_revisit_keeps_frontmatter() -> None:
    result = handle("revisit", DEMO, {"key": "alex-rivera"})
    assert result["text"].startswith("---")
    assert "id: alex-rivera" in result["text"]
    assert "Economics lecturer" in result["text"]
    assert result["path"] == "20-identity/alex-rivera.md"


def test_inbox_lists_unfiled_sources(brain: Path) -> None:
    result = handle("inbox", brain, {})
    assert "sources/dean-email.md" in result["unfiled"]


def test_draft_queues_and_writes_nothing(brain: Path) -> None:
    result = handle("draft", brain, {"proposal": CREATE})
    assert result["status"] == "queued"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()


def test_pending_lists_waiting_drafts(brain: Path) -> None:
    handle("draft", brain, {"proposal": CREATE})
    result = handle("pending", brain, {})
    assert len(result["items"]) == 1
    assert result["items"][0]["proposal"]["id"] == "dana-whitfield"


def test_file_without_id_skips_low_confidence(brain: Path) -> None:
    low = dict(CREATE, provenance="agent:cursor, 2026-09-10")
    del low["source"]
    queued = handle("draft", brain, {"proposal": low})
    assert queued["confidence"] == "medium"
    result = handle("file", brain, {})
    assert result["outcomes"][0]["status"] == "queued"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()


def test_file_and_note_leave_sources_untouched(brain: Path) -> None:
    source = brain / "sources" / "dean-email.md"
    before = source.read_text(encoding="utf-8")
    handle("draft", brain, {"proposal": CREATE})
    handle("file", brain, {})
    handle(
        "note",
        brain,
        {
            "claim": "Samir will draft the first case.",
            "provenance": "user, 2026-09-10",
            "target": "samir-okonkwo",
            "as_of": "2026-09-10",
        },
    )
    assert source.read_text(encoding="utf-8") == before


def test_note_writes_one_fact(brain: Path) -> None:
    result = handle(
        "note",
        brain,
        {
            "claim": "Samir will draft the first case.",
            "provenance": "user, 2026-09-10",
            "target": "samir-okonkwo",
            "as_of": "2026-09-10",
        },
    )
    assert result["status"] == "inserted"
    text = get_note(brain, "samir-okonkwo").text
    assert "- 2026-09-10 | user, 2026-09-10 | Samir will draft the first case." in text


def test_note_without_provenance_refuses(brain: Path) -> None:
    with pytest.raises(ValueError, match="provenance"):
        handle("note", brain, {"claim": "A fact.", "target": "alex-rivera"})
    assert "A fact." not in get_note(brain, "alex-rivera").text
