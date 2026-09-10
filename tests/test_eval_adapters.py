from pathlib import Path

from personal_memory.check import SKIP_NAMES
from personal_memory.evals.adapters import ADAPTERS, grep_adapter, recall_adapter

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"

NOTE = """---
id: {id}
type: area
as_of: 2026-09-01
status: {status}
confidence: {confidence}
---

# {title}

{body}
"""


def test_adapters_registry() -> None:
    assert sorted(ADAPTERS) == ["grep", "recall"]


def test_recall_adapter_current_only() -> None:
    hits = recall_adapter(DEMO, "teaching load", False)
    assert hits[0].path == "40-areas/teaching-load-2026-09.md"
    assert hits[0].status == "current"
    assert hits[0].confidence == "high"
    assert hits[0].start_line <= hits[0].end_line
    assert hits[0].contradicted_by == ()
    assert "40-areas/teaching-load-2026-01.md" not in [hit.path for hit in hits]


def test_recall_adapter_historical_includes_superseded() -> None:
    hits = recall_adapter(DEMO, "teaching load", True)
    by_path = {hit.path: hit for hit in hits}
    assert by_path["40-areas/teaching-load-2026-01.md"].status == "superseded"
    assert by_path["40-areas/teaching-load-2026-09.md"].status == "current"


def test_recall_adapter_no_match_is_empty() -> None:
    assert recall_adapter(DEMO, "quantum pineapple syllabus", False) == []


def test_grep_adapter_ignores_historical_and_reads_status() -> None:
    default = grep_adapter(DEMO, "teaching load", False)
    historical = grep_adapter(DEMO, "teaching load", True)
    assert default == historical
    by_path = {hit.path: hit for hit in default}
    assert by_path["40-areas/teaching-load-2026-01.md"].status == "superseded"
    assert by_path["40-areas/teaching-load-2026-09.md"].status == "current"
    assert by_path["40-areas/teaching-load-2026-09.md"].confidence == "high"
    assert {hit.path for hit in default[:2]} == {
        "40-areas/teaching-load-2026-01.md",
        "40-areas/teaching-load-2026-09.md",
    }
    for hit in default:
        assert hit.start_line == hit.end_line >= 1
        assert hit.contradicted_by == ()


def test_grep_adapter_ranks_by_count_then_path(tmp_path: Path) -> None:
    (tmp_path / "b.md").write_text(
        NOTE.format(id="b", status="current", confidence="high", title="B", body="budget budget budget"),
        encoding="utf-8",
    )
    (tmp_path / "a.md").write_text(
        NOTE.format(id="a", status="superseded", confidence="low", title="A", body="budget once"),
        encoding="utf-8",
    )
    (tmp_path / "c.md").write_text(
        NOTE.format(id="c", status="current", confidence="medium", title="C", body="budget once"),
        encoding="utf-8",
    )
    (tmp_path / "d.md").write_text(
        NOTE.format(id="d", status="current", confidence="medium", title="D", body="nothing relevant"),
        encoding="utf-8",
    )
    hits = grep_adapter(tmp_path, "Budget", False)
    assert [hit.path for hit in hits] == ["b.md", "a.md", "c.md"]
    assert hits[0].start_line == hits[0].end_line == 11
    assert (hits[1].status, hits[1].confidence) == ("superseded", "low")


def test_grep_adapter_first_matching_line_may_be_frontmatter(tmp_path: Path) -> None:
    (tmp_path / "n.md").write_text(
        NOTE.format(id="office-hours", status="current", confidence="high", title="Office hours", body="Tuesdays."),
        encoding="utf-8",
    )
    hits = grep_adapter(tmp_path, "office hours", False)
    assert hits[0].start_line == 2


def test_grep_adapter_no_frontmatter_gives_empty_status(tmp_path: Path) -> None:
    (tmp_path / "loose.md").write_text("# Loose page\n\nbudget talk\n", encoding="utf-8")
    (tmp_path / "broken.md").write_text("---\nid: Bad Id\n---\n\nbudget talk\n", encoding="utf-8")
    hits = grep_adapter(tmp_path, "budget", False)
    assert [(hit.path, hit.status, hit.confidence) for hit in hits] == [
        ("broken.md", "", ""),
        ("loose.md", "", ""),
    ]


def test_grep_adapter_no_match_is_empty() -> None:
    assert grep_adapter(DEMO, "quantum pineapple syllabus", False) == []
    assert grep_adapter(DEMO, "", False) == []


def test_grep_adapter_skips_protocol_files(tmp_path: Path) -> None:
    for name in SKIP_NAMES:
        (tmp_path / name).write_text("budget everywhere\n", encoding="utf-8")
    (tmp_path / "n.md").write_text(
        NOTE.format(id="n", status="current", confidence="high", title="N", body="budget"),
        encoding="utf-8",
    )
    assert [hit.path for hit in grep_adapter(tmp_path, "budget", False)] == ["n.md"]
