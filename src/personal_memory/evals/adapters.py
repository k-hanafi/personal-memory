from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
import re

from personal_memory.check import SKIP_NAMES
from personal_memory.frontmatter import FrontmatterError, parse_frontmatter, split_frontmatter
from personal_memory.recall import recall

TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass(frozen=True)
class Hit:
    path: str
    start_line: int
    end_line: int
    status: str
    confidence: str
    contradicted_by: tuple[str, ...]


Adapter = Callable[[Path, str, bool], list[Hit]]


def recall_adapter(corpus_root: Path, query: str, historical: bool) -> list[Hit]:
    result = recall(corpus_root, query, historical=historical)
    return [
        Hit(
            path=card.path.as_posix(),
            start_line=card.start_line,
            end_line=card.end_line,
            status=card.status,
            confidence=card.confidence,
            contradicted_by=tuple(Path(p).as_posix() for p in card.contradicted_by),
        )
        for card in result.cards
    ]


def grep_adapter(corpus_root: Path, query: str, historical: bool) -> list[Hit]:
    """Plain text search. Ignores historical because grep does not know what status means."""
    tokens = TOKEN_RE.findall(query.lower())
    if not tokens:
        return []

    scored: list[tuple[int, str, Hit]] = []
    for path in sorted(corpus_root.rglob("*.md")):
        if path.name in SKIP_NAMES:
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        score = sum(lowered.count(token) for token in tokens)
        if score == 0:
            continue
        line = next(
            number
            for number, content in enumerate(lowered.splitlines(), start=1)
            if any(token in content for token in tokens)
        )
        status, confidence = _meta(text)
        relative = path.relative_to(corpus_root).as_posix()
        scored.append((score, relative, Hit(relative, line, line, status, confidence, ())))

    scored.sort(key=lambda item: (-item[0], item[1]))
    return [hit for _score, _path, hit in scored]


def _meta(text: str) -> tuple[str, str]:
    try:
        split = split_frontmatter(text)
        if split is None:
            return "", ""
        meta = parse_frontmatter(split[0])
    except FrontmatterError:
        return "", ""
    return meta.status, meta.confidence


ADAPTERS: dict[str, Adapter] = {"recall": recall_adapter, "grep": grep_adapter}
