from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pith.check import check_brain


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pith",
        description="Git-native memory for coding agents. v1 is schema check only.",
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

    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args.brain)
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


if __name__ == "__main__":
    raise SystemExit(main())
