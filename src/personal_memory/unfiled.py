from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from personal_memory.notelog import parse_log
from personal_memory.notes import load_notes


@dataclass(frozen=True)
class UnfiledResult:
    sources: int
    unfiled: tuple[Path, ...]


def resolve_source(root: Path, source: str, sources_dir: str) -> str | None:
    """Posix path of source relative to root, if it is a file under sources_dir/."""
    path = (root / source).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    if path.is_file() and relative.parts[:1] == (sources_dir,):
        return relative.as_posix()
    return None


def unfiled(root: Path, *, sources_dir: str = "sources") -> UnfiledResult:
    """Files under sources/ that no note names as its source.

    A source counts as filed when a note's frontmatter says `source: <path>`
    or a Log line's provenance is `source:<path>`. Nothing under sources/ is
    read, moved, or edited.
    """
    root = root.resolve()
    folder = root / sources_dir
    if not folder.is_dir():
        return UnfiledResult(0, ())
    filed: set[str] = set()
    for note in load_notes(root):
        source = note.meta.extra.get("source", "").strip()
        if source:
            filed.add(resolve_source(root, source, sources_dir) or source)
        for entry in parse_log(note.text).entries:
            if entry.provenance.startswith("source:"):
                raw = entry.provenance.removeprefix("source:").strip()
                filed.add(resolve_source(root, raw, sources_dir) or raw)
    items = sorted(
        path.relative_to(root)
        for path in folder.rglob("*")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )
    return UnfiledResult(len(items), tuple(path for path in items if path.as_posix() not in filed))
