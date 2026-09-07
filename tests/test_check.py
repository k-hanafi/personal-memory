from pathlib import Path

from personal_memory.check import check_brain
from personal_memory.frontmatter import FrontmatterError, parse_frontmatter, split_frontmatter

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


def test_demo_brain_passes_check() -> None:
    result = check_brain(DEMO)
    assert result.ok, [f"{i.path.name}: {i.message}" for i in result.issues]
    assert result.notes >= 6


def test_split_skips_files_without_frontmatter() -> None:
    assert split_frontmatter("# just a heading\n") is None


def test_parse_rejects_non_kebab_id() -> None:
    try:
        parse_frontmatter(
            {
                "id": "Teaching Load",
                "type": "area",
                "as_of": "2026-09-01",
                "status": "current",
                "confidence": "high",
            }
        )
    except FrontmatterError as exc:
        assert "kebab-case" in str(exc)
    else:
        raise AssertionError("expected FrontmatterError")


def test_parse_rejects_bad_status() -> None:
    try:
        parse_frontmatter(
            {
                "id": "teaching-load",
                "type": "area",
                "as_of": "2026-09-01",
                "status": "active",
                "confidence": "high",
            }
        )
    except FrontmatterError as exc:
        assert "status" in str(exc)
    else:
        raise AssertionError("expected FrontmatterError")
