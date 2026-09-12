from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re

from personal_memory.notelog import LOG_ENTRY_RE
from personal_memory.notes import Note, load_notes, norm, tokenize

WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
TITLE_SCORE = 8
ID_SCORE = 10
BODY_SCORE = 1
HOP_SCORE = 1


def _wikilink_visible(match: re.Match[str]) -> str:
    return match.group(2) or match.group(1)


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
class _Hit:
    rank: int
    exact: bool
    note: Note
    claim: str
    start: int
    end: int


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
        hits.append(_Hit(rank, exact, note, claim, start, end))

    if any(hit.exact for hit in hits):
        hits = [hit for hit in hits if hit.exact]

    hits = _hop(hits, notes, tokens, historical=historical)

    hits.sort(key=lambda hit: (-hit.rank, 0 if hit.note.meta.status == "current" else 1, str(hit.note.relative)))

    current_paths = [str(hit.note.relative) for hit in hits if hit.note.meta.status == "current"]
    cards: list[EvidenceCard] = []
    for hit in hits:
        note = hit.note
        if note.meta.status == "current" and len(current_paths) > 1:
            contradicted = tuple(p for p in current_paths if p != str(note.relative))
        else:
            contradicted = ()
        claim, as_of = _log_line(note, hit.start, hit.claim)
        cards.append(
            EvidenceCard(
                claim=claim,
                path=note.relative,
                start_line=hit.start,
                end_line=hit.end,
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
    body = WIKILINK_RE.sub(_wikilink_visible, note.body).lower()
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
    index_of = {hit.note.meta.id: index for index, hit in enumerate(hits)}
    result = list(hits)
    for hit in hits:
        for match in WIKILINK_RE.finditer(hit.claim):
            target = by_id.get(match.group(1).strip())
            if target is None or (not historical and target.meta.status != "current"):
                continue
            hop_rank = hit.rank + HOP_SCORE
            index = index_of.get(target.meta.id)
            if index is None:
                index_of[target.meta.id] = len(result)
                claim, start, end = _claim_span(target, tokens, exact=False)
                result.append(_Hit(hop_rank, False, target, claim, start, end))
            elif result[index].rank < hop_rank:
                result[index] = replace(result[index], rank=hop_rank)
    return result


def _claim_span(note: Note, tokens: list[str], *, exact: bool) -> tuple[str, int, int]:
    lines = list(enumerate(note.text.splitlines(), start=1))
    title_hit = _find_title_line(lines, note.title)
    if exact:
        return note.title, title_hit, title_hit

    best: tuple[int, int, str] | None = None
    for number, line in lines:
        if number < note.body_start_line:
            continue
        visible = WIKILINK_RE.sub(_wikilink_visible, line)
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
