from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.check import SKIP_NAMES
from personal_memory.frontmatter import Frontmatter, FrontmatterError, parse_frontmatter, split_frontmatter


@dataclass(frozen=True)
class NoteDoc:
    path: Path
    text: str
    meta: Frontmatter


def get_note(root: Path, key: str) -> NoteDoc | None:
    """Return one note by id or path, frontmatter included. None if missing."""
    key = key.strip()
    if not key:
        return None

    by_path = _from_path(root, key)
    if by_path is not None:
        return by_path

    return _from_id(root, key)


def _from_path(root: Path, key: str) -> NoteDoc | None:
    root = root.resolve()
    candidate = (root / key).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file() or candidate.suffix != ".md":
        return None
    return _load(root, candidate)


def _from_id(root: Path, note_id: str) -> NoteDoc | None:
    for path in sorted(root.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        doc = _load(root, path)
        if doc is not None and doc.meta.id == note_id:
            return doc
    return None


def _load(root: Path, path: Path) -> NoteDoc | None:
    text = path.read_text(encoding="utf-8")
    try:
        split = split_frontmatter(text)
    except FrontmatterError:
        return None
    if split is None:
        return None
    fields, _body = split
    try:
        meta = parse_frontmatter(fields)
    except FrontmatterError:
        return None
    return NoteDoc(path=path.relative_to(root.resolve()), text=text, meta=meta)
