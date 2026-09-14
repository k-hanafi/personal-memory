from functools import lru_cache
from pathlib import Path

import pytest

from personal_memory.evals.fixtures import Case, Family, load_fixtures

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "evals" / "fixtures"
BRAIN = ROOT / "evals" / "brain"


@lru_cache
def _families() -> tuple[Family, ...]:
    return tuple(load_fixtures(FIXTURES))


def case_id(item: Family | Case) -> str:
    return item.id if isinstance(item, Case) else item.name


def referenced_paths(case: Case) -> list[str]:
    paths = list(case.forbid_paths) + list(case.contradiction) + [entry.path for entry in case.also_present]
    if case.expect_path is not None:
        paths.append(case.expect_path)
    return paths


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "case" in metafunc.fixturenames:
        pairs = [(family, case) for family in _families() for case in family.cases]
        metafunc.parametrize(("family", "case"), pairs, ids=case_id)
    elif "family" in metafunc.fixturenames:
        metafunc.parametrize("family", _families(), ids=lambda family: family.source.stem)


def test_every_fixture_file_loads() -> None:
    families = _families()
    assert len(families) == len(list(FIXTURES.glob("*.toml")))
    assert families, "no fixture files found"


def test_family_name_matches_filename(family: Family) -> None:
    assert family.name == family.source.stem


def test_referenced_paths_exist_in_brain(family: Family, case: Case) -> None:
    assert case.holdout is False
    missing = [path for path in referenced_paths(case) if not (BRAIN / path).is_file()]
    assert not missing


def test_expect_line_is_a_real_non_empty_line(family: Family, case: Case) -> None:
    if case.expect_line is None:
        return
    lines = (BRAIN / case.expect_path).read_text(encoding="utf-8").splitlines()
    assert 1 <= case.expect_line <= len(lines)
    assert lines[case.expect_line - 1].strip()
