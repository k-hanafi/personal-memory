from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.frontmatter import (
    FRONTMATTER_RE,
    Frontmatter,
    FrontmatterError,
    parse_frontmatter,
    split_frontmatter,
)

SKIP_NAMES = frozenset({"README.md", "AGENTS.md", "CHANGELOG.md"})


@dataclass(frozen=True)
class Note:
    path: Path
    relative: Path
    text: str
    meta: Frontmatter
    body: str
    body_start_line: int
    title: str

    @property
    def aliases(self) -> str:
        return self.meta.extra.get("aliases", "")


def markdown_paths(root: Path) -> list[Path]:
    return [path for path in sorted(root.rglob("*.md")) if path.name not in SKIP_NAMES]


def load_notes(root: Path) -> list[Note]:
    notes: list[Note] = []
    for path in markdown_paths(root):
        note = load_note(root, path)
        if note is not None:
            notes.append(note)
    return notes


def load_note(root: Path, path: Path, text: str | None = None) -> Note | None:
    note, _error = try_load_note(root, path, text)
    return note


def try_load_note(
    root: Path, path: Path, text: str | None = None
) -> tuple[Note | None, str | None]:
    """Return (note, None), (None, None) if skipped, or (None, message) if invalid."""
    if path.name in SKIP_NAMES:
        return None, None
    if text is None:
        text = path.read_text(encoding="utf-8")
    try:
        split = split_frontmatter(text)
    except FrontmatterError as exc:
        return None, str(exc)
    if split is None:
        return None, None
    fields, body = split
    try:
        meta = parse_frontmatter(fields)
    except FrontmatterError as exc:
        return None, str(exc)
    return (
        Note(
            path=path,
            relative=path.relative_to(root),
            text=text,
            meta=meta,
            body=body,
            body_start_line=_body_start_line(text),
            title=_title_of(body, meta.id),
        ),
        None,
    )


def _body_start_line(text: str) -> int:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        return 1
    return text[: match.end()].count("\n") + 1


def _title_of(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback
