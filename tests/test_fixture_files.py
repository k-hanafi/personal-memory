"""The committed fixture files point at real notes and real lines in the eval corpus."""

from pathlib import Path

import pytest

from personal_memory.evals.fixtures import Case, Family, load_fixtures

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "evals" / "fixtures"
BRAIN = ROOT / "evals" / "brain"

FAMILIES = load_fixtures(FIXTURES)
CASES = [(family, case) for family in FAMILIES for case in family.cases]


def case_id(item: Family | Case) -> str:
    return item.id if isinstance(item, Case) else item.name


def referenced_paths(case: Case) -> list[str]:
    paths = list(case.forbid_paths) + list(case.contradiction) + [entry.path for entry in case.also_present]
    if case.expect_path is not None:
        paths.append(case.expect_path)
    return paths


def test_every_fixture_file_loads() -> None:
    assert len(FAMILIES) == len(list(FIXTURES.glob("*.toml")))
    assert FAMILIES, "no fixture files found"


@pytest.mark.parametrize("family", FAMILIES, ids=lambda family: family.source.stem)
def test_family_name_matches_filename(family: Family) -> None:
    assert family.name == family.source.stem


@pytest.mark.parametrize(("family", "case"), CASES, ids=case_id)
def test_referenced_paths_exist_in_brain(family: Family, case: Case) -> None:
    missing = [path for path in referenced_paths(case) if not (BRAIN / path).is_file()]
    assert not missing


@pytest.mark.parametrize(("family", "case"), CASES, ids=case_id)
def test_expect_line_is_a_real_non_empty_line(family: Family, case: Case) -> None:
    if case.expect_line is None:
        return
    lines = (BRAIN / case.expect_path).read_text(encoding="utf-8").splitlines()
    assert 1 <= case.expect_line <= len(lines)
    assert lines[case.expect_line - 1].strip()


@pytest.mark.parametrize(("family", "case"), CASES, ids=case_id)
def test_abstain_cases_declare_nothing_else(family: Family, case: Case) -> None:
    if not case.abstain:
        return
    assert case.expect_path is None
    assert case.expect_line is None
    assert case.expect_status is None
    assert case.expect_confidence is None
    assert case.forbid_paths == ()
    assert case.also_present == ()
    assert case.contradiction == ()
