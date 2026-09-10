from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


class FixtureError(ValueError):
    """A fixture file is malformed or breaks a validation rule."""


@dataclass(frozen=True)
class AlsoPresent:
    path: str
    status: str


@dataclass(frozen=True)
class Case:
    id: str
    query: str
    historical: bool = False
    expect_path: str | None = None
    expect_line: int | None = None
    expect_status: str | None = None
    expect_confidence: str | None = None
    forbid_paths: tuple[str, ...] = ()
    also_present: tuple[AlsoPresent, ...] = ()
    abstain: bool = False
    contradiction: tuple[str, ...] = ()
    holdout: bool = False
    note: str = ""


@dataclass(frozen=True)
class Family:
    name: str
    description: str
    cases: tuple[Case, ...]
    source: Path


TOP_KEYS = frozenset({"family", "description", "case"})
CASE_KEYS = frozenset(Case.__dataclass_fields__)
ALSO_PRESENT_KEYS = frozenset(AlsoPresent.__dataclass_fields__)


def load_fixture_file(path: Path) -> Family:
    """Parse one TOML fixture file into a Family, validating every case."""
    where = str(path)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise FixtureError(f"{where}: {exc}") from exc

    _reject_unknown(data, TOP_KEYS, where)
    name = _typed(data, "family", str, where, required=True)
    description = _typed(data, "description", str, where) or ""

    cases: list[Case] = []
    seen: set[str] = set()
    for raw in _table_list(data, "case", where):
        case = _parse_case(raw, where)
        if case.id in seen:
            raise FixtureError(f"{where}: duplicate case id {case.id!r}")
        seen.add(case.id)
        cases.append(case)
    return Family(name=name, description=description, cases=tuple(cases), source=path)


def load_fixtures(directory: Path) -> list[Family]:
    """Load every *.toml in directory, sorted by name. Case ids must be unique across files."""
    families: list[Family] = []
    seen: dict[str, Path] = {}
    for path in sorted(directory.glob("*.toml")):
        family = load_fixture_file(path)
        for case in family.cases:
            previous = seen.get(case.id)
            if previous is not None:
                raise FixtureError(f"{path}: duplicate case id {case.id!r} (also in {previous})")
            seen[case.id] = path
        families.append(family)
    return families


def _parse_case(raw: dict, file_where: str) -> Case:
    case_id = raw.get("id")
    where = f"{file_where}: case {case_id!r}" if isinstance(case_id, str) else file_where
    _reject_unknown(raw, CASE_KEYS, where)

    expect_path = _typed(raw, "expect_path", str, where)
    expect_line = _typed(raw, "expect_line", int, where)
    expect_status = _typed(raw, "expect_status", str, where)
    expect_confidence = _typed(raw, "expect_confidence", str, where)
    also_present = tuple(_parse_also_present(entry, where) for entry in _table_list(raw, "also_present", where))
    abstain = _typed(raw, "abstain", bool, where) or False
    contradiction = _str_list(raw, "contradiction", where)

    if expect_line is not None and expect_path is None:
        raise FixtureError(f"{where}: expect_line requires expect_path")
    if abstain and (
        expect_path is not None
        or expect_status is not None
        or expect_confidence is not None
        or also_present
        or contradiction
    ):
        raise FixtureError(
            f"{where}: abstain cannot be combined with expect_path, expect_status, "
            "expect_confidence, also_present, or contradiction"
        )
    if len(contradiction) == 1:
        raise FixtureError(f"{where}: contradiction needs at least two paths")

    return Case(
        id=_typed(raw, "id", str, where, required=True),
        query=_typed(raw, "query", str, where, required=True),
        historical=_typed(raw, "historical", bool, where) or False,
        expect_path=expect_path,
        expect_line=expect_line,
        expect_status=expect_status,
        expect_confidence=expect_confidence,
        forbid_paths=_str_list(raw, "forbid_paths", where),
        also_present=also_present,
        abstain=abstain,
        contradiction=contradiction,
        holdout=_typed(raw, "holdout", bool, where) or False,
        note=_typed(raw, "note", str, where) or "",
    )


def _parse_also_present(raw: dict, where: str) -> AlsoPresent:
    _reject_unknown(raw, ALSO_PRESENT_KEYS, f"{where}: also_present")
    return AlsoPresent(
        path=_typed(raw, "path", str, f"{where}: also_present", required=True),
        status=_typed(raw, "status", str, f"{where}: also_present", required=True),
    )


def _reject_unknown(table: dict, allowed: frozenset[str], where: str) -> None:
    unknown = sorted(set(table) - allowed)
    if unknown:
        raise FixtureError(f"{where}: unknown key {unknown[0]!r}")


def _typed(table: dict, key: str, kind: type, where: str, *, required: bool = False):
    if key not in table:
        if required:
            raise FixtureError(f"{where}: missing {key!r}")
        return None
    value = table[key]
    if not isinstance(value, kind) or (kind is int and isinstance(value, bool)):
        raise FixtureError(f"{where}: {key!r} must be {kind.__name__}, got {type(value).__name__}")
    return value


def _str_list(table: dict, key: str, where: str) -> tuple[str, ...]:
    values = _typed(table, key, list, where) or []
    if not all(isinstance(value, str) for value in values):
        raise FixtureError(f"{where}: {key!r} must be a list of strings")
    return tuple(values)


def _table_list(table: dict, key: str, where: str) -> list[dict]:
    values = _typed(table, key, list, where) or []
    if not all(isinstance(value, dict) for value in values):
        raise FixtureError(f"{where}: {key!r} must be an array of tables")
    return values
