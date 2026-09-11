from __future__ import annotations

import argparse
from datetime import datetime
import json
import sys
from pathlib import Path

from personal_memory.check import check_brain
from personal_memory.evals.adapters import ADAPTERS
from personal_memory.evals.baseline import BASELINE_PATH, compare, gate, to_baseline
from personal_memory.evals.receipt import write_receipt
from personal_memory.evals.report import render
from personal_memory.evals.runner import DEFAULT_CORPUS, DEFAULT_FIXTURES, run
from personal_memory.get import get_note
from personal_memory.recall import recall


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="personal-memory",
        description="Git-native memory for coding agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    check_parser = sub.add_parser(
        "check",
        help="Validate frontmatter on every note in a brain folder",
    )
    check_parser.add_argument(
        "brain",
        type=Path,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )

    recall_parser = sub.add_parser(
        "recall",
        help="Search a brain and print evidence cards",
    )
    recall_parser.add_argument(
        "brain",
        type=Path,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )
    recall_parser.add_argument(
        "query",
        nargs="+",
        help="Words to search for",
    )
    recall_parser.add_argument(
        "--historical",
        action="store_true",
        help="Include superseded notes. Default is current notes only.",
    )

    get_parser = sub.add_parser(
        "get",
        help="Fetch one note by id or path, with frontmatter intact",
    )
    get_parser.add_argument(
        "brain",
        type=Path,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )
    get_parser.add_argument(
        "key",
        help="Note id (alex-rivera) or path relative to the brain",
    )

    eval_parser = sub.add_parser(
        "eval",
        help="Measure retrieval against fixture files",
    )
    eval_sub = eval_parser.add_subparsers(dest="eval_command", required=True)
    eval_run_parser = eval_sub.add_parser(
        "run",
        help="Run every fixture through each adapter, print the table, write a receipt",
    )
    _add_corpus_fixtures(eval_run_parser)
    eval_run_parser.add_argument(
        "--adapter",
        action="append",
        choices=sorted(ADAPTERS),
        help="Adapter to run. Repeatable. Default is every adapter.",
    )
    eval_run_parser.add_argument(
        "--family",
        action="append",
        help="Family to run. Repeatable. Default is every family.",
    )
    eval_run_parser.add_argument(
        "--out",
        type=Path,
        help="Where to write the receipt (default evals/runs/<UTC timestamp>.json)",
    )
    eval_run_parser.add_argument(
        "--baseline",
        type=Path,
        default=Path(BASELINE_PATH),
        help=f"Baseline the vs main column compares against, if the file exists (default {BASELINE_PATH})",
    )
    eval_run_parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Rewrite the baseline file from this run, keeping any existing justification",
    )
    eval_compare_parser = eval_sub.add_parser(
        "compare",
        help="Print which cases flipped between two receipts or baselines",
    )
    eval_compare_parser.add_argument("main", type=Path, help="Receipt or baseline to compare from")
    eval_compare_parser.add_argument("head", type=Path, help="Receipt or baseline to compare to")
    eval_gate_parser = eval_sub.add_parser(
        "gate",
        help="Run the suite and exit 1 if a gold recall case regressed against the main baseline",
    )
    _add_corpus_fixtures(eval_gate_parser)
    eval_gate_parser.add_argument(
        "--main-baseline",
        type=Path,
        required=True,
        help="Baseline as committed on main. A missing file means main has none yet.",
    )

    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args.brain)
    if args.command == "recall":
        return _run_recall(args.brain, " ".join(args.query), historical=args.historical)
    if args.command == "get":
        return _run_get(args.brain, args.key)
    if args.command == "eval" and args.eval_command == "run":
        return _run_eval(
            args.corpus,
            args.fixtures,
            adapters=args.adapter or list(ADAPTERS),
            families=args.family,
            out=args.out,
            baseline=args.baseline,
            update_baseline=args.update_baseline,
        )
    if args.command == "eval" and args.eval_command == "compare":
        return _run_eval_compare(args.main, args.head)
    return _run_eval_gate(args.main_baseline, args.corpus, args.fixtures)


def _add_corpus_fixtures(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="Folder of markdown notes to search (default evals/brain)",
    )
    parser.add_argument(
        "--fixtures",
        type=Path,
        default=DEFAULT_FIXTURES,
        help="Folder of TOML fixture files, or one file (default evals/fixtures)",
    )


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve()


def _run_check(brain: Path) -> int:
    root = _resolve(brain)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = check_brain(root)
    print(f"{root}: {result.notes} notes, {result.skipped} skipped")
    for issue in result.issues:
        rel = issue.path.relative_to(root)
        print(f"  {rel}: {issue.message}", file=sys.stderr)
    if not result.ok:
        return 1
    print("ok")
    return 0


def _run_recall(brain: Path, query: str, *, historical: bool) -> int:
    root = _resolve(brain)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    result = recall(root, query, historical=historical)
    if not result.cards:
        print("the brain does not have this")
        return 0
    for card in result.cards:
        print(f"{card.path}:{card.start_line}-{card.end_line}")
        print(f"  claim: {card.claim}")
        print(
            f"  status: {card.status}  as_of: {card.as_of}  "
            f"confidence: {card.confidence}"
        )
        if card.contradicted_by:
            print(f"  contradicted: {', '.join(card.contradicted_by)}")
    return 0


def _run_get(brain: Path, key: str) -> int:
    root = _resolve(brain)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    doc = get_note(root, key)
    if doc is None:
        print("the brain does not have this")
        return 0
    print(doc.text, end="" if doc.text.endswith("\n") else "\n")
    return 0


def _run_eval(
    corpus: Path,
    fixtures: Path,
    *,
    adapters: list[str],
    families: list[str] | None,
    out: Path | None,
    baseline: Path,
    update_baseline: bool,
) -> int:
    corpus = _resolve(corpus)
    fixtures = _resolve(fixtures)
    baseline = _resolve(baseline)
    if out is not None:
        out = _resolve(out)
    if not corpus.is_dir():
        print(f"not a directory: {corpus}", file=sys.stderr)
        return 2
    if not fixtures.exists():
        print(f"fixtures path does not exist: {fixtures}", file=sys.stderr)
        return 2
    try:
        receipt = run(corpus, fixtures, adapters, families)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    if out is None:
        stamp = datetime.fromisoformat(receipt["timestamp"]).strftime("%Y%m%dT%H%M%SZ")
        out = Path("evals/runs") / f"{stamp}.json"
    write_receipt(receipt, out)
    existing = _load_json(baseline)
    print(render(receipt, existing))
    print(out)
    if update_baseline:
        new_baseline = to_baseline(receipt)
        if existing is not None and "justification" in existing:
            new_baseline["justification"] = existing["justification"]
        write_receipt(new_baseline, baseline)
        print(baseline)
    return 0


def _run_eval_compare(main_path: Path, head_path: Path) -> int:
    main = _load_json(_resolve(main_path))
    head = _load_json(_resolve(head_path))
    if main is None or head is None:
        print(f"file not found: {main_path if main is None else head_path}", file=sys.stderr)
        return 2
    comparison = compare(main, head)
    for adapter in sorted(head["adapters"]):
        if adapter not in main["adapters"]:
            continue
        print(adapter)
        for family in head["adapters"][adapter]["families"]:
            improved = comparison.improved.get(adapter, {}).get(family, [])
            regressed = comparison.regressed.get(adapter, {}).get(family, [])
            print(f"  {family}  +{len(improved)} / -{len(regressed)}")
            for case_id in improved:
                print(f"    + {case_id}")
            for case_id in regressed:
                print(f"    - {case_id}")
    if comparison.hash_changed:
        print("fixtures hash changed")
    return 0


def _run_eval_gate(main_baseline_path: Path, corpus: Path, fixtures: Path) -> int:
    try:
        fresh = run(_resolve(corpus), _resolve(fixtures), list(ADAPTERS))
    except (OSError, ValueError) as exc:
        print(f"run eval gate from the repository root: {exc}", file=sys.stderr)
        return 2
    main_baseline = _load_json(_resolve(main_baseline_path))
    head_baseline = _load_json(_resolve(Path(BASELINE_PATH)))
    print(render(fresh, main_baseline))
    result = gate(fresh, main_baseline, head_baseline)
    for message in result.messages:
        print(message)
    print("gate: ok" if result.ok else "gate: FAIL")
    return 0 if result.ok else 1


def _load_json(path: Path) -> dict | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
