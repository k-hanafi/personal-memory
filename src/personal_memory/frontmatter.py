from __future__ import annotations

from dataclasses import dataclass
import re

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
REQUIRED = ("id", "type", "as_of", "status", "confidence")
STATUSES = frozenset({"current", "superseded"})
CONFIDENCES = frozenset({"high", "medium", "low"})
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class FrontmatterError(ValueError):
    """A note's YAML header is missing, malformed, or breaks the v1 contract."""


@dataclass(frozen=True)
class Frontmatter:
    id: str
    type: str
    as_of: str
    status: str
    confidence: str
    extra: dict[str, str]


def split_frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    """Return (fields, body) if the file starts with YAML frontmatter, else None."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    raw = match.group(1)
    body = text[match.end() :]
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise FrontmatterError(f"not a key: value line: {stripped}")
        key, _, value = stripped.partition(":")
        fields[key.strip()] = value.strip()
    return fields, body


def parse_frontmatter(fields: dict[str, str]) -> Frontmatter:
    missing = [key for key in REQUIRED if not fields.get(key)]
    if missing:
        raise FrontmatterError(f"missing required fields: {', '.join(missing)}")

    note_id = fields["id"]
    if not ID_RE.match(note_id):
        raise FrontmatterError(f"id must be kebab-case, got {note_id!r}")

    as_of = fields["as_of"]
    if not DATE_RE.match(as_of):
        raise FrontmatterError(f"as_of must be YYYY-MM-DD, got {as_of!r}")

    status = fields["status"]
    if status not in STATUSES:
        raise FrontmatterError(f"status must be current or superseded, got {status!r}")

    confidence = fields["confidence"]
    if confidence not in CONFIDENCES:
        raise FrontmatterError(
            f"confidence must be high, medium, or low, got {confidence!r}"
        )

    extra = {key: value for key, value in fields.items() if key not in REQUIRED}
    return Frontmatter(
        id=note_id,
        type=fields["type"],
        as_of=as_of,
        status=status,
        confidence=confidence,
        extra=extra,
    )
