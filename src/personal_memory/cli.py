from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime
import json
import sys
import tempfile
from pathlib import Path

from personal_memory.check import check_brain
from personal_memory.evals.adapters import ADAPTERS
from personal_memory.evals.baseline import BASELINE_PATH, compare, gate, to_baseline
from personal_memory.evals.receipt import write_receipt
from personal_memory.evals.report import render
from personal_memory.evals.runner import DEFAULT_CORPUS, DEFAULT_FIXTURES, run
from personal_memory.filing import Outcome, Proposal, apply, list_queue, note, submit
from personal_memory.get import get_note
from personal_memory.recall import recall
from personal_memory.unfiled import unfiled


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="personal-memory",
        description="Hosted memory for coding agents. Clients paste a URL and a key.",
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

    remember_parser = sub.add_parser(
        "remember",
        help="Search a brain and print evidence cards",
    )
    remember_parser.add_argument(
        "brain",
        type=Path,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )
    remember_parser.add_argument(
        "query",
        nargs="+",
        help="Words to search for",
    )
    remember_parser.add_argument(
        "--historical",
        action="store_true",
        help="Include superseded notes. Default is current notes only.",
    )

    revisit_parser = sub.add_parser(
        "revisit",
        help="Fetch one note by id or path, with frontmatter intact",
    )
    revisit_parser.add_argument(
        "brain",
        type=Path,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )
    revisit_parser.add_argument(
        "key",
        help="Note id (alex-rivera) or path relative to the brain",
    )

    def brain_arg(p: argparse.ArgumentParser) -> None:
        p.add_argument("brain", type=Path, help="Folder of markdown notes (for example examples/demo-brain)")
        p.add_argument("--sources", default="sources", metavar="DIR", help="Immutable dump folder inside the brain (default sources)")
        p.add_argument("--json", action="store_true", help="Print the result as JSON for an agent to read")

    draft_parser = sub.add_parser(
        "draft",
        help="Validate a filing proposal (JSON) and queue it. Writes no note.",
    )
    brain_arg(draft_parser)
    draft_parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        help="Proposal JSON: kind, provenance, confidence, as_of, and the kind's fields. Default stdin.",
    )

    pending_parser = sub.add_parser("pending", help="List queued proposals and what the engine thinks of each")
    brain_arg(pending_parser)

    file_parser = sub.add_parser(
        "file",
        help="Write queued proposals: every high-confidence one, or the one you name at any confidence",
    )
    brain_arg(file_parser)
    file_parser.add_argument("id", nargs="?", help="Proposal id to write regardless of confidence")

    note_parser = sub.add_parser(
        "note",
        help="Save one fact now: append to a note, or stub-create one at --path",
    )
    brain_arg(note_parser)
    note_parser.add_argument("claim", help="One fact, one line")
    note_parser.add_argument(
        "--provenance",
        required=True,
        help="Who proposed it and when, for example 'user, 2026-09-10' or 'agent:claude-code, 2026-09-10'",
    )
    note_parser.add_argument("--target", help="Note id to append the fact to")
    note_parser.add_argument("--path", help="Where to create a new note when there is no target")
    note_parser.add_argument("--type", help="Note type for a new note")
    note_parser.add_argument("--as-of", dest="as_of", help="When the fact was true (default UTC calendar day)")

    inbox_parser = sub.add_parser("inbox", help="List files under sources/ that no note has filed yet")
    brain_arg(inbox_parser)

    mcp_parser = sub.add_parser(
        "mcp",
        help="Start the stdio MCP server (tests, CI, Layer 1 evals). v1 clients use serve.",
    )
    mcp_parser.add_argument(
        "--brain",
        type=Path,
        required=True,
        help="Folder of markdown notes (for example examples/demo-brain)",
    )
    mcp_parser.add_argument(
        "--sources",
        default="sources",
        metavar="DIR",
        help="Immutable dump folder inside the brain (default sources)",
    )

    serve_parser = sub.add_parser(
        "serve",
        help="Start the hosted MCP server. Clients paste the URL and a key.",
    )
    serve_parser.add_argument(
        "--key",
        default=None,
        help="Shared secret sent as Authorization: Bearer. Prefer PERSONAL_MEMORY_API_KEY.",
    )
    serve_parser.add_argument(
        "--brain",
        type=Path,
        default=None,
        help="Folder store used as a stub until Postgres. Default is an empty temp folder.",
    )
    serve_parser.add_argument(
        "--sources",
        default="sources",
        metavar="DIR",
        help="Immutable dump folder inside the brain (default sources)",
    )
    serve_parser.add_argument("--host", default="127.0.0.1", help="Bind address (default 127.0.0.1)")
    serve_parser.add_argument("--port", type=int, default=8000, help="Bind port (default 8000)")

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
    if args.command == "serve":
        return _run_serve(args)
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
    if args.command == "eval":
        return _run_eval_gate(args.main_baseline, args.corpus, args.fixtures)

    root = args.brain.expanduser().resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    if args.command == "check":
        return _run_check(root)
    if args.command == "remember":
        return _run_remember(root, " ".join(args.query), historical=args.historical)
    if args.command == "revisit":
        return _run_revisit(root, args.key)
    if args.command == "mcp":
        return _run_mcp(root, args.sources)
    if args.command == "draft":
        return _run_draft(root, args.file, args.sources, args.json)
    if args.command == "pending":
        return _run_pending(root, args.sources, args.json)
    if args.command == "file":
        return _run_file(root, args.id, args.sources, args.json)
    if args.command == "note":
        return _run_note(root, args)
    return _run_inbox(root, args.sources, args.json)


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


def _run_check(root: Path) -> int:
    result = check_brain(root)
    print(f"{root}: {result.notes} notes, {result.skipped} skipped")
    for issue in result.issues:
        rel = issue.path.relative_to(root)
        print(f"  {rel}: {issue.message}", file=sys.stderr)
    if not result.ok:
        return 1
    print("ok")
    return 0


def _run_remember(root: Path, query: str, *, historical: bool) -> int:
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


def _run_revisit(root: Path, key: str) -> int:
    note = get_note(root, key)
    if note is None:
        print("the brain does not have this")
        return 0
    print(note.text, end="" if note.text.endswith("\n") else "\n")
    return 0


def _run_mcp(root: Path, sources: str) -> int:
    from personal_memory.mcp import serve

    serve(root, sources=sources)
    return 0


def _run_serve(args: argparse.Namespace) -> int:
    from personal_memory.http import MCP_PATH, resolve_api_key, serve_http

    try:
        key = resolve_api_key(args.key)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2
    stub: tempfile.TemporaryDirectory[str] | None = None
    if args.brain is None:
        stub = tempfile.TemporaryDirectory(prefix="personal-memory-stub-")
        root = Path(stub.name)
        store = "empty stub folder (Postgres is a later slice)"
    else:
        root = args.brain.expanduser().resolve()
        if not root.is_dir():
            print(f"not a directory: {root}", file=sys.stderr)
            return 2
        store = f"{root} (folder stub until Postgres)"
    display_host = "127.0.0.1" if args.host in ("0.0.0.0", "::") else args.host
    print(f"store: {store}")
    print(f"listening: http://{display_host}:{args.port}{MCP_PATH}")
    try:
        serve_http(root, key, sources=args.sources, host=args.host, port=args.port)
    finally:
        if stub is not None:
            stub.cleanup()
    return 0


def _run_draft(root: Path, file: Path | None, sources: str, as_json: bool) -> int:
    raw = sys.stdin.read() if file is None else file.read_text(encoding="utf-8")
    try:
        proposal = Proposal.from_dict(json.loads(raw))
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        print(f"proposal must be a JSON object with kind, provenance, confidence, as_of: {exc}", file=sys.stderr)
        return 2
    outcome = submit(root, proposal, sources_dir=sources)
    _print_outcomes([outcome], as_json)
    return 0 if outcome.status == "queued" else 1


def _run_pending(root: Path, sources: str, as_json: bool) -> int:
    items = list_queue(root, sources_dir=sources)
    if as_json:
        print(json.dumps([{"id": q.proposal_id, "submitted_at": q.submitted_at, "proposal": asdict(q.proposal), "outcome": asdict(q.outcome)} for q in items], indent=2))
        return 0
    if not items:
        print("queue is empty")
        return 0
    for item in items:
        p = item.proposal
        what = p.claim if p.kind == "append" else f"{p.path} ({p.title})"
        print(f"{item.proposal_id}  {p.kind:<9} {item.outcome.status:<9} {item.outcome.confidence or p.confidence:<6} {what}")
        if item.outcome.reason:
            print(f"  {item.outcome.reason}")
    return 0


def _run_file(root: Path, proposal_id: str | None, sources: str, as_json: bool) -> int:
    outcomes = apply(root, proposal_id=proposal_id, sources_dir=sources)
    _print_outcomes(outcomes, as_json)
    if proposal_id is not None and outcomes and outcomes[0].status not in ("inserted", "superseded"):
        return 1
    return 0


def _run_note(root: Path, args: argparse.Namespace) -> int:
    outcome = note(
        root,
        args.claim,
        args.provenance,
        target=args.target,
        path=args.path,
        type=args.type,
        as_of=args.as_of,
        sources_dir=args.sources,
    )
    _print_outcomes([outcome], args.json)
    return 0 if outcome.status in ("inserted", "queued") else 1


def _run_inbox(root: Path, sources: str, as_json: bool) -> int:
    result = unfiled(root, sources_dir=sources)
    if as_json:
        print(json.dumps({"sources": result.sources, "unfiled": [p.as_posix() for p in result.unfiled]}, indent=2))
        return 0
    print(f"{result.sources} files under {sources}/, {len(result.unfiled)} unfiled")
    for path in result.unfiled:
        print(f"  {path.as_posix()}")
    return 0


def _print_outcomes(outcomes: list[Outcome], as_json: bool) -> None:
    if as_json:
        print(json.dumps([asdict(o) for o in outcomes], indent=2))
        return
    if not outcomes:
        print("nothing to apply")
        return
    for o in outcomes:
        line = f"{o.status}  {o.proposal_id}"
        if o.confidence:
            line += f"  confidence: {o.confidence}"
        print(line)
        for path in o.paths:
            print(f"  wrote {path}")
        if o.target and o.status in ("duplicate", "blocked"):
            print(f"  target: {o.target}")
        if o.reason:
            print(f"  {o.reason}")
        if o.candidates:
            print(f"  candidates: {', '.join(o.candidates)}")
        for kind, tally in o.placement.items():
            if tally:
                folders = ", ".join(f"{folder} ({n})" for folder, n in sorted(tally.items(), key=lambda kv: -kv[1]))
                print(f"  {kind} live in: {folders}")


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
    corpus = _resolve(corpus)
    fixtures = _resolve(fixtures)
    if not corpus.is_dir():
        print(f"not a directory: {corpus}", file=sys.stderr)
        return 2
    if not fixtures.exists():
        print(f"fixtures path does not exist: {fixtures}", file=sys.stderr)
        return 2
    try:
        fresh = run(corpus, fixtures, list(ADAPTERS))
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
