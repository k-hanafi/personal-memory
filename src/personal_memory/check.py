from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.notes import SKIP_NAMES, try_load_note


@dataclass(frozen=True)
class NoteIssue:
    path: Path
    message: str


@dataclass(frozen=True)
class CheckResult:
    notes: int
    skipped: int
    issues: list[NoteIssue]

    @property
    def ok(self) -> bool:
        return not self.issues


def check_brain(root: Path) -> CheckResult:
    """Validate every markdown note under root.

    Files without frontmatter are skipped (protocol files, READMEs). Files
    that start with frontmatter must satisfy the v1 contract.
    """
    issues: list[NoteIssue] = []
    notes = 0
    skipped = 0
    seen_ids: dict[str, Path] = {}

    for path in sorted(root.rglob("*.md")):
        if path.name in SKIP_NAMES:
            skipped += 1
            continue
        note, error = try_load_note(root, path)
        if error is not None:
            issues.append(NoteIssue(path, error))
            continue
        if note is None:
            skipped += 1
            continue
        notes += 1
        previous = seen_ids.get(note.meta.id)
        if previous is not None:
            issues.append(
                NoteIssue(
                    path,
                    f"duplicate id {note.meta.id!r} (also {previous.relative_to(root)})",
                )
            )
        else:
            seen_ids[note.meta.id] = path

    return CheckResult(notes=notes, skipped=skipped, issues=issues)
