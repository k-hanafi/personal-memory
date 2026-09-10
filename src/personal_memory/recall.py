from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from personal_memory.frontmatter import split_frontmatter
from personal_memory.notelog import LOG_ENTRY_RE
from personal_memory.notes import Note, load_notes, norm, tokenize

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
TITLE_SCORE = 8
ID_SCORE = 10
BODY_SCORE = 1
HOP_SCORE = 1


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


_Hit = tuple[int, bool, Note, str, int, int]


def recall(root: Path, query: str, *, historical: bool = False) -> RecallResult:
    """Return evidence cards for notes that match query.

    Default is current notes only. historical=True includes superseded notes.
    Wikilinks on a hit's claim line are followed one hop to the target note.
    """
    tokens = tokenize(query)
    notes = load_notes(root)
    hits: list[_Hit] = []

    for note in notes:
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

    hits = _hop(hits, notes, tokens, historical=historical)

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
        claim, as_of = _log_line(note, start, claim)
        cards.append(
            EvidenceCard(
                claim=claim,
                path=note.relative,
                start_line=start,
                end_line=end,
                status=note.meta.status,
                as_of=as_of,
                confidence=note.meta.confidence,
                contradicted_by=contradicted,
            )
        )
    return RecallResult(tuple(cards))


def _exact_match(note: Note, query: str) -> bool:
    stripped = query.strip().lower()
    if not stripped:
        return False
    if stripped == note.meta.id.lower():
        return True
    if norm(query) == norm(note.title):
        return True
    aliases = norm(note.aliases)
    return bool(aliases) and norm(query) == aliases


def _keyword_score(note: Note, tokens: list[str]) -> int:
    if not tokens:
        return 0
    body = WIKILINK_RE.sub(lambda match: match.group(2) or "", _body_of(note.text)).lower()
    score = 0
    for token in tokens:
        if token in note.meta.id:
            score += ID_SCORE
        elif token in norm(note.title) or token in norm(note.aliases):
            score += TITLE_SCORE
        elif token in body:
            score += BODY_SCORE
        else:
            return 0
    return score


def _hop(hits: list[_Hit], notes: list[Note], tokens: list[str], *, historical: bool) -> list[_Hit]:
    by_id = {note.meta.id: note for note in notes}
    index_of = {hit[2].meta.id: index for index, hit in enumerate(hits)}
    result = list(hits)
    for rank, _exact, _note, claim, _start, _end in hits:
        for match in WIKILINK_RE.finditer(claim):
            target = by_id.get(match.group(1).strip())
            if target is None or (not historical and target.meta.status != "current"):
                continue
            hop_rank = rank + HOP_SCORE
            index = index_of.get(target.meta.id)
            if index is None:
                index_of[target.meta.id] = len(result)
                result.append((hop_rank, False, target, *_claim_span(target, tokens, exact=False)))
            elif result[index][0] < hop_rank:
                result[index] = (hop_rank, *result[index][1:])
    return result


def _body_of(text: str) -> str:
    split = split_frontmatter(text)
    if split is None:
        return text
    return split[1]


def _claim_span(note: Note, tokens: list[str], *, exact: bool) -> tuple[str, int, int]:
    lines = list(enumerate(note.text.splitlines(), start=1))
    title_hit = _find_title_line(lines, note.title)
    if exact:
        return note.title, title_hit, title_hit

    body_start = _body_start_line(note.text)
    best: tuple[int, int, str] | None = None
    for number, line in lines:
        if number < body_start:
            continue
        visible = WIKILINK_RE.sub(lambda match: match.group(2) or "", line)
        hits = sum(1 for token in tokens if token in visible.lower())
        if hits == 0:
            continue
        if best is None or hits > best[0]:
            best = (hits, number, line.strip())
    if best is None:
        return note.title, title_hit, title_hit
    claim = best[2].lstrip("#").strip() or note.title
    return claim, best[1], best[1]


def _log_line(note: Note, line_number: int, claim: str) -> tuple[str, str]:
    """A claim line that is a Log entry carries its own date; use it as as_of."""
    lines = note.text.splitlines()
    if 1 <= line_number <= len(lines):
        match = LOG_ENTRY_RE.match(lines[line_number - 1])
        if match is not None:
            return match.group(3), match.group(1)
    return claim, note.meta.as_of


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
