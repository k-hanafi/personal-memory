# Personal Memory

This GitHub repo is **private** until v1 is something a stranger can install.

Personal Memory is a personal brain for coding agents (Claude Code, Codex, Cursor). The
brain is a git folder of markdown. The engine answers with citations,
freshness, and confidence. Vector search is optional and off unless you turn
it on later.

The plan lives in [docs/v1-spec.md](docs/v1-spec.md). Read that before writing
code.

## Status

2026-09-07: renamed from pith. Spec plus a schema checker. No MCP server yet.
Filing loop is specified in `docs/v1-spec.md` (sources dump, agent proposes,
the engine applies, human reviews low confidence).

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
personal-memory check examples/demo-brain
pytest
```

`python3 -m venv .venv` creates a project-local install folder so Personal Memory
does not land in your system Python. `source .venv/bin/activate` makes that folder
the active Python for this terminal. `python -m pip install -e ".[dev]"` installs
the CLI plus test tools. The `-e` means edits to `src/` show up without reinstalling.

## Evals

Retrieval is measured by fixed questions against a fictional corpus. `recall` is our
engine. `grep` is a plain text search run on the same questions, so a reader can see
what searching the folder already gets you before installing anything.

| family | recall | grep |
|---|---|---|
| abstention | 2/6 | 1/6 |
| citation | 4/6 | 0/6 |
| contradiction | 4/4 | 2/4 |
| named-thing | 11/12 | 2/12 |
| supersession | 7/8 | 2/8 |

These numbers are for the fictional corpus in `evals/brain/` and match the committed
baseline in `evals/baselines/main.json`. Cases that fail today are capability targets,
not bugs in the fixtures. How scoring and the CI gate work is in
[docs/evals-spec.md](docs/evals-spec.md).

```bash
personal-memory eval run
personal-memory eval run --update-baseline
bash scripts/eval-gate.sh
```

`eval run` prints the table and writes a receipt to `evals/runs/`. `--update-baseline`
rewrites `evals/baselines/main.json` from that run. `scripts/eval-gate.sh` compares a
fresh run to the baseline on `origin/main` and exits 1 if a passing `recall` case broke.

## Layout

| Path | What it is |
|---|---|
| `docs/v1-spec.md` | Product plan. Wins over code until we change it. |
| `examples/demo-brain/` | Fake notes for tests and a future install walkthrough |
| `src/personal_memory/` | Engine (today: frontmatter check only) |
