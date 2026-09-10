from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess

from personal_memory.evals.adapters import ADAPTERS, Hit
from personal_memory.evals.checks import check_case
from personal_memory.evals.fixtures import Family, load_fixture_file, load_fixtures

TOP_N = 5


def fixtures_hash(fixtures: Path, corpus_root: Path) -> str:
    """sha256 over every fixture file and every corpus note, as relative path plus bytes."""
    digest = hashlib.sha256()
    fixture_files = [fixtures] if fixtures.is_file() else sorted(fixtures.glob("*.toml"))
    for root, paths in ((fixtures, fixture_files), (corpus_root, sorted(corpus_root.rglob("*.md")))):
        for path in paths:
            relative = path.name if path == root else path.relative_to(root).as_posix()
            digest.update(relative.encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def run(
    corpus_root: Path,
    fixtures: Path,
    adapters: list[str],
    families: list[str] | None = None,
) -> dict:
    """Run every case through every requested adapter and return the receipt."""
    loaded = [load_fixture_file(fixtures)] if fixtures.is_file() else load_fixtures(fixtures)
    if families is not None:
        loaded = [family for family in loaded if family.name in families]
    if not loaded:
        raise ValueError(f"no fixture families loaded from {fixtures}")

    return {
        "commit": _git_commit(),
        "fixtures_hash": fixtures_hash(fixtures, corpus_root),
        "corpus": str(corpus_root),
        "fixtures": str(fixtures),
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "adapters": {name: _run_adapter(name, corpus_root, loaded) for name in adapters},
    }


def _run_adapter(name: str, corpus_root: Path, families: list[Family]) -> dict:
    search = ADAPTERS[name]
    result: dict = {"families": {}, "superseded_leaks": 0}
    abstain_total = 0
    abstain_correct = 0

    for family in families:
        cases: dict[str, dict] = {}
        ranked_total = 0
        top1 = 0
        top5 = 0
        for case in family.cases:
            hits = search(corpus_root, case.query, case.historical)
            failure = check_case(case, hits)
            cases[case.id] = {
                "pass": failure is None,
                "failure": failure,
                "holdout": case.holdout,
                "hits": [_hit_dict(hit) for hit in hits[:TOP_N]],
            }
            if case.expect_path is not None:
                top_paths = [hit.path for hit in hits[:TOP_N]]
                ranked_total += 1
                top1 += top_paths[:1] == [case.expect_path]
                top5 += case.expect_path in top_paths
            if case.abstain:
                abstain_total += 1
                abstain_correct += not hits
            if not case.historical and _superseded_leak(hits):
                result["superseded_leaks"] += 1
        result["families"][family.name] = {
            "passed": sum(record["pass"] for record in cases.values()),
            "total": len(cases),
            "hit_at_1": _ratio(top1, ranked_total),
            "recall_at_5": _ratio(top5, ranked_total),
            "cases": cases,
        }

    result["abstention_accuracy"] = _ratio(abstain_correct, abstain_total)
    return result


def _hit_dict(hit: Hit) -> dict:
    return {**asdict(hit), "contradicted_by": list(hit.contradicted_by)}


def _superseded_leak(hits: list[Hit]) -> bool:
    statuses = [hit.status for hit in hits]
    if "current" not in statuses:
        return False
    last_current = len(statuses) - 1 - statuses[::-1].index("current")
    return "superseded" in statuses[:last_current]


def _ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def _git_commit() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return completed.stdout.strip()
