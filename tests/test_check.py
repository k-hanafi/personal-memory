from pathlib import Path

import pytest

from personal_memory.check import check_brain
from personal_memory.frontmatter import FrontmatterError, parse_frontmatter, split_frontmatter
from personal_memory.notes import SKIP_NAMES

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


def test_demo_brain_passes_check() -> None:
    result = check_brain(DEMO)
    assert result.ok, [f"{i.path.name}: {i.message}" for i in result.issues]
    assert result.notes >= 6


def test_check_skips_protocol_names_and_reports_invalid_frontmatter(tmp_path: Path) -> None:
    for name in SKIP_NAMES:
        (tmp_path / name).write_text("# protocol\n", encoding="utf-8")
    (tmp_path / "loose.md").write_text("# no frontmatter\n", encoding="utf-8")
    (tmp_path / "bad.md").write_text(
        "---\nid: Bad Id\ntype: area\nas_of: 2026-09-01\nstatus: current\nconfidence: high\n---\n\n# Bad\n",
        encoding="utf-8",
    )
    result = check_brain(tmp_path)
    assert result.notes == 0
    assert result.skipped == len(SKIP_NAMES) + 1
    assert not result.ok
    assert "kebab-case" in result.issues[0].message


def test_split_skips_files_without_frontmatter() -> None:
    assert split_frontmatter("# just a heading\n") is None


def test_parse_rejects_non_kebab_id() -> None:
    with pytest.raises(FrontmatterError, match="kebab-case"):
        parse_frontmatter(
            {
                "id": "Teaching Load",
                "type": "area",
                "as_of": "2026-09-01",
                "status": "current",
                "confidence": "high",
            }
        )


def test_parse_rejects_bad_status() -> None:
    with pytest.raises(FrontmatterError, match="status"):
        parse_frontmatter(
            {
                "id": "teaching-load",
                "type": "area",
                "as_of": "2026-09-01",
                "status": "active",
                "confidence": "high",
            }
        )
