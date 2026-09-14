from pathlib import Path

from personal_memory.get import get_note
from personal_memory.notes import SKIP_NAMES

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


def test_get_by_path_skips_protocol_names(tmp_path: Path) -> None:
    text = (
        "---\nid: readme\ntype: area\nas_of: 2026-09-01\n"
        "status: current\nconfidence: high\n---\n\n# Readme\n"
    )
    for name in SKIP_NAMES:
        (tmp_path / name).write_text(text, encoding="utf-8")
        assert get_note(tmp_path, name) is None
        assert get_note(tmp_path, "readme") is None


def test_cli_revisit_prints_note(capsys, _cli) -> None:
    code = _cli(["revisit", str(DEMO), "alex-rivera"])
    captured = capsys.readouterr()
    assert code == 0
    assert captured.out.startswith("---")
    assert "id: alex-rivera" in captured.out
    assert "Economics lecturer" in captured.out


def test_cli_revisit_missing_is_success(capsys, _cli) -> None:
    code = _cli(["revisit", str(DEMO), "no-such-note"])
    captured = capsys.readouterr()
    assert code == 0
    assert "the brain does not have this" in captured.out


def test_cli_get_is_unknown(_cli) -> None:
    assert _cli(["get", str(DEMO), "alex-rivera"]) == 2
