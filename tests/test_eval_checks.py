from personal_memory.evals.adapters import Hit
from personal_memory.evals.checks import (
    check_abstain,
    check_also_present,
    check_case,
    check_contradiction,
    check_expect_confidence,
    check_expect_line,
    check_expect_path,
    check_expect_status,
    check_forbid_paths,
)
from personal_memory.evals.fixtures import AlsoPresent, Case


def hit(path: str, status: str = "current", start: int = 10, end: int = 12, **kwargs) -> Hit:
    return Hit(
        path=path,
        start_line=start,
        end_line=end,
        status=status,
        confidence=kwargs.get("confidence", "high"),
        contradicted_by=kwargs.get("contradicted_by", ()),
    )


NEW = hit("40-areas/teaching-load-2026-09.md")
OLD = hit("40-areas/teaching-load-2026-01.md", status="superseded", confidence="medium")
HITS = [NEW, OLD]


def test_unset_fields_are_skipped() -> None:
    case = Case(id="c", query="q")
    assert check_case(case, []) is None
    assert check_case(case, HITS) is None


def test_abstain() -> None:
    case = Case(id="c", query="q", abstain=True)
    assert check_abstain(case, []) is None
    assert check_abstain(case, HITS) == "abstain"


def test_expect_path() -> None:
    case = Case(id="c", query="q", expect_path=NEW.path)
    assert check_expect_path(case, HITS) is None
    assert check_expect_path(case, [OLD, NEW]) == "expect_path"
    assert check_expect_path(case, []) == "expect_path"


def test_expect_line() -> None:
    inside = Case(id="c", query="q", expect_path=NEW.path, expect_line=11)
    edge = Case(id="c", query="q", expect_path=NEW.path, expect_line=12)
    outside = Case(id="c", query="q", expect_path=NEW.path, expect_line=13)
    assert check_expect_line(inside, HITS) is None
    assert check_expect_line(edge, HITS) is None
    assert check_expect_line(outside, HITS) == "expect_line"
    assert check_expect_line(inside, []) == "expect_line"


def test_expect_status() -> None:
    case = Case(id="c", query="q", expect_status="current")
    assert check_expect_status(case, HITS) is None
    assert check_expect_status(case, [OLD]) == "expect_status"
    assert check_expect_status(case, []) == "expect_status"


def test_expect_confidence() -> None:
    case = Case(id="c", query="q", expect_confidence="high")
    assert check_expect_confidence(case, HITS) is None
    assert check_expect_confidence(case, [OLD]) == "expect_confidence"
    assert check_expect_confidence(case, []) == "expect_confidence"


def test_forbid_paths_only_looks_at_top_five() -> None:
    case = Case(id="c", query="q", forbid_paths=("bad.md",))
    filler = [hit(f"{n}.md") for n in range(5)]
    assert check_forbid_paths(case, filler) is None
    assert check_forbid_paths(case, filler + [hit("bad.md")]) is None
    assert check_forbid_paths(case, filler[:4] + [hit("bad.md")]) == "forbid_paths"
    assert check_forbid_paths(case, []) is None


def test_also_present_requires_exact_status() -> None:
    case = Case(id="c", query="q", also_present=(AlsoPresent(OLD.path, "superseded"),))
    assert check_also_present(case, HITS) is None
    assert check_also_present(case, [NEW]) == "also_present"
    wrong_status = hit(OLD.path, status="current")
    assert check_also_present(case, [NEW, wrong_status]) == "also_present"


def test_contradiction_needs_every_path_to_name_the_others() -> None:
    a, b, c = "a.md", "b.md", "c.md"
    case = Case(id="c", query="q", contradiction=(a, b))
    good = [hit(a, contradicted_by=(b, c)), hit(b, contradicted_by=(a,)), hit(c)]
    assert check_contradiction(case, good) is None
    missing_b = [hit(a, contradicted_by=(b,))]
    assert check_contradiction(case, missing_b) == "contradiction"
    one_way = [hit(a, contradicted_by=(b,)), hit(b, contradicted_by=())]
    assert check_contradiction(case, one_way) == "contradiction"


def test_check_case_returns_first_failure_in_fixed_order() -> None:
    everything_wrong = Case(
        id="c",
        query="q",
        expect_path="other.md",
        expect_line=1,
        expect_status="superseded",
        expect_confidence="low",
        forbid_paths=(NEW.path,),
        also_present=(AlsoPresent("missing.md", "current"),),
        contradiction=("x.md", "y.md"),
    )
    assert check_case(everything_wrong, HITS) == "expect_path"

    order = [
        (Case(id="c", query="q", abstain=True), "abstain"),
        (Case(id="c", query="q", expect_path="other.md", expect_status="superseded"), "expect_path"),
        (Case(id="c", query="q", expect_status="superseded", expect_confidence="low"), "expect_status"),
        (Case(id="c", query="q", expect_confidence="low", expect_path=NEW.path, expect_line=1), "expect_confidence"),
        (Case(id="c", query="q", expect_path=NEW.path, expect_line=1, forbid_paths=(NEW.path,)), "expect_line"),
        (Case(id="c", query="q", forbid_paths=(NEW.path,), also_present=(AlsoPresent("m.md", "current"),)), "forbid_paths"),
        (Case(id="c", query="q", also_present=(AlsoPresent("m.md", "current"),), contradiction=("x.md", "y.md")), "also_present"),
        (Case(id="c", query="q", contradiction=("x.md", "y.md")), "contradiction"),
    ]
    for case, expected in order:
        assert check_case(case, HITS) == expected

    passing = Case(
        id="c",
        query="q",
        expect_path=NEW.path,
        expect_line=10,
        expect_status="current",
        expect_confidence="high",
        forbid_paths=("nowhere.md",),
        also_present=(AlsoPresent(OLD.path, "superseded"),),
    )
    assert check_case(passing, HITS) is None
