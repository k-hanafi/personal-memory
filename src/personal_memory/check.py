from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.frontmatter import FrontmatterError, parse_frontmatter, split_frontmatter

SKIP_NAMES = frozenset({"README.md", "AGENTS.md", "CHANGELOG.md"})


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
        text = path.read_text(encoding="utf-8")
        try:
            split = split_frontmatter(text)
        except FrontmatterError as exc:
            issues.append(NoteIssue(path, str(exc)))
            continue
        if split is None:
            skipped += 1
            continue
        fields, _body = split
        try:
            meta = parse_frontmatter(fields)
        except FrontmatterError as exc:
            issues.append(NoteIssue(path, str(exc)))
            continue
        notes += 1
        previous = seen_ids.get(meta.id)
        if previous is not None:
            issues.append(
                NoteIssue(
                    path,
                    f"duplicate id {meta.id!r} (also {previous.relative_to(root)})",
                )
            )
        else:
            seen_ids[meta.id] = path

    return CheckResult(notes=notes, skipped=skipped, issues=issues)
