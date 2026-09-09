from pathlib import Path

from personal_memory.cli import main
from personal_memory.get import get_note

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


def test_get_by_id_keeps_frontmatter() -> None:
    doc = get_note(DEMO, "alex-rivera")
    assert doc is not None
    assert doc.meta.id == "alex-rivera"
    assert doc.meta.status == "current"
    assert doc.path.as_posix() == "20-identity/alex-rivera.md"
    assert doc.text.startswith("---")
    assert "id: alex-rivera" in doc.text
    assert "Economics lecturer" in doc.text


def test_get_by_relative_path() -> None:
    doc = get_note(DEMO, "20-identity/alex-rivera.md")
    assert doc is not None
    assert doc.meta.id == "alex-rivera"
    assert doc.text.startswith("---")


def test_get_returns_superseded_note() -> None:
    doc = get_note(DEMO, "teaching-load-2026-01")
    assert doc is not None
    assert doc.meta.status == "superseded"
    assert "Four courses" in doc.text


def test_get_missing_is_none() -> None:
    assert get_note(DEMO, "no-such-note") is None
    assert get_note(DEMO, "../outside.md") is None


def test_cli_get_prints_note(capsys) -> None:
    code = main(["get", str(DEMO), "alex-rivera"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.startswith("---")
    assert "id: alex-rivera" in captured.out
    assert "Economics lecturer" in captured.out


def test_cli_get_missing_is_success(capsys) -> None:
    code = main(["get", str(DEMO), "no-such-note"])
    captured = capsys.readouterr()
    assert code == 0
    assert "the brain does not have this" in captured.out
