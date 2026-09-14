from pathlib import Path

from personal_memory.check import check_brain
from personal_memory.notelog import append_entry, parse_log
from personal_memory.recall import recall

NOTE = """---
id: sabbatical-plan
type: project
as_of: 2026-08-01
status: current
confidence: high
---

# Sabbatical plan

Start date undecided.

## Log
- 2026-09-01 | user | Dean approved the sabbatical request.
- 2026-09-10 | agent:claude-code | Start date moved to January.
"""


def _brain(tmp_path: Path, text: str = NOTE) -> Path:
    (tmp_path / "30-projects").mkdir()
    (tmp_path / "30-projects" / "sabbatical-plan.md").write_text(text, encoding="utf-8")
    return tmp_path


def test_parse_log_reads_entries_in_order() -> None:
    section = parse_log(NOTE)
    assert section.present
    assert [e.date for e in section.entries] == ["2026-09-01", "2026-09-10"]
    assert section.entries[1].provenance == "agent:claude-code"
    assert section.entries[1].claim == "Start date moved to January."
    assert section.bad_lines == ()


def test_parse_log_stops_at_next_heading() -> None:
    text = NOTE + "\n## See also\n- not a log line\n"
    assert parse_log(text).bad_lines == ()


def test_append_entry_adds_after_last_entry() -> None:
    text = append_entry(NOTE, "2026-09-12", "user", "Funding confirmed.")
    lines = text.splitlines()
    assert lines[-1] == "- 2026-09-12 | user | Funding confirmed."
    assert lines[-2].startswith("- 2026-09-10")


def test_append_entry_creates_section_when_missing() -> None:
    plain = NOTE.split("## Log")[0]
    text = append_entry(plain, "2026-09-12", "user", "Funding confirmed.")
    section = parse_log(text)
    assert section.present
    assert [e.claim for e in section.entries] == ["Funding confirmed."]
    assert text.endswith("\n")


def test_check_rejects_malformed_log_line(tmp_path: Path) -> None:
    root = _brain(tmp_path, NOTE + "- no date here\n")
    result = check_brain(root)
    assert not result.ok
    assert "Log entry must be" in result.issues[0].message


def test_check_accepts_well_formed_log(tmp_path: Path) -> None:
    assert check_brain(_brain(tmp_path)).ok


def test_recall_card_on_log_line_uses_line_date(tmp_path: Path) -> None:
    result = recall(_brain(tmp_path), "start date moved January")
    card = result.cards[0]
    assert card.claim == "Start date moved to January."
    assert card.as_of == "2026-09-10"
    assert card.start_line == 15


def test_recall_card_on_state_line_uses_frontmatter_date(tmp_path: Path) -> None:
    result = recall(_brain(tmp_path), "start date undecided")
    card = result.cards[0]
    assert card.as_of == "2026-08-01"
