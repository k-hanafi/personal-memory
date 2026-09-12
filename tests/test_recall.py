from pathlib import Path

from personal_memory.cli import main
from personal_memory.recall import recall

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"
BRAIN = Path(__file__).resolve().parents[1] / "evals" / "brain"


def _write_note(root: Path, name: str, note_id: str, status: str, title: str, body: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_text(
        f"---\nid: {note_id}\ntype: area\nas_of: 2026-09-01\nstatus: {status}\nconfidence: high\n---\n\n"
        f"# {title}\n\n{body}\n",
        encoding="utf-8",
    )


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


def test_claim_line_wikilink_hops_to_department_chair() -> None:
    result = recall(BRAIN, "who is the department chair")
    paths = [str(card.path) for card in result.cards]
    assert paths[:2] == ["50-people/dana-whitfield.md", "40-areas/department-service.md"]
    assert result.cards[0].start_line == 11


def test_hop_target_superseded_is_added_only_with_historical(tmp_path: Path) -> None:
    _write_note(tmp_path, "source.md", "source", "current", "Source", "The chair is [[dana]].")
    _write_note(tmp_path, "dana.md", "dana", "superseded", "Dana", "Retired.")
    assert [str(card.path) for card in recall(tmp_path, "chair").cards] == ["source.md"]
    historical = recall(tmp_path, "chair", historical=True)
    assert [(str(card.path), card.status) for card in historical.cards] == [
        ("dana.md", "superseded"),
        ("source.md", "current"),
    ]
    assert historical.cards[0].claim == "Dana"


def test_broken_wikilink_on_claim_line_is_ignored(tmp_path: Path) -> None:
    _write_note(tmp_path, "source.md", "source", "current", "Source", "The chair is [[no-such-note]].")
    result = recall(tmp_path, "chair")
    assert [str(card.path) for card in result.cards] == ["source.md"]


def test_hops_do_not_chain(tmp_path: Path) -> None:
    _write_note(tmp_path, "source.md", "source", "current", "Source", "The chair is [[middle]].")
    _write_note(tmp_path, "middle.md", "middle", "current", "Middle", "See [[far]].")
    _write_note(tmp_path, "far.md", "far", "current", "Far", "Nothing here.")
    result = recall(tmp_path, "chair")
    assert [str(card.path) for card in result.cards] == ["middle.md", "source.md"]
    assert result.cards[0].claim == "Middle"


def test_unlabeled_wikilink_uses_id_labeled_uses_label(tmp_path: Path) -> None:
    _write_note(tmp_path, "unlabeled.md", "unlabeled", "current", "Unlabeled", "See [[zirconium-note]].")
    _write_note(tmp_path, "labeled.md", "labeled", "current", "Labeled", "See [[zirconium-note|the metal]].")
    assert [str(card.path) for card in recall(tmp_path, "zirconium").cards] == ["unlabeled.md"]
    assert [str(card.path) for card in recall(tmp_path, "metal").cards] == ["labeled.md"]


def test_query_without_claim_line_wikilinks_is_unchanged() -> None:
    result = recall(DEMO, "teaching load")
    assert [card.path.name for card in result.cards] == ["teaching-load-2026-09.md"]
    assert result.cards[0].claim == "Teaching load (fall)"
    assert result.cards[0].start_line == 10


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
