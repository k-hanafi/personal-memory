from pathlib import Path

from personal_memory.cli import main
from personal_memory.recall import recall

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


def test_present_tense_teaching_load_is_september_not_january() -> None:
    result = recall(DEMO, "teaching load")
    paths = [card.path.name for card in result.cards]
    assert "teaching-load-2026-09.md" in paths
    assert "teaching-load-2026-01.md" not in paths
    sept = next(card for card in result.cards if card.path.name == "teaching-load-2026-09.md")
    assert sept.status == "current"
    assert sept.as_of == "2026-09-01"
    assert sept.start_line >= 1
    assert sept.end_line >= sept.start_line
    assert sept.claim


def test_historical_includes_january_as_superseded() -> None:
    result = recall(DEMO, "teaching load", historical=True)
    by_name = {card.path.name: card for card in result.cards}
    assert by_name["teaching-load-2026-01.md"].status == "superseded"
    assert by_name["teaching-load-2026-09.md"].status == "current"
    assert by_name["teaching-load-2026-09.md"].contradicted_by == ()


def test_no_match_is_empty_not_an_error() -> None:
    result = recall(DEMO, "quantum pineapple syllabus")
    assert result.cards == ()


def test_exact_id_returns_that_note() -> None:
    result = recall(DEMO, "teaching-load-2026-09")
    assert len(result.cards) == 1
    card = result.cards[0]
    assert card.path.name == "teaching-load-2026-09.md"
    assert card.claim == "Teaching load (fall)"
    assert card.status == "current"


def test_two_current_matches_are_marked_contradicted() -> None:
    result = recall(DEMO, "case competition")
    current = [card for card in result.cards if card.status == "current"]
    assert len(current) >= 2
    paths = {str(card.path) for card in current}
    for card in current:
        assert set(card.contradicted_by) == paths - {str(card.path)}


def test_cli_recall_prints_september(capsys) -> None:
    code = main(["recall", str(DEMO), "teaching", "load"])
    captured = capsys.readouterr()
    assert code == 0
    assert "teaching-load-2026-09.md" in captured.out
    assert "teaching-load-2026-01.md" not in captured.out
    assert "current" in captured.out


def test_cli_recall_empty_is_success(capsys) -> None:
    code = main(["recall", str(DEMO), "quantum", "pineapple"])
    captured = capsys.readouterr()
    assert code == 0
    assert "the brain does not have this" in captured.out
