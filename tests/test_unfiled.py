import shutil
from pathlib import Path

import pytest

from personal_memory.filing import Proposal, apply, submit
from personal_memory.unfiled import unfiled

DEMO = Path(__file__).resolve().parents[1] / "examples" / "demo-brain"


@pytest.fixture
def brain(tmp_path: Path) -> Path:
    root = tmp_path / "brain"
    shutil.copytree(DEMO, root)
    sources = root / "sources"
    (sources / "2026-09").mkdir(parents=True)
    (sources / "dean-email.md").write_text("Sabbatical approved.\n", encoding="utf-8")
    (sources / "2026-09" / "syllabus.pdf").write_bytes(b"%PDF-1.4")
    (sources / ".DS_Store").write_bytes(b"")
    return root


def test_everything_is_unfiled_at_first(brain: Path) -> None:
    result = unfiled(brain)
    assert result.sources == 2
    assert [p.as_posix() for p in result.unfiled] == ["sources/2026-09/syllabus.pdf", "sources/dean-email.md"]


def test_no_sources_folder_means_nothing_to_file(tmp_path: Path) -> None:
    assert unfiled(tmp_path).sources == 0


def test_created_note_with_source_files_it(brain: Path) -> None:
    submit(
        brain,
        Proposal(
            "create",
            "agent:codex, 2026-09-10",
            "high",
            "2026-09-10",
            path="30-projects/sabbatical.md",
            id="sabbatical",
            type="project",
            title="Sabbatical",
            source="sources/dean-email.md",
        ),
    )
    apply(brain)
    assert [p.as_posix() for p in unfiled(brain).unfiled] == ["sources/2026-09/syllabus.pdf"]


def test_log_line_with_source_provenance_files_it(brain: Path) -> None:
    submit(
        brain,
        Proposal(
            "append",
            "source:sources/2026-09/syllabus.pdf",
            "high",
            "2026-09-10",
            target="teaching-load-2026-09",
            claim="Syllabus for econometrics posted.",
        ),
    )
    apply(brain)
    assert [p.as_posix() for p in unfiled(brain).unfiled] == ["sources/dean-email.md"]


def test_custom_sources_folder(tmp_path: Path) -> None:
    (tmp_path / "70-sources").mkdir()
    (tmp_path / "70-sources" / "x.md").write_text("x\n", encoding="utf-8")
    result = unfiled(tmp_path, sources_dir="70-sources")
    assert [p.as_posix() for p in result.unfiled] == ["70-sources/x.md"]
