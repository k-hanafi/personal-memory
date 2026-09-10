from __future__ import annotations

from personal_memory.evals.adapters import Hit
from personal_memory.evals.fixtures import Case


def check_abstain(case: Case, hits: list[Hit]) -> str | None:
    if not case.abstain:
        return None
    return None if not hits else "abstain"


def check_expect_path(case: Case, hits: list[Hit]) -> str | None:
    if case.expect_path is None:
        return None
    return None if hits and hits[0].path == case.expect_path else "expect_path"


def check_expect_line(case: Case, hits: list[Hit]) -> str | None:
    if case.expect_line is None:
        return None
    if hits and hits[0].start_line <= case.expect_line <= hits[0].end_line:
        return None
    return "expect_line"


def check_expect_status(case: Case, hits: list[Hit]) -> str | None:
    if case.expect_status is None:
        return None
    return None if hits and hits[0].status == case.expect_status else "expect_status"


def check_expect_confidence(case: Case, hits: list[Hit]) -> str | None:
    if case.expect_confidence is None:
        return None
    return None if hits and hits[0].confidence == case.expect_confidence else "expect_confidence"


def check_forbid_paths(case: Case, hits: list[Hit]) -> str | None:
    if not case.forbid_paths:
        return None
    top = {hit.path for hit in hits[:5]}
    return "forbid_paths" if any(path in top for path in case.forbid_paths) else None


def check_also_present(case: Case, hits: list[Hit]) -> str | None:
    if not case.also_present:
        return None
    for entry in case.also_present:
        if not any(hit.path == entry.path and hit.status == entry.status for hit in hits):
            return "also_present"
    return None


def check_contradiction(case: Case, hits: list[Hit]) -> str | None:
    if not case.contradiction:
        return None
    listed = set(case.contradiction)
    by_path = {hit.path: hit for hit in hits}
    for path in case.contradiction:
        hit = by_path.get(path)
        if hit is None or not (listed - {path}) <= set(hit.contradicted_by):
            return "contradiction"
    return None


CHECKS = (
    check_abstain,
    check_expect_path,
    check_expect_status,
    check_expect_confidence,
    check_expect_line,
    check_forbid_paths,
    check_also_present,
    check_contradiction,
)


def check_case(case: Case, hits: list[Hit]) -> str | None:
    """Return the first failing field name in the fixed order, or None if the case passes."""
    for check in CHECKS:
        failed = check(case, hits)
        if failed is not None:
            return failed
    return None
