# Personal Memory

This GitHub repo is **private** until v1 is something a stranger can install.

Personal Memory is a personal brain for coding agents (Claude Code, Codex, Cursor). The
brain is a git folder of markdown. The engine answers with citations,
freshness, and confidence. Vector search is optional and off unless you turn
it on later.

The plan lives in [docs/v1-spec.md](docs/v1-spec.md). Read that before writing
code.

## Status

2026-09-12: spec locked. `check` validates frontmatter. `recall` returns
evidence cards. `get` fetches one note by id or path. Layer 1 evals are
complete (`personal-memory eval run`, committed baseline, `eval-gate` CI).
The write path exists (`propose`, `queue`, `apply`, `remember`, `unfiled`).
No MCP server yet. The engine holds no model: the coding agent decides what
to file, the engine validates and writes. See the Write section of
`docs/v1-spec.md`.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
personal-memory check examples/demo-brain
personal-memory recall examples/demo-brain teaching load
personal-memory get examples/demo-brain alex-rivera
personal-memory eval run
bash scripts/eval-gate.sh
```

## Writing to a brain

```bash
personal-memory remember ~/brain "Dean approved the sabbatical." --provenance "user, 2026-09-10" --target sabbatical-plan
personal-memory propose ~/brain proposal.json
personal-memory queue ~/brain
personal-memory apply ~/brain
personal-memory unfiled ~/brain
```

`remember` saves one fact as a dated line in the note's `## Log`, or stub-creates a
note when you pass `--path` and `--type` instead of `--target`. `propose` queues a
JSON proposal (`create`, `append`, or `supersede`) after validating it against the
brain. `apply` writes every high-confidence proposal; `apply <id>` writes one you
chose. High confidence needs a boring signal (the user said it, a real `sources/`
file, or an exact-id target), otherwise the proposal waits in the queue for you.
`unfiled` lists files under `sources/` that no note names yet.

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
| named-thing | 10/11 | 2/11 |
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
| `docs/evals-spec.md` | Eval architecture, fixtures, and the CI gate. |
| `examples/demo-brain/` | Fake notes for tests and a future install walkthrough |
| `evals/brain/` | Fictional Layer 1 eval corpus |
| `src/personal_memory/` | Engine: `check`, `recall`, `get`, filing (`propose`, `apply`, `remember`), `unfiled`, and `eval` |
