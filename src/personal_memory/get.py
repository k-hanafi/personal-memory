from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.frontmatter import Frontmatter
from personal_memory.notes import Note, load_note, load_notes


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

    root = root.resolve()
    by_path = _from_path(root, key)
    if by_path is not None:
        return by_path

    return _from_id(root, key)


def _from_path(root: Path, key: str) -> NoteDoc | None:
    candidate = (root / key).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file() or candidate.suffix != ".md":
        return None
    return _as_doc(load_note(root, candidate))


def _from_id(root: Path, note_id: str) -> NoteDoc | None:
    for note in load_notes(root):
        if note.meta.id == note_id:
            return _as_doc(note)
    return None


def _as_doc(note: Note | None) -> NoteDoc | None:
    if note is None:
        return None
    return NoteDoc(path=note.relative, text=note.text, meta=note.meta)
