from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from personal_memory.check import SKIP_NAMES
from personal_memory.frontmatter import Frontmatter, FrontmatterError, parse_frontmatter, split_frontmatter

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "do",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "my",
        "of",
        "on",
        "or",
        "the",
        "this",
        "to",
        "was",
        "what",
        "when",
        "where",
        "who",
        "why",
        "with",
    }
)


@dataclass(frozen=True)
class Note:
    path: Path
    relative: Path
    text: str
    meta: Frontmatter
    title: str

    @property
    def aliases(self) -> str:
        return self.meta.extra.get("aliases", "")


def load_notes(root: Path) -> list[Note]:
    """Every markdown file under root that carries valid frontmatter."""
    notes: list[Note] = []
    for path in sorted(root.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        try:
            split = split_frontmatter(text)
        except FrontmatterError:
            continue
        if split is None:
            continue
        fields, body = split
        try:
            meta = parse_frontmatter(fields)
        except FrontmatterError:
            continue
        notes.append(
            Note(
                path=path,
                relative=path.relative_to(root),
                text=text,
                meta=meta,
                title=title_of(body, meta.id),
            )
        )
    return notes


def title_of(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def norm(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def tokenize(query: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(query.lower()) if token not in STOPWORDS and len(token) > 1]
