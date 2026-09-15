from pathlib import Path

import pytest

from personal_memory.evals.fixtures import AlsoPresent, FixtureError, load_fixture_file, load_fixtures

VALID = """
family = "supersession"

[[case]]
id = "current-wins"
query = "teaching load"
expect_path = "40-areas/teaching-load-2026-09.md"
expect_line = 12
expect_status = "current"
expect_confidence = "high"
forbid_paths = ["40-areas/teaching-load-2026-01.md"]

[[case]]
id = "history-labels-old"
query = "teaching load"
historical = true
expect_path = "40-areas/teaching-load-2026-09.md"

[[case.also_present]]
path = "40-areas/teaching-load-2026-01.md"
status = "superseded"

[[case]]
id = "nothing-here"
query = "parking permit"
abstain = true
holdout = true

[[case]]
id = "budget-disagrees"
query = "research budget"
contradiction = ["40-areas/a.md", "40-areas/b.md"]
"""


def write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def one_case(body: str) -> str:
    return f'family = "f"\n\n[[case]]\n{body}\n'


def test_valid_file_loads_with_field_values(tmp_path: Path) -> None:
    path = write(tmp_path, "supersession.toml", VALID)
    family = load_fixture_file(path)
    assert family.name == "supersession"
    assert family.source == path
    first, second, third, fourth = family.cases

    assert first.id == "current-wins"
    assert first.query == "teaching load"
    assert first.historical is False
    assert first.expect_path == "40-areas/teaching-load-2026-09.md"
    assert first.expect_line == 12
    assert first.expect_status == "current"
    assert first.expect_confidence == "high"
    assert first.forbid_paths == ("40-areas/teaching-load-2026-01.md",)
    assert first.also_present == ()
    assert first.abstain is False
    assert first.holdout is False

    assert second.historical is True
    assert second.also_present == (AlsoPresent(path="40-areas/teaching-load-2026-01.md", status="superseded"),)

    assert third.abstain is True
    assert third.holdout is True
    assert third.expect_path is None

    assert fourth.contradiction == ("40-areas/a.md", "40-areas/b.md")


def test_family_without_cases(tmp_path: Path) -> None:
    path = write(tmp_path, "f.toml", 'family = "f"\n')
    with pytest.raises(FixtureError, match="f.toml.*no cases"):
        load_fixture_file(path)


def test_case_without_assert_fields(tmp_path: Path) -> None:
    path = write(tmp_path, "bad.toml", one_case('id = "x"\nquery = "q"'))
    with pytest.raises(FixtureError, match="assert"):
        load_fixture_file(path)


def test_missing_family_names_file(tmp_path: Path) -> None:
    path = write(tmp_path, "nofamily.toml", '[[case]]\nid = "x"\nquery = "q"\n')
    with pytest.raises(FixtureError, match="nofamily.toml.*family"):
        load_fixture_file(path)


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ('id = "x"\nquery = "q"\nexpect_paths = "a.md"', "expect_paths"),
        ('id = "x"\nquery = "q"\n[[case.also_present]]\npath = "a.md"\nstatus = "current"\nwhy = "no"', "why"),
        ('id = "x"\nquery = "q"\n[[case.also_present]]\npath = "a.md"', "status"),
        ('id = "x"\nquery = "q"\nexpect_line = 3', "expect_line"),
        ('id = "x"\nquery = "q"\nabstain = true\nexpect_path = "a.md"', "abstain"),
        ('id = "x"\nquery = "q"\nabstain = true\nexpect_status = "current"', "abstain"),
        ('id = "x"\nquery = "q"\nabstain = true\nexpect_confidence = "high"', "abstain"),
        ('id = "x"\nquery = "q"\nabstain = true\n[[case.also_present]]\npath = "a.md"\nstatus = "current"', "abstain"),
        ('id = "x"\nquery = "q"\nabstain = true\ncontradiction = ["a.md", "b.md"]', "abstain"),
        ('id = "x"\nquery = "q"\nabstain = true\nforbid_paths = ["a.md"]', "abstain"),
        ('id = "x"\nquery = "q"\ncontradiction = ["a.md"]', "contradiction"),
        ('id = "x"\nquery = "q"\nhistorical = "yes"', "historical"),
        ('id = "x"\nquery = "q"\nexpect_path = "a.md"\nexpect_line = true', "expect_line"),
        ('id = "x"\nquery = "q"\nexpect_line = "12"\nexpect_path = "a.md"', "expect_line"),
        ('id = "x"\nquery = "q"\nforbid_paths = "a.md"', "forbid_paths"),
        ('id = "x"\nquery = "q"\ncontradiction = [1, 2]', "contradiction"),
        ('id = "x"\nquery = "q"\nholdout = 3', "holdout"),
        ('id = "x"\nquery = "q"\nnote = "unused"', "note"),
        ('id = "x"\nquery = 7', "query"),
        ('id = "x"\nquery = "q"\nhistorical = true', "assert"),
    ],
)
def test_invalid_case_names_file_and_case_id(tmp_path: Path, body: str, fragment: str) -> None:
    path = write(tmp_path, "bad.toml", one_case(body))
    with pytest.raises(FixtureError) as info:
        load_fixture_file(path)
    message = str(info.value)
    assert "bad.toml" in message
    assert "'x'" in message
    assert fragment in message


@pytest.mark.parametrize(
    ("body", "fragment"),
    [
        ('query = "q"', "id"),
        ('id = "x"', "query"),
        ('id = 5\nquery = "q"', "id"),
    ],
)
def test_missing_or_bad_id_and_query(tmp_path: Path, body: str, fragment: str) -> None:
    path = write(tmp_path, "bad.toml", one_case(body))
    with pytest.raises(FixtureError) as info:
        load_fixture_file(path)
    assert "bad.toml" in str(info.value)
    assert fragment in str(info.value)


def test_unknown_top_level_key_is_rejected(tmp_path: Path) -> None:
    path = write(tmp_path, "bad.toml", 'family = "f"\n\n[[cases]]\nid = "x"\nquery = "q"\n')
    with pytest.raises(FixtureError, match="cases"):
        load_fixture_file(path)


def test_duplicate_id_within_one_file(tmp_path: Path) -> None:
    text = (
        'family = "f"\n\n[[case]]\nid = "x"\nquery = "a"\nabstain = true\n\n'
        '[[case]]\nid = "x"\nquery = "b"\nabstain = true\n'
    )
    with pytest.raises(FixtureError, match="'x'"):
        load_fixture_file(write(tmp_path, "dup.toml", text))


def test_duplicate_id_across_files(tmp_path: Path) -> None:
    write(tmp_path, "a.toml", one_case('id = "shared"\nquery = "a"\nabstain = true'))
    write(tmp_path, "b.toml", one_case('id = "shared"\nquery = "b"\nabstain = true'))
    with pytest.raises(FixtureError) as info:
        load_fixtures(tmp_path)
    message = str(info.value)
    assert "'shared'" in message
    assert "a.toml" in message
    assert "b.toml" in message


def test_load_fixtures_sorted_by_filename(tmp_path: Path) -> None:
    write(tmp_path, "b.toml", 'family = "second"\n\n[[case]]\nid = "b"\nquery = "q"\nabstain = true\n')
    write(tmp_path, "a.toml", 'family = "first"\n\n[[case]]\nid = "a"\nquery = "q"\nabstain = true\n')
    write(tmp_path, "ignored.txt", "not toml")
    assert [family.name for family in load_fixtures(tmp_path)] == ["first", "second"]
