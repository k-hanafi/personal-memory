from __future__ import annotations

from pathlib import Path

from personal_memory.notes import Note, load_note, load_notes


def get_note(root: Path, key: str) -> Note | None:
    """Return one note by id or path, frontmatter included. None if missing."""
    key = key.strip()
    if not key:
        return None

    root = root.resolve()
    by_path = _from_path(root, key)
    if by_path is not None:
        return by_path

    return _from_id(root, key)


def _from_path(root: Path, key: str) -> Note | None:
    candidate = (root / key).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file() or candidate.suffix != ".md":
        return None
    return load_note(root, candidate)


def _from_id(root: Path, note_id: str) -> Note | None:
    for note in load_notes(root):
        if note.meta.id == note_id:
            return note
    return None
