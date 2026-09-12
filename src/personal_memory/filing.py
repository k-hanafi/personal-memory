from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path

from personal_memory.check import link_target
from personal_memory.frontmatter import DATE_RE, FRONTMATTER_RE, FrontmatterError, parse_frontmatter
from personal_memory.notelog import append_entry, normalize_claim, parse_log
from personal_memory.notes import Note, load_notes, norm, tokenize
from personal_memory.recall import WIKILINK_RE

QUEUE_DIR = Path(".personal-memory") / "queue"
APPLIED_DIR = Path(".personal-memory") / "applied"
KINDS = ("create", "append", "supersede")
FRONTMATTER_ORDER = ("id", "type", "as_of", "status", "confidence", "aliases", "supersedes", "source", "provenance")


@dataclass(frozen=True)
class Proposal:
    kind: str
    provenance: str
    confidence: str
    as_of: str
    path: str | None = None
    id: str | None = None
    type: str | None = None
    title: str | None = None
    body: str = ""
    aliases: str | None = None
    source: str | None = None
    supersedes: str | None = None
    target: str | None = None
    claim: str | None = None

    @property
    def proposal_id(self) -> str:
        canonical = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12]

    @classmethod
    def from_dict(cls, data: dict) -> Proposal:
        fields = {name for name in cls.__dataclass_fields__}
        return cls(**{key: value for key, value in data.items() if key in fields})


@dataclass(frozen=True)
class Outcome:
    status: str
    proposal_id: str
    reason: str | None = None
    target: str | None = None
    paths: tuple[str, ...] = ()
    confidence: str | None = None
    candidates: tuple[str, ...] = ()
    placement: dict[str, dict[str, int]] = field(default_factory=dict)


@dataclass(frozen=True)
class Queued:
    proposal_id: str
    proposal: Proposal
    submitted_at: str
    outcome: Outcome


@dataclass(frozen=True)
class _Verdict:
    status: str
    reason: str | None = None
    target: str | None = None


def today() -> str:
    return date.today().isoformat()


def submit(root: Path, proposal: Proposal, *, sources_dir: str = "sources") -> Outcome:
    """Validate a proposal and queue it if it passes. Never writes a note."""
    root = root.resolve()
    notes = load_notes(root)
    verdict = _validate(root, notes, proposal, sources_dir)
    confidence = _effective_confidence(root, proposal, sources_dir)
    extras = {"candidates": _candidates(notes, proposal), "placement": _placement(notes, proposal)}
    if verdict.status != "valid":
        return Outcome(verdict.status, proposal.proposal_id, verdict.reason, verdict.target, confidence=confidence, **extras)
    queue = root / QUEUE_DIR
    queue.mkdir(parents=True, exist_ok=True)
    record = {
        "id": proposal.proposal_id,
        "submitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "proposal": asdict(proposal),
    }
    (queue / f"{proposal.proposal_id}.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return Outcome("queued", proposal.proposal_id, confidence=confidence, **extras)


def list_queue(root: Path, *, sources_dir: str = "sources") -> list[Queued]:
    """Open proposals with their validation as of now, oldest first."""
    root = root.resolve()
    queue = root / QUEUE_DIR
    if not queue.is_dir():
        return []
    notes = load_notes(root)
    items: list[Queued] = []
    for path in sorted(queue.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        proposal = Proposal.from_dict(record["proposal"])
        verdict = _validate(root, notes, proposal, sources_dir)
        status = "queued" if verdict.status == "valid" else verdict.status
        outcome = Outcome(
            status,
            record["id"],
            verdict.reason,
            verdict.target,
            confidence=_effective_confidence(root, proposal, sources_dir),
        )
        items.append(Queued(record["id"], proposal, record["submitted_at"], outcome))
    items.sort(key=lambda item: item.submitted_at)
    return items


def apply(root: Path, *, proposal_id: str | None = None, sources_dir: str = "sources") -> list[Outcome]:
    """Write queued proposals.

    With no id: every valid proposal whose effective confidence is high.
    With an id: that proposal at any confidence (the person chose).
    """
    root = root.resolve()
    outcomes: list[Outcome] = []
    for item in list_queue(root, sources_dir=sources_dir):
        if proposal_id is not None and item.proposal_id != proposal_id:
            continue
        verdict = _validate(root, load_notes(root), item.proposal, sources_dir)
        status = "queued" if verdict.status == "valid" else verdict.status
        item = replace(
            item,
            outcome=Outcome(
                status,
                item.proposal_id,
                verdict.reason,
                verdict.target,
                confidence=_effective_confidence(root, item.proposal, sources_dir),
            ),
        )
        if item.outcome.status != "queued":
            outcomes.append(item.outcome)
            continue
        if proposal_id is None and item.outcome.confidence != "high":
            outcomes.append(item.outcome)
            continue
        outcome = _write(root, item.proposal, item.outcome.confidence or item.proposal.confidence)
        _archive(root, item, outcome)
        outcomes.append(outcome)
    if proposal_id is not None and not outcomes:
        outcomes.append(Outcome("blocked", proposal_id, reason=f"no queued proposal with id {proposal_id}"))
    return outcomes


def remember(
    root: Path,
    claim: str,
    provenance: str,
    *,
    target: str | None = None,
    path: str | None = None,
    type: str | None = None,
    as_of: str | None = None,
    title: str | None = None,
    sources_dir: str = "sources",
) -> Outcome:
    """Save one fact: append to target, or stub-create a note at path."""
    as_of = as_of or today()
    if target is not None:
        proposal = Proposal("append", provenance, "high", as_of, target=target, claim=claim)
    else:
        if not path or not type:
            return Outcome("blocked", "", reason="remember without a target needs path and type")
        note_id = Path(path).stem
        proposal = Proposal(
            "create",
            provenance,
            "high",
            as_of,
            path=path,
            id=note_id,
            type=type,
            title=title or note_id.replace("-", " ").capitalize(),
            claim=claim,
        )
    submitted = submit(root, proposal, sources_dir=sources_dir)
    if submitted.status != "queued" or submitted.confidence != "high":
        return submitted
    applied = apply(root, proposal_id=proposal.proposal_id, sources_dir=sources_dir)[0]
    return replace(applied, candidates=submitted.candidates, placement=submitted.placement)


def _validate(root: Path, notes: list[Note], proposal: Proposal, sources_dir: str) -> _Verdict:
    if proposal.kind not in KINDS:
        return _Verdict("blocked", f"kind must be one of {', '.join(KINDS)}, got {proposal.kind!r}")
    if not proposal.provenance.strip():
        return _Verdict("blocked", "provenance is required: who proposed this and when")
    if not DATE_RE.match(proposal.as_of):
        return _Verdict("blocked", f"as_of must be YYYY-MM-DD, got {proposal.as_of!r}")
    for name in ("provenance", "claim"):
        value = getattr(proposal, name) or ""
        if "|" in value or "\n" in value:
            return _Verdict("blocked", f"{name} must be one line without '|'")
    if proposal.kind in ("create", "supersede"):
        return _validate_new_note(root, notes, proposal, sources_dir)
    return _validate_append(notes, proposal)


def _validate_new_note(root: Path, notes: list[Note], proposal: Proposal, sources_dir: str) -> _Verdict:
    if not proposal.path:
        return _Verdict("blocked", "path is required")
    target = (root / proposal.path).resolve()
    try:
        relative = target.relative_to(root)
    except ValueError:
        return _Verdict("blocked", f"path {proposal.path!r} is outside the brain")
    if target.suffix != ".md":
        return _Verdict("blocked", f"path {proposal.path!r} must end in .md")
    if relative.parts and relative.parts[0] == sources_dir:
        return _Verdict("blocked", f"{sources_dir}/ is immutable; file the note elsewhere and name the source")
    if target.exists():
        return _Verdict("blocked", f"a file already exists at {proposal.path!r}")
    if not proposal.title:
        return _Verdict("blocked", "title is required")
    try:
        parse_frontmatter(_frontmatter_fields(proposal, proposal.confidence))
    except FrontmatterError as exc:
        return _Verdict("blocked", str(exc))
    if proposal.source is not None and not _is_source(root, proposal.source, sources_dir):
        return _Verdict("blocked", f"source {proposal.source!r} is not a file under {sources_dir}/")

    for note in notes:
        if note.meta.id == proposal.id:
            return _Verdict("duplicate", f"a note with id {proposal.id!r} already exists", note.meta.id)
    wanted = norm(proposal.title)
    for note in notes:
        if note.meta.status != "current" or note.meta.id == proposal.supersedes:
            continue
        aliases = [norm(alias) for alias in note.aliases.split(",") if alias.strip()]
        if norm(note.title) == wanted or wanted in aliases:
            return _Verdict("duplicate", f"{note.meta.id!r} already has this title or alias; append to it instead", note.meta.id)

    if proposal.kind == "supersede":
        if not proposal.supersedes:
            return _Verdict("blocked", "supersede needs the id of the note it replaces")
        old = next((note for note in notes if note.meta.id == proposal.supersedes), None)
        if old is None:
            return _Verdict("blocked", f"supersedes {proposal.supersedes!r}, which is not a note in this brain")
        if old.meta.status != "current":
            return _Verdict("blocked", f"{proposal.supersedes!r} is already superseded")
    return _Verdict("valid")


def _validate_append(notes: list[Note], proposal: Proposal) -> _Verdict:
    if not proposal.target:
        return _Verdict("blocked", "append needs a target note id")
    if not (proposal.claim or "").strip():
        return _Verdict("blocked", "claim is required")
    target = next((note for note in notes if note.meta.id == proposal.target), None)
    if target is None:
        return _Verdict("blocked", f"target {proposal.target!r} is not a note in this brain")
    if target.meta.status != "current":
        return _Verdict("blocked", f"target {proposal.target!r} is superseded; append to {link_target(target.meta.extra.get('superseded_by', '')) or 'its replacement'}")
    wanted = normalize_claim(proposal.claim)
    for entry in parse_log(target.text).entries:
        if normalize_claim(entry.claim) == wanted:
            return _Verdict("duplicate", f"{target.meta.id!r} already logs this claim on line {entry.line}", target.meta.id)
    return _Verdict("valid")


def _effective_confidence(root: Path, proposal: Proposal, sources_dir: str) -> str:
    if proposal.confidence != "high":
        return proposal.confidence
    if proposal.provenance.strip().lower().startswith("user"):
        return "high"
    if proposal.kind in ("append", "supersede"):
        return "high"
    if proposal.source and _is_source(root, proposal.source, sources_dir):
        return "high"
    return "medium"


def _is_source(root: Path, source: str, sources_dir: str) -> bool:
    path = (root / source).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return False
    return path.is_file() and relative.parts[:1] == (sources_dir,)


def _candidates(notes: list[Note], proposal: Proposal) -> tuple[str, ...]:
    wanted = {token for token in tokenize(" ".join(filter(None, (proposal.title, proposal.claim)))) if not token.isdigit()}
    if not wanted:
        return ()
    found = []
    for note in notes:
        if note.meta.id in (proposal.id, proposal.supersedes):
            continue
        own = set(tokenize(f"{note.meta.id.replace('-', ' ')} {note.title} {note.aliases}"))
        if wanted & own:
            found.append(note.meta.id)
    return tuple(found)


def _placement(notes: list[Note], proposal: Proposal) -> dict[str, dict[str, int]]:
    by_type: dict[str, int] = {}
    by_link: dict[str, int] = {}
    linked = {match.group(1).strip() for match in WIKILINK_RE.finditer(" ".join(filter(None, (proposal.body, proposal.claim))))}
    for note in notes:
        folder = str(note.relative.parent)
        if proposal.type and note.meta.type == proposal.type:
            by_type[folder] = by_type.get(folder, 0) + 1
        if note.meta.id in linked:
            by_link[folder] = by_link.get(folder, 0) + 1
    return {"type": by_type, "links": by_link}


def _frontmatter_fields(proposal: Proposal, confidence: str) -> dict[str, str]:
    fields = {
        "id": proposal.id or "",
        "type": proposal.type or "",
        "as_of": proposal.as_of,
        "status": "current",
        "confidence": confidence,
        "aliases": proposal.aliases or "",
        "supersedes": proposal.supersedes or "",
        "source": proposal.source or "",
        "provenance": proposal.provenance,
    }
    return {key: value for key, value in fields.items() if value}


def _render_note(proposal: Proposal, confidence: str) -> str:
    fields = _frontmatter_fields(proposal, confidence)
    header = "\n".join(f"{key}: {fields[key]}" for key in FRONTMATTER_ORDER if key in fields)
    body = proposal.body.strip("\n")
    text = f"---\n{header}\n---\n\n# {proposal.title}\n"
    if body:
        text += f"\n{body}\n"
    if proposal.claim:
        text = append_entry(text, proposal.as_of, proposal.provenance, proposal.claim)
    return text


def _write(root: Path, proposal: Proposal, confidence: str) -> Outcome:
    if proposal.kind == "append":
        note = next(note for note in load_notes(root) if note.meta.id == proposal.target)
        (root / note.relative).write_text(append_entry(note.text, proposal.as_of, proposal.provenance, proposal.claim or ""), encoding="utf-8")
        return Outcome("inserted", proposal.proposal_id, target=note.meta.id, paths=(str(note.relative),), confidence=confidence)

    new_path = root / (proposal.path or "")
    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_text(_render_note(proposal, confidence), encoding="utf-8")
    if proposal.kind == "create":
        return Outcome("inserted", proposal.proposal_id, target=proposal.id, paths=(proposal.path or "",), confidence=confidence)

    old = next(note for note in load_notes(root) if note.meta.id == proposal.supersedes)
    text = _set_frontmatter(old.text, "status", "superseded")
    text = _set_frontmatter(text, "superseded_by", proposal.id or "")
    (root / old.relative).write_text(text, encoding="utf-8")
    return Outcome(
        "superseded",
        proposal.proposal_id,
        target=proposal.id,
        paths=(str(old.relative), proposal.path or ""),
        confidence=confidence,
    )


def _set_frontmatter(text: str, key: str, value: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if match is None:
        raise FrontmatterError("note has no frontmatter to edit")
    lines = match.group(1).splitlines()
    for index, line in enumerate(lines):
        if line.partition(":")[0].strip() == key:
            lines[index] = f"{key}: {value}"
            break
    else:
        lines.append(f"{key}: {value}")
    return text[: match.start(1)] + "\n".join(lines) + text[match.end(1) :]


def _archive(root: Path, item: Queued, outcome: Outcome) -> None:
    applied = root / APPLIED_DIR
    applied.mkdir(parents=True, exist_ok=True)
    source = root / QUEUE_DIR / f"{item.proposal_id}.json"
    record = json.loads(source.read_text(encoding="utf-8"))
    record["applied_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record["result"] = {"status": outcome.status, "paths": list(outcome.paths), "confidence": outcome.confidence}
    (applied / source.name).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    source.unlink()
