import json
import shutil
from pathlib import Path

import pytest

from personal_memory.check import check_brain
from personal_memory.filing import APPLIED_DIR, QUEUE_DIR, Proposal, apply, list_queue, remember, submit
from personal_memory.get import get_note
from personal_memory.recall import recall

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    root = tmp_path / "brain"
    shutil.copytree(DEMO, root)
    (root / "sources").mkdir()
    (root / "sources" / "dean-email.md").write_text("Sabbatical approved.\n", encoding="utf-8")
    return root


def _create(**overrides) -> Proposal:
    base = dict(
        kind="create",
        provenance="user, 2026-09-10",
        confidence="high",
        as_of="2026-09-10",
        path="50-people/dana-whitfield.md",
        id="dana-whitfield",
        type="person",
        title="Dana Whitfield",
        body="Department chair. Works with [[alex-rivera]].",
    )
    base.update(overrides)
    return Proposal(**base)


def test_submit_queues_a_valid_proposal(brain: Path) -> None:
    outcome = submit(brain, _create())
    assert outcome.status == "queued"
    assert outcome.confidence == "high"
    files = list((brain / QUEUE_DIR).glob("*.json"))
    assert [f.stem for f in files] == [outcome.proposal_id]
    assert outcome.placement["links"] == {"20-identity": 1}
    assert outcome.placement["type"] == {"50-people": 1}


def test_submit_is_idempotent_on_content(brain: Path) -> None:
    first = submit(brain, _create())
    second = submit(brain, _create())
    assert first.proposal_id == second.proposal_id
    assert len(list((brain / QUEUE_DIR).glob("*.json"))) == 1


def test_submit_refuses_empty_provenance(brain: Path) -> None:
    outcome = submit(brain, _create(provenance=" "))
    assert outcome.status == "blocked"
    assert "provenance is required" in outcome.reason
    assert not (brain / QUEUE_DIR).exists()


def test_submit_refuses_path_under_sources(brain: Path) -> None:
    outcome = submit(brain, _create(path="sources/dana.md"))
    assert outcome.status == "blocked"
    assert "immutable" in outcome.reason


def test_submit_refuses_path_outside_brain(brain: Path) -> None:
    outcome = submit(brain, _create(path="../escape.md"))
    assert outcome.status == "blocked"
    assert "outside the brain" in outcome.reason


def test_submit_refuses_bad_frontmatter(brain: Path) -> None:
    outcome = submit(brain, _create(id="Dana Whitfield"))
    assert outcome.status == "blocked"
    assert "kebab-case" in outcome.reason


def test_submit_reports_duplicate_id_and_names_target(brain: Path) -> None:
    outcome = submit(brain, _create(path="50-people/samir.md", id="samir-okonkwo", title="Someone else"))
    assert outcome.status == "duplicate"
    assert outcome.target == "samir-okonkwo"


def test_submit_reports_duplicate_title(brain: Path) -> None:
    outcome = submit(brain, _create(path="50-people/samir-2.md", id="samir-2", title="Samir Okonkwo"))
    assert outcome.status == "duplicate"
    assert outcome.target == "samir-okonkwo"
    assert "append to it instead" in outcome.reason


def test_agent_high_confidence_is_capped_to_medium_without_boring_signal(brain: Path) -> None:
    outcome = submit(brain, _create(provenance="agent:claude-code, 2026-09-10"))
    assert outcome.status == "queued"
    assert outcome.confidence == "medium"
    assert apply(brain)[0].status == "queued"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()


def test_source_under_sources_is_a_boring_signal(brain: Path) -> None:
    outcome = submit(brain, _create(provenance="agent:claude-code, 2026-09-10", source="sources/dean-email.md"))
    assert outcome.confidence == "high"


def test_missing_source_is_blocked(brain: Path) -> None:
    outcome = submit(brain, _create(source="sources/nope.md"))
    assert outcome.status == "blocked"


def test_apply_writes_high_confidence_create_and_archives(brain: Path) -> None:
    submitted = submit(brain, _create(source="sources/dean-email.md"))
    outcomes = apply(brain)
    assert [o.status for o in outcomes] == ["inserted"]
    note = get_note(brain, "dana-whitfield")
    assert note is not None
    assert note.meta.extra["provenance"] == "user, 2026-09-10"
    assert note.meta.extra["source"] == "sources/dean-email.md"
    assert "# Dana Whitfield" in note.text
    assert check_brain(brain).ok
    assert not (brain / QUEUE_DIR / f"{submitted.proposal_id}.json").exists()
    archived = json.loads((brain / APPLIED_DIR / f"{submitted.proposal_id}.json").read_text())
    assert archived["result"]["status"] == "inserted"


def test_apply_by_id_writes_medium_confidence(brain: Path) -> None:
    submitted = submit(brain, _create(provenance="agent:codex, 2026-09-10"))
    outcome = apply(brain, proposal_id=submitted.proposal_id)[0]
    assert outcome.status == "inserted"
    assert outcome.confidence == "medium"
    assert get_note(brain, "dana-whitfield").meta.confidence == "medium"


def test_apply_unknown_id_is_blocked(brain: Path) -> None:
    assert apply(brain, proposal_id="nope")[0].status == "blocked"


def test_append_adds_log_line_and_recall_dates_it(brain: Path) -> None:
    proposal = Proposal(
        "append", "user, 2026-09-10", "high", "2026-09-10", target="undergrad-case-competition", claim="First case locked: pricing at a bakery."
    )
    assert submit(brain, proposal).status == "queued"
    assert apply(brain)[0].status == "inserted"
    text = get_note(brain, "undergrad-case-competition").text
    assert text.rstrip().endswith("- 2026-09-10 | user, 2026-09-10 | First case locked: pricing at a bakery.")
    card = recall(brain, "case locked bakery pricing").cards[0]
    assert card.as_of == "2026-09-10"
    assert card.claim == "First case locked: pricing at a bakery."
    assert check_brain(brain).ok


def test_append_same_claim_twice_is_duplicate(brain: Path) -> None:
    proposal = Proposal("append", "user, 2026-09-10", "high", "2026-09-10", target="undergrad-case-competition", claim="Cases locked.")
    submit(brain, proposal)
    apply(brain)
    again = submit(brain, Proposal("append", "user, 2026-09-11", "high", "2026-09-11", target="undergrad-case-competition", claim="Cases locked!"))
    assert again.status == "duplicate"
    assert "already logs this claim" in again.reason


def test_append_to_superseded_note_is_blocked(brain: Path) -> None:
    proposal = Proposal("append", "user, 2026-09-10", "high", "2026-09-10", target="teaching-load-2026-01", claim="x")
    outcome = submit(brain, proposal)
    assert outcome.status == "blocked"
    assert "teaching-load-2026-09" in outcome.reason


def test_append_with_pipe_is_blocked(brain: Path) -> None:
    proposal = Proposal("append", "user", "high", "2026-09-10", target="undergrad-case-competition", claim="a | b")
    assert submit(brain, proposal).status == "blocked"


def test_supersede_writes_new_and_flips_old_in_one_apply(brain: Path) -> None:
    proposal = Proposal(
        "supersede",
        "user, 2027-01-05",
        "high",
        "2027-01-05",
        path="40-areas/teaching-load-2027-01.md",
        id="teaching-load-2027-01",
        type="area",
        title="Teaching load (fall)",
        body="Three courses.",
        supersedes="teaching-load-2026-09",
    )
    assert submit(brain, proposal).status == "queued"
    outcome = apply(brain)[0]
    assert outcome.status == "superseded"
    assert outcome.paths == ("40-areas/teaching-load-2026-09.md", "40-areas/teaching-load-2027-01.md")
    old = get_note(brain, "teaching-load-2026-09")
    assert old.meta.status == "superseded"
    assert old.meta.extra["superseded_by"] == "teaching-load-2027-01"
    assert old.meta.extra["supersedes"] == "teaching-load-2026-01"
    new = get_note(brain, "teaching-load-2027-01")
    assert new.meta.extra["supersedes"] == "teaching-load-2026-09"
    assert check_brain(brain).ok
    current = recall(brain, "teaching load").cards
    assert [str(c.path) for c in current] == ["40-areas/teaching-load-2027-01.md"]


def test_supersede_already_superseded_is_blocked(brain: Path) -> None:
    proposal = Proposal(
        "supersede", "user", "high", "2027-01-05", path="40-areas/x.md", id="x", type="area", title="X", supersedes="teaching-load-2026-01"
    )
    assert "already superseded" in submit(brain, proposal).reason


def test_list_queue_revalidates_against_the_current_brain(brain: Path) -> None:
    first = submit(brain, _create(provenance="agent:a, 2026-09-10"))
    second = submit(brain, _create(provenance="agent:b, 2026-09-10", path="50-people/dana-w.md", id="dana-w"))
    apply(brain, proposal_id=first.proposal_id)
    remaining = list_queue(brain)
    assert [q.proposal_id for q in remaining] == [second.proposal_id]
    assert remaining[0].outcome.status == "duplicate"
    assert remaining[0].outcome.target == "dana-whitfield"


def test_apply_revalidates_between_batch_writes(brain: Path) -> None:
    first = Proposal(
        "supersede",
        "user, 2027-01-05",
        "high",
        "2027-01-05",
        path="40-areas/teaching-load-2027-01.md",
        id="teaching-load-2027-01",
        type="area",
        title="Teaching load (fall)",
        body="Three courses.",
        supersedes="teaching-load-2026-09",
    )
    second = Proposal(
        "supersede",
        "user, 2027-01-06",
        "high",
        "2027-01-06",
        path="40-areas/teaching-load-2027-02.md",
        id="teaching-load-2027-02",
        type="area",
        title="Teaching load (winter)",
        body="Four courses.",
        supersedes="teaching-load-2026-09",
    )
    submit(brain, first)
    submit(brain, second)
    by_id = {outcome.proposal_id: outcome for outcome in apply(brain)}
    written = [outcome for outcome in by_id.values() if outcome.status == "superseded"]
    refused = [outcome for outcome in by_id.values() if outcome.status == "blocked"]
    assert len(written) == 1
    assert len(refused) == 1
    assert "already superseded" in (refused[0].reason or "")
    winner = written[0].target
    loser = "teaching-load-2027-02" if winner == "teaching-load-2027-01" else "teaching-load-2027-01"
    assert get_note(brain, "teaching-load-2026-09").meta.extra["superseded_by"] == winner
    assert get_note(brain, winner).meta.status == "current"
    assert get_note(brain, loser) is None
    remaining = list_queue(brain)
    assert [item.proposal_id for item in remaining] == [refused[0].proposal_id]
    assert remaining[0].outcome.status == "blocked"
    assert check_brain(brain).ok


def test_apply_second_create_at_same_path_stays_queued(brain: Path) -> None:
    first = _create()
    second = _create(as_of="2026-09-11", id="dana-other", title="Dana Other")
    submit(brain, first)
    submit(brain, second)
    by_id = {outcome.proposal_id: outcome for outcome in apply(brain)}
    written = [outcome for outcome in by_id.values() if outcome.status == "inserted"]
    refused = [outcome for outcome in by_id.values() if outcome.status == "blocked"]
    assert len(written) == 1
    assert len(refused) == 1
    assert "already exists" in (refused[0].reason or "")
    winner = written[0].target
    loser = "dana-other" if winner == "dana-whitfield" else "dana-whitfield"
    assert get_note(brain, winner) is not None
    assert get_note(brain, loser) is None
    assert [item.proposal_id for item in list_queue(brain)] == [refused[0].proposal_id]
    assert check_brain(brain).ok


def test_apply_second_append_of_same_claim_stays_queued(brain: Path) -> None:
    first = Proposal(
        "append", "user, 2026-09-10", "high", "2026-09-10", target="undergrad-case-competition", claim="Cases locked."
    )
    second = Proposal(
        "append", "user, 2026-09-11", "high", "2026-09-11", target="undergrad-case-competition", claim="Cases locked!"
    )
    submit(brain, first)
    submit(brain, second)
    by_id = {outcome.proposal_id: outcome for outcome in apply(brain)}
    written = [outcome for outcome in by_id.values() if outcome.status == "inserted"]
    refused = [outcome for outcome in by_id.values() if outcome.status == "duplicate"]
    assert len(written) == 1
    assert len(refused) == 1
    text = get_note(brain, "undergrad-case-competition").text
    assert text.count("Cases locked") == 1
    assert [item.proposal_id for item in list_queue(brain)] == [refused[0].proposal_id]
    assert check_brain(brain).ok


def test_remember_appends_when_target_given(brain: Path) -> None:
    outcome = remember(brain, "Samir will draft the first case.", "user, 2026-09-10", target="samir-okonkwo", as_of="2026-09-10")
    assert outcome.status == "inserted"
    assert outcome.paths == ("50-people/samir-okonkwo.md",)
    assert list_queue(brain) == []
    assert "- 2026-09-10 | user, 2026-09-10 | Samir will draft the first case." in get_note(brain, "samir-okonkwo").text


def test_remember_stub_creates_when_no_target(brain: Path) -> None:
    outcome = remember(
        brain, "Dana chairs the department.", "user, 2026-09-10", path="50-people/dana-whitfield.md", type="person", as_of="2026-09-10"
    )
    assert outcome.status == "inserted"
    note = get_note(brain, "dana-whitfield")
    assert note.text.startswith("---\nid: dana-whitfield\ntype: person\nas_of: 2026-09-10\nstatus: current\nconfidence: high\n")
    assert "# Dana whitfield" in note.text
    assert "## Log\n- 2026-09-10 | user, 2026-09-10 | Dana chairs the department." in note.text
    assert check_brain(brain).ok


def test_remember_from_agent_queues_instead_of_writing(brain: Path) -> None:
    outcome = remember(brain, "Dana chairs the department.", "agent:cursor, 2026-09-10", path="50-people/dana-whitfield.md", type="person")
    assert outcome.status == "queued"
    assert outcome.confidence == "medium"
    assert not (brain / "50-people" / "dana-whitfield.md").exists()
    assert len(list_queue(brain)) == 1


def test_remember_reports_duplicate_and_candidates(brain: Path) -> None:
    outcome = remember(brain, "Samir Okonkwo teaches finance.", "user", path="50-people/sam.md", type="person", title="Samir Okonkwo")
    assert outcome.status == "duplicate"
    assert outcome.target == "samir-okonkwo"
    assert "samir-okonkwo" in outcome.candidates


def test_remember_without_target_needs_path_and_type(brain: Path) -> None:
    assert remember(brain, "x", "user").status == "blocked"
