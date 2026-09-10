from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from personal_memory.check import SKIP_NAMES
from personal_memory.frontmatter import Frontmatter, FrontmatterError, parse_frontmatter, split_frontmatter

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
WIKILINK_RE = re.compile(r"\[\[[^\]|]+(?:\|([^\]]+))?\]\]")
TOKEN_RE = re.compile(r"[a-z0-9]+")
TITLE_SCORE = 0
ID_SCORE = 10
BODY_SCORE = 1


@dataclass(frozen=True)
class EvidenceCard:
    claim: str
    path: Path
    start_line: int
    end_line: int
    status: str
    as_of: str
    confidence: str
    contradicted_by: tuple[str, ...]


@dataclass(frozen=True)
class RecallResult:
    cards: tuple[EvidenceCard, ...]


@dataclass(frozen=True)
class _LoadedNote:
    path: Path
    relative: Path
    text: str
    meta: Frontmatter
    title: str


def recall(root: Path, query: str, *, historical: bool = False) -> RecallResult:
    """Return evidence cards for notes that match query.

    Default is current notes only. historical=True includes superseded notes.
    Wikilink targets are not searched (hops are a later slice).
    """
    tokens = _tokens(query)
    hits: list[tuple[int, bool, _LoadedNote, str, int, int]] = []

    for note in _iter_notes(root):
        if not historical and note.meta.status != "current":
            continue
        exact = _exact_match(note, query)
        score = _keyword_score(note, tokens)
        if not exact and score == 0:
            continue
        claim, start, end = _claim_span(note, tokens, exact=exact)
        rank = score + (50 if exact else 0)
        hits.append((rank, exact, note, claim, start, end))

    if any(exact for _rank, exact, _note, _claim, _start, _end in hits):
        hits = [hit for hit in hits if hit[1]]

    hits.sort(key=lambda item: (-item[0], 0 if item[2].meta.status == "current" else 1, str(item[2].relative)))

    current_paths = [
        str(note.relative) for _rank, _exact, note, _claim, _start, _end in hits if note.meta.status == "current"
    ]
    cards: list[EvidenceCard] = []
    for _rank, _exact, note, claim, start, end in hits:
        if note.meta.status == "current" and len(current_paths) > 1:
            contradicted = tuple(p for p in current_paths if p != str(note.relative))
        else:
            contradicted = ()
        cards.append(
            EvidenceCard(
                claim=claim,
                path=note.relative,
                start_line=start,
                end_line=end,
                status=note.meta.status,
                as_of=note.meta.as_of,
                confidence=note.meta.confidence,
                contradicted_by=contradicted,
            )
        )
    return RecallResult(tuple(cards))


def _iter_notes(root: Path) -> list[_LoadedNote]:
    notes: list[_LoadedNote] = []
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
            _LoadedNote(
                path=path,
                relative=path.relative_to(root),
                text=text,
                meta=meta,
                title=_title(body, meta.id),
            )
        )
    return notes


def _title(body: str, fallback: str) -> str:
    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return fallback


def _norm(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def _tokens(query: str) -> list[str]:
    return [token for token in TOKEN_RE.findall(query.lower()) if token not in STOPWORDS and len(token) > 1]


def _aliases(note: _LoadedNote) -> str:
    return note.meta.extra.get("aliases", "")


def _exact_match(note: _LoadedNote, query: str) -> bool:
    stripped = query.strip().lower()
    if not stripped:
        return False
    if stripped == note.meta.id.lower():
        return True
    if _norm(query) == _norm(note.title):
        return True
    aliases = _norm(_aliases(note))
    return bool(aliases) and _norm(query) == aliases


def _keyword_score(note: _LoadedNote, tokens: list[str]) -> int:
    if not tokens:
        return 0
    body = WIKILINK_RE.sub(lambda match: match.group(1) or "", _body_of(note.text)).lower()
    score = 0
    for token in tokens:
        if token in note.meta.id:
            score += ID_SCORE
        elif token in _norm(note.title) or token in _norm(_aliases(note)):
            score += TITLE_SCORE
        elif token in body:
            score += BODY_SCORE
        else:
            return 0
    return score


def _body_of(text: str) -> str:
    split = split_frontmatter(text)
    if split is None:
        return text
    return split[1]


def _claim_span(note: _LoadedNote, tokens: list[str], *, exact: bool) -> tuple[str, int, int]:
    lines = list(enumerate(note.text.splitlines(), start=1))
    title_hit = _find_title_line(lines, note.title)
    if exact:
        return note.title, title_hit, title_hit

    body_start = _body_start_line(note.text)
    best: tuple[int, int, str] | None = None
    for number, line in lines:
        if number < body_start:
            continue
        visible = WIKILINK_RE.sub(lambda match: match.group(1) or "", line)
        hits = sum(1 for token in tokens if token in visible.lower())
        if hits == 0:
            continue
        if best is None or hits > best[0]:
            best = (hits, number, line.strip())
    if best is None:
        return note.title, title_hit, title_hit
    claim = best[2].lstrip("#").strip() or note.title
    return claim, best[1], best[1]


def _find_title_line(lines: list[tuple[int, str]], title: str) -> int:
    for number, line in lines:
        if line.strip().lstrip("#").strip() == title:
            return number
    return 1


def _body_start_line(text: str) -> int:
    match = re.match(r"\A---\r?\n.*?\r?\n---(?:\r?\n|\Z)", text, re.DOTALL)
    if not match:
        return 1
    return text[: match.end()].count("\n") + 1
