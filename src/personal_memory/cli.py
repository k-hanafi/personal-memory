from __future__ import annotations

import argparse
from datetime import datetime
import sys
from pathlib import Path

from personal_memory.check import check_brain
from personal_memory.evals.adapters import ADAPTERS
from personal_memory.evals.receipt import write_receipt
from personal_memory.evals.report import render
from personal_memory.evals.runner import run
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
    eval_run_parser.add_argument(
        "--corpus",
        type=Path,
        default=Path("evals/brain"),
        help="Folder of markdown notes to search (default evals/brain)",
    )
    eval_run_parser.add_argument(
        "--fixtures",
        type=Path,
        default=Path("evals/fixtures"),
        help="Folder of TOML fixture files, or one file (default evals/fixtures)",
    )
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

    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args.brain)
    if args.command == "recall":
        return _run_recall(args.brain, " ".join(args.query), historical=args.historical)
    if args.command == "get":
        return _run_get(args.brain, args.key)
    if args.command == "eval":
        return _run_eval(
            args.corpus,
            args.fixtures,
            adapters=args.adapter or list(ADAPTERS),
            families=args.family,
            out=args.out,
        )
    parser.error(f"unknown command {args.command}")
    return 2


def _run_check(brain: Path) -> int:
    root = brain.expanduser().resolve()
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
    root = brain.expanduser().resolve()
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
    root = brain.expanduser().resolve()
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
) -> int:
    corpus = corpus.expanduser()
    fixtures = fixtures.expanduser()
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
    print(render(receipt))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
