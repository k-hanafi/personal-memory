from __future__ import annotations

from dataclasses import dataclass
import re

LOG_HEADING_RE = re.compile(r"^##\s+Log\s*$")
HEADING_RE = re.compile(r"^#{1,6}\s")
LOG_ENTRY_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2}) \| ([^|]+?) \| (.+?)\s*$")


@dataclass(frozen=True)
class LogEntry:
    line: int
    date: str
    provenance: str
    claim: str


@dataclass(frozen=True)
class LogSection:
    heading_line: int | None
    entries: tuple[LogEntry, ...]
    bad_lines: tuple[tuple[int, str], ...]

    @property
    def present(self) -> bool:
        return self.heading_line is not None


def parse_log(text: str) -> LogSection:
    """Find the `## Log` section and parse its entries.

    Every non-blank line under the heading, up to the next heading, must be
    `- YYYY-MM-DD | provenance | claim`. Lines that do not parse are reported,
    not skipped, so `check` can refuse them.
    """
    heading_line: int | None = None
    entries: list[LogEntry] = []
    bad: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if heading_line is None:
            if LOG_HEADING_RE.match(line.strip()):
                heading_line = number
            continue
        if HEADING_RE.match(line):
            break
        if not line.strip():
            continue
        match = LOG_ENTRY_RE.match(line)
        if match is None:
            bad.append((number, line))
            continue
        entries.append(LogEntry(number, match.group(1), match.group(2).strip(), match.group(3)))
    return LogSection(heading_line, tuple(entries), tuple(bad))


def format_entry(date: str, provenance: str, claim: str) -> str:
    return f"- {date} | {provenance} | {claim}"


def append_entry(text: str, date: str, provenance: str, claim: str) -> str:
    """Return text with one Log line added, creating the section if needed."""
    entry = format_entry(date, provenance, claim)
    section = parse_log(text)
    lines = text.splitlines()
    if not section.present:
        while lines and not lines[-1].strip():
            lines.pop()
        lines.extend(["", "## Log", entry])
        return "\n".join(lines) + "\n"

    insert_at = section.heading_line
    for number, line in enumerate(lines[section.heading_line :], start=section.heading_line + 1):
        if HEADING_RE.match(line):
            break
        if line.strip():
            insert_at = number
    lines.insert(insert_at, entry)
    return "\n".join(lines) + "\n"


def normalize_claim(claim: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", claim.lower()))
